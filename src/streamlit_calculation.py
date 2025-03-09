import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
#import pingouin as pg
import numpy as np
from scipy import stats
from sklearn.preprocessing import LabelEncoder
from sklearn.pipeline import Pipeline
from feature_engine.encoding import OrdinalEncoder
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

"""
streamlit page study
"""
# Function to calculate skewness and kurtosis for each column
def calculate_skew_kurtosis(df, col):
    skewness = df[col].skew().round(2)
    kurtosis = df[col].kurtosis().round(2)
    return skewness, kurtosis

# Function to plot the distributions and QQ plots for numeric columns
def distribution_skew_kurtosis(df):
    # Select only numeric columns
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    # Create a container to hold the plots
    for col in numeric_columns:
        st.write(f"### *** {col} ***")
        # Create subplots
        fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(12, 4))
        # Histogram with KDE plot
        sns.histplot(data=df, x=col, kde=True, ax=axes[0])
        axes[0].set_title("Histogram")
        # QQ plot using pingouin
        # pg.qqplot(df[col].dropna(), dist='norm', ax=axes[1]) # handling missing values
        # QQ plot using scipy
        stats.probplot(df[col].dropna(), dist='norm', plot=axes[1])
        axes[1].set_title("QQ Plot")
        plt.tight_layout()
        # Display
        st.pyplot(fig)
        # Calculate and print skewness and kurtosis
        skewness, kurtosis = calculate_skew_kurtosis(df, col)
        st.write(f"**Skewness**: {skewness} | **Kurtosis**: {kurtosis}")
        st.write(" \n")

# Function to convert categorical variables to numerical values
def convert_categorical_into_numerical(df, variable_name):
    label_encoder = LabelEncoder()
    df[variable_name] = label_encoder.fit_transform(df[variable_name])
    
# Function for Feature correlation analysis Spearman
def feature_correlation_analysis_spearman(df):
    # Convert categorical variables to numerical values 
    convert_categorical_into_numerical(df, 'vict_sex')
    convert_categorical_into_numerical(df, 'vict_descent')
    # Select only numeric columns for correlation
    numeric_df = df.select_dtypes(include=['float64', 'int64'])
    # Calculate the correlation matrix for numeric features using Spearman method
    corr_matrix_spearman = numeric_df.corr(method='spearman')
    # Create a heatmap
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_matrix_spearman, annot=True, cmap='coolwarm', fmt='.2f', square=True, linewidths=0.5)
    # Add titles and labels
    plt.title("Heatmap")
    plt.tight_layout()
    # Display
    st.pyplot(plt)
    st.write(" \n")

# Function to fetch six best correlated features Spearman
def six_best_correlated_features_correlation_analysis_spearman(df, variable_name, drop_feature=None):
    # Convert categorical variables to numerical values
    convert_categorical_into_numerical(df, 'vict_sex')
    convert_categorical_into_numerical(df, 'vict_descent')
    # Select only numeric columns for correlation
    numeric_df = df.select_dtypes(include=['float64', 'int64'])
    # Calculate the correlation matrix for numeric features using Spearman method
    if variable_name in numeric_df.columns:
        top_corr_features = numeric_df.corr(method='spearman')[variable_name].sort_values(key=abs, ascending=False)[2:8]
        st.write(f"### Top 6 features correlated with **{variable_name}** appart from '{drop_feature}'")
        st.write(top_corr_features)
    st.write(" \n")

# Function to predict cluster
def predict_cluster(X_live, cluster_features, cluster_pipeline, cluster_profile):

    #'X_live' is the live data input from the user via Streamlit widgets
    #'cluster_features' contains only the relevant features used by the clustering model
    #'x_live_cluster' is created by filtering only these features from X_live
    #subset the live Data for Clustering:
    x_live_cluster= X_live.filter(cluster_features)

    #'cluster_pipeline' is the trained clustering model
    #'.predict()' method assigns the new user to a specific cluster based on the model
    #'cluster_predictin[0]' stores the predicted cluster number
    #use the clustering model to predict the cluster:
    cluster_prediction = cluster_pipeline.predict(x_live_cluster)


    #display the cluster prediction
    statement = (f"### The prospect is expected to belong to **cluster {cluster_prediction[0]}**")
    st.write("---")
    st.write(statement)

    #provide a risk-based analysis for the damage
    #'based on past data...

    #explain cluster profiles for user understanding
    #This cluster profile... 

    #also add cluster importance graph, see 7Cluster.ipynb

    #display the cluster profile as a table
    cluster_profile.index = [" "] * len(cluster_profile)
    st.table(cluster_profile)

