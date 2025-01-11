import streamlit as st
import pandas as pd
from helpers import initialize_global_session_variables_if_not_yet


def change_difficulty_level():
    st.session_state.hardcore_mode = (st.session_state.difficulty_level == "Hardcore 💪")


# Hello page
st.set_page_config(page_title="Start", page_icon="🍌")  # Should change the naming later on

"""
This script uses Streamlit to visualize and analyze a cleaned dataset of car sales from eBay Germany.
Future improvements:
- Refactor the code for better readability and maintainability.
- Add markdown sections for better explanations and context.
- Enhance data visualizations and add more graphs.
- Optimize performance by using pre-downloaded data instead of downloading from Kaggle.
- Provide detailed explanations for numerical data correlations with categorical variables to improve readability.
"""

initialize_global_session_variables_if_not_yet()

st.sidebar.success('This is a success message! 🎉')

st.markdown('''
## Project Overview 🚗💻

Welcome to our exciting project! Here, you'll find everything you need to dive into a fascinating dataset of car sales from eBay Germany. For now, we're leaving you with a couple of useful links:

### Resources

- [Dataset](https://www.kaggle.com/datasets/shaunoilund/auto-sales-ebay-germany-random-50k-cleaned/code) 📊
- [MyGit](https://mygit.th-deg.de/ma06524/sas-thd) 🔗

''')

st.write(
    "In this project, we present two ways to interact with the app:"
    " explore the dataset on your own or take a guided tour to see how we analyzed it. "
    "🚀 **If you're new to data analysis** (or you are the teacher that want to grade this project),"
    " we highly recommend starting with the beginner-friendly mode. "
    "We'll walk you through everything step by step. "
    "💡 But, if you're feeling bold and want to test your skills, you can try out the hardcore mode and compare "
    "your results with ours! Don't worry, a brief theoretical introduction, as well as the option to edit everything, "
    "will be available in either mode."
)

st.radio(
    "Choose your adventure level:",
    ("Beginner 🚀", "Hardcore 💪"),
    key="difficulty_level",
    on_change=change_difficulty_level,
    index=0 if not st.session_state.hardcore_mode else 1
)

# Display a message under the radio buttons
if st.session_state.hardcore_mode:
    st.markdown(
        "<p style='font-size: 12px; color: gray;'>Looks like you're ready to tackle the challenge! 💥</p>",
        unsafe_allow_html=True
    )
else:
    st.markdown(
        "<p style='font-size: 12px; color: gray;'>It's okay to start small—every expert was once a beginner! 😊</p>",
        unsafe_allow_html=True
    )

st.write("Regardless of what you choose, we strongly recommend that you do not skip pages and go in order. Good luck!")
st.write(st.session_state.hardcore_mode)