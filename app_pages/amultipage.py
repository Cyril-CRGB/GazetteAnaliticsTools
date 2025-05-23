# app_pages/amultipage.py

import streamlit as st

class MultiPage:
    def __init__(self, app_name) -> None:
        """
        Initializes the MultiPage class.
        - app_name (str): the name of the application
        """
        self.pages = []
        self.app_name = app_name
        # <<-- remove the st.set_page_config call from here
        # st.set_page_config(page_title=self.app_name)

    def add_page(self, title, func) -> None:
        """
        Adds a new page to the app.
        - title (str): page title shown in the sidebar
        - func (callable): function that renders the page
        """
        self.pages.append({"title": title, "function": func})

    def run(self):
        """Renders the sidebar and the selected page."""
        st.title(self.app_name)
        page = st.sidebar.radio(
            "Menu",
            self.pages,
            format_func=lambda page: page["title"]
        )
        page["function"]()