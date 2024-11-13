import streamlit as st

# Hello page
st.set_page_config(page_title="Start", page_icon="🍌",) #Should change the naming later on

st.sidebar.success('This is a success message!')

st.markdown('''
## Project Explanation

This page should contain an explanation of our project, info, and so on. For now, I will just leave a URL to a dataset that we will use during the project.

### Resources

- [Dataset](https://www.kaggle.com/datasets/shaunoilund/auto-sales-ebay-germany-random-50k-cleaned/code)
- [MyGit](https://mygit.th-deg.de/ma06524/sas-thd)
            
''')

