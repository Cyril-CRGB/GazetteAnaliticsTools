import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from ydata_profiling import ProfileReport
from scipy import stats
from feature_engine.encoding import OrdinalEncoder
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from streamlit_data_management import load_pkl_file


sns.set_style('dark')

def cluster_body():

    # load cluster analysis files and pipeline
    version1 = 'v1'
    version2 = 'v2'
    
    try:
        cluster_elbow = plt.imread(
            f"outputs/pictures/{version1}/elbow_method.png")
        cluster_silhouette = plt.imread(
            f"outputs/pictures/{version1}/silhouette_score.png")
        best_features = plt.imread(
            f"outputs/pictures/{version1}/best_features_v1.png")
        cluster_frequencies = plt.imread(
            f"outputs/pictures/{version1}/cluster_frequencies_v1.png")  
        cluster_profile = pd.read_csv(
            f"outputs/datasets/other/{version1}/clusters_profile.csv")

        cluster_elbow_v2 = plt.imread(
            f"outputs/pictures/{version2}/elbow_method_v2.png")
        cluster_silhouette_v2 = plt.imread(
            f"outputs/pictures/{version2}/silhouette_score_v2.png")
        best_features_v2 = plt.imread(
            f"outputs/pictures/{version2}/best_features_v2.png")
        cluster_frequencies_v2 = plt.imread(
            f"outputs/pictures/{version2}/cluster_frequencies_v2.png")
        cluster_profile_v2 = pd.read_csv(
            f"outputs/datasets/other/{version2}/clusters_profile_v2.csv")
        confusion_matrix_v2 = plt.imread(
            f"outputs/pictures/{version2}/confusion_matrix_v2.png")

    except FileNotFoundError as e:
        st.error(f"Error loading files: {e}")
        return


    st.write("## ML Cluster")

    st.info(
        f"* We modeled a cluster pipeline. \n"
        f"* We used **Principal Component Analysis (PCA)** to determine the right number of features to train the model with. \n"
        f"* We dertermine the number of cluster needed with Elbow and Silhouette methode\n"
        f"* We then profiled the cluster\n"
        f"* Finally we used a Classifier to determine the best features: **GradientBoostingClassifier**, and repeated the entire process and compared"
    )

    #create two columns
    col1, col2 = st.columns(2) # on test environnement write st.beta_columns

    with col1:
        st.write("## All features")
        st.write("")
        st.write("#### The most important features")
        st.image(best_features)

        st.write("#### Cluster frequencies")
        st.image(cluster_frequencies)

        st.write("#### Clusters Elbow Plot")
        st.image(cluster_elbow)

        st.write("#### Clusters Silhouette Plot")
        st.image(cluster_silhouette)
            
        st.write("#### Clusters Profiling")
        cluster_profile.index = [" "] * len(cluster_profile)
        st.dataframe(cluster_profile, height=300)

    with col2:
        st.write("## Best features")
        st.write("")
        st.write("#### The most important features")
        st.image(best_features_v2)

        st.write("#### Cluster frequencies")
        st.image(cluster_frequencies_v2)

        st.write("#### Clusters Elbow Plot")
        st.image(cluster_elbow_v2)

        st.write("#### Clusters Silhouette Plot")
        st.image(cluster_silhouette_v2)
            
        st.write("#### Clusters Profiling")
        cluster_profile_v2.index = [" "] * len(cluster_profile_v2)
        st.dataframe(cluster_profile_v2, height=300)

    st.success(
        f"* The pipeline trained with only 5 features, is different than the one trained with all the features. It would need to be improved by further developpement. \n"
        f"* We decided to keep 5 clusters, although the reduced model indicated that 4 was more suitable. \n"
        f"* Here is the confusion matrix with both data, we can see that the only Cluster 'comparable' is the 'All 1' and 'Best 1': \n"
    )
    st.write("### Confusion matrix")
    st.image(confusion_matrix_v2)