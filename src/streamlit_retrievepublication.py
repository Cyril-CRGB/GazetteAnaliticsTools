# streamlit_retrievepublication_optimized.py

import os
import math
import uuid
import asyncio
import aiohttp
import xmltodict
import pandas as pd
from decimal import Decimal
from datetime import datetime, date
from typing import Optional, List
from sqlalchemy import create_engine, text
from psycopg2.extras import execute_values
import time

# ── 1) DATABASE ENGINE ─────────────────────────────────────────────────────────

def get_engine():
    """
    Returns a cached SQLAlchemy engine for your Heroku Postgres, normalizing
    the URL scheme so SQLAlchemy can find the right dialect plugin.
    """
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("Please set the DATABASE_URL environment variable")
    # Heroku gives: postgres://user:pass@… which SQLAlchemy no longer recognizes
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    # Now SQLAlchemy will load the correct 'postgresql' dialect
    return create_engine(url, connect_args={"sslmode":"require"})


# ── 2) METADATA FETCHER ─────────────────────────────────────────────────────────

def fetch_metadata_for_date(
    target_day: date = None,
    tenant: str = "shab",
    page_size: int = 2000
) -> pd.DataFrame:
    """
    Calls the bulk-export API for `target_day` (defaults to today),
    filters to HR01/02/03, and returns a flat DataFrame of the metadata.
    """
    if target_day is None:
        target_day = date.today()
    iso_day = target_day.isoformat()
    
    API_BASE = "https://amtsblattportal.ch/api/v1/publications/xml"
    params = {
        "publicationStates":     "PUBLISHED",
        "publicationDate.start": iso_day,
        "publicationDate.end":   iso_day,
        "tenant":                tenant,
        "pageRequest.size":      page_size,
        "pageRequest.page":      0
    }
    
    import requests
    resp = requests.get(API_BASE, params=params)
    resp.raise_for_status()
    data = xmltodict.parse(resp.text)
    
    # namespace-agnostic root
    root_key = next(k for k in data if k.endswith("bulk-export"))
    pubs = data[root_key].get("publication", [])
    if not isinstance(pubs, list):
        pubs = [pubs]
    
    rubric_map = {"HR01":"New entries","HR02":"Change","HR03":"Deletion"}
    rows = []
    for pub in pubs:
        meta = pub.get("meta",{})
        sub  = meta.get("subRubric","")
        if sub not in rubric_map:
            continue
        
        rows.append({
            "ref":             pub.get("@ref"),
            "schemaLocation":  pub.get("@schemaLocation"),
            "id":              meta.get("id") or str(uuid.uuid4()),
            "entryType":       rubric_map[sub],
            "subRubric":       sub,
            "language":        meta.get("language"),
            "publicationDate": _parse_date(meta.get("publicationDate")),
            "legalRemedy":     meta.get("legalRemedy"),
            "cantons":         meta.get("cantons"),
            "title_en":        meta.get("title",{}).get("en")
        })
    return pd.DataFrame(rows)


# ── 3) ASYNC CONTENT FETCHER ────────────────────────────────────────────────────

async def fetch_single_ref(session: aiohttp.ClientSession, url: str, semaphore: asyncio.Semaphore) -> dict:
    """
    Fetch and parse a single publication XML URL with concurrency control.
    Returns the parsed data dict, or a dict with error info if failed.
    """
    async with semaphore:  # Limit concurrent requests
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                text = await response.text()
                result = parse_publication_xml(text)
                return {"status": "success", "data": result, "url": url}
        except aiohttp.ClientError as e:
            return {"status": "http_error", "error": str(e), "url": url}
        except Exception as e:
            return {"status": "parse_error", "error": str(e), "url": url}

def parse_publication_xml(xml_text: str) -> dict:
    """
    Parse publication XML and extract relevant data.
    """
    rubric_map = {"HR01":"New entries","HR02":"Change","HR03":"Deletion"}
    
    data = xmltodict.parse(xml_text)
    root_key = next((k for k in data if k.endswith("publication")), None)
    pub = data[root_key] if root_key else {}
    
    meta = pub.get("meta", {})
    content = pub.get("content", {})
    sub = meta.get("subRubric", "")
    
    # choose correct commons block
    commons = content.get("commonsActual") if sub == "HR03" else content.get("commonsNew")
    comp = commons.get("company", {}) or {}
    addr = comp.get("address", {}) or {}
    cap = commons.get("capital", {}) or {}
    rev = commons.get("revision", {}) or {}
    dele = content.get("transaction", {}).get("delete", {}) or {}
    
    return {
        # meta
        "id": meta.get("id"),
        "entryType": rubric_map.get(sub),
        "language": meta.get("language"),
        "publicationDate": _parse_date(meta.get("publicationDate")),
        "legalRemedy": meta.get("legalRemedy"),
        "cantons": meta.get("cantons"),
        "title_en": meta.get("title", {}).get("en"),
        # content
        "journal_date": _parse_date(content.get("journalDate")),
        "publication_text": content.get("publicationText"),
        # company
        "company_name": comp.get("name"),
        "company_uid": comp.get("uid"),
        "company_code13": comp.get("code13"),
        "company_seat": comp.get("seat"),
        "company_legalForm": comp.get("legalForm"),
        "company_street_and_number": _join(addr.get("street"), addr.get("houseNumber")),
        "company_zip_and_town": _join(addr.get("swissZipCode"), addr.get("town")),
        "company_purpose": commons.get("purpose"),
        # capital & revision
        "company_capital_nominal": _to_decimal(cap.get("nominal")),
        "company_capital_paid": _to_decimal(cap.get("paid")),
        "company_optingout": _to_bool(rev.get("optingOut")),
        # deletion
        "company_deletiondate": _parse_date(dele.get("deletionDate"))
    }

async def process_batch_async(refs: List[str], max_concurrent: int = 50) -> tuple[pd.DataFrame, dict]:
    """
    Process a batch of refs using async HTTP requests with concurrency control.
    Returns (dataframe, error_summary)
    """
    semaphore = asyncio.Semaphore(max_concurrent)
    
    # Configure session with connection pooling and timeouts
    connector = aiohttp.TCPConnector(
        limit=100,  # Total connection pool size
        limit_per_host=50,  # Max connections per host
        ttl_dns_cache=300,  # DNS cache TTL
        use_dns_cache=True,
    )
    
    timeout = aiohttp.ClientTimeout(total=30, connect=10)
    
    async with aiohttp.ClientSession(
        connector=connector,
        timeout=timeout,
        headers={'User-Agent': 'Publication-Fetcher/1.0'}
    ) as session:
        tasks = [fetch_single_ref(session, url, semaphore) for url in refs]
        results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Separate successful results from errors
    successful_records = []
    errors = {
        "http_errors": [],
        "parse_errors": [],
        "unexpected_exceptions": []
    }
    
    for result in results:
        if isinstance(result, Exception):
            # This shouldn't happen with our error handling, but just in case
            errors["unexpected_exceptions"].append({
                "error": str(result),
                "type": type(result).__name__
            })
        elif isinstance(result, dict):
            if result.get("status") == "success":
                successful_records.append(result["data"])
            elif result.get("status") == "http_error":
                errors["http_errors"].append({
                    "url": result["url"],
                    "error": result["error"]
                })
            elif result.get("status") == "parse_error":
                errors["parse_errors"].append({
                    "url": result["url"], 
                    "error": result["error"]
                })
    
    return pd.DataFrame(successful_records), errors

# ── 4) OPTIMIZED UPLOAD TO POSTGRES ──────────────────────────────────────────────

def push_data_to_db_batch(df: pd.DataFrame, table: str = "gazette_contentdata", batch_size: int = 1000):
    """
    Bulk upsert `df` into `table` by primary key `id`, processing in batches.
    """
    if df.empty:
        return
        
    # normalize: Python None for nulls
    df = df.where(pd.notnull(df), None)
    cols = df.columns.tolist()
    
    # Prepare the upsert SQL
    insert_sql = f"""
    INSERT INTO {table} ({','.join(cols)})
    VALUES %s
    ON CONFLICT (id) DO UPDATE
      SET {', '.join(f"{c}=EXCLUDED.{c}" for c in cols if c != "id")},
          fetched_at = NOW()
    """
    
    engine = get_engine()
    
    # Process in batches to avoid memory issues and improve performance
    total_rows = len(df)
    for i in range(0, total_rows, batch_size):
        batch_df = df.iloc[i:i + batch_size]
        values = batch_df.to_dict(orient="records")
        
        with engine.begin() as conn:
            raw = conn.connection
            with raw.cursor() as cur:
                execute_values(
                    cur, 
                    insert_sql, 
                    [[rec[c] for c in cols] for rec in values],
                    template=None, 
                    page_size=500
                )
        print(f"Processed batch {i//batch_size + 1}/{math.ceil(total_rows/batch_size)} ({len(batch_df)} rows)")


# ── 5) HELPERS ───────────────────────────────────────────────────────────────────

def _parse_date(val: str) -> Optional[date]:
    """
    Parse an ISO date string "YYYY-MM-DD" or fallback to None.
    Returns a datetime.date or None if parsing fails or val is falsy.
    """
    if not val or not isinstance(val, str):
        return None
    try:
        # Primary ISO format
        return datetime.strptime(val, "%Y-%m-%d").date()
    except ValueError:
        # Try European "DD.MM.YYYY" just in case
        try:
            return datetime.strptime(val, "%d.%m.%Y").date()
        except ValueError:
            return None

def _to_decimal(val) -> Optional[Decimal]:
    """
    Convert val to Decimal, or return None if it can't be parsed.
    """
    try:
        return Decimal(str(val))
    except Exception:
        return None

def _to_bool(val) -> Optional[bool]:
    """
    Convert val to bool (True for 'true', 'yes', '1'; False for 'false', 'no', '0'),
    or None if it's unrecognized.
    """
    if isinstance(val, bool):
        return val
    txt = str(val).strip().lower()
    if txt in ("true", "yes", "1"):
        return True
    if txt in ("false", "no", "0"):
        return False
    return None

def _join(a, b, sep=" "):
    if a and b:
        return f"{a}{sep}{b}"
    return a or b


# ── 6) MAIN ENTRYPOINT ─────────────────────────────────────────────────────────

async def main_async(target_day: Optional[date] = None, page_size: int = 3000, max_concurrent: int = 50):
    """
    Async version of main function with concurrent processing.
    """
    if target_day is None:
        target_day = date.today()

    start_time = time.time()
    print(f"Starting fetch for {target_day}")

    # 1) fetch metadata, extract refs
    meta_df = fetch_metadata_for_date(target_day=target_day, page_size=page_size)
    refs = meta_df["ref"].dropna().unique().tolist()
    print(f"Found {len(refs)} publication refs to process")

    # 2) Process all refs with async concurrency
    content_df, errors = await process_batch_async(refs, max_concurrent=max_concurrent)
    
    # 3) Report on results and errors
    print(f"\n📊 PROCESSING SUMMARY:")
    print(f"  ✅ Successfully processed: {len(content_df)} publications")
    print(f"  ❌ Failed requests: {len(errors['http_errors']) + len(errors['parse_errors']) + len(errors['unexpected_exceptions'])}")
    
    # Show detailed error breakdown if there are any errors
    total_errors = sum(len(error_list) for error_list in errors.values())
    if total_errors > 0:
        print(f"\n🚨 ERROR BREAKDOWN:")
        if errors['http_errors']:
            print(f"  📡 HTTP/Network errors: {len(errors['http_errors'])}")
            # Show first few HTTP errors as examples
            for i, err in enumerate(errors['http_errors'][:3]):
                print(f"    • {err['url']}: {err['error']}")
            if len(errors['http_errors']) > 3:
                print(f"    • ... and {len(errors['http_errors']) - 3} more HTTP errors")
        
        if errors['parse_errors']:
            print(f"  🔧 XML parsing errors: {len(errors['parse_errors'])}")
            # Show first few parse errors as examples
            for i, err in enumerate(errors['parse_errors'][:3]):
                print(f"    • {err['url']}: {err['error']}")
            if len(errors['parse_errors']) > 3:
                print(f"    • ... and {len(errors['parse_errors']) - 3} more parse errors")
        
        if errors['unexpected_exceptions']:
            print(f"  ⚠️  Unexpected exceptions: {len(errors['unexpected_exceptions'])}")
            for err in errors['unexpected_exceptions']:
                print(f"    • {err['type']}: {err['error']}")
        
        print(f"\n💡 Note: {len(content_df)} successful records will still be saved to database")

    # 4) Upload successful results to database
    if not content_df.empty:
        push_data_to_db_batch(content_df)
        print(f"\n✅ Database upsert complete!")
    else:
        print(f"\n⚠️  No successful records to save to database")
    
    elapsed = time.time() - start_time
    success_rate = (len(content_df) / len(refs)) * 100 if refs else 0
    print(f"\n🎯 FINAL RESULTS:")
    print(f"  Total time: {elapsed:.2f} seconds")
    print(f"  Success rate: {success_rate:.1f}% ({len(content_df)}/{len(refs)})")
    
    # Return summary for programmatic use
    return {
        "total_refs": len(refs),
        "successful": len(content_df),
        "failed": total_errors,
        "errors": errors,
        "elapsed_time": elapsed
    }

def main(target_day: Optional[date] = None, page_size: int = 3000, max_concurrent: int = 50):
    """
    Synchronous wrapper for the async main function.
    """
    return asyncio.run(main_async(target_day, page_size, max_concurrent))

if __name__ == "__main__":
    main()