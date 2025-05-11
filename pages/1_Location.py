import streamlit as st
import json
import pandas as pd
import plotly.express as px
from streamlit_js_eval import get_geolocation  # pip install streamlit_js_eval

st.title("Disneyland Rides Map")

# — load rides.json (must include rideId, name, lat, lon, description) —
with open("rides_with_descriptions.json", "r") as f:
    rides = json.load(f)
df = pd.DataFrame(rides)

# — keep user_loc in session state —
if "user_loc" not in st.session_state:
    st.session_state.user_loc = None

# — prompt once for geolocation —
if st.session_state.user_loc is None:
    loc = get_geolocation()
    if loc:
        lat = loc["coords"]["latitude"]
        lon = loc["coords"]["longitude"]
        st.session_state.user_loc = (lat, lon)
        st.session_state.location_set = True
        st.session_state.latitude = lat
        st.session_state.longitude = lon
        
# — build map, centering & dropping marker if we have coords —
def make_map(user_loc=None):
    fig = px.scatter_mapbox(
        df,
        lat="lat",
        lon="lon",
        hover_name="name",
        custom_data=["description"],      # supply description without label
        zoom=16,
        height=600,
        color_discrete_sequence=["red"],
    )
    fig.update_traces(
    marker=dict(size=12),
    selector=dict(mode="markers")     # only the ride dots (not your blue user‐dot)
    )

    # use a hovertemplate to show only name & description,
    # and left-align both lines
    fig.update_traces(
        hovertemplate=(
            "<b>%{hovertext}</b><br>%{customdata[0]}<extra></extra>"
        ),
        hoverlabel=dict(align="left")
    )

    if user_loc:
        lat, lon = user_loc
        fig.update_layout(mapbox_center={"lat": lat, "lon": lon})
        fig.add_scattermapbox(
            lat=[lat],
            lon=[lon],
            mode="markers+text",
            marker=dict(size=12, color="blue"),
            textposition="top right",
            showlegend=False,
            name="",
            hovertemplate="You are here!<extra></extra>",
        )

    fig.update_layout(
        mapbox_style="open-street-map",
        margin=dict(l=0, r=0, t=0, b=0),
        shapes=[                          # thin black border
            dict(
                type="rect",
                xref="paper",
                yref="paper",
                x0=0, y0=0, x1=1, y1=1,
                line=dict(color="black", width=3),
                fillcolor="rgba(0,0,0,0)",
            )
        ],
    )

    return fig

# — render the map —
st.plotly_chart(make_map(st.session_state.user_loc), use_container_width=True)