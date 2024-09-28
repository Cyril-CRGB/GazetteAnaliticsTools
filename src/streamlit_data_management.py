import streamlit as st
import pandas as pd
import numpy as np
import joblib

@st.cache(suppress_st_warning=True, allow_output_mutation=True)
def load_original_data():
    dforigine = pd.read_csv("inputs/datasets/raw/Crime_Data_from_2020_to_Present.csv")
    return dforigine

@st.cache(suppress_st_warning=True, allow_output_mutation=True)
def load_crime_committed_analyses():
    dfcca = pd.read_csv("inputs/datasets/raw/Crm_Cd_Desc_analyses.csv", delimiter=';') # change the delimiter as needed
    return dfcca

def load_cleaned_data():
    dfcleaned = pd.read_csv("outputs/datasets/collection/dataPP5_cleaned.csv")
    return dfcleaned

def load_cleaned_data_short():
    dfcleanedshort = pd.read_csv("outputs/datasets/collection/dataPP5_cleaned_10k.csv")
    return dfcleanedshort