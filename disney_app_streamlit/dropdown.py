import boto3
import json
import streamlit as st
from get_rides import get_all_ride_names_from_dynamodb

# Page configuration for better appearance
st.set_page_config(
    page_title="Disneyland Ride Planner",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stSelectbox, .stMultiSelect {
        margin-bottom: 1.5rem;
    }
    .ride-item {
        padding: 0.5rem;
        background-color: #f0f2f6;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .selected-rides-container {
        margin-top: 1rem;
        padding: 1rem;
        background-color: #f9f9f9;
        border-radius: 0.5rem;
        border: 1px solid #e0e0e0;
    }
    .search-container {
        margin-bottom: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'all_rides' not in st.session_state:
    st.session_state.all_rides = []
    with st.spinner("Loading rides..."):
        result = get_all_ride_names_from_dynamodb()
        if result.get("status") == "success":
            st.session_state.all_rides = sorted(result['rides'])
        else:
            st.error(f"Error loading rides: {result.get('message')}")
            st.session_state.all_rides = []

if 'selected_rides' not in st.session_state:
    st.session_state.selected_rides = []

# Main app header
st.title("🎢 Disneyland Ride Planner")

# Create two columns for main layout
left_col, right_col = st.columns([3, 2])

with left_col:
    st.subheader("Find and Select Rides")
    
    # Auto-complete search box
    search_query = st.text_input("🔍 Search for rides", key="search")
    
    # Filter rides based on search query
    if search_query:
        filtered_rides = [ride for ride in st.session_state.all_rides 
                         if search_query.lower() in ride.lower()]
    else:
        filtered_rides = st.session_state.all_rides
    
    # Display number of matching rides
    st.caption(f"Found {len(filtered_rides)} rides")
    
    # Function to add a ride to selected list
    def add_ride(ride_name):
        if ride_name not in st.session_state.selected_rides:
            st.session_state.selected_rides.append(ride_name)
    
    # Display filtered rides with "Add" buttons
    if filtered_rides:
        st.write("### Available Rides")
        
        # Create a container for scrollable list
        with st.container():
            for ride in filtered_rides[:20]:  # Limit initial display to prevent overwhelming
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"**{ride}**")
                with col2:
                    if st.button("Add", key=f"add_{ride}", use_container_width=True):
                        add_ride(ride)
                        st.rerun()
            
            if len(filtered_rides) > 20:
                with st.expander("Show more rides"):
                    for ride in filtered_rides[20:]:
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.write(f"**{ride}**")
                        with col2:
                            if st.button("Add", key=f"add_{ride}", use_container_width=True):
                                add_ride(ride)
                                st.rerun()
    else:
        st.info("No rides match your search")

    # Quick add from dropdown
    st.write("### Quick Add")
    quick_add = st.selectbox(
        "Select a ride to add:",
        options=[""] + [r for r in st.session_state.all_rides if r not in st.session_state.selected_rides],
        index=0
    )
    
    if quick_add and st.button("Add Selected Ride", use_container_width=True):
        add_ride(quick_add)
        st.rerun()

with right_col:
    st.subheader("Your Selected Rides")
    
    # Display selected rides with remove buttons
    if st.session_state.selected_rides:
        for i, ride in enumerate(st.session_state.selected_rides):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"**{i+1}. {ride}**")
            with col2:
                if st.button("Remove", key=f"remove_{i}", use_container_width=True):
                    st.session_state.selected_rides.pop(i)
                    st.rerun()
        
        # Clear all button
        if st.button("Clear All Selections", type="secondary", use_container_width=True):
            st.session_state.selected_rides = []
            st.rerun()
        
        # Create JSON of the plan
        plan_json = {
            "selected_ride_count": len(st.session_state.selected_rides),
            "selected_rides": st.session_state.selected_rides
        }
        
        # Download button
        st.download_button(
            label="Download Ride Plan",
            data=json.dumps(plan_json, indent=2),
            file_name="disney_ride_plan.json",
            mime="application/json",
            use_container_width=True
        )
    else:
        st.info("No rides selected yet. Use the search or dropdown on the left to add rides to your plan.")

# Footer
st.markdown("---")
st.caption("Plan your perfect day at Disneyland by selecting the rides you want to experience.")