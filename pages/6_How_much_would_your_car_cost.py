import os

import pandas as pd
import streamlit as st
from pandas import DataFrame

from DashboardManager.DashboardManagerEnums import PreprocessingTypes
from DashboardManager.Model.Model import MLModel
from helpers import initialize_global_session_variables_if_not_yet, CATEGORICAL_COLUMNS, NUMERICAL_COLUMNS, \
    reverse_preprocessing, do_preprocessing

st.set_page_config(page_title="CarLab How Much Would Your Car Cost", page_icon="🧪")
initialize_global_session_variables_if_not_yet()
PAGE_NUMBER = os.path.basename(__file__).split("_")[0]  # The number in front of the filename

df: DataFrame = st.session_state.df2
init_df = st.session_state.df
ml_model = MLModel(df)

st.write("## Prediction Tool")
st.write("Here you can estimate the cost of the car of your dreams")
st.write("- - -")

if ml_model.model is None:
    st.warning("Please train the model first on the previous pages.")
else:
    x_column_names = ml_model.x_column_names

    st.write("")
    x_data = []
    col1, col2 = st.columns([1, 1])
    col1.write("##### **Please input here the data about your car**", )
    col2.write("##### **The values as they will be transferred to the model**")

    col1, col2 = st.columns([1, 1])
    col1.write("The data here should be natural (initial), without any preprocessing actions applied.")
    col2.write("We apply all the preprocessing actions on the data from the left. The preprocessing actions are taken "
               "from the *Preprocrssings* page.")

    # Input for vehicle_type
    with st.container(border=False):
        col1, col2 = st.columns([1, 1])
        # Get the input value from the user
        col1.selectbox("Please select the type of desired car",
                       sorted(list(set(init_df["vehicle_type"]))),
                       index=0,
                       key="p6_vehicle_type")

        vehicle_type = st.session_state["p6_vehicle_type"]

        new_value = do_preprocessing("vehicle_type", vehicle_type)
        x_data.append(new_value)

        col2.write("")  # write nothing to make a space
        col2.write("")  # write nothing to make a space
        col2.markdown(f"Processed value ``{new_value}``")

    # Input for registration year
    with st.container(border=False):
        col1, col2 = st.columns([1, 1])

        # Get the input value from the user
        col1.number_input("Please select the desired registration year",
                          min_value=min(init_df["registration_year"]),
                          max_value=max(init_df["registration_year"]),
                          step=1,
                          value=2010,  # default value
                          key="p6_registration_year")

        registration_year = st.session_state["p6_registration_year"]

        new_value = do_preprocessing("registration_year", registration_year)
        x_data.append(new_value)

        col2.write("")  # write nothing to make a space
        col2.write("")  # write nothing to make a space
        col2.markdown(f"Processed value ``{new_value}``")

    # Input for transmission
    with st.container():
        col1, col2 = st.columns([1, 1])
        col1.selectbox(
            "Please select the transmission type",
            sorted(list(set(init_df["transmission"]))),
            index=0,
            key="p6_transmission",
        )
        transmission = st.session_state["p6_transmission"]
        new_value = do_preprocessing("transmission", transmission)
        x_data.append(new_value)
        col2.write("")  # write nothing to make a space
        col2.write("")  # write nothing to make a space
        col2.markdown(f"Processed value ``{new_value}``")

    # Input for power_ps
    with st.container():
        col1, col2 = st.columns([1, 1])
        col1.number_input(
            "Please input the engine power (PS)",
            min_value=min(init_df["power_ps"]),
            max_value=max(init_df["power_ps"]),
            step=1,
            value=100,
            key="p6_power_ps",
            help="Make sure better not to put in too big number that was excluded with outliers on previous pages."
        )
        power_ps = st.session_state["p6_power_ps"]
        new_value = do_preprocessing("power_ps", power_ps)
        x_data.append(new_value)
        col2.write("")  # write nothing to make a space
        col2.write("")  # write nothing to make a space
        col2.markdown(f"Processed value ``{new_value}``")

    # Input for model
    with st.container():
        col1, col2 = st.columns([1, 1])
        col1.selectbox(
            "Please select the vehicle model",
            sorted(list(set(init_df["model"]))),
            index=0,
            key="p6_model",
        )
        model = st.session_state["p6_model"]
        new_value = do_preprocessing("model", model)
        x_data.append(new_value)
        col2.write("")  # write nothing to make a space
        col2.write("")  # write nothing to make a space
        col2.markdown(f"Processed value ``{new_value}``")

    # Input for odometer_km
    with st.container():
        col1, col2 = st.columns([1, 1])
        col1.number_input(
            "Please input the mileage (km)",
            min_value=min(init_df["odometer_km"]),
            max_value=max(init_df["odometer_km"]),
            step=1000,
            value=50000,
            key="p6_odometer_km",
        )
        odometer_km = st.session_state["p6_odometer_km"]
        new_value = do_preprocessing("odometer_km", odometer_km)
        x_data.append(new_value)
        col2.write("")  # write nothing to make a space
        col2.write("")  # write nothing to make a space
        col2.markdown(f"Processed value ``{new_value}``")

    # Input for fuel_type
    with st.container():
        col1, col2 = st.columns([1, 1])
        col1.selectbox(
            "Please select the fuel type",
            sorted(list(set(init_df["fuel_type"]))),
            index=0,
            key="p6_fuel_type",
        )
        fuel_type = st.session_state["p6_fuel_type"]
        new_value = do_preprocessing("fuel_type", fuel_type)
        x_data.append(new_value)
        col2.write("")  # write nothing to make a space
        col2.write("")  # write nothing to make a space
        col2.markdown(f"Processed value ``{new_value}``")

    # Input for brand
    with st.container():
        col1, col2 = st.columns([1, 1])
        col1.selectbox(
            "Please select the vehicle brand",
            sorted(list(set(init_df["brand"]))),
            index=0,
            key="p6_brand",
        )
        brand = st.session_state["p6_brand"]
        new_value = do_preprocessing("brand", brand)
        x_data.append(new_value)
        col2.write("")  # write nothing to make a space
        col2.write("")  # write nothing to make a space
        col2.markdown(f"Processed value ``{new_value}``")

    # Input for unrepaired_damage
    with st.container():
        col1, col2 = st.columns([1, 1])
        col1.selectbox(
            "Please indicate if the vehicle has unrepaired damage",
            sorted(list(set(init_df["unrepaired_damage"]))),
            index=2,
            key="p6_unrepaired_damage",
        )
        unrepaired_damage = st.session_state["p6_unrepaired_damage"]
        new_value = do_preprocessing("unrepaired_damage", unrepaired_damage)
        x_data.append(new_value)
        col2.write("")  # write nothing to make a space
        col2.write("")  # write nothing to make a space
        col2.markdown(f"Processed value ``{new_value}``")

    # Input for postal_code
    with st.container():
        col1, col2 = st.columns([1, 1])
        col1.number_input(
            "Please input the postal code",
            min_value=min(init_df["postal_code"]),
            max_value=max(init_df["postal_code"]),
            step=1,
            value=10000,
            key="p6_postal_code",
        )
        postal_code = st.session_state["p6_postal_code"]
        new_value = do_preprocessing("postal_code", postal_code)
        x_data.append(new_value)
        col2.write("")  # write nothing to make a space
        col2.write("")  # write nothing to make a space
        col2.markdown(f"Processed value ``{new_value}``")

    input_data = pd.DataFrame([x_data], columns=ml_model.x_column_names)
    st.write("*X_data* preview:")
    st.write(input_data)

    # Making the prediction
    if st.button("Predict"):

        prediction = ml_model.model.predict(input_data)[0]
        reversed_prediction = reverse_preprocessing("price_EUR", prediction)
        st.write(f"Approximated Auto Cost: ``{int(reversed_prediction)}`` EUR")
