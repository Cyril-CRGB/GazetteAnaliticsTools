import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt
from datetime import date
import os, re
import time

from streamlit_data_management import load_gazette_content
from src.streamlit_calculation import load_publication_coverage, get_publication_date_bounds, find_duplicate_ids

sns.set_style('dark')

def coverage_body():
    # load data
    df_gaz = load_gazette_content()
    earliest, latest = get_publication_date_bounds()
    
    if df_gaz.empty:
        st.warning(
            f"This page is designed to **CHECK** the quality of the data.  \n"
            f"⚠️ No Gazette data loaded. \n"
        )
    else:
        st.info(
            f"This page is designed to **CHECK** the quality of the data. In paticular: \n"
            f"* Check 1: if all the publication were downloaded from the Gazette server.  \n"
            f"* Check 2: if there are no duplicated ID.\n\n"
            f"The dataset was correctly loaded, and it contains **{df_gaz.shape[0]}** rows and **{df_gaz.shape[1]}** columns.  \n"
            f"Going from **{earliest}** up to **{latest}**. \n"
        )

    st.markdown("""---""")

    st.header("📅 Publication Date Coverage")

    # ── Year picker based on available CSVs ─────────────────────────────
    files = [f for f in os.listdir("inputs/other") if re.match(r"publications_\d{4}\.csv", f)]
    years = sorted(int(re.search(r"publications_(\d{4})\.csv", f).group(1)) for f in files)
    default_ix = years.index(date.today().year) if date.today().year in years else 0
    year = st.selectbox("Select a year", years, index=default_ix)

    # ── Refresh button ───────────────────────────────────────────────────
    if st.button("🔄 Refresh data"):
        # Clear both caches so next loads hit the DB/API anew
        load_gazette_content.clear()
        load_publication_coverage.clear()
        get_publication_date_bounds.clear()
        placeholder = st.empty()
        placeholder.success("🆕 Caches cleared — loading fresh data…")
        time.sleep(3)
        placeholder.empty()

    st.markdown("""---""")

    # ── Load coverage for that year ─────────────────────────────────────
    cov = load_publication_coverage(year)
    if cov.empty:
        st.warning("No publication dates found in CSV or DB.")
        return
    # If the user picked the current year, ignore future dates
    if year == date.today().year:
        cov = cov[cov["date"] <= date.today()]

    # ── Chart ────────────────────────────────────────────────────────────
    chart = (
        alt.Chart(cov)
        .mark_point(filled=True, size=100)
        .encode(
            x=alt.X("date:T", title="Publication Dates"),
            color=alt.condition(
                alt.datum.present,
                alt.value("green"),
                alt.value("lightgray")
            ),
            tooltip=[
                alt.Tooltip("date:T", title="Date"),
                alt.Tooltip("present:O", title="In DB?")
            ]
        )
        .properties(height=100)
    )
    st.altair_chart(chart, use_container_width=True)

    # -- summary/status for users --
    today = date.today()
    cov_until_today = cov[cov["date"] <= today]
    total   = len(cov_until_today)
    present = int(cov_until_today["present"].sum())
    missing = total - present
    if missing == 0:
        st.success(f"Check 1 (success): 🎉 All {total} publication dates up to {today} are present in the database.")
    else:
        st.error(
            f"Check 1 (fail): ⚠️ {missing} of {total} dates up to {today} are missing!  \n"
            f"Hover over the lightgray circles to see which ones."
        )
        if st.checkbox("🔍 See the list of missing publication dates:"):
            st.write(", ".join(str(d) for d in cov_until_today.loc[~cov_until_today.present, "date"]))

    st.markdown("""---""")

    dups = find_duplicate_ids()
    if dups:
        st.error(f"Check 2 (fail): ⚠️ Found duplicate IDs: {', '.join(dups)}")
    else:
        st.success("Check 2 (success): ✅ All IDs are unique.")
