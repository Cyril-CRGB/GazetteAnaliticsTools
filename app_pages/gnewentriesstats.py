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

def newentriesstats_body():

    # load data
    df_gaz = load_gazette_content()

    st.header("🆕 Analysis of the new entries, Today vs. Same Day Last Year")

    # ── Refresh control ────────────────────────────────────────────────
    if st.button("🔄 Refresh"):
        load_gazette_content.clear()
        st.success("Cache cleared. Data will refresh below.")

    # ── Load and validate data ─────────────────────────────────────────
    df = load_gazette_content(limit=None)
    if df.empty:
        st.warning("No Gazette data loaded.")
        return

    # Filter to New entries and parse dates
    df_new = df[df["entrytype"] == "New entries"].copy()
    df_new["pubDate"] = pd.to_datetime(
        df_new["publicationdate"], errors="coerce"
    ).dt.date
    df_new = df_new.dropna(subset=["pubDate"])

    today      = date.today()
    last_year  = today.replace(year=today.year - 1)

    # Count per legalForm for today and for same day last year
    today_counts     = df_new[df_new["pubDate"] == today]     .groupby("company_legalform").size()
    lastyear_counts  = df_new[df_new["pubDate"] == last_year] .groupby("company_legalform").size()

    all_forms = sorted(set(today_counts.index) | set(lastyear_counts.index))

    # Build rows
    rows = []
    for form in all_forms:
        cnt_today    = int(today_counts.get(form, 0))
        cnt_lastyear = int(lastyear_counts.get(form, 0))
        if cnt_lastyear == 0:
            ratio = "n/a"
        else:
            ratio = round(cnt_today / cnt_lastyear - 1, 4)
        rows.append({
            "company_legalform": form,
            str(last_year):     cnt_lastyear,
            str(today):         cnt_today,
            "ratio":            ratio
        })

    # Total row
    total_today    = sum(r[str(today)]      for r in rows)
    total_lastyear = sum(r[str(last_year)] for r in rows)
    if total_lastyear == 0:
        total_ratio = "n/a"
    else:
        total_ratio = round(total_today / total_lastyear - 1, 4)
    rows.append({
        "company_legalform": f"Total new entries",
        str(last_year):      total_lastyear,
        str(today):          total_today,
        "ratio":             total_ratio
    })

    # Display table
    df_stats = pd.DataFrame(rows)
    st.table(df_stats)