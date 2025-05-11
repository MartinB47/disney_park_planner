import streamlit as st
import json
import sys
import os
import time
import pandas as pd
from datetime import datetime, timedelta

# Set page configuration at the very beginning
st.set_page_config(
    page_title="Optimize Your Route",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Add the root directory to sys.path to enable imports from utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.session import initialize_session_state
from utils.ride_mapping import get_ride_ids_from_names
from utils.route_optimizer import optimize_routes

# Initialize session state
initialize_session_state()

# Check if rides are selected
if not st.session_state.get("selected_rides"):
    st.warning("⚠️ Please select rides first!")
    if st.button("Go to Rides Page"):
        st.switch_page("pages/2_Rides.py")
    st.stop()

# Custom CSS for better styling
st.markdown(
    """
<style>
    .main {
        padding: 2rem;
    }
    .route-container {
        margin-top: 1.5rem;
        padding: 1.5rem;
        background-color: #f9f9f9;
        border-radius: 0.5rem;
        border: 1px solid #e0e0e0;
    }
    .route-step {
        padding: 1rem;
        margin-bottom: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #4CAF50;
    }
    .route-step:nth-child(odd) {
        background-color: #f0f8ff;
    }
    .route-step:nth-child(even) {
        background-color: #f5f5f5;
    }
    .step-number {
        font-size: 1.2rem;
        font-weight: bold;
        color: #1E88E5;
    }
    .step-title {
        font-size: 1.3rem;
        font-weight: bold;
    }
    .step-details {
        margin-top: 0.5rem;
        color: #555;
    }
    .stats-container {
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
        margin-bottom: 1.5rem;
    }
    .stat-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        flex: 1;
        min-width: 200px;
        text-align: center;
    }
    .stat-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #1E88E5;
    }
    .stat-label {
        color: #555;
    }
    .map-container {
        margin-top: 1.5rem;
        height: 400px;
        border-radius: 0.5rem;
        overflow: hidden;
    }
    .loading-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 3rem;
    }
    .loading-text {
        margin-top: 1rem;
        font-size: 1.2rem;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Page title
st.title("🗺️ Optimize Your Disney Route")

# Display user location and selected rides
st.write(
    f"Your starting location: ({st.session_state.latitude:.6f}, {st.session_state.longitude:.6f})"
)
st.write(f"Selected rides: {len(st.session_state.selected_rides)}")


# Function to format time duration
def format_duration(minutes):
    hours = int(minutes // 60)
    mins = int(minutes % 60)
    if hours > 0:
        return f"{hours} hr {mins} min"
    return f"{mins} min"


# Function to calculate estimated time
def calculate_time_estimate(start_time, minutes_to_add):
    return start_time + timedelta(minutes=minutes_to_add)


# Main optimization process
if st.button("Optimize My Route", type="primary", use_container_width=True):
    with st.spinner("Optimizing your route..."):
        # Step 1: Get ride IDs for the selected ride names
        ride_id_result = get_ride_ids_from_names(st.session_state.selected_rides)

        if ride_id_result["status"] != "success" or ride_id_result["found_count"] == 0:
            st.error(
                f"Failed to get ride IDs: {ride_id_result.get('message', 'No ride IDs found')}"
            )
            if ride_id_result.get("missing_rides"):
                st.warning(
                    f"Could not find IDs for these rides: {', '.join(ride_id_result['missing_rides'])}"
                )
            st.stop()

        # Step 2: Call the optimization API
        ride_ids = ride_id_result["ride_ids"]
        st.info(f"Found {len(ride_ids)} ride IDs. Calling optimization API...")

        # Add a progress bar for visual feedback
        progress_bar = st.progress(0)
        for i in range(100):
            # Simulate progress while waiting for API
            time.sleep(0.02)
            progress_bar.progress(i + 1)

        optimization_result = optimize_routes(
            st.session_state.latitude, st.session_state.longitude, ride_ids
        )

        if optimization_result["status"] != "success":
            st.error(
                f"Failed to optimize route: {optimization_result.get('message', 'Unknown error')}"
            )
            if optimization_result.get("details"):
                with st.expander("Error Details"):
                    st.code(optimization_result["details"])
            st.stop()

        # Process successful result
        route_data = optimization_result["data"]

        # Extract the ordered rides and total time from the API response
        ordered_rides = route_data.get("orderedRides", [])
        total_time_minutes = route_data.get("totalTimeMinutes", 0)

        # Create tabs for different views
        # tab1, tab2, tab3 = st.tabs(["Route Overview", "Detailed Itinerary", "Map View"])
        tab1, tab2 = st.tabs(["Route Overview", "Detailed Itinerary"])

        with tab1:
            # Display summary statistics
            st.subheader("Route Summary")

            # Extract key statistics
            total_wait_time = sum(ride.get("waitTime", 0) for ride in ordered_rides)
            avg_wait_time = total_wait_time / len(ordered_rides) if ordered_rides else 0
            ride_count = len(ordered_rides)

            # Display statistics in cards
            st.markdown('<div class="stats-container">', unsafe_allow_html=True)

            # # Total time
            # st.markdown(f'''
            # <div class="stat-card">
            #     <div class="stat-value">{format_duration(total_time_minutes)}</div>
            #     <div class="stat-label">Total Experience Time</div>
            # </div>
            # ''', unsafe_allow_html=True)

            # Total wait time
            st.markdown(
                f"""
            <div class="stat-card">
                <div class="stat-value">{format_duration(total_wait_time)}</div>
                <div class="stat-label">Total Wait Time</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

            # Average wait time
            st.markdown(
                f"""
            <div class="stat-card">
                <div class="stat-value">{format_duration(avg_wait_time)}</div>
                <div class="stat-label">Average Wait Time</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

            # Ride count
            st.markdown(
                f"""
            <div class="stat-card">
                <div class="stat-value">{ride_count}</div>
                <div class="stat-label">Attractions</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

            st.markdown("</div>", unsafe_allow_html=True)

            # Display route overview
            st.subheader("Route Overview")

            if ordered_rides:
                # Create a DataFrame for the route
                route_df = pd.DataFrame(ordered_rides)

                # Rename columns for better display
                display_df = pd.DataFrame(
                    {
                        "Order": range(1, len(ordered_rides) + 1),
                        "Attraction": [
                            ride.get("name", "Unknown") for ride in ordered_rides
                        ],
                        "Wait Time": [
                            f"{ride.get('waitTime', 0)} min" for ride in ordered_rides
                        ],
                    }
                )

                # Display the table
                st.dataframe(display_df, use_container_width=True)
            else:
                st.info("No route steps found in the optimization result.")

        with tab2:
            st.subheader("Detailed Itinerary")

            # Display each step in the route with rich formatting
            if ordered_rides:
                # Get the current time to calculate actual times
                now = datetime.now()
                current_time = now

                # Estimate ride duration (since it's not provided by the API)
                estimated_ride_duration = 10  # minutes per ride, on average

                for i, ride in enumerate(ordered_rides):
                    ride_name = ride.get("name", "Unknown Ride")
                    wait_time = ride.get("waitTime", 0)

                    # Calculate estimated times
                    wait_end_time = calculate_time_estimate(current_time, wait_time)
                    ride_end_time = calculate_time_estimate(
                        wait_end_time, estimated_ride_duration
                    )

                    # Format for display
                    arrival_time_str = current_time.strftime("%I:%M %p")
                    wait_end_str = wait_end_time.strftime("%I:%M %p")
                    ride_end_str = ride_end_time.strftime("%I:%M %p")

                    # Calculate walking time to next attraction (estimate)
                    walking_time = 0
                    walking_distance = 0

                    if i < len(ordered_rides) - 1:
                        # Calculate distance between current and next ride
                        next_ride = ordered_rides[i + 1]
                        if all(key in ride for key in ["lat", "lon"]) and all(
                            key in next_ride for key in ["lat", "lon"]
                        ):
                            from math import sin, cos, sqrt, atan2, radians

                            # Approximate radius of earth in km
                            R = 6373.0

                            lat1 = radians(ride.get("lat"))
                            lon1 = radians(ride.get("lon"))
                            lat2 = radians(next_ride.get("lat"))
                            lon2 = radians(next_ride.get("lon"))

                            dlon = lon2 - lon1
                            dlat = lat2 - lat1

                            a = (
                                sin(dlat / 2) ** 2
                                + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
                            )
                            c = 2 * atan2(sqrt(a), sqrt(1 - a))

                            walking_distance = R * c
                            # Assume average walking speed of 5 km/h or 0.083 km/min
                            walking_time = walking_distance / 0.083

                    # Create a styled step card
                    st.markdown(
                        f"""
                    <div class="route-step">
                        <div class="step-number">Step {i+1}</div>
                        <div class="step-title" style="color: purple;">{ride_name}</div>
                        <div class="step-details">
                            <p><strong>Arrival:</strong> {arrival_time_str}</p>
                            <p><strong>Wait Time:</strong> {format_duration(wait_time)} (until {wait_end_str})</p>
                            <p><strong>Ride Time:</strong> {format_duration(estimated_ride_duration)} (until {ride_end_str})</p>
                            <p><strong>Walking to Next:</strong> {format_duration(walking_time)} ({walking_distance:.1f} km)</p>
                        </div>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )

                    # Update current time for next attraction
                    current_time = calculate_time_estimate(ride_end_time, walking_time)
            else:
                st.info("No route steps found in the optimization result.")

        # with tab3:
        #     st.subheader("Map View")

        #     # Check if we have coordinates for the rides
        #     has_coordinates = all(["lat" in ride and "lon" in ride for ride in ordered_rides])

        #     if has_coordinates and ordered_rides:
        #         # Create a map with the optimized route
        #         map_data = []

        #         # Add starting point
        #         map_data.append({
        #             "lat": st.session_state.latitude,
        #             "lon": st.session_state.longitude,
        #             "name": "Your Location (Start)"
        #         })

        #         # Add each ride location
        #         for i, ride in enumerate(ordered_rides):
        #             map_data.append({
        #                 "lat": ride.get("lat"),
        #                 "lon": ride.get("lon"),
        #                 "name": f"{i+1}. {ride.get('name', 'Unknown Ride')}"
        #             })

        #         # Convert to DataFrame for map
        #         map_df = pd.DataFrame(map_data)

        #         # Display the map with the route
        #         st.map(map_df, latitude="lat", longitude="lon")

        #         # Display the route order as a table
        #         route_order_df = pd.DataFrame({
        #             "Order": ["Start"] + [f"Stop {i+1}" for i in range(len(ordered_rides))],
        #             "Location": [map_data[0]["name"]] + [point["name"] for point in map_data[1:]]
        #         })

        #         st.subheader("Route Order")
        #         st.table(route_order_df)
        #     else:
        #         st.warning("Map view is not available because coordinate data is missing for some attractions.")

        #     # Provide option to download the itinerary
        #     st.download_button(
        #         label="Download Itinerary as JSON",
        #         data=json.dumps(route_data, indent=2),
        #         file_name="disney_optimized_route.json",
        #         mime="application/json"
        #     )

    # Final success message
    st.success(
        "✅ Route optimization complete! Follow the itinerary above for the most efficient way to experience your selected attractions."
    )

    # Tips for the user
    with st.expander("Tips for Your Visit"):
        st.markdown(
            """
        - **Arrive Early**: The park is less crowded in the morning.
        - **Stay Hydrated**: Bring a refillable water bottle.
        - **Take Breaks**: Schedule short breaks between attractions.
        - **Check Show Times**: Some shows have specific schedules.
        - **Use Mobile Ordering**: Save time by ordering food in advance.
        """
        )

else:
    # Display instructions when the page loads
    st.info(
        "Click the 'Optimize My Route' button to generate the most efficient path through your selected attractions."
    )

    # Show selected rides
    st.subheader("Your Selected Rides")
    for ride in st.session_state.selected_rides:
        st.write(f"- {ride}")
