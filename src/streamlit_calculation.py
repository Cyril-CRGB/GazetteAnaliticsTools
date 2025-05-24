import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
#import pingouin as pg
import numpy as np
from datetime import date
from typing import Optional, Tuple, List
#import re
#from scipy import stats
#from sklearn.preprocessing import LabelEncoder
#from sklearn.pipeline import Pipeline
#from feature_engine.encoding import OrdinalEncoder
#from sklearn.preprocessing import StandardScaler
#from sklearn.decomposition import PCA
#from sklearn.cluster import KMeans

from streamlit_data_management import load_gazette_content, get_engine_resource

@st.cache_data(show_spinner=False)
def show_columnsheaders_and_an_example(data: pd.DataFrame) -> pd.DataFrame:
    if data.empty:
        st.warning("No data available!")
        return pd.DataFrame()  # return empty DF so caller can handle it

    cols = data.columns.tolist()
    entry_types = ["New entries", "Change", "Deletion"]
    examples = {}

    for col in cols:
        ex_row = []
        for et in entry_types:
            series = data.loc[data["entrytype"] == et, col].dropna()
            ex_row.append(series.iloc[0] if not series.empty else "")
        examples[col] = ex_row

    df_examples = pd.DataFrame(examples, index=entry_types).T
    df_examples.columns = entry_types
    return df_examples


@st.cache_data(show_spinner=False)
def load_publication_coverage(year: int) -> pd.DataFrame:
    """
    Reads 'inputs/other/publications_<year>.csv', parses its dates,
    filters to that year, then compares against the DB for that same year.
    Returns a DataFrame with columns ['date','present'].
    """
    # 1) Load the CSV for that year, parse into datetimes
    path = f"inputs/other/publications_{year}.csv"
    df = pd.read_csv(
        path,
        #sep=";",
        parse_dates=["Publication"],
        dayfirst=True,
        infer_datetime_format=True,
        # coerce errors so bad rows become NaT
        date_parser=lambda s: pd.to_datetime(s, dayfirst=True, errors="coerce")
    )

    # 2) Filter to only that calendar year using the datetime64 column
    df = df[df["Publication"].dt.year == year].copy()

    # 3) Now extract a pure date column for display
    df["date"] = df["Publication"].dt.date

    # 4) Pull existing dates from the DB (as date objects)
    df_gaz = load_gazette_content(limit=None)
    existing = (
        pd.to_datetime(df_gaz["publicationdate"], errors="coerce")
          .dt.date
    )
    existing_year = {d for d in existing if d and d.year == year}

    # 5) Build coverage DataFrame
    all_dates = sorted(df["date"].dropna().unique())
    cov = pd.DataFrame({"date": all_dates})
    cov["present"] = cov["date"].isin(existing_year)

    return cov

@st.cache_data(show_spinner=False)
def get_new_clients_of_today() -> pd.DataFrame:
    """
    Returns only those rows from gazette_contentdata where
    entryType = "New entries" and publicationDate = today.
    """
    # 1) load everything
    df = load_gazette_content(limit=None)
    if df.empty:
        return pd.DataFrame()

    # 2) normalize and filter dates
    df["pubDate"] = (
        pd.to_datetime(df["publicationdate"], errors="coerce")
          .dt.date
    )
    today = date.today()

    # 3) filter to new entries *and* today’s date
    df_filtered = df[
        (df["entrytype"] == "New entries") &
        (df["pubDate"]    == today)
    ].copy()

    return df_filtered

@st.cache_data(show_spinner=False)
def get_publication_date_bounds() -> Tuple[Optional[date], Optional[date]]:
    """
    Returns (earliest_date, latest_date) from gazette_contentdata.publicationDate,
    or (None, None) if the table is empty.
    """
    engine = get_engine_resource()
    sql = """
        SELECT
          MIN(publicationDate) AS earliest,
          MAX(publicationDate) AS latest
        FROM gazette_contentdata
    """
    df = pd.read_sql(sql, engine)
    if df.empty:
        return None, None

    # Pull out the Timestamp values
    earliest_ts = df.at[0, "earliest"]
    latest_ts   = df.at[0, "latest"]

    # Convert to Python date
    earliest: Optional[date]
    latest:   Optional[date]

    if pd.isna(earliest_ts):
        earliest = None
    else:
        # If it's already a date or Timestamp, convert to date
        earliest = earliest_ts if isinstance(earliest_ts, date) else earliest_ts.date()  # type: ignore

    if pd.isna(latest_ts):
        latest = None
    else:
        latest = latest_ts if isinstance(latest_ts, date) else latest_ts.date()  # type: ignore

    return earliest, latest

@st.cache_data(show_spinner=False)
def find_duplicate_ids() -> List[str]:
    """
    Returns a list of any 'id' values in gazette_contentdata
    that occur more than once. If there are no duplicates,
    returns an empty list.
    """
    engine = get_engine_resource()
    sql = """
      SELECT id
      FROM gazette_contentdata
      GROUP BY id
      HAVING COUNT(*) > 1
    """
    df = pd.read_sql(sql, engine)
    # df['id'] will be the duplicate values
    return df["id"].tolist()
