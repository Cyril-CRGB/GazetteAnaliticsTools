# app_pages/gnewentriesstats.py
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import date
from sqlalchemy import text
from streamlit_data_management import load_gazette_content

sns.set_style('dark')

def newclientsoftheday_body():

    # load data
    df_gaz = load_gazette_content()

    st.header("🤝 New potential clients")

    # ── Refresh control ────────────────────────────────────────────────
    if st.button("🔄 Refresh"):
        load_gazette_content.clear()
        st.success("Cache cleared. Data will refresh below.")
    
        # 1) Load and fixed‐filter the data
    df = load_gazette_content(limit=None)
    if df.empty:
        st.warning("No Gazette data loaded.")
        return

    today = date.today()
    # ensure publicationDate is a date
    df["pubDate"] = pd.to_datetime(df["publicationdate"], errors="coerce").dt.date
    df = df[
        (df["entrytype"] == "New entries") &
        (df["pubDate"]    == today)
    ]
    if df.empty:
        st.warning(f"No New entries for {today}.")
        return

    # 2) User‐selectable filters
    langs = st.multiselect(
        "Language",
        options=sorted(df["language"].dropna().unique()),
        default=sorted(df["language"].dropna().unique())
    )
    cants = st.multiselect(
        "Cantons",
        options=sorted(df["cantons"].dropna().unique()),
        default=sorted(df["cantons"].dropna().unique())
    )
    seats = st.multiselect(
        "Company Seat",
        options=sorted(df["company_seat"].dropna().unique()),
        default=sorted(df["company_seat"].dropna().unique())
    )
    forms = st.multiselect(
        "Legal Form",
        options=sorted(df["company_legalform"].dropna().unique()),
        default=sorted(df["company_legalform"].dropna().unique())
    )

    df = df[
        df["language"].isin(langs) &
        df["cantons"].isin(cants)  &
        df["company_seat"].isin(seats) &
        df["company_legalform"].isin(forms)
    ]
    if df.empty:
        st.info("No entries match selected filters.")
        return

    # 3) Sort by company_name
    df = df.sort_values("company_name")

    # 4) Create one tab per starting letter
    letters = sorted(df["company_name"].str[0].str.upper().unique())
    tabs = st.tabs(letters)

    for tab, letter in zip(tabs, letters):
        with tab:
            sub = df[df["company_name"].str.startswith(letter)]
            if sub.empty:
                st.write("No entries under this letter.")
                continue

            # 5) Show each row as an expander
            for _, row in sub.iterrows():
                header = (
                    f"{row['company_uid']} | {row['company_name']} | "
                    f"{row['company_street_and_number']} | {row['company_zip_and_town']}"
                )
                with st.expander(header):
                    st.write("**Publication Text:**")
                    st.write(row.get("publication_text", ""))
                    st.write("**Company Purpose:**")
                    st.write(row.get("company_purpose", ""))