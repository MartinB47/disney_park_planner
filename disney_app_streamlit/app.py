import streamlit as st
import os
import sys

# Set page configuration at the very beginning
st.set_page_config(
    page_title="Disney Park Planner",
    page_icon="🏰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add the current directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils.session import initialize_session_state

# Initialize session state
initialize_session_state()

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    .step-card {
        padding: 1.5rem;
        border-radius: 0.5rem;
        background-color: #f8f9fa;
        margin-bottom: 1rem;
        border-left: 4px solid #4CAF50;
    }
    .step-number {
        font-size: 1.5rem;
        font-weight: bold;
        color: #4CAF50;
        margin-bottom: 0.5rem;
    }
    .step-title {
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .step-description {
        color: #555;
    }
    .feature-container {
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
        margin-top: 2rem;
    }
    .feature-card {
        flex: 1;
        min-width: 250px;
        padding: 1.5rem;
        border-radius: 0.5rem;
        background-color: #f0f7ff;
        text-align: center;
    }
    .feature-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }
    .feature-title {
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Main page content
st.markdown('<h1 class="main-header">🏰 Disney Park Planner</h1>', unsafe_allow_html=True)
st.write("Plan your perfect Disney day with our intelligent route optimizer! Follow the steps below to create your personalized itinerary.")

# Step-by-step instructions with improved styling
st.markdown("""
<div class="step-card">
    <div class="step-number">Step 1</div>
    <div class="step-title">📍 Set Your Location</div>
    <div class="step-description">
        Start by providing your current location or where you plan to start your Disney adventure. 
        This helps us calculate the optimal route for your visit.
    </div>
</div>

<div class="step-card">
    <div class="step-number">Step 2</div>
    <div class="step-title">🎢 Select Your Rides</div>
    <div class="step-description">
        Choose the attractions you want to experience during your visit. 
        Search for rides by name or browse the complete list to create your perfect Disney day.
    </div>
</div>

<div class="step-card">
    <div class="step-number">Step 3</div>
    <div class="step-title">🗺️ Optimize Your Route</div>
    <div class="step-description">
        Let our algorithm calculate the most efficient route between your selected attractions.
        We'll minimize walking distance and wait times to help you make the most of your day.
    </div>
</div>
""", unsafe_allow_html=True)

# Feature highlights
st.markdown('<div class="feature-container">', unsafe_allow_html=True)

st.markdown("""
<div class="feature-card">
    <div class="feature-icon">⏱️</div>
    <div class="feature-title">Save Time</div>
    <p>Our optimization algorithm minimizes walking distance and wait times</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="feature-card">
    <div class="feature-icon">📱</div>
    <div class="feature-title">Easy to Use</div>
    <p>Simple interface makes planning your Disney day quick and hassle-free</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="feature-card">
    <div class="feature-icon">📊</div>
    <div class="feature-title">Smart Planning</div>
    <p>Get detailed itineraries with timing information for each attraction</p>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Get started button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("Get Started", type="primary", use_container_width=True):
        st.switch_page("pages/1_Location.py")

# Sidebar navigation
st.sidebar.title("Navigation")
st.sidebar.info(
    "Follow these steps to plan your visit:\n\n"
    "1️⃣ **Location** - Set your starting point\n\n"
    "2️⃣ **Rides** - Select attractions\n\n"
    "3️⃣ **Optimize** - Get your route"
)

# App information in the sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("About")
st.sidebar.info(
    "This app uses advanced algorithms to help you plan the most efficient route "
    "through Disney parks, minimizing walking distance and wait times."
)

# Footer
st.markdown("---")
st.caption("Disney Park Planner © 2023 | Not affiliated with Disney")