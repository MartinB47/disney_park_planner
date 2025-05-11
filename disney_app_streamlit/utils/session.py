import streamlit as st

def initialize_session_state():
    """Initialize session state variables if they don't exist"""
    if "location_set" not in st.session_state:
        st.session_state.location_set = False
    
    if "latitude" not in st.session_state:
        st.session_state.latitude = 33.8121  # Default to Disneyland Anaheim
    
    if "longitude" not in st.session_state:
        st.session_state.longitude = -117.9190  # Default to Disneyland Anaheim
    
    if "all_rides" not in st.session_state:
        st.session_state.all_rides = []
    
    if "selected_rides" not in st.session_state:
        st.session_state.selected_rides = []