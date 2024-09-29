import streamlit as st
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

from src.streamlit_data_management import load_original_data
from src.streamlit_data_management import load_crime_committed_analyses
from src.streamlit_data_management import load_cleaned_data_short

sns.set_style('dark')



def data_body():

    # load data
    df = load_original_data()
    dfcca = load_crime_committed_analyses()
    dfcleanedshort = load_cleaned_data_short()
    
    st.write("## Data")
    st.info(
        f"The client is interested in understanding the data.\n"
        f"* Determine what the data means.\n"
        f"* Determine if we have all information we need and no unusable variables.\n"
        f"* Determine how we can add the information we need to the data.\n"
        f"* Make the change!"
    )
    
    # display raw data
    if st.checkbox("Have a look at the raw data"):
        st.write(
            f"The dataset has {df.shape[0]} rows and {df.shape[1]} columns, "
            f"find below the first rows."
        )
        st.write(df.head(10))

    st.write("""---""")

    st.info(
            f"The meaning of each variable is the following: \n"
            f"\n"
            f"**DR_NO**: 'police case unique number', **Date Rptd**: 'the day the crime was reported', **DATE OCC**: 'the day the crime was committed', **TIME OCC**: 'the time the crime was committed', **AREA**: 'the area code'," 
            f" **AREA NAME**: 'the area name', **Rpt Dist No**: 'unkown signification', **Part 1-2**: 'unkown signification', **Crm Cd**: 'the crime code', **Crm Cd Desc**: 'the crime code description',"
            f" **Mocodes**: 'the description of the event, as a list of codes', **Vict Age**: 'the age of the victims', **Vict Sex**: 'the sex of the victims', **Vict Descent**: 'the place of birth of the victims',"
            f" **Premis Cd**: 'the premis code', **Premis Desc**: 'the premis description', **Weapon Used Cd**: 'the weapon used code', **Weapon Desc**: 'the weapon used description',"
            f" **Status**: 'unkown signification', **Status Desc**: 'unknown signification', **Crm Cd 1**: 'the crime code 2', **Crm Cd 2**: 'the crime code 3', **Crm Cd 3**: 'the crime code 4',"
            f" **Crm Cd 4**: 'the crime code 5', **LOCATION**: 'location code and description', **Cross Street**: 'cross ctreet', **LAT**: 'latitude', **LON**: 'longitude'"
        )

    # examples of each variables
    if st.checkbox('Show an examples of each columns'):
        # Loop through each columns in the DataFrame
        example_list = []
        for column in df.columns:
            # Get 1 example
            example = df[column].head(1).tolist()
            # Create a dictionary for the column and its example
            example_list.append({"Column name": column, "Example": ', '.join(map(str, example))})
        # Create a DataFrame from the examples list
        example_df = pd.DataFrame(example_list)
        st.dataframe(example_df)

    st.write("""---""")

    st.info(
            f"There is no duplicates: \n"
            f"* we will use 'DR_NO' variable to find out \n"
        )

    # Display the checkbox for missing values
    if st.checkbox('Show duplicate count "DR_NO"'):
        # Count occurrences of each 'DR_NO'
        duplicate_counts = df['DR_NO'].value_counts().reset_index()
        duplicate_counts.columns = ['DR_NO', 'Count'] # Rename columns
        # Filter to show only duplicates (count > 1)
        duplicates_only = duplicate_counts[duplicate_counts['Count'] > 1]
        st.dataframe(duplicates_only)

    st.write("""---""")

    st.info(
            f"The missing information are: \n"
            f"* there are missing variables 'n/a'\n"
            f"* there is no columns that gives away the **Amount** of the damage endured by the victim. However we found two information that could help us: \n"
            f"1) Some of **Crm Cd Desc** variables contain a '$'. \n"
            f"2) we found a list on the internet that gives all definition of the **Mocodes**, '2046' contains the indication that the damage **Amount** would have exceeded $25'000. \n"
        )

    # Display the checkbox for missing values
    if st.checkbox('Show missing values count "n/a"'):
        # Calculate the count of missing values and convert to DataFrame
        missing_values = df.isna().sum()
        missing_values_df = pd.DataFrame(missing_values).reset_index()
        # Rename columns
        missing_values_df.columns = ['Column name', 'Missing values count']
        # Filter to show only columns with missing values
        missing_values_filtered = missing_values_df[missing_values_df['Missing values count'] > 0]
        # Display
        st.dataframe(missing_values_filtered)

    st.write("""---""")

    st.info(
            f"With the list of unique **Crm Cd Desc** we decided to create another dataset containing: \n"
            f"* **Crm CD Desc** \n"
            f"* **Min $** (new value) \n"
            f"* **Max $** (new value) \n"
            f"* **Crm Cd** \n"
            f"\n"
            f"We also decided to add other **Crm CD Desc** although they did not contain a '$' like for instance 'Purs snatching'. \n"
            f"This list will allow us to add our two variables **Damage** and **Amount** to the raw dataset. \n"
        )

    # display data Crm Cd Desc analyses
    if st.checkbox("Have a look at the additional dataset"):
        st.write(
            f"The new dataset has {dfcca.shape[0]} rows and {dfcca.shape[1]} columns, "
            f"find below the first rows."
        )
        st.write(dfcca)

    st.write("""---""")

    st.info(
            f"Analysis of **Vict Sex**: \n"
            f"* there are 6 different variables: 'M', 'F', 'NaN', 'H', 'X', '-'. \n"
            f"* For the purpose of this exercise, we decided to merge 'NaN', 'H', 'X', '-' together. \n"
            f"* We consider that this merge will not make us lose any meaning, 'X' meaning 'other'. \n"
        )

    # display data 'Vict Sex' analyses
    if st.checkbox("Show the variables 'Vict Sex'"):
        # Get all unique values of 'Vict Sex'
        unique_values_vict_sex = df['Vict Sex'].unique()
        unique_values_vict_sex_count = len(unique_values_vict_sex)
        st.write(f"***{unique_values_vict_sex_count} unique values:***")
        # Get the unique values and their counts
        unique_values_vict_sex_count_2 = df['Vict Sex'].value_counts(dropna=False)
        # Display as dataframe
        st.dataframe(unique_values_vict_sex_count_2.reset_index().rename(columns={'index': 'Victime Sex', 'Vict Sex': 'Count'}))

    st.write("""---""")

    st.info(
            f"Analysis of **Vict Descent**: \n"
            f"* A - Other Asian B - Black C - Chinese D - Cambodian F - Filipino G - Guamanian H - Hispanic/Latin/Mexican I - American Indian/Alaskan Native J - Japanese K - Korean L - Laotian O - Other P - Pacific Islander S - Samoan U - Hawaiian V - Vietnamese W - White X - Unknown Z - Asian Indian. \n"
            f"* For the purpose of this exercise, we decided to merge 'NaN', 'O', 'X', '-' together. \n"
            f"* We consider that this merge will not make us lose any meaning, 'X' meaning 'unkown'. \n"
        )

    # display data 'Vict Descent' analyses
    if st.checkbox("Show the variables 'Vict Descent'"):
        # Get all unique values of 'Vict Descent'
        unique_values_vict_desc = df['Vict Descent'].unique()
        unique_values_vict_desc_count = len(unique_values_vict_desc)
        st.write(f"***{unique_values_vict_desc_count} unique values:***")
        # Get the unique values and their counts
        unique_values_vict_desc_count_2 = df['Vict Descent'].value_counts(dropna=False)
        # Display as dataframe
        st.dataframe(unique_values_vict_desc_count_2.reset_index().rename(columns={'index': 'Victime Descent', 'Vict Descent': 'Count'}))

    st.write("""---""")

    st.info(
            f"Working with other variables: \n"
            f"* Missing values for **Premis Cd** and **Premis Desc** replaced by '116' and 'OTHER/OUTSIDE'. \n"
            f"* Missing values for **Weapon used Cd** and **Weapon Desc** replaced by '999' and 'NO WEAPON'. \n"
            f"* Missing values for **Cross Street** replaced by 'NO CROSS STREET'. \n"
            f"* **Date Occ**: extracted the day of the week. \n"
            f"* Dropped those variables: **DR_NO**, **Date Rptd**, **Rpt Dist No**, **Part 1-2**, **Mocodes**, **Status**, **Status Desc**, **Crm Cd 1, 2, 3, 4**. \n"
            f"* We also randomly selected 10K lignes in order to avoid overfitting the model."
        )
    
    # display data cleaned and shorted analyses
    if st.checkbox("Have a look at the shorted and cleaned data"):
        st.write(
            f"The dataset has {dfcleanedshort.shape[0]} rows and {dfcleanedshort.shape[1]} columns, "
            f"find below the first 10 rows."
        )
        st.write(dfcleanedshort.head(10))