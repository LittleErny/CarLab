# imports
import streamlit as st
from helpers import initialize_global_session_variables_if_not_yet, download_dataset


# Return the dataset back to the initial state
# def reset_dataset():
#     # Get the dataset from cache
#     st.session_state.df = download_dataset()
#     st.session_state.df2 = download_dataset()


# -------- Start of the page execution --------

st.set_page_config(page_title="CarLab Dataset", page_icon="💾")

# In case this page was the first to be load by the user in the whole application,
# this will initialize them; and do nothing in the opposite case
initialize_global_session_variables_if_not_yet()

# Dataset description
st.title("Auto Sales Dataset Overview")
st.write(
    "If you want to have a precise look at the dataset, place the cursor on the dataset and click the ``Fullscreen`` "
    "button in the upper right corner ->")
st.write(
    "If you want to download the dataset, place the cursor on the dataset and click the ``Download`` button in the upper"
    " right corner ->")

# Display the dataset
st.write(st.session_state.df)

# Reset dataset button (to be implemented in the future versions)
# st.button("🔄 Reset Dataset", on_click=reset_dataset)

st.markdown("""
---

### About the Dataset
This dataset contains **~38K random and cleaned records** of vehicle sales on eBay Germany in 2016. 

[📂 View the Dataset on Kaggle](https://www.kaggle.com/datasets/shaunoilund/auto-sales-ebay-germany-random-50k-cleaned)

---

### Columns in the Dataset
Numerical columns:
- **`price`**: Price of the vehicle (in EUR). The target variable in this research.
- **`registration_year`**: Year the vehicle was first registered.
- **`power_ps`**: Engine power in PS (metric horsepower).
- **`odometer_km`**: Mileage of the vehicle (in kilometers).

Categorical Columns:
- **`vehicleType`**: Type of vehicle (e.g., limousine, coupe).
- **`transmission`**: Transmission type (e.g., manual, automatic).
- **`model`**: Model of the vehicle.
- **`fuel_type`**: Type of fuel used (e.g., petrol, diesel).
- **`brand`**: Vehicle brand (e.g., BMW, Audi).
- **`unrepaired_damage`**: Indicates if the vehicle has unrepaired damages (`yes`, `no`, or `unknown`).
- **`postal_code`**: The postal code where the auto was sold.

Note: Some other columns from the initial dataset were excluded, as they were not related to autos.
""")

st.write("### Data types in the Dataset:")
st.write("Note: ``object`` is actually a string.")
st.write(st.session_state.df2.dtypes)
