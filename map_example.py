import streamlit as st
import pandas as pd
import pydeck as pdk
import json

st.title("Map Location Picker")

# Initialize session state to store the selected location
if 'latitude' not in st.session_state:
    st.session_state.latitude = 37.7749  # Default: San Francisco
if 'longitude' not in st.session_state:
    st.session_state.longitude = -122.4194

# Function to update coordinates when sliders change
def update_coords():
    location_json = json.dumps({
        "latitude": st.session_state.latitude,
        "longitude": st.session_state.longitude
    }, indent=4)
    
    st.session_state.location_json = location_json

# Create sliders for precise location selection
st.subheader("Select Location")
st.slider("Latitude", min_value=-90.0, max_value=90.0, value=st.session_state.latitude, 
          key="latitude", on_change=update_coords, step=0.0001, format="%.4f")
st.slider("Longitude", min_value=-180.0, max_value=180.0, value=st.session_state.longitude, 
          key="longitude", on_change=update_coords, step=0.0001, format="%.4f")

# Create a visual map with the selected point
view_state = pdk.ViewState(
    latitude=st.session_state.latitude,
    longitude=st.session_state.longitude,
    zoom=13,
    pitch=0
)

# Create a layer with a single point
layer = pdk.Layer(
    'ScatterplotLayer',
    data=[{
        'position': [st.session_state.longitude, st.session_state.latitude],
        'radius': 100,
        'color': [255, 0, 0]
    }],
    get_position='position',
    get_radius='radius',
    get_color='color',
    pickable=True
)

# Render the map
st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/light-v9',
    initial_view_state=view_state,
    layers=[layer]
))

# Display the JSON
if hasattr(st.session_state, 'location_json'):
    st.subheader("Location as JSON:")
    st.code(st.session_state.location_json, language="json")
else:
    update_coords()  # Initialize the JSON display
    st.subheader("Location as JSON:")
    st.code(st.session_state.location_json, language="json")

# Additional instructions
st.info("Use the sliders to select a precise location. The map will update to show your selected point.")