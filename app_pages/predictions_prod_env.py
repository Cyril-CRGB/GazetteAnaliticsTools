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


def predictions_body_prod():

    #load data
    df = load_original_data()
    dfcca = load_crime_committed_analyses()
    dfcleanedshort = load_cleaned_data_short()

    #dfcleanedshort.columns = dfcleanedshort.columns.str.title().str.replace("_", " ")
    #st.write(dfcleanedshort.columns)

    #load cluster analysis files
    version = 'v2'
    cluster_features_testing = ['Vict Sex', 'Weapon Used Cd', 'Premis Desc', 'Vict Age', 'Amount']
    cluster_pipeline = load_pkl_file(f"outputs/ml_pipeline/cluster_analysis/{version}/LuxuriusClusterv2.pkl")
    cluster_profile = pd.read_csv(f"outputs/datasets/other/{version}/clusters_profile_v2.csv")

    st.write("## Predictions")
    st.info(
        f"* Enter the individual informations and find out the risk involved, and the subscribtion fee to charge.\n"
    )
    st.write("---")

    # Generate Live Data
    X_live = DrawInputsWidgets()
    #st.write(cluster_features_testing)
    #st.write(X_live)

    z_live_cluster = X_live.filter(cluster_features_testing)
    z_live_cluster = z_live_cluster[cluster_features_testing]
    z_live_cluster = pd.DataFrame(z_live_cluster)
    pipeline_features = cluster_pipeline.named_steps["OrdinalCategoricalEncoder"].variables
    if list(z_live_cluster.columns) != list(pipeline_features):
        statement = (f"Column mismatch! Expected: {pipeline_features}, but got: {list(z_live_cluster.columns)}")
        st.write(statement)

    # Predict on live data
    if st.button("Make Prediction"):
        predict_cluster(X_live, cluster_features_testing, cluster_pipeline, cluster_profile)


def DrawInputsWidgets():
    #load data
    df = load_original_data()
    dfcca = load_crime_committed_analyses()
    dfcleanedshort = load_cleaned_data_short()

    # Creating input widgets for 5 features
    col1, col2, col3 = st.columns(3)
    col4, col5 = st.columns(2)

    #create an empty DataFrame, which will be the live data
    X_live = pd.DataFrame([], index=[0])

    #dfcleanedshort.columns = dfcleanedshort.columns.str.title().str.replace("_", " ")
    #st.write(dfcleanedshort.columns)

    # from here on we draw the widget based on the variable type (numerical or categorical)
    # and set initial values
    with col1:
        feature = "Vict Sex"
        st_widget = st.selectbox(
            label="Sex or Gender",
            options=dfcleanedshort[feature].unique()
        )
    X_live[feature] = st_widget

    with col2:
        feature = "Weapon Used Cd" # the value we want to store
        feature_desc = "Weapon Desc" # the value we want to display
        # drop missing values and create a mapping dictionary
        weapon_mapping = dfcleanedshort.dropna(subset=[feature, feature_desc]).drop_duplicates(subset=[feature, feature_desc]).set_index(feature_desc)[feature].to_dict()
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
            max_value=int(dfcleanedshort[feature].max()),
            value=int(dfcleanedshort[feature].median()),
            step=1
        )
    X_live[feature] = st_widget

    with col4:
        feature = "Premis Desc"
        st_widget = st.selectbox(
            label="Location most often visited",
            options=dfcleanedshort[feature].unique()
        )
    X_live[feature] = st_widget

    with col5:
        feature = "Amount"
        st_widget = st.selectbox(
            label="Value in $ of the good at risk",
            options=dfcleanedshort[feature].unique()
        )
    X_live[feature] = st_widget

    #st.write(X_live)

    return X_live


