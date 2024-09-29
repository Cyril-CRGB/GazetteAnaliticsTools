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

def study_body():

    # load data
    dfcleanedshort = load_cleaned_data_short()
    
    st.write("## Study")
    st.info(
        f"The client is interested in understanding the data, with the help of some Exploratory Data Analysis tools (EDA).\n"
        f"* We need to understand statistical information about the data, with basic profiling. \n"
        f"* We will print Skewness and Kurtosis analysis. \n"
        f"* We will print a heatmap showing the spearman top 5 best correlation. \n"
    )

    st.write("""---""")

    st.success(
        f"**Profiling report:**\n"
        f"\n**Vict Age** has 24.6% of '0' as value and a negative value, this might also be confusing.\n"
        f"\n**Vict Descent** as 'X' 31.5% of the time, therefore this groupe 'unknown' is the most representated, this might influence the result.\n"
    )

    # display The Profiling Report
    if st.checkbox("Generate Profiling Report"):
        # Create the profile report
        pandas_report = ProfileReport(dfcleanedshort, minimal=True)
        # Save the report to a temporary HTML file
        report_html = pandas_report.to_html()
        # Display
        st.components.v1.html(report_html, height=400, scrolling=True)

    st.write("""---""")

    st.success(
        f"**Skewness and Kurtosis analysis:**\n"
        f"\nThese values suggest that while some variables may have outliers or are influenced by extremes values, the majority of the dataset does **not present exteme tail** behavior.\n"
    )
     
    # display The Skewness and Kurtosis analysis
    if st.checkbox("Show distribution, skewness and kurtosis"):
        distribution_skew_kurtosis(dfcleanedshort)

    st.warning(
        f"***Remarques:*** *Skewness and Kurtosis, a quick recap.* \n"
        f"\n*Skewness is the asymmetry of the data. A distribution is symmetric when it looks the same to the left and right of the centre point. It is horizontally mirrored. Positive Skewness happens when the tail on the right side is longer. Negative skewness is the opposite.* \n"
        f"\n*Kurtosis relates to the tails of the distribution. It is a measure of outliers in the distribution. A negative kurtosis indicates the distribution has thin tails. Positive kurtosis indicates that the distribution is peaked and has thick tails.* \n"
    )

    st.write("""---""")

    st.success(
        f"**Correlation analysis:**\n"
        f"\nThe top 6 correlated values with 'Damage' and 'Amount' are identical (not of the same importance).\n"
        f"\nThose correlations are negative as well as positive, they are between Moderate and Weak. \n"
        f"\nWe will go with this result for the rest of the project, yet if we wanted we could calculate a Predictive Power Score (PPS) using 'pps.matrix'. Now this could be usefull if we had categorical variables that where not already present in the numerical data. It is not really the case therefore we renounced it.\n"
    )

    # display The correlation analysis
    if st.checkbox("Show feature correlation analysis"):
        feature_correlation_analysis_spearman(dfcleanedshort)

    # display The correlation analysis
    if st.checkbox("Show top 6 features correlation"):
        six_best_correlated_features_correlation_analysis_spearman(dfcleanedshort, 'amount', 'damage')
        six_best_correlated_features_correlation_analysis_spearman(dfcleanedshort, 'damage', 'amount')

    st.warning(
        f"***Remarques:*** *Feature correlation analysis on numerical variables.* \n"
        f"\n*We preselected the best between the methods Spearman and Person: Spearman.* \n"
        f"\n*We converted categorical variables **Vict Sex** and **Vict Descent** into numerical using label encoding.* \n"
    )

    st.write("""---""")
