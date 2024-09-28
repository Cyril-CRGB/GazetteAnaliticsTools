import streamlit as st

# Class to generate multiple Streamlit pages using an object-oriented approach
class MultiPage:

    def __init__(self, app_name) -> None:
        """
        Initializes the MultiPage class.
        - app_name (str): the name of the application
        """
        # List to hold the pages
        self.pages = [] 

        # Store the application name
        self.app_name = app_name 

        # Set the configuration for the Streamlit page
        st.set_page_config(page_title=self.app_name)

    def add_page(self, title, func) -> None:
        """
        Adds a new page to the app.
        Parameters:
        - Title (str): the title of the page.
        - func (callable): the function that renders the page's content.
        """
        self.pages.append({"title": title, "function": func}) # Append page details to the list

    def run(self):
        """Runs the application by rendering the selected page."""
        # Display the app name as the title
        st.title(self.app_name) 
        # Create a sidebar menu for page navigation
        page = st.sidebar.radio('Menu', self.pages, format_func=lambda page: page['title']) # Display page titles in the sidebar
        page['function']() # Call the selected page's function
