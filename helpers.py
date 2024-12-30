import kagglehub
import streamlit as st
import pandas as pd

# The names of session variables that needed to be initialized
COMMON_SESSION_VARIABLES_NAMES = [
    'df', 'df_mappings', 'df_quantitative', 'hardcore_mode',    # common variables
    'p2_items', 'p2_chart_counter', 'p2_editing_mode'                             # variables for page 2
]

KAGGLE_DATASET_PATH = "shaunoilund/auto-sales-ebay-germany-random-50k-cleaned"
IRRELEVANT_COLUMNS = ['ab_test', 'date_crawled', 'last_seen', 'ad_created', 'car_name', 'registration_month',
                      'Unnamed: 0']
CATEGORICAL_COLUMNS = ['vehicle_type', 'transmission', 'model', 'fuel_type', 'brand', 'unrepaired_damage']
NON_NUMERICAL_COLUMNS = CATEGORICAL_COLUMNS + ['postal_code']

# All the columns minus non-numerical
NUMERICAL_COLUMNS = ["price_EUR", "registration_year", "power_ps", "odometer_km"]


# Downloads dataset from Kaggle
@st.cache_data
def download_dataset():
    # Download the dataset
    print("dataset downloading")
    path = kagglehub.dataset_download(KAGGLE_DATASET_PATH)
    df = pd.read_csv(f"{path}/autos_random_50k_cleaned.csv")

    # Drop irrelevant columns
    df = df.drop(columns=IRRELEVANT_COLUMNS)

    return df


# Makes the postal code column kinda categorical - the 1st digit represents the region in Germany
# Updates the initial df, no return or variable assignment required
def update_postal_codes():
    # From postal codes, drop everything except the region
    # If the postal code is not German, using category "other" instead
    print("Updating postal codes")
    st.session_state.df['postal_code'] = st.session_state.df['postal_code'].astype(str).apply(
        lambda x: int(x[0]) if len(x) == 5 else 10)


# Function to map categorical columns to numerical values
def map_column(df, column_name):
    mapping = {i: idx for idx, i in enumerate(df[column_name].unique())}
    df[column_name] = df[column_name].map(mapping)
    return mapping


def create_quantitative_dataset(df):
    # Exclude these columns, leaving only quantitative features
    df_quantitative = df.drop(columns=NON_NUMERICAL_COLUMNS)

    return df_quantitative


def initialize_global_session_variables_if_not_yet():
    # if any of session variables is not initialized, do it
    if any(map(lambda x: x not in st.session_state, COMMON_SESSION_VARIABLES_NAMES)):
        # print(list(filter(lambda x: x not in st.session_state, COMMON_SESSION_VARIABLES_NAMES)))
        # print("Initializing the session variables")
        # Just empty in the very beginning; should be downloaded in the "1_Dataset.py" page
        st.session_state.df = download_dataset()
        st.session_state.df_quantitative = None

        # st.session_state.df_quantitative = pd.DataFrame()
        st.session_state.df_mappings = {}

        st.session_state.hardcore_mode = False

        st.session_state.p2_items = {}     # key - id of the item; value - the item
        st.session_state.p2_chart_counter = 0
        st.session_state.p2_editing_mode = False


