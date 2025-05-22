import os
import streamlit as st
import pandas as pd
import joblib
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")




# Connect to your database
@st.cache(suppress_st_warning=True, allow_output_mutation=True)
def connect_to_db():
    if not DATABASE_URL:
        st.error("DATABASE_URL is not set.")
        return None
    try:
        return psycopg2.connect(DATABASE_URL, sslmode="require", cursor_factory=RealDictCursor)
    except Exception as e:
        st.error(f"Connection to database failed: {e}")
        return None


@st.cache
def load_gazette_content(limit=None):
    conn = connect_to_db()
    if not conn: return pd.DataFrame()
    base = """
      SELECT * 
      FROM gazette_contentdata
      ORDER BY fetched_at DESC
    """
    if limit is not None:
        base += f"\nLIMIT {int(limit)}"
    df = pd.read_sql(base, conn)
    conn.close()
    return df
