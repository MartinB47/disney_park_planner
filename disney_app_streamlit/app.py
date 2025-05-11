import streamlit as st
import os
import sys

# Set page configuration at the very beginning
st.set_page_config(
    page_title="Disney Planner",
    page_icon="🏰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add the current directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils.session import initialize_session_state

# Initialize session state
initialize_session_state()

# Main page content
st.title("🏰 Disney Park Planner")
st.write("Welcome to the Disney Park Planner! Use the navigation in the sidebar to plan your visit.")

# Instructions
st.markdown("""
## How to Use This App

1. **Set Your Location**: First, provide your current location to help plan your visit.
2. **Select Rides**: Choose the rides you want to experience during your visit.

Use the sidebar navigation to move between pages.
""")

# Sidebar navigation
st.sidebar.title("Navigation")
st.sidebar.info(
    "Use the pages in the sidebar to navigate through the app:\n"
    "1. Location - Set your starting point\n"
    "2. Rides - Select rides for your visit"
)