import streamlit as st

def summary_body():

    # st.title("Machin Learning Project for Los Angeles based insurance companies")
    
    st.write("## Summary")

    st.info(
        f"**Project Terms & Jargon**\n"
        f"* **Dataset** is a collection of data that is used for analysis or training machine learning models.\n"
        f"* **Feature** refers to an individual measurable property or characteristic of the dataset.\n"
        f"* **Damage** refers to possibility of an individual living in Los Angeles and beeing victim of a crime to ask an insurance for compensation of the damage.\n"
        f"* **Amount** refers to the evaluation of the amount that the victim could ask for.\n"
        f"\n"
        f"This application is using a **free public** dataset from Kaggle called 'Crime_Data_from_2020_to_Present.csv', and showcases the use of varius Machine Learning tasks like: *classification*, *regression*, and *clustering*.\n"
        f"\n"
        f"Find the Dataset on https://www.kaggle.com/datasets/candacegostinski/crime-data-analysis/data.\n"
    )

    st.write(
        f"* For additional information, please visit and **read** the "
        f"[PP5_My_project](https://github.com/Cyril-CRGB/PP5_My_project.git)."
    )


    st.success(
        f"The project has 2 business requirements:\n"
        f"* 1 - The client is interested in understanding who amongs the victim dataset also had damage dealt to his/her property. This will be referred to as **Damage**.\n"
        f"* 2 - The client is interested in figuring the range of the damage that the insurance could repay to the victim. This will be referred to as **Amount**.\n"
    )