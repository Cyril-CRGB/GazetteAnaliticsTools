import os, pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
load_dotenv()

def main():
    input_path  = "inputs/contentdata/gazette_contentdata_jupyter.csv"
    output_table = "gazette_contentdata"

    # 1. Read CSV, parse date columns into pandas datetime
    date_cols = ["publicationDate", "journal_date", "company_deletiondate"]
    df = pd.read_csv(input_path, parse_dates=date_cols, dayfirst=False)

    # 2. Convert pandas Timestamps to Python dates, coerce invalid → NaT
    for c in date_cols:
        df[c] = pd.to_datetime(df[c], errors="coerce").dt.date

    # 3. Replace any NaT (for dates) or NaN (for numeric/text) with Python None
    df = df.where(pd.notnull(df), None)

    # 4. Prepare insert
    cols   = list(df.columns)
    records = df.to_dict("records") 
    values = [[ rec[col] for col in cols ] for rec in records]

    insert_sql = f"""
    INSERT INTO {output_table} ({','.join(cols)})
    VALUES %s
    ON CONFLICT (id) DO NOTHING
    """

    # 5. Connect & execute
    conn = psycopg2.connect(os.getenv("DATABASE_URL"), sslmode="require")
    with conn, conn.cursor() as cur:
        execute_values(cur, insert_sql, values)

    print(f"Upserted {len(records)} rows into {output_table}")

if __name__ == "__main__":
    main()