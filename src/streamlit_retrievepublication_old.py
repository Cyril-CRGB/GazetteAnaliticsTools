# streamlit_retrievepublication.py

import os
import math
import uuid
import requests
import xmltodict
import pandas as pd
from decimal import Decimal
from datetime import datetime, date
from typing import Optional
from sqlalchemy import create_engine, text
from psycopg2.extras import execute_values

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


# ── 3) CONTENT FETCHER ──────────────────────────────────────────────────────────

def process_batch(refs: list[str]) -> pd.DataFrame:
    """
    Given a list of publication-XML URLs, fetch & flatten their content.
    Returns a DataFrame.
    """
    rubric_map = {"HR01":"New entries","HR02":"Change","HR03":"Deletion"}
    records = []
    
    for url in refs:
        resp = requests.get(url); resp.raise_for_status()
        data = xmltodict.parse(resp.text)
        root_key = next((k for k in data if k.endswith("publication")), None)
        pub      = data[root_key] if root_key else {}
        
        meta    = pub.get("meta",{})
        content = pub.get("content",{})
        sub     = meta.get("subRubric","")
        
        # choose correct commons block
        commons = content.get("commonsActual") if sub=="HR03" else content.get("commonsNew")
        comp    = commons.get("company",{}) or {}
        addr    = comp.get("address",{}) or {}
        cap     = commons.get("capital",{}) or {}
        rev     = commons.get("revision",{}) or {}
        dele    = content.get("transaction",{}).get("delete",{}) or {}
        
        rec = {
            # meta
            "id":                meta.get("id"),
            "entryType":         rubric_map.get(sub),
            "language":          meta.get("language"),
            "publicationDate":   _parse_date(meta.get("publicationDate")),
            "legalRemedy":       meta.get("legalRemedy"),
            "cantons":           meta.get("cantons"),
            "title_en":          meta.get("title",{}).get("en"),
            # content
            "journal_date":      _parse_date(content.get("journalDate")),
            "publication_text":  content.get("publicationText"),
            # company
            "company_name":      comp.get("name"),
            "company_uid":       comp.get("uid"),
            "company_code13":    comp.get("code13"),
            "company_seat":      comp.get("seat"),
            "company_legalForm": comp.get("legalForm"),
            "company_street_and_number":
                                 _join(addr.get("street"), addr.get("houseNumber")),
            "company_zip_and_town":
                                 _join(addr.get("swissZipCode"), addr.get("town")),
            "company_purpose":   commons.get("purpose"),
            # capital & revision
            "company_capital_nominal": _to_decimal(cap.get("nominal")),
            "company_capital_paid":    _to_decimal(cap.get("paid")),
            "company_optingout":       _to_bool(rev.get("optingOut")),
            # deletion
            "company_deletiondate":    _parse_date(dele.get("deletionDate"))
        }
        records.append(rec)
    
    return pd.DataFrame(records)


# ── 4) UPLOAD TO POSTGRES ────────────────────────────────────────────────────────

def push_data_to_db(df: pd.DataFrame, table: str="gazette_contentdata"):
    """
    Bulk upsert `df` into `table` by primary key `id`, skipping duplicates.
    """
    # normalize: Python None for nulls
    df = df.where(pd.notnull(df), None)
    cols = df.columns.tolist()
    values = df.to_dict(orient="records")
    
    insert_sql = f"""
    INSERT INTO {table} ({','.join(cols)})
    VALUES %s
    ON CONFLICT (id) DO UPDATE
      SET {', '.join(f"{c}=EXCLUDED.{c}" for c in cols if c!="id")},
          fetched_at = NOW()
    """
    engine = get_engine()
    with engine.begin() as conn:
        # use psycopg2 execute_values via raw connection
        raw = conn.connection
        with raw.cursor() as cur:
            execute_values(cur, insert_sql, [
                [rec[c] for c in cols] for rec in values
            ], template=None, page_size=500)
    

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

def main(target_day: Optional[date] = None, page_size: int = 3000):
    """
    Fetch & upsert for the given target_day (defaults to today)
    and using the given page_size (default 3000).
    """
    if target_day is None:
        target_day = date.today()

    # 1) fetch metadata, extract refs
    meta_df = fetch_metadata_for_date(target_day=target_day, page_size=page_size)
    refs    = meta_df["ref"].dropna().unique().tolist()
    
    # 2) split into two batches & process
    half = math.ceil(len(refs)/2)
    batches = [refs[:half], refs[half:]]
    
    for batch in batches:
        content_df = process_batch(batch)
        print(f"Processing batch of {len(batch)} refs → {len(content_df)} rows")
        push_data_to_db(content_df)
        print("Upsert complete.")

if __name__ == "__main__":
    main()
