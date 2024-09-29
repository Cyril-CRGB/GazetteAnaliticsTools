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

"""
streamlit page cluster
"""
# Function Pipeline LuxuriusCluster, from 7Cluster.ipynb
def LuxuriusCluster():
    pipeline_base = Pipeline([
        ("OrdinalCategoricalEncoder", OrdinalEncoder(encoding_method='arbitrary',
                                                variables=['Vict Sex', 'Vict Descent', 'Premis Desc', 'Weapon Desc',
                                                        'LOCATION', 'Cross Street'])),
        ("scaler", StandardScaler()),
        ("PCA", PCA(n_components=11, random_state=77)),
        ("model", KMeans(n_clusters=5, random_state=77)),
    ])
    return pipeline_base

# Function for PCA, from 7Cluster.ipynb
def pca_on_streamlit(df):
    pipeline_cluster = LuxuriusCluster()
    pipeline_pca = Pipeline(pipeline_cluster.steps[:-2])
    df_pca = pipeline_pca.fit_transform(df)
    # Set the number of components as all columns in the data, we are aiming for 90%
    n_components = 11
    # Set PCA object and fit to the data
    pca = PCA(n_components=n_components).fit(df_pca)
    # Array with transformed PCA
    x_PCA = pca.transform(df_pca)
    # the PCA object has .explained_variance_ratio_ attribute, which tells
    # how much information (variance) each component has
    # We store that to a DataFrame relating each component to its variance explanation
    ComponentsList = ["Component " + str(number) for number in range(n_components)]
    dfExplVarRatio = pd.DataFrame(
        data= np.round(100 * pca.explained_variance_ratio_, 3),
        index=ComponentsList,
        columns=['Explained Variance Ratio %)']
    )
    # prints how much of the dataset these components explain (naturally in this case will be 100%)
    PercentageOfDataExplained = dfExplVarRatio['Explained Variance Ratio %)'].sum()
    # Display
    print(f"* The {n_components} components explain {round(PercentageOfDataExplained,2)}% of the data \n")
    print(dfExplVarRatio)
    

