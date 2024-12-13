# imports
import kagglehub
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from helpers import initialize_session_variables_if_not_yet, download_dataset, update_postal_codes

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

st.write(st.session_state.df)

st.button("Reset dataset", on_click=reset_dataset)
st.button("Update postal codes", on_click=update_postal_codes)
