import streamlit as st
from helpers import initialize_global_session_variables_if_not_yet
import os

# In case this page was the first to be load by the user in the whole application,
# this will initialize them; and do nothing in the opposite case
initialize_global_session_variables_if_not_yet()

st.write("## This is the sample page (to be removed)")
st.write("Do not forget to use `initialize_session_variables_if_not_yet()` in the beginning of every page")

PAGE_NUMBER = os.path.basename(__file__).split("_")[0]  # The number in front of the filename

st.write("### Sample of how to use input fields more properly")
st.write(
    "Problem: In Streamlit, changes to interactive elements (like radio buttons, selectboxes, and text inputs) "
    "often require an extra page reload to properly synchronize their state with session_state. This solution ensures "
    "immediate synchronization of user inputs with session_state using `on_change` callbacks."
)
st.write("Below is an example illustrating the problem and its solution.")

# --- Example of the Problem ---
st.write("#### Example: Problematic Implementation")
st.write("This implementation does not synchronize state immediately after user interaction.")

# Initialize session state for problematic example
if "problem_radio" not in st.session_state:
    st.session_state["problem_radio"] = "1"

# Problematic radio button implementation
problem_radio_value = st.radio(
    "Problematic Radio Button",
    ["1", "2", "3"],
    index=["1", "2", "3"].index(st.session_state["problem_radio"]),
    key="problem_temp_radio"
)

# Display the state directly, without immediate synchronization
st.write(f"Problematic Radio Button state: {st.session_state['problem_radio']}")

# Sync the value manually for demonstration (would only happen on subsequent render)
if st.session_state.get("problem_temp_radio", None) != st.session_state["problem_radio"]:
    st.session_state["problem_radio"] = st.session_state["problem_temp_radio"]

st.write("---")

# --- Solution ---
st.write("#### Example: Proper Implementation")
st.write("This implementation ensures immediate synchronization of state without requiring additional interaction.")


# Functions to handle changes for each input element
def update_session_state(key):
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

# Render the elements with the new approach
st.radio(
    "Choose an option",
    ["1", "2", "3"],
    key=f"temp_{radio_key}",
    index=["1", "2", "3"].index(st.session_state[radio_key]),
    on_change=update_session_state,
    args=(radio_key,)
)

st.selectbox(
    "Select an option",
    ["Option 1", "Option 2", "Option 3"],
    key=f"temp_{selectbox_key}",
    index=["Option 1", "Option 2", "Option 3"].index(st.session_state[selectbox_key]),
    on_change=update_session_state,
    args=(selectbox_key,)
)

st.text_input(
    "Enter some text",
    key=f"temp_{text_input_key}",
    value=st.session_state[text_input_key],
    on_change=update_session_state,
    args=(text_input_key,)
)

# Display current states
st.write(f"Radio state: {st.session_state[radio_key]}")
st.write(f"Selectbox state: {st.session_state[selectbox_key]}")
st.write(f"Text input state: {st.session_state[text_input_key]}")

# Uncomment to debug session state
# st.write(st.session_state)
