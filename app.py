import streamlit as st
from app_pages.multipage import MultiPage

# load pages scripts
from app_pages.summary import summary_body
from app_pages.data import data_body
from app_pages.study import study_body
from app_pages.hypothesis import hypothesis_body





# Create an instance of the app
app = MultiPage(app_name= "Insurance Prospecter")


# App pages 
app.add_page("Summary", summary_body)
app.add_page("Data", data_body)
app.add_page("Study", study_body)
app.add_page("Hypothesis & Validation", hypothesis_body)





# Run the app
app.run()