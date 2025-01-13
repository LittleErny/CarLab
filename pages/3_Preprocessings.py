import streamlit as st
from helpers import initialize_global_session_variables_if_not_yet, CATEGORICAL_COLUMNS, NUMERICAL_COLUMNS
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


# In case this page was the first to be load by the user in the whole application,
# this will initialize them; and do nothing in the opposite case
initialize_global_session_variables_if_not_yet()


# Helper function to remove outliers
def remove_outliers(df, column, method, threshold):
    if method == 'top':
        return df[df[column] <= df[column].quantile(1 - threshold / 100)]
    elif method == 'bottom':
        return df[df[column] >= df[column].quantile(threshold / 100)]
    elif method == 'both':
        lower_bound = df[column].quantile(threshold / 100)
        upper_bound = df[column].quantile(1 - threshold / 100)
        return df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]
    else:
        return df


# Title and description
st.title("Preprocessing Tool")

st.markdown("""
### Data Preprocessing Overview
This tool allows you to preprocess your dataset interactively. The following steps are available:
- **Outliers Removal**: Identify and remove outliers to improve model accuracy and reduce biases.
- **Label Encoding**: Convert categorical variables into numerical representations.
- **Scaling**: Normalize or standardize numerical features for better model performance.
- **Removing Unnecessary Columns**: Remove irrelevant columns or filter rows based on specific categories.
""")

df = st.session_state.df

# Stack for user actions
if 'actions_stack' not in st.session_state:
    st.session_state['actions_stack'] = []

# Outliers Section
with st.expander("Outliers Removal", expanded=False):
    st.markdown("""
    ### What is Outlier Removal?
    Outliers are data points that differ significantly from other observations in the dataset.
    Removing or handling outliers can:
    - Enhance visualization and interpretation of data.
    - Improve the accuracy of machine learning models.
    - Prevent bias in statistical analyses.

    Use this section to define and apply outlier removal actions.
    """)

    # Columns to choose from

    # User input for outlier removal
    with st.container():
        st.markdown("#### Create New Outlier Removal Action")
        st.write("Define the parameters for outlier removal and apply the action.")
        column = st.selectbox("Select column", NUMERICAL_COLUMNS, key="outlier_column")
        method = st.selectbox("Select method", ["top", "bottom", "both"], key="outlier_method")
        threshold = st.slider("Threshold (in %)", min_value=0.5, max_value=25.0, value=5.0, step=0.25,
                              key="outlier_threshold")

        if st.button("Apply Action", key="apply_outlier_action"):
            action = {
                "column": column,
                "method": method,
                "threshold": threshold
            }
            st.session_state['actions_stack'].append(action)
            df = remove_outliers(df, column, method, threshold)
            st.session_state.df = df

# Label Encoding Section
with st.expander("Label Encoding", expanded=False):
    st.markdown("""
    ### What is Label Encoding?
    Label Encoding is the process of converting categorical variables into numerical values. 
    It is useful for preparing data for machine learning models that require numerical inputs.

    Use this section to select categorical columns and apply label encoding.
    """)

    # User input for label encoding
    with st.container():
        st.markdown("#### Create New Label Encoding Action")
        st.write("Select a categorical column to apply label encoding.")
        column = st.selectbox("Select column", CATEGORICAL_COLUMNS, key="label_encoding_column")

        if st.button("Apply Label Encoding", key="apply_label_encoding_action"):
            encoded_mapping = dict(enumerate(df[column].astype('category').cat.categories))
            df[column] = df[column].astype('category').cat.codes
            action = {
                "column": column,
                "action": "label_encoding",
                "mapping": encoded_mapping
            }
            st.session_state['actions_stack'].append(action)
            st.session_state.df = df

# Scaling Section
with st.expander("Scaling", expanded=False):
    st.markdown("""
    ### What is Scaling?
    Scaling is the process of normalizing or standardizing numerical features.
    It ensures that all features contribute equally to the model and avoids bias caused by differing feature magnitudes.

    Use this section to apply scaling techniques to your dataset.
    """)

    # Column to choose from

    with st.container():
        st.markdown("#### Create New Scaling Action")
        st.write("Select a column to apply scaling.")
        column = st.selectbox("Select column", NUMERICAL_COLUMNS, key="scaling_column")
        scaling_method = st.selectbox("Select scaling method", ["Min-Max Scaling", "Standard Scaling"],
                                      key="scaling_method")

        if st.button("Apply Scaling", key="apply_scaling_action"):
            if scaling_method == "Min-Max Scaling":
                df[column] = (df[column] - df[column].min()) / (df[column].max() - df[column].min())
            elif scaling_method == "Standard Scaling":
                df[column] = (df[column] - df[column].mean()) / df[column].std()

            action = {
                "column": column,
                "action": "scaling",
                "scaling_method": scaling_method
            }
            st.session_state['actions_stack'].append(action)
            st.session_state.df = df

# Removing Unnecessary Columns Section
with st.expander("Removing Unnecessary Columns", expanded=False):
    st.markdown("""
    ### What is Removing Unnecessary Columns?
    This step helps clean your dataset by dropping irrelevant columns or filtering rows based on specific categories.
    This reduces noise and improves the performance of your model.

    Use this section to define and remove unnecessary columns or rows.
    """)

    with st.container():
        st.markdown("#### Create New Column Removal Action")
        st.write("Select columns to remove or filter.")
        column_to_remove = st.selectbox("Select columns to remove", df.columns.tolist(), key="columns_to_remove")

        if st.button("Apply Column Removal", key="apply_column_removal_action"):
            df = df.drop(columns=[column_to_remove])
            action = {
                "column_removed": column_to_remove,
                "action": "column_removal"
            }
            st.session_state['actions_stack'].append(action)
            st.session_state.df = df

# Show action stack
st.sidebar.markdown("### Action Stack")
if st.session_state['actions_stack']:
    for i, action in enumerate(st.session_state['actions_stack']):
        if action.get("action") == "label_encoding":
            with st.sidebar.expander(f"**Action {i + 1}:** Apply label encoding to column `{action['column']}`"):
                st.write(action['mapping'])
        elif action.get("action") == "scaling":
            with st.sidebar.container(border=True):
                st.write(f"**Action {i + 1}:** Applied {action['scaling_method']} to column `{action['column']}`")

        elif action.get("action") == "column_removal":
            with st.sidebar.container(border=True):
                st.write(f"**Action {i + 1}:** Removed column: `{action['column_removed']}`")
        else:
            with st.sidebar.container(border=True):
                st.write(
                    f"**Action {i + 1}:** Remove {action['method']} {action['threshold']}% outliers from column `{action['column']}`"
                )
else:
    st.sidebar.write("No actions defined yet.")
