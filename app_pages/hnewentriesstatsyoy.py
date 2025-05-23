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

def newentriesstatsyoy_body():

    # load data
    df_gaz = load_gazette_content()

    st.header("🆕 Analysis of the new entries since the beginning of the year (Year-over-Year)")

    # ── Refresh control ────────────────────────────────────────────────
    if st.button("🔄 Refresh"):
        load_gazette_content.clear()
        st.success("Cache cleared. Data will refresh below.")

    # ── Load and validate data ─────────────────────────────────────────
    df = load_gazette_content(limit=None)
    if df.empty:
        st.warning("No Gazette data loaded.")
        return

    df_new = df[df["entrytype"] == "New entries"].copy()
    df_new["pubDate"] = pd.to_datetime(df_new["publicationdate"], errors="coerce").dt.date
    df_new = df_new.dropna(subset=["pubDate"])

    today = date.today()
    cy, py = today.year, today.year - 1

    # Define matching date ranges
    start_py = date(py, 1, 1)
    end_py   = date(py, today.month, today.day)
    start_cy = date(cy, 1, 1)
    end_cy   = date(cy, today.month, today.day)

    # Helper to get counts per legalForm in a date window
    def counts_in_window(start_dt, end_dt):
        mask = (df_new["pubDate"] >= start_dt) & (df_new["pubDate"] <= end_dt)
        return df_new.loc[mask].groupby("company_legalform").size()

    # Get series for each period (fill missing forms with 0)
    cnt_py = counts_in_window(start_py, end_py)
    cnt_cy = counts_in_window(start_cy, end_cy)
    all_forms = sorted(set(cnt_py.index) | set(cnt_cy.index))

    # Build rows
    rows = []
    for form in all_forms:
        prev_count = int(cnt_py.get(form, 0))
        curr_count = int(cnt_cy.get(form, 0))
        ratio = "n/a" if prev_count == 0 else round(curr_count / prev_count - 1, 4)
        rows.append({
            "company_legalform": form,
            f"{start_py}→{end_py}": prev_count,
            f"{start_cy}→{end_cy}": curr_count,
            "ratio": ratio
        })

    # Total row
    total_prev = sum(r[f"{start_py}→{end_py}"] for r in rows)
    total_curr = sum(r[f"{start_cy}→{end_cy}"] for r in rows)
    total_ratio = "n/a" if total_prev == 0 else round(total_curr / total_prev - 1, 4)
    rows.append({
        "company_legalform": "Total new entries",
        f"{start_py}→{end_py}": total_prev,
        f"{start_cy}→{end_cy}": total_curr,
        "ratio": total_ratio
    })

    # Display
    df_stats = pd.DataFrame(rows)
    st.table(df_stats)