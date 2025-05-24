import os
import streamlit as st
import pandas as pd
import joblib
from sqlalchemy import create_engine
from dotenv import load_dotenv
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Connect to your database
@st.cache_resource 
def get_engine_resource():
    url = DATABASE_URL
    if not url:
        raise RuntimeError("DATABASE_URL is not set")
    # Normalize Heroku's URL prefix
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return create_engine(url, connect_args={"sslmode":"require"})

@st.cache_data(show_spinner=False)
def load_gazette_content(limit=None) -> pd.DataFrame:
    url = DATABASE_URL
    if not url:
        return pd.DataFrame()
    engine = get_engine_resource()
    sql = "SELECT * FROM gazette_contentdata ORDER BY fetched_at DESC"
    if limit:
        sql += f" LIMIT {int(limit)}"
    df = pd.read_sql(sql, engine)
    return df

