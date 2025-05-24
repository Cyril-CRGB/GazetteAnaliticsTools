# app_pages/inewclientsoftheday.py

import streamlit as st
import pandas as pd
from datetime import date, timedelta
from streamlit_data_management import load_gazette_content

def inewclientsoftheweek_body():
    st.header("🆕 New Clients This Week")

    # 1) Load all data
    df = load_gazette_content(limit=None)
    if df.empty:
        st.warning("No Gazette data loaded.")
        return

    # 2) Compute the week span: this Monday → today
    today = date.today()
    monday = today - timedelta(days=today.weekday())

    df["pubDate"] = (
        pd.to_datetime(df["publicationdate"], errors="coerce")
          .dt.date
    )
    # filter entryType and this week
    df = df[
        (df["entrytype"] == "New entries") &
        (df["pubDate"] >= monday) &
        (df["pubDate"] <= today)
    ]
    if df.empty:
        st.warning(f"No New entries from {monday} through {today}.")
        return

    # 3) Show date span and list of seats in header
    # seats = sorted(df["company_seat"].dropna().unique())
    st.info(
        f"Showing New entries from **{monday}** through **{today}** "
        f"(this week).  \n"
    )

    # 4) User‐selectable filters (minus seats)
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
    forms = st.multiselect(
        "Legal Form",
        options=sorted(df["company_legalform"].dropna().unique()),
        default=sorted(df["company_legalform"].dropna().unique())
    )

    df = df[
        df["language"].isin(langs) &
        df["cantons"].isin(cants) &
        df["company_legalform"].isin(forms)
    ]
    if df.empty:
        st.info("No entries match selected filters.")
        return

    # 5) Sort & tabs by first letter
    df = df.sort_values("company_name")
    letters = sorted(df["company_name"].str[0].str.upper().unique())
    tabs = st.tabs(letters)

    for tab, letter in zip(tabs, letters):
        with tab:
            sub = df[df["company_name"].str.startswith(letter)]
            if sub.empty:
                st.write("No entries under this letter.")
                continue

            for _, row in sub.iterrows():
                header = (
                    f"{row['company_uid']} | {row['company_name']} | "
                    f"{row['company_street_and_number']} | {row['company_zip_and_town']} | "
                    f"{row['company_seat']}"
                )
                with st.expander(header):
                    st.write("**Publication Text:**")
                    st.write(row.get("publication_text", ""))
                    st.write("**Company Purpose:**")
                    st.write(row.get("company_purpose", ""))