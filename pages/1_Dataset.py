# imports
import streamlit as st
from helpers import initialize_session_variables_if_not_yet, download_dataset


# Возможный баг в будущем - кешируя преобразования датафрейма, где мы его берем на вход, кеш-функция может проверить
# только (не)уникальность ссылки на df, но не проверить (не)уникальность его содержимого, что может привести к
# получению неверных данных

# Еще баг - при обновлении страницы сессионные переменные стираются, но @st.cache_data сохраняется.
# Итог: либо делать свой кеш, либо не использовать @st.cache_data с процедурными функциями(второе).


# Return the dataset back to the initial state
def reset_dataset():
    print("Dataset resetting")
    # Get the dataset from cache
    st.session_state.df = download_dataset()


# -------- Start of the page execution --------

# In case this page was the first to be load by the user in the whole application,
# this will initialize them; and do nothing in the opposite case
initialize_session_variables_if_not_yet()

# Dataset description
st.title("📊 Auto Sales Dataset Overview")

# Display the dataset
st.write(st.session_state.df)

# Reset dataset button
st.button("🔄 Reset Dataset", on_click=reset_dataset)

st.markdown("""
---

### About the Dataset
This dataset contains **~38K random and cleaned records** of vehicle sales on eBay Germany in 2016. 

[📂 View the Dataset on Kaggle](https://www.kaggle.com/datasets/shaunoilund/auto-sales-ebay-germany-random-50k-cleaned)

---

### Columns in the Dataset
- **`price`**: Price of the vehicle (in EUR). The target variable in this research.
- **`vehicleType`**: Type of vehicle (e.g., limousine, coupe).
- **`registration_year`**: Year the vehicle was first registered.
- **`transmission`**: Transmission type (e.g., manual, automatic).
- **`power_ps`**: Engine power in PS (metric horsepower).
- **`model`**: Model of the vehicle.
- **`odometer_km`**: Mileage of the vehicle (in kilometers).
- **`fuel_type`**: Type of fuel used (e.g., petrol, diesel).
- **`brand`**: Vehicle brand (e.g., BMW, Audi).
- **`unrepaired_damage`**: Indicates if the vehicle has unrepaired damages (`yes`, `no`, or `unknown`).
- **`postal_code`**: The postal code where the auto was sold.

Note: Some other columns from the initial dataset were excluded, as they were not related to autos.
""")
