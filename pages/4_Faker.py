import streamlit as st
from helpers import initialize_global_session_variables_if_not_yet, CATEGORICAL_COLUMNS, NUMERICAL_COLUMNS
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

import random
from faker import Faker

st.set_page_config(page_title="CarLab Faker", page_icon="🎭")

# Initialize Faker
fake = Faker()
initialize_global_session_variables_if_not_yet()


# Functions for data generation
def generate_random_data(num_rows, odometer_range, price_range):
    data = []
    vehicle_type_options = set(st.session_state.df2["vehicle_type"])
    transmission_options = set(st.session_state.df2["transmission"])
    model_options = set(st.session_state.df2["model"])
    fuel_type_options = set(st.session_state.df2["fuel_type"])
    brand_options = set(st.session_state.df2["brand"])
    unrepaired_damage_options = set(st.session_state.df2["unrepaired_damage"])
    postal_code_options = set(st.session_state.df2["postal_code"])
    for _ in range(num_rows):
        row = {
            "price_EUR": random.randint(*price_range),
            "vehicle_type": fake.random_element(vehicle_type_options),
            "registration_year": random.randint(1990, 2022),
            "transmission": fake.random_element(transmission_options),
            "power_ps": random.randint(50, 400),
            "model": fake.random_element(model_options),
            "odometer_km": random.randint(*odometer_range),
            "fuel_type": fake.random_element(fuel_type_options),
            "brand": fake.random_element(brand_options),
            "unrepaired_damage": fake.random_element(unrepaired_damage_options),
            "postal_code": fake.random_element(postal_code_options),
        }
        data.append(row)
    return pd.DataFrame(data)


def generate_proportional_data(num_rows, df):
    # Gather statistics from the existing dataset
    vehicle_type_probs = df['vehicle_type'].value_counts(normalize=True).to_dict()
    transmission_probs = df['transmission'].value_counts(normalize=True).to_dict()
    fuel_type_probs = df['fuel_type'].value_counts(normalize=True).to_dict()
    brand_probs = df['brand'].value_counts(normalize=True).to_dict()

    price_mean, price_std = df['price_EUR'].mean(), df['price_EUR'].std()
    odometer_mean, odometer_std = df['odometer_km'].mean(), df['odometer_km'].std()
    registration_year_min, registration_year_max = df['registration_year'].min(), df['registration_year'].max()
    power_ps_min, power_ps_max = df['power_ps'].min(), df['power_ps'].max()

    data = []
    for _ in range(num_rows):
        row = {
            "price_EUR": max(500, int(random.gauss(price_mean, price_std))),
            "vehicle_type": random.choices(list(vehicle_type_probs.keys()), weights=vehicle_type_probs.values(), k=1)[
                0],
            "registration_year": random.randint(registration_year_min, registration_year_max),
            "transmission": random.choices(list(transmission_probs.keys()), weights=transmission_probs.values(), k=1)[
                0],
            "power_ps": random.randint(power_ps_min, power_ps_max),
            "model": fake.random_element(df['model'].unique()),
            "odometer_km": max(0, int(random.gauss(odometer_mean, odometer_std))),
            "fuel_type": random.choices(list(fuel_type_probs.keys()), weights=fuel_type_probs.values(), k=1)[0],
            "brand": random.choices(list(brand_probs.keys()), weights=brand_probs.values(), k=1)[0],
            "unrepaired_damage": fake.random_element(["ja", "nein", "Unknown"]),
            "postal_code": random.randint(10000, 99999),
        }
        data.append(row)
    return pd.DataFrame(data)


# Streamlit Interface
st.title("Synthetic Data Generator for Cars")

with st.expander("Instruction & Method Description", expanded=False):
    st.markdown(
        """
### Brief Theory on Data Generation Methods

In data science, synthetic data generation is often used to augment datasets or create examples for testing. Two common 
approaches are:

#### 1. **Random Data Generation**
   - **Description:** This method generates data by assigning random values to each feature within specified ranges or 
   sets of possible values. 
   - **Advantages:**
     - Simple and quick to implement.
     - Useful for testing systems where data diversity is needed without regard for realism.
   - **Limitations:**  
     - Does not reflect real-world distributions.
     - Ignores patterns or relationships between features, leading to unrealistic data.

#### 2. **Proportional Data Generation**
   - **Description:** This method creates synthetic data based on the statistical properties of an existing dataset, 
   such as distributions of categorical variables and the mean, standard deviation, or range of numerical variables.
   - **Advantages:**
     - Produces more realistic data by replicating the proportions and variability in the original dataset.
     - Better suited for scenarios requiring realism in the generated data.
   - **Limitations:**  
     - Does not capture correlations between features (e.g., higher power corresponding to higher price).
     - Can introduce biases if the original dataset contains imbalances or errors.

These methods can be useful for specific tasks but must be applied carefully to avoid compromising the quality of 
analysis or model training.

### How do I proceed?

If you want to generate fake data, please refer to the sidebar from the left. First, select the method, and 
suggested parameters, if needed. After pressing `Generate Data` button, new data will be automatically generated and added 
to the end of existing dataset.

Note: If you want to visualize the dataset after creating augmented data, please return back to the page 3, press the \
`🔄 Update Charts` button, and move to the bottom of the page. There you will be able to make the visualisations as
on the page 2.
        """
    )

if not st.session_state.hardcore_mode:
    with st.expander("The Authors' approach", expanded=False):
        st.markdown(
            """
            After implementing and testing both approaches, none of them was used in the final version of the code. 
            Both methods introduced additional noise and inconsistencies that negatively impacted model training 
            results. Since the original dataset already contains ~37,000 rows of real data, augmenting it with synthetic
             data was unnecessary and counterproductive. The real data provided sufficient diversity and relevance for 
             accurate and robust training.
            """
        )
st.sidebar.header("Generation Settings")

if "p4_method_selection" not in st.session_state:
    st.session_state["p4_method_selection"] = "Random"

# Select generation method
st.sidebar.selectbox("Data Generation Method",
                     ["Random", "Proportional"],
                     key="p4_method_selection",
                     index=["Random", "Proportional"].index(
                         st.session_state["p4_method_selection"])
                     )

method = st.session_state["p4_method_selection"]

if "p4_number_of_new_rows" not in st.session_state:
    st.session_state["p4_number_of_new_rows"] = 25,

# Select the number of rows
st.sidebar.slider("How much procent of Fake data should be added",
                  min_value=1,
                  max_value=100,
                  step=1,
                  key="p4_number_of_new_rows",
                  )

num_rows = len(st.session_state.df2) * st.session_state["p4_number_of_new_rows"][0] // 100

if method == "Random":
    # We need those sliders only for this method
    odometer_range = st.sidebar.slider("Odometer Range (km)",
                                       min_value=0,
                                       max_value=300000,
                                       value=(50000, 200000),
                                       step=1000,
                                       key="p4_odometer_range"
                                       )

    if "p4_price_range" not in st.session_state:
        st.session_state["p4_price_range"] = (1000, 20000)

    price_range = st.sidebar.slider("Price Range (€)",
                                    min_value=500,
                                    max_value=50000,
                                    value=st.session_state["p4_price_range"],
                                    step=500)

# Button to generate data
if st.sidebar.button("Generate Data"):
    if method == "Random":
        generated_data = generate_random_data(num_rows, odometer_range, price_range)
    elif method == "Proportional":
        if not st.session_state.df2.empty:
            generated_data = generate_proportional_data(num_rows, st.session_state.df2)
        else:
            st.error("Proportional generation requires existing data.")
            generated_data = pd.DataFrame()
    elif method == "No Generation":
        generated_data = pd.DataFrame()
        st.info("Generation is disabled.")
    else:
        raise ValueError("Unknown method of generating Fake Data.")

    st.session_state.df2 = pd.concat([st.session_state.df2, generated_data], ignore_index=True)
    st.session_state.fake_df = pd.concat([st.session_state.fake_df, generated_data], ignore_index=True)
    # len(st.session_state.fake_df):len(st.session_state.fake_df) + len(generated_data) - 1] = generated_data.iloc[:]

    st.success("Synthetic data successfully added!")

# Display data
st.subheader("Current State of Dataset")
st.dataframe(st.session_state.df2)

st.subheader("Fake data")
st.dataframe(st.session_state.fake_df)
