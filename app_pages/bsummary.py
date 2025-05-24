import streamlit as st

def summary_body():

    # st.title("Machin Learning Project for Los Angeles based insurance companies")
    
    st.header("🔡 Summary")

    st.info(
        f"**Project Terms & Jargon**\n"
        f"* **Explains** the **data** and gives exemples.\n"
        f"* **Covers** the **quality** of the data stored in our **database**.\n"
        f"* **Retrieves** the data for a **specific day**.\n"
        f"* **Deletes** the data for a **specific day**.\n"
        f"\n"
        f"This application is using the public API from the https://official-gazettes-portal.ch.\n\n"
        f"We are only interested in: \n" 
        f"* **HR01** = 'New entries', \n"
        f"* **HR02** = 'Change', \n"
        f"* **HR03** = 'Deletion'. \n"
    )

    st.write(
        f"For additional information, please visit and **read** my Github page: "
        f"[GazetteAnaliticsTools](https://github.com/Cyril-CRGB/GazetteAnaliticsTools.git)."
    )


    st.success(
        f"The project has 3 business requirements:\n"
        f"* 1 - Create an usable database and functions to manage it.\n"
        f"* 2 - Create an easy to understand and breathtaking publishable report.\n"
        f"* 3 - Create an AI assisted Client Relationship Manager (CRM) application.\n"
    )

