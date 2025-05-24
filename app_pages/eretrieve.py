import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt
from datetime import date
from sqlalchemy import text

from streamlit_data_management import load_gazette_content, get_engine_resource
from src.streamlit_retrievepublication import main as fetch_and_upload
from src.streamlit_calculation import load_publication_coverage, get_publication_date_bounds

sns.set_style('dark')

def retrieve_body():
    # load data
    df_gaz = load_gazette_content()
    earliest, latest = get_publication_date_bounds()
    
    if df_gaz.empty:
        st.warning(
            f"This page is designed to **RETRIEVE** the data from the Gazette server.  \n"
            f"⚠️ No Gazette data loaded. \n"
        )
    else:
        st.info(
            f"This page is designed to **RETRIEVE** the data from the Gazette server.  \n"
            f"The dataset was correctly loaded, and it contains **{df_gaz.shape[0]} rows** and **{df_gaz.shape[1]} columns**.  \n"
            f"Going from **{earliest}** up to **{latest}**. \n"
        )

    st.markdown("""---""")

    st.header("📥 Fetch & Upload Gazette Publications")

    # 1. User controls
    target_day = st.date_input(
        "Select publication date",
        value=date.today(),
        help="Which day's Gazette feed should we fetch?"
    )
    page_size = st.number_input(
        "Page size",
        min_value=1,
        value=3000,
        help="How many items to request per API page (max 2000)."
    )

    # 2. Trigger fetch/upload
    if st.button("Fetch & Upload"):
        engine = get_engine_resource()
        # 2a. Check if any rows already exist for this date
        with st.spinner("Checking if database already contains this publication date."):
            with engine.connect() as conn:
                existing_count = conn.execute(
                    text("""
                        SELECT COUNT(*) 
                        FROM gazette_contentdata 
                        WHERE publicationDate = :pub_date
                    """),
                    {"pub_date": target_day}
                ).scalar()
        if existing_count > 0:
            st.warning(
                f"⚠️ There are already {existing_count} rows in the database "
                f"for {target_day}. Skipping 'Fetch & Upload'."
            )
        else:
            # 2b. No existing rows → do the fetch & upsert
            with st.spinner("Contacting API and uploading to database…"):
                try:
                    fetch_and_upload(target_day=target_day, page_size=page_size)
                    st.success("✅ Done! Data has been fetched and upserted.")
                    # 2c. Clear caches so other pages reload fresh
                    load_gazette_content.clear()
                    load_publication_coverage.clear()
                    get_publication_date_bounds.clear()
                except Exception as e:
                    st.error(
                        f"❌ Failed: {e}\n"
                        "Go to 'Delete' page and remove this date to avoid partial data."
                    )

    st.markdown("---")

    df_gaz = load_gazette_content()
    st.write(f"… contains {df_gaz.shape[0]} rows …")