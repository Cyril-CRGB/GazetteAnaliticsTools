#!/usr/bin/env python3
import os
import sys
import psycopg2
from dotenv import load_dotenv
load_dotenv()
# DATABASE_URL = os.getenv("DATABASE_URL")

def main():
    # 1. Grab the DATABASE_URL from env
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("❌ Please set the DATABASE_URL environment variable", file=sys.stderr)
        sys.exit(1)

    # 2. Connect
    conn = psycopg2.connect(DATABASE_URL, sslmode="require")
    try:
        with conn:
            with conn.cursor() as cur:
                # 3. Run the LPAD update for any code shorter than 4 chars
                cur.execute("""
                    UPDATE gazette_contentdata
                       SET company_legalform = LPAD(company_legalform, 4, '0')
                     WHERE char_length(company_legalform) < 4
                """)
                updated = cur.rowcount
        print(f"✅ Normalized company_legalform on {updated} rows.")
    finally:
        conn.close()

if __name__ == "__main__":
    main()