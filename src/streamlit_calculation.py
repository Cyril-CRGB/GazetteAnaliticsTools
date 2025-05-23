import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
#import pingouin as pg
import numpy as np
#import re
#from scipy import stats
#from sklearn.preprocessing import LabelEncoder
#from sklearn.pipeline import Pipeline
#from feature_engine.encoding import OrdinalEncoder
#from sklearn.preprocessing import StandardScaler
#from sklearn.decomposition import PCA
#from sklearn.cluster import KMeans

from streamlit_data_management import load_gazette_content

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
def load_publication_coverage(csv_path: str = "inputs/other/publications.csv"
) -> pd.DataFrame:
    # 1. Read semicolon CSV, keep only the two cols you care about
    df = pd.read_csv(csv_path)  # Publication is in dd.mm.yyyy / df = pd.read_csv(csv_path, sep=";")

    # 2. Force‐parse “Publication” with dayfirst
    df["Publication"] = pd.to_datetime(
        df["Publication"],
        dayfirst=True,
        errors="coerce"
    )

    # 3. Drop any rows that still failed to parse
    df = df.dropna(subset=["Publication"])

    # 4. Extract pure date objects
    df["date"] = df["Publication"].dt.date

    # 5. Pull existing publicationDate from your DB and normalize
    df_gaz = load_gazette_content(limit=None)
    existing_dates = set(
        pd.to_datetime(df_gaz["publicationdate"], errors="coerce", dayfirst=True)
          .dt.date
          .dropna()
    )

    # 6. Build coverage table
    all_dates = sorted(df["date"].unique())
    cov = pd.DataFrame({"date": all_dates})
    cov["present"] = cov["date"].isin(existing_dates)
    return cov