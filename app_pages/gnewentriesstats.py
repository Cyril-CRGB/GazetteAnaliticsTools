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

    st.header("🆕 Analysis of the new entries of the last publication")

    # ── Refresh control ────────────────────────────────────────────────
    if st.button("🔄 Refresh"):
        load_gazette_content.clear()
        st.success("Cache cleared. Data will refresh below.")

    # ── Load and validate data ─────────────────────────────────────────
    df = load_gazette_content(limit=None)
    if df.empty:
        st.warning("No Gazette data loaded.")
        return

    # ── Filter to New entries and normalize date ───────────────────────
    df_new = df[df["entrytype"] == "New entries"].copy()
    df_new["publicationdate"] = pd.to_datetime(
        df_new["publicationdate"], errors="coerce"
    )
    df_new = df_new.dropna(subset=["publicationdate"])
    df_new["year"] = df_new["publicationdate"].dt.year

    # ── Compute current vs previous year ───────────────────────────────
    today = date.today()
    cy = today.year
    py = cy - 1

    # Group counts by legal form and year
    grp = (
        df_new
        .groupby(["company_legalform", "year"])
        .size()
        .unstack(fill_value=0)
    )

    # Build stats rows
    rows = []
    for form in grp.index:
        prev_count = grp.loc[form].get(py, 0)
        curr_count = grp.loc[form].get(cy, 0)
        ratio = (
            "n/a"
            if prev_count == 0
            else round(curr_count / prev_count - 1, 4)
        )
        rows.append({
            "company_legalform": form,
            str(py): prev_count,
            str(cy): curr_count,
            "ratio": ratio
        })

    # Total row
    total_prev = sum(r[str(py)] for r in rows)
    total_curr = sum(r[str(cy)] for r in rows)
    total_ratio = (
        "n/a"
        if total_prev == 0
        else round(total_curr / total_prev - 1, 4)
    )
    rows.append({
        "company_legalform": "Total new entries",
        str(py): total_prev,
        str(cy): total_curr,
        "ratio": total_ratio
    })

    # ── Display table ───────────────────────────────────────────────────
    df_stats = pd.DataFrame(rows)
    st.table(df_stats)