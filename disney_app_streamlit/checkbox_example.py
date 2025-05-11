import streamlit as st
import json

st.title("Checkbox to JSON Example")

# Create 5 checkboxes
option1 = st.checkbox("Option 1")
option2 = st.checkbox("Option 2")
option3 = st.checkbox("Option 3")
option4 = st.checkbox("Option 4")
option5 = st.checkbox("Option 5")

# Create a dictionary of the selected options
selected_options = {
    "Option 1": option1,
    "Option 2": option2,
    "Option 3": option3,
    "Option 4": option4,
    "Option 5": option5
}

# Convert the dictionary to JSON
json_result = json.dumps(selected_options, indent=4)

# Display the JSON
st.subheader("Selected Options as JSON:")
st.code(json_result, language="json")

# Optional: Show only selected options
selected_only = {k: v for k, v in selected_options.items() if v}
if selected_only:
    st.subheader("Only Selected Options:")
    st.code(json.dumps(selected_only, indent=4), language="json")
else:
    st.info("No options selected yet.")