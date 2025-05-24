# app_pages/houtreach.py

import streamlit as st
from datetime import date
from src.streamlit_calculation import get_new_clients_of_today  # a helper that returns the df filtered inewclientsoftheday
from src.streamlit_social_agent import (
    find_on_twitter, find_on_linkedin,
    generate_message,
    send_twitter_dm, send_linkedin_message
)

def newoutreach_body():
    st.header("🤖 AI-Powered Outreach")

    df = get_new_clients_of_today()  # same filter: New entries & today
    if df.empty:
        st.warning("No new clients today.")
        return

    # Let user pick a target
    choice = st.selectbox(
        "Pick a company/person to reach out to",
        df["company_name"].tolist()
    )
    row = df[df["company_name"] == choice].iloc[0]

    st.markdown(f"**Target:** {choice} ({row['company_uid']})")

    # 1) Discover social profile
    if st.button("🔍 Lookup on Twitter & LinkedIn"):
        twitter_user = find_on_twitter(choice)
        linkedin_profile = find_on_linkedin(choice)
        st.write("Twitter:", twitter_user.screen_name if twitter_user else "❌ Not found")
        st.write("LinkedIn:", linkedin_profile.get("id") if linkedin_profile else "❌ Not found")

    # 2) Generate outreach
    if st.button("✍️ Generate message"):
        msg = generate_message(choice, row["company_name"])
        st.code(msg)

    # 3) Send it (choose channel)
    channel = st.radio("Send via", ["Twitter DM", "LinkedIn"])
    if st.button("🚀 Send message"):
        if channel == "Twitter DM" and twitter_user:
            send_twitter_dm(twitter_user.id_str, msg)
            st.success("Twitter DM sent!")
        elif channel == "LinkedIn" and linkedin_profile:
            send_linkedin_message(linkedin_profile["id"], msg)
            st.success("LinkedIn message sent!")
        else:
            st.error("Profile not found or invalid channel.")