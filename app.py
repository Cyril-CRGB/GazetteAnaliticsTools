import streamlit as st
from app_pages.multipage import MultiPage

# load pages scripts
from app_pages.summary import summary_body
from app_pages.data import data_body
from app_pages.study import study_body
from app_pages.hypothesis import hypothesis_body
from app_pages.cluster import cluster_body
from app_pages.predictions_prod_env import predictions_body_prod
from app_pages.predictions_test_env import predictions_body_test




# Create an instance of the app
app = MultiPage(app_name= "Insurance Prospecter")


# App pages 
app.add_page("Summary", summary_body)
app.add_page("Data", data_body)
app.add_page("Study", study_body)
app.add_page("Hypothesis & Validation", hypothesis_body)
app.add_page("ML Cluster", cluster_body)
#for prod
app.add_page("Predictions prod", predictions_body_prod)
#for testing
#app.add_page("Predictions testing", predictions_body_test)





# Run the app
app.run()