import streamlit as st
from helpers import initialize_session_variables_if_not_yet


# In case this page was the first to be load by the user in the whole application,
# this will initialize them; and do nothing in the opposite case
initialize_session_variables_if_not_yet()

st.write("## This is the sample page(to be removed)")
st.write("Do not forget to use ``initialize_session_variables_if_not_yet()`` in the beginning of every page")
