import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from streamlit_data_management import load_gazette_content
from src.streamlit_calculation import show_columnsheaders_and_an_example, get_publication_date_bounds

sns.set_style('dark')

def data_body():

    # load data
    df_gaz = load_gazette_content()
    earliest, latest = get_publication_date_bounds()
    
    if df_gaz.empty:
        st.warning(
            f"This page is designed to **EXPLAIN** the data retrieved on the Gazette server.  \n"
            f"⚠️ No Gazette data loaded. \n"
        )
    else:
        st.info(
            f"This page is designed to **EXPLAIN** the data retrieved on the Gazette server.  \n"
            f"The dataset was correctly loaded, and it contains **{df_gaz.shape[0]} rows** and **{df_gaz.shape[1]} columns**.  \n"
            f"Going from **{earliest}** up to **{latest}**. \n"
        )

    st.write("""---""")

    # display raw data
    st.header("📑 Data")
    st.info(f"The database is hosted on Heroku, the name of the table is 'gazette_contentdata'. \n")
    if st.checkbox("🔍 Have a look at the first 10 rows:"):
        st.dataframe(df_gaz.head(10))

    st.write("""---""")

    st.header("📑 Table Columns and Categories")
    st.info(
            f"We select only 3 categories of publications made by the Swiss official Gazette:\n"
            f"* 'New entries',  \n"
            f"* 'Changes',  \n"
            f"* 'Deletion'.\n\n"
            f"There are {df_gaz.shape[1]} columns.  \n"
        )
    if st.checkbox("🔍 Have a look at the columns header with an example per category:"):
        df_examples = show_columnsheaders_and_an_example(df_gaz)
        st.dataframe(df_examples)
