import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from streamlit_data_management import load_original_data
from streamlit_data_management import load_crime_committed_analyses
from streamlit_data_management import load_cleaned_data_short
from streamlit_data_management import load_pkl_file

#from src.streamlit_calculation import predict_cluster # to code

sns.set_style('dark')


def predictions_body():

    # load cluster analysis files
    version = 'v1'
    # cluster_features = (data...
    #                        .columns
    #                        .to_list()
    #                        )
    cluster_pipeline = load_pkl_file(f"outputs/ml_pipeline/cluster_analysis/{version}/LuxuriusCluster.pkl")
    cluster_profile = pd.read_csv(f"outputs/datasets/other/{version}/clusters_profile.csv")

    st.write("## Predictions")
    st.info(
        f"* Enter the individual informations and find out the risk involved, and the subscribtion fee to charge.\n"
    )
    st.write("---")

    # Generate Live Data
    # check_variables_for_UI(cluster_features)
    X_live = DrawInputsWidgets()

    # Predict on live data
    if st.button("Predict"):
        predict_cluster(X_Live, cluster_features, cluster_pipeline, cluster_profile)


def check_variables_for_UI(cluster_features):
    import itertools
    # The widgets inputs are the features used in the pipeline
    # We combine them only with unique values
    combines_features = set(
        list(
            itertools.chain(cluster_features)
        )
    )
    st.write(f"* There are {len(combined_features)} features for the UI: \n\n {combines_features}"
    )

def DrawInputsWidgets():

    #load data
    df = load_original_data()
    dfcca = load_crime_committed_analyses()
    dfcleanedshort = load_cleaned_data_short()

    # Creating input widgets only for 4 features
    col1, col2, col3, col4 = st.beta_columns(4)

    #Using the features to feed the ML Pipeline -> values from check_variables_for_UI() result

    #here i need to find back the names of the weapon

    #create an empty DataFrame, which will be the live data
    X_live = pd.DataFrame([], index=[0])

    # from here on we draw the widget based on the variable type (numerical or categorical)
    # and set initial values
    with col1:
        feature = "vict_sex"
        st_widget = st.selectbox(
            label=feature,
            options=dfcleanedshort[feature].unique()
        )
    X_live[feature] = st_widget




