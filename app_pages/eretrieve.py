import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt
from datetime import date

from streamlit_data_management import load_gazette_content
from src.streamlit_retrievepublication import main as fetch_and_upload

sns.set_style('dark')

def retrieve_body():
    # load data
    df_gaz = load_gazette_content()
    
    if df_gaz.empty:
        st.warning(
            f"This page is designed to **RETRIEVE** the data from the Gazette server.  \n"
            f"⚠️ No Gazette data loaded. \n"
        )
    else:
        st.info(
            f"This page is designed to **RETRIEVE** the data from the Gazette server.  \n"
            f"The dataset was correctly loaded. It contains {df_gaz.shape[0]} rows and {df_gaz.shape[1]} columns. \n"
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
        with st.spinner("Contacting API and uploading to database…"):
            try:
                fetch_and_upload(target_day=target_day, page_size=page_size)
                load_gazette_content.clear()
                st.success("✅ Done! Data has been fetched and upserted.")
            except Exception as e:
                st.error(f"❌ Failed: {e}")

    st.markdown("---")

    df_gaz = load_gazette_content()
    st.write(f"… contains {df_gaz.shape[0]} rows …")