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
    for _ in range(num_rows):
        row = {
            "price_EUR": random.randint(*price_range),
            "vehicle_type": fake.random_element(["cabrio", "kleinwagen", "suv", "kombi", "limousine"]),
            "registration_year": random.randint(1990, 2022),
            "transmission": fake.random_element(["manuell", "automatik"]),
            "power_ps": random.randint(50, 400),
            "model": fake.random_element(["astra", "andere", "xc_reihe", "mondeo", "a4", "3er", "passat"]),
            "odometer_km": random.randint(*odometer_range),
            "fuel_type": fake.random_element(["Unknown", "benzin", "diesel"]),
            "brand": fake.random_element(["opel", "fiat", "volvo", "ford", "audi", "bmw", "sonstig", "volkswagen"]),
            "unrepaired_damage": fake.random_element(["ja", "nein", "Unknown"]),
            "postal_code": random.randint(10000, 99999),
        }
        data.append(row)
    return pd.DataFrame(data)


def generate_faker_data(num_rows):
    data = []
    for _ in range(num_rows):
        row = {
            "price_EUR": random.randint(500, 50000),
            "vehicle_type": fake.random_element(["cabrio", "kleinwagen", "suv", "kombi", "limousine"]),
            "registration_year": random.randint(1990, 2022),
            "transmission": fake.random_element(["manuell", "automatik"]),
            "power_ps": random.randint(50, 400),
            "model": fake.word(),
            "odometer_km": random.randint(0, 300000),
            "fuel_type": fake.random_element(["Unknown", "benzin", "diesel"]),
            "brand": fake.company(),
            "unrepaired_damage": fake.random_element(["ja", "nein", "Unknown"]),
            "postal_code": random.randint(10000, 99999),
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
st.sidebar.header("Generation Settings")

if "p4_method_selection" not in st.session_state:
    st.session_state["p4_method_selection"] = "Random"

# Select generation method
st.sidebar.selectbox("Data Generation Method",
                     ["Random", "Faker", "Proportional", "No Generation"],
                     key="p4_method_selection",
                     index=["Random", "Faker", "Proportional", "No Generation"].index(
                         st.session_state["p4_method_selection"])
                     )

method = st.session_state["p4_method_selection"]

if "p4_number_of_new_rows" not in st.session_state:
    st.session_state["p4_number_of_new_rows"] = 100,

# Select the number of rows
st.sidebar.slider("Number of Rows",
                  min_value=10,
                  max_value=1000,
                  step=10,
                  key="p4_number_of_new_rows",
                  )

num_rows = st.session_state["p4_number_of_new_rows"]

# # Additional settings for Random and Proportional
# if "p4_odometer_range" not in st.session_state:
#     st.session_state["p4_odometer_range"] = (50000, 200000)


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
    elif method == "Faker":
        generated_data = generate_faker_data(num_rows)
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
        generated_data = pd.DataFrame()

    st.session_state.df2 = pd.concat([st.session_state.df2, generated_data], ignore_index=True)
    st.success("Synthetic data successfully added!")

# Display data
st.subheader("Existing Data")
st.dataframe(st.session_state.df2)

# Option to download data
if not st.session_state.df2.empty:
    csv = st.session_state.df2.to_csv(index=False).encode('utf-8')
    st.download_button("Download Data as CSV", data=csv, file_name="synthetic_data.csv", mime="text/csv")
