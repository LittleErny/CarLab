import streamlit as st
import pandas as pd
from helpers import initialize_session_variables_if_not_yet

# Hello page
st.set_page_config(page_title="Start", page_icon="🍌",) # Should change the naming later on

"""
This script uses Streamlit to visualize and analyze a cleaned dataset of car sales from eBay Germany.
Future improvements:
- Refactor the code for better readability and maintainability.
- Add markdown sections for better explanations and context.
- Enhance data visualizations and add more graphs.
- Optimize performance by using pre-downloaded data instead of downloading from Kaggle.
- Provide detailed explanations for numerical data correlations with categorical variables to improve readability.
"""

initialize_session_variables_if_not_yet()


st.sidebar.success('This is a success message!')

st.markdown('''
## Project Explanation

This page should contain an explanation of our project, info, and so on. For now, I will just leave a URL to a dataset that we will use during the project.

### Resources

- [Dataset](https://www.kaggle.com/datasets/shaunoilund/auto-sales-ebay-germany-random-50k-cleaned/code)
- [MyGit](https://mygit.th-deg.de/ma06524/sas-thd)
            
''')

