import streamlit as st
import json
import sys
import os

# Set page configuration at the very beginning
st.set_page_config(
    page_title="Location Setup",
    page_icon="📍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add the root directory to sys.path to enable imports from utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.session import initialize_session_state

# Initialize session state
initialize_session_state()

# Page title
st.title("📍 Set Your Location")
st.write("Please provide your current location to help plan your visit.")

# Create two columns for the layout
col1, col2 = st.columns([1, 1])

with col1:
    # Location input
    st.subheader("Enter Coordinates")
    latitude = st.number_input(
        "Latitude", 
        min_value=-90.0, 
        max_value=90.0, 
        value=st.session_state.get("latitude", 33.8121),  # Default to Disneyland Anaheim
        format="%.6f",
        help="Enter your latitude coordinate"
    )
    
    longitude = st.number_input(
        "Longitude", 
        min_value=-180.0, 
        max_value=180.0, 
        value=st.session_state.get("longitude", -117.9190),  # Default to Disneyland Anaheim
        format="%.6f",
        help="Enter your longitude coordinate"
    )
    
    # Save button
    if st.button("Save Location", use_container_width=True):
        st.session_state.latitude = latitude
        st.session_state.longitude = longitude
        st.session_state.location_set = True
        st.success("Location saved! You can now proceed to select rides.")
        
        # Create location JSON
        location_json = {
            "latitude": latitude,
            "longitude": longitude
        }
        st.session_state.location_json = json.dumps(location_json, indent=2)

with col2:
    # Display map with the location
    if st.session_state.get("latitude") and st.session_state.get("longitude"):
        st.subheader("Your Location")
        map_data = {
            "lat": [st.session_state.latitude],
            "lon": [st.session_state.longitude]
        }
        st.map(map_data)
        
        # Display the location as JSON
        st.subheader("Location Data")
        if st.session_state.get("location_json"):
            st.code(st.session_state.location_json, language="json")

# Navigation guidance
st.markdown("---")
if st.session_state.get("location_set"):
    st.info("✅ Location set! Click on 'Rides' in the sidebar to continue.")
else:
    st.warning("Please set your location before proceeding to ride selection.")

# Next page button
if st.session_state.get("location_set"):
    if st.button("Continue to Ride Selection →", use_container_width=True):
        st.switch_page("pages/2_Rides.py")