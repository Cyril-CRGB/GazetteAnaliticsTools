import os
import streamlit as st
import pandas as pd
import numpy as np
import joblib
import psycopg2 # import the PostgresQL connector

from dotenv import load_dotenv
import env

load_dotenv()



# Connect to your database
@st.cache(suppress_st_warning=True, allow_output_mutation=True)
def connect_to_db():
    DATABASE_URL = os.environ.get('DATABASE_URL') # Fetch the DATABASE_URL from environnement variables
    conn = psycopg2.connect(DATABASE_URL, sslmode='require') # Connect to the database
    return conn

@st.cache(suppress_st_warning=True, allow_output_mutation=True)
def load_original_data():
    conn = connect_to_db()
    query = "SELECT * FROM crime_description_table;" # Update table
    dforigine = pd.read_sql(query, conn) # fetch data from the database
    conn.close() # Close the connection
    return dforigine

@st.cache(suppress_st_warning=True, allow_output_mutation=True)
def load_crime_committed_analyses():
    conn = connect_to_db()
    query = "SELECT * FROM crime_description_table;" # Update table
    dfcca = pd.read_sql(query, conn) # change the delimiter if needed
    conn.close()
    return dfcca

@st.cache(suppress_st_warning=True, allow_output_mutation=True)
def load_cleaned_data_short():
    conn = connect_to_db()
    query = "SELECT * FROM crime_description_table;" # Update table
    dfcleanedshort = pd.read_sql(query, conn)
    conn.close()
    return dfcleanedshort