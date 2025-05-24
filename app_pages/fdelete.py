# app_pages/fdelete.py

import streamlit as st
from datetime import date
from sqlalchemy import text
from streamlit_data_management import load_gazette_content
from src.streamlit_calculation import load_publication_coverage, get_publication_date_bounds
from src.streamlit_retrievepublication import get_engine

def delete_body():
    # load data
    df_gaz = load_gazette_content()
    earliest, latest = get_publication_date_bounds()
    if df_gaz.empty:
        st.warning(
            f"This page is designed to **DELETE** the data from the Gazette database.  \n"
            f"⚠️ No Gazette data loaded. \n"
        )
    else:
        st.info(
            f"This page is designed to **DELETE** the data from the Gazette database.  \n"
            f"The dataset was correctly loaded, and it contains **{df_gaz.shape[0]} rows** and **{df_gaz.shape[1]} columns**.  \n"
            f"Going from **{earliest}** up to **{latest}**. \n"
        )

    st.markdown("""---""")

    st.header("🗑️ Delete Gazette Data by Publication Date")

    # 1) Date picker
    del_date = st.date_input(
        "Select publication date to delete",
        value=date.today(),
        help="All rows with this publicationDate will be removed."
    )

    # 2) Delete button
    if st.button("Delete rows"):
        engine = get_engine()
        with engine.begin() as conn:
            result = conn.execute(
                text("DELETE FROM gazette_contentdata WHERE publicationDate = :pub_date"),
                {"pub_date": del_date}
            )
            deleted = result.rowcount

        # 3) Clear caches so other pages reload fresh
        load_gazette_content.clear()
        load_publication_coverage.clear()

        # 4) Feedback
        if deleted:
            st.success(f"✅ Deleted {deleted} rows for date {del_date}.")
        else:
            st.info(f"ℹ️ No rows found for date {del_date}.")