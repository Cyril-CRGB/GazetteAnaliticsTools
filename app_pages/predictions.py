import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from streamlit_data_management import load_original_data
from streamlit_data_management import load_crime_committed_analyses
from streamlit_data_management import load_cleaned_data_short
from streamlit_data_management import load_pkl_file

from src.streamlit_calculation import predict_cluster

sns.set_style('dark')


def predictions_body():

    #load data
    df = load_original_data()
    dfcca = load_crime_committed_analyses()
    dfcleanedshort = load_cleaned_data_short()

    #load cluster analysis files
    version = 'v2'
    #cluster_features = (dfcleanedshort.columns.to_list())
    cluster_features_testing = ['Vict Sex', 'Weapon Used Cd', 'Premis Desc', 'Vict Age', 'Amount']
    cluster_pipeline = load_pkl_file(f"outputs/ml_pipeline/cluster_analysis/{version}/LuxuriusClusterv2.pkl")
    cluster_profile = pd.read_csv(f"outputs/datasets/other/{version}/clusters_profile_v2.csv")

    st.write("## Predictions")
    st.info(
        f"* Enter the individual informations and find out the risk involved, and the subscribtion fee to charge.\n"
    )
    st.write("---")

    # Generate Live Data
    #check_variables_for_UI(cluster_features_testing)
    #st.write(cluster_features_testing)
    X_live = DrawInputsWidgets()
    #st.write(X_live)

    # Predict on live data
    if st.button("Make Prediction"):
        predict_cluster(X_live, cluster_features_testing, cluster_pipeline, cluster_profile)

    

def check_variables_for_UI(cluster_features_testing):
    import itertools
    # The widgets inputs are the features used in the pipeline
    # We combine them only with unique values
    combined_features = set(
        list(
            itertools.chain(cluster_features_testing) #need to get rid of '_testing' befor going into PRODUCTION
        )
    )
    st.write(f"* There are {len(combined_features)} features for the UI: \n\n {combined_features}"
    )

def DrawInputsWidgets():

    #load data
    df = load_original_data()
    dfcca = load_crime_committed_analyses()
    dfcleanedshort = load_cleaned_data_short()
    #version = 'v1'
    #dftesting = pd.read_csv(f"outputs/datasets/datacleaned/{version}/dataPP5_cleaned_10k.csv")

    # Creating input widgets for 5 features
    col1, col2, col3 = st.columns(3)
    col4, col5 = st.columns(2) #on test environnement write:st.beta_columns
    #col6, col7, col8 = st.beta_columns(3)

    #Using the features to feed the ML Pipeline -> values from check_variables_for_UI() result

    #here i need to find back the names of the weapon

    #create an empty DataFrame, which will be the live data
    X_live = pd.DataFrame([], index=[0])

    # from here on we draw the widget based on the variable type (numerical or categorical)
    # and set initial values
    with col1:
        feature = "Vict Sex"
        st_widget = st.selectbox(
            label="Sex or Gender",
            options=dfcleanedshort['vict_sex'].unique()
        )
    X_live[feature] = st_widget

    with col2:
        feature = "Weapon Used Cd" # the value we want to store
        feature_desc = "Weapon Desc" # the value we want to display
        # drop missing values and create a mapping dictionary
        weapon_mapping = dfcleanedshort.dropna(subset=['weapon_used_cd', 'weapon_desc']).drop_duplicates(subset=['weapon_used_cd', 'weapon_desc']).set_index(feature_desc)['weapon_used_cd'].to_dict()
        # show descriptions (Weapon Desc) in the dropdown
        widget_desc = st.selectbox(
            label="Weapon ownership or regularly seen",
            options=list(weapon_mapping.keys()) # display only weapon descriptions
        )
        # convert back to the corresponding weapon Used Cd
        st_widget = weapon_mapping[widget_desc]
    X_live[feature] = st_widget
    #X_live[feature_desc] = widget_desc

    with col3:
        feature = "Vict Age"
        st_widget = st.number_input(
            label="Age",
            min_value=int(0),
            max_value=int(dfcleanedshort['vict_age'].max()),
            value=int(dfcleanedshort['vict_age'].median()),
            step=1
        )
    X_live[feature] = st_widget

    with col4:
        feature = "Premis Desc"
        st_widget = st.selectbox(
            label="Location most often visited",
            options=dfcleanedshort['premis_desc'].unique()
        )
    X_live[feature] = st_widget

    with col5:
        feature = "Amount"
        st_widget = st.selectbox(
            label="Value in $ of the good at risk",
            options=dfcleanedshort['amount'].unique()
        )
    X_live[feature] = st_widget

    #st.write(X_live)

    return X_live


