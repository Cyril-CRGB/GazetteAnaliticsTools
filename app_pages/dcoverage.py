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
    total   = len(cov)
    present = int(cov["present"].sum())
    missing = total - present
    if missing == 0:
        st.success(f"🎉 All {total} publication dates are present in the database.")
    else:
        st.error(
            f"{missing} of {total} dates are missing! "
            "Hover over the white circles to see which ones."
        )
        if st.checkbox("🔍 See the list of missing publication dates:"):
            st.write(", ".join(str(d) for d in cov.loc[~cov.present, "date"]))

    st.markdown("""---""")

    