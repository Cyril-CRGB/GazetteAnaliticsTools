import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt
from datetime import date

from streamlit_data_management import load_gazette_content
from src.streamlit_calculation import load_publication_coverage

sns.set_style('dark')

def coverage_body():
    # load data
    df_gaz = load_gazette_content()
    
    if df_gaz.empty:
        st.warning(
            f"This page is designed to **CHECK** if all the publication were downloaded from the Gazette server.  \n"
            f"⚠️ No Gazette data loaded. \n"
        )
    else:
        st.info(
            f"This page is designed to **CHECK** if all the publication were downloaded from the Gazette server.  \n"
            f"The dataset was correctly loaded. It contains {df_gaz.shape[0]} rows and {df_gaz.shape[1]} columns. \n"
        )

    st.markdown("""---""")

    if st.button("🔄 Refresh data"):
        # Clear both caches so next loads hit the DB/API anew
        load_gazette_content.clear()
        load_publication_coverage.clear()
        st.success("🆕 Caches cleared — loading fresh data…")

    st.markdown("""---""")

    st.header("📅 Publication Date Coverage")
    cov = load_publication_coverage()
    if cov.empty:
        st.warning("No publication dates found in CSV or DB.")
        return
    # Build the chart
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
        st.success(f"🎉 All {total} publication dates up to {today} are present in the database.")
    else:
        st.error(
            f"{missing} of {total} dates up to {today} are missing! "
            "Hover over the white circles to see which ones."
        )
        if st.checkbox("🔍 See the list of missing publication dates:"):
            st.write(", ".join(str(d) for d in cov_until_today.loc[~cov_until_today.present, "date"]))

    st.markdown("""---""")
