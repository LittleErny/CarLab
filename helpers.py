import kagglehub
import streamlit as st
import pandas as pd

# from DashboardManager.DashboardManager import DashboardManager
from DashboardManager.DashboardManagerEnums import PreprocessingTypes, DashboardItemTypes

# The names of session variables that needed to be initialized
COMMON_SESSION_VARIABLES_NAMES = [
    'df', 'df_mappings', 'df_quantitative', 'hardcore_mode', 'chart_hashes',  # common variables
    'categorical_columns', 'numerical_columns'  # dynamic lists of columns of different types
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
        st.session_state.df = download_dataset()

        # The second is for page 3 and later - can be edited in preprocessing function
        st.session_state.df2 = download_dataset()

        st.session_state.df_quantitative = None

        # st.session_state.df_quantitative = pd.DataFrame()
        st.session_state.df_mappings = {}

        st.session_state.hardcore_mode = False
        st.session_state.chart_hashes = {}

        # dynamic lists of columns of different types(if we delete or add new columns)
        st.session_state.categorical_columns = CATEGORICAL_COLUMNS.copy()
        st.session_state.numerical_columns = NUMERICAL_COLUMNS.copy()

        # preprocessing history for being able to do the same preprocessing on the 6th page (counting from 0)
        st.session_state.preprocessing_history = []

        st.session_state.page_2_was_ever_rendered = False

        st.success('Dataset was successfully downloaded from Kaggle!')
        print("-------------------------------------")
        print("The App is run.")
        print("-------------------------------------")

def execute_preprocessing_action(action_type, manager, df, column=None, method=None, mapping=None, threshold=None, scaling_method=None):
    """
    Executes a preprocessing action based on the given parameters.

    :param action_type: Type of preprocessing action to perform (e.g., OUTLIER_REMOVAL, LABEL_ENCODING, SCALING).
    :param column: Column on which the action is performed.
    :param method: Method for preprocessing (e.g., 'top', 'bottom', 'both').
    :param threshold: Threshold value for preprocessing.
    :param scaling_method: Scaling method (e.g., 'Min-Max Scaling', 'Standard Scaling').
    """



    if action_type == PreprocessingTypes.OUTLIER_REMOVAL:
        if not column or not method or threshold is None:
            raise ValueError("Missing parameters for OUTLIER_REMOVAL.")

        def remove_outliers(column, method, threshold):
            if method == 'top':
                df.drop(df[df[column] > df[column].quantile(1 - threshold / 100)].index, inplace=True)
            elif method == 'bottom':
                df.drop(df[df[column] < df[column].quantile(threshold / 100)].index, inplace=True)
            elif method == 'both':
                lower_bound = df[column].quantile(threshold / 100)
                upper_bound = df[column].quantile(1 - threshold / 100)
                df.drop(df[(df[column] < lower_bound) | (df[column] > upper_bound)].index, inplace=True)
            else:
                raise ValueError("Unknown method for outlier removal.")

        remove_outliers(column, method, threshold)

        action = {
            "column": column,
            "method": method,
            "threshold": threshold
        }
        manager.create_item(
            item_pos=len(manager.items),
            item_type=DashboardItemTypes.PREPROCESSING_BOX,
            action=action,
            preproc_type=PreprocessingTypes.OUTLIER_REMOVAL
        )

        st.session_state.preprocessing_history.append(
            {
                "preproc_type": action_type,
                "column": column,
                "method": method,
                "threshold": threshold
            }
        )

    elif action_type == PreprocessingTypes.LABEL_ENCODING:
        if not column:
            raise ValueError("Missing column for LABEL_ENCODING.")

        encoded_mapping = mapping if mapping is not None \
            else dict(enumerate(df[column].astype('category').cat.categories))
        st.session_state.df2[column] = st.session_state.df2[column].astype('category').cat.codes

        action = {
            "column": column,
            "action": "label_encoding",
            "mapping": encoded_mapping
        }
        manager.create_item(
            item_pos=len(manager.items),
            item_type=DashboardItemTypes.PREPROCESSING_BOX,
            action=action,
            preproc_type=PreprocessingTypes.LABEL_ENCODING
        )

        st.session_state.preprocessing_history.append(
            {
                "preproc_type": action_type,
                "column": column,
                "method": method,
                "mapping": encoded_mapping
            }
        )

    elif action_type == PreprocessingTypes.SCALING:
        if not column or not scaling_method:
            raise ValueError("Missing parameters for SCALING.")

        if scaling_method == "Min-Max Scaling":
            df[column] = ((df[column] - df[column].min()) /
                          (df[column].max() - df[column].min()))

            st.session_state.preprocessing_history.append(
                {
                    "preproc_type": action_type,
                    "column": column,
                    "method": method,
                    "scaling_method": scaling_method,
                    "min": df[column].min(),
                    "max": df[column].max()
                }
            )

        elif scaling_method == "Standard Scaling":
            df[column] = (df[column] - df[column].mean()) / df[column].std()

            st.session_state.preprocessing_history.append(
                {
                    "preproc_type": action_type,
                    "column": column,
                    "method": method,
                    "scaling_method": scaling_method,
                    "mean": df[column].mean(),
                    "std": df[column].std()
                }
            )

        else:
            raise ValueError(f"Unknown scaling_method: {scaling_method}")

        action = {
            "column": column,
            "action": "scaling",
            "scaling_method": scaling_method
        }
        manager.create_item(
            item_pos=len(manager.items),
            item_type=DashboardItemTypes.PREPROCESSING_BOX,
            action=action,
            preproc_type=PreprocessingTypes.SCALING
        )


    else:
        raise ValueError(f"Unknown action_type: {action_type}")
