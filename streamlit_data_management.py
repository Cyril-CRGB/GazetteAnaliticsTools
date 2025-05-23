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
@st.cache_resource #(suppress_st_warning=True, allow_output_mutation=True)
def connect_to_db():
    if not DATABASE_URL:
        st.error("DATABASE_URL is not set.")
        return None
    try:
        return psycopg2.connect(DATABASE_URL, sslmode="require") #, cursor_factory=RealDictCursor
    except Exception as e:
        st.error(f"Connection to database failed: {e}")
        return None


    # @st.cache_data(show_spinner=False)
    # def load_gazette_content(limit=None):
    #     conn = connect_to_db()
    #     if not conn: return pd.DataFrame()
    #     base = """
    #       SELECT * 
    #       FROM gazette_contentdata
    #       ORDER BY fetched_at DESC
    #     """
    #     if limit is not None:
    #         base += f"\nLIMIT {int(limit)}"
    #     df = pd.read_sql(base, conn)
    #     conn.close()
    #     return df

@st.cache_data(show_spinner=False)
def load_gazette_content(limit=None) -> pd.DataFrame:
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        return pd.DataFrame()
    # open, query, close each time
    conn = psycopg2.connect(DATABASE_URL, sslmode="require")
    sql = "SELECT * FROM gazette_contentdata ORDER BY fetched_at DESC"
    if limit:
        sql += f" LIMIT {int(limit)}"
    df = pd.read_sql(sql, conn)
    conn.close()
    return df

