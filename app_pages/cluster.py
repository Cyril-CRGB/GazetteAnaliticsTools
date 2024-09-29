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

sns.set_style('dark')

def cluster_body():

    # load data
    dfcleanedshort = load_cleaned_data_short()

    st.write("## ML Cluster")

    st.info(
        f"* We used **Principal Component Analysis (PCA)** to determine the best features to train the model with. \n"
        f"* \n"
    )
    # display data "Cluster's Pipeline" analyses
    if st.checkbox("Show the Cluster's Pipeline"):
        LuxuriusCluster()