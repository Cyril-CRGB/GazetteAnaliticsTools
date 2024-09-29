import os
import streamlit as st
import pandas as pd
import numpy as np
import joblib
import psycopg2 # import the PostgresQL connector

# Connect to your database
@st.cache(suppress_st_warning=True, allow_output_mutation=True)
def connect_to_db():
    DATABASE_URL = os.environ.get('DATABAE_URL') # Fetch the DATABASE_URL from environnement variables
    conn = psycopg2.connect(DATABASE_URL, sslmode='require') # Connect to the database
    return conn

@st.cache(suppress_st_warning=True, allow_output_mutation=True)
def load_original_data():
    conn = connect_to_db()
    query = "SELECT * FROM inputs/datasets/raw/Crime_Data_from_2020_to_Present.csv;" # Update table
    dforigine = pd.read_sql(query, conn) # fetch data from the database
    conn.close() # Close the connection
    return dforigine

@st.cache(suppress_st_warning=True, allow_output_mutation=True)
def load_crime_committed_analyses():
    conn = connect_to_db()
    query = "SELECT * FROM inputs/datasets/raw/Crm_Cd_Desc_analyses.csv;" # Update table
    dfcca = pd.read_sql(query, conn) # change the delimiter if needed
    conn.close()
    return dfcca

@st.cache(suppress_st_warning=True, allow_output_mutation=True)
def load_cleaned_data_short():
    conn = connect_to_db()
    query = "SELECT * FROM outputs/datasets/collection/dataPP5_cleaned_10k.csv;" # Update table
    dfcleanedshort = pd.read_sql(query, conn)
    conn.close()
    return dfcleanedshort