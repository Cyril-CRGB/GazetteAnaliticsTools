import streamlit as st
from app_pages.amultipage import MultiPage

st.set_page_config(
    page_title="Gazette analytics tools",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)
# load pages scripts
from app_pages.bsummary import summary_body
from app_pages.cdata import data_body
from app_pages.dcoverage import coverage_body
from app_pages.eretrieve import retrieve_body

# Create an instance of the app
app = MultiPage(app_name= "Gazette analytics tools")

# App pages 
app.add_page("🔡 Summary", summary_body)
app.add_page("📑 Data", data_body)
app.add_page("📅 Coverage", coverage_body)
app.add_page("📥 Retrieve", retrieve_body)

# Run the app
app.run()