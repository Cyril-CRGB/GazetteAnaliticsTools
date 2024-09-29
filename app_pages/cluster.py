import streamlit as st
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from ydata_profiling import ProfileReport
# import pingouin as pg
from scipy import stats


from streamlit_data_management import load_cleaned_data_short
from src.streamlit_calculation import distribution_skew_kurtosis, feature_correlation_analysis_spearman, six_best_correlated_features_correlation_analysis_spearman
from src.streamlit_calculation import LuxuriusCluster, pca_on_streamlit


sns.set_style('dark')

def cluster_body():

    # load data
    dfcleanedshort = load_cleaned_data_short()
    # Drop the specified variables from the dataframe
    if not isinstance(dfcleanedshort, pd.DataFrame):
        #Convert to DataFrame
        dfcleanedshort = pd.DataFrame(dfcleanedshort)
    dfcleanedshort = dfcleanedshort.drop(labels=['date_occ', 'area_name', 'crm_cd_desc', 'lat', 'lon', 'damage'], axis=1)
    # df = pd.read_csv('outputs/datasets/collection/dataPP5_cleaned_10k.csv')
    st.write(dfcleanedshort.head(4))

    st.write("## ML Cluster")

    st.info(
        f"* We modeled a cluster pipeline. \n"
        f"* We used **Principal Component Analysis (PCA)** to determine the best features to train the model with. \n"
        f"* \n"
    )
    # display data "Cluster's Pipeline" analyses
    if st.checkbox("Show the Cluster's Pipeline"):
        LuxuriusCluster()

    # display PCA best features
    if st.checkbox("Show PCA best features"):
        pca_on_streamlit(dfcleanedshort)