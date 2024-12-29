import streamlit as st
from helpers import initialize_global_session_variables_if_not_yet
import os

# In case this page was the first to be load by the user in the whole application,
# this will initialize them; and do nothing in the opposite case
initialize_global_session_variables_if_not_yet()

st.write("## This is the sample page(to be removed)")
st.write("Do not forget to use `initialize_session_variables_if_not_yet() in the beginning of every page")

PAGE_NUMBER = os.path.basename(__file__).split("_")[0]  # The number in front of the filename

st.write("### Sample of how to use input fields more properly")
st.write(
    "Problem: In Streamlit, changes to interactive elements (like radio buttons, selectboxes, and text inputs)"
    " often require an extra page reload to properly synchronize their state with session_state. This solution ensures"
    " immediate synchronization of user inputs with session_state using `on_change` callbacks.")
st.write("Below is the solution to this problem.")


# Functions to handle changes for each input element
def update_radio_state(key):
    st.session_state[key] = st.session_state[f"temp_{key}"]


def update_selectbox_state(key):
    st.session_state[key] = st.session_state[f"temp_{key}"]


def update_text_input_state(key):
    st.session_state[key] = st.session_state[f"temp_{key}"]


# Initialize session states for the elements
radio_key = "radio"
selectbox_key = "selectbox"
text_input_key = "text_input"

if radio_key not in st.session_state:
    st.session_state[radio_key] = "1"

if selectbox_key not in st.session_state:
    st.session_state[selectbox_key] = "Option 1"

if text_input_key not in st.session_state:
    st.session_state[text_input_key] = ""

# Render the elements with new approach
st.radio(
    "Choose an option",
    ["1", "2", "3"],
    key=f"temp_{radio_key}",
    index=["1", "2", "3"].index(st.session_state[radio_key]),
    on_change=update_radio_state,
    args=(radio_key,)
)

st.selectbox(
    "Select an option",
    ["Option 1", "Option 2", "Option 3"],
    key=f"temp_{selectbox_key}",
    index=["Option 1", "Option 2", "Option 3"].index(st.session_state[selectbox_key]),
    on_change=update_selectbox_state,
    args=(selectbox_key,)
)

st.text_input(
    "Enter some text",
    key=f"temp_{text_input_key}",
    value=st.session_state[text_input_key],
    on_change=update_text_input_state,
    args=(text_input_key,)
)

# Display current states
st.write(f"Radio state: {st.session_state[radio_key]}")
st.write(f"Selectbox state: {st.session_state[selectbox_key]}")
st.write(f"Text input state: {st.session_state[text_input_key]}")

# st.write(st.session_state)  # Uncomment to debug session state
