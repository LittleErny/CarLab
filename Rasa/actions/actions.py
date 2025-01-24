import pandas as pd
import re
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from kagglehub import dataset_download

# Load dataset from Kaggle
path = dataset_download("shaunoilund/auto-sales-ebay-germany-random-50k-cleaned")
data_path = f"{path}/autos_random_50k_cleaned.csv"
try:
    data = pd.read_csv(data_path)
except FileNotFoundError:
    data = None

# Unique values for categorical fields
unique_vehicle_types = ["cabrio", "kleinwagen", "suv", "kombi", "limousine", "coupe", "bus", "andere", "unknown"]
unique_transmissions = ["manuell", "automatik", "unknown"]
unique_fuel_types = ["unknown", "benzin", "diesel", "lpg", "andere", "cng", "hybrid", "elektro"]
unique_brands = [
    "opel", "fiat", "volvo", "ford", "audi", "bmw", "sonstige_autos", "volkswagen", "hyundai",
    "mercedes_benz", "renault", "peugeot", "skoda", "toyota", "citroen", "dacia", "mazda", "mitsubishi",
    "seat", "smart", "alfa_romeo", "mini", "chrysler", "subaru", "nissan", "jeep", "honda", "porsche", "kia",
    "chevrolet", "trabant", "lancia", "saab", "daihatsu", "suzuki", "land_rover", "jaguar", "daewoo", "rover",
    "lada"
]

def extract_text_from_message(message: str, valid_values: List[str]) -> str:
    """
    Extracts the first matching value from the list of valid values in the message.
    """
    for value in valid_values:
        if value.lower() in message.lower():
            return value
    return None

def filter_data(filters: Dict[Text, Any]) -> pd.DataFrame:
    """
    Filters the dataset based on the provided filters.
    """
    if data is None:
        return pd.DataFrame()

    filtered_data = data.copy()
    for key, value in filters.items():
        if value is not None:
            # Handle numeric filters
            if key in ["price_EUR", "registration_year", "power_ps", "odometer_km"]:
                try:
                    numeric_value = float(value)  # Convert to float
                    filtered_data = filtered_data[
                        (filtered_data[key] >= numeric_value * 0.9) & (filtered_data[key] <= numeric_value * 1.1)
                    ]
                except ValueError:
                    # Skip this filter if conversion fails
                    continue
            # Handle categorical filters
            elif isinstance(value, str):
                filtered_data = filtered_data[filtered_data[key].str.lower() == value.lower()]
    return filtered_data


class ActionProvideRecommendation(Action):

    def name(self) -> Text:
        return "action_provide_recommendation"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict) -> List[Dict[Text, Any]]:
        # Extract user message
        user_message = tracker.latest_message.get("text", "")

        # Extract and validate slot values
        filters = {
            "price_EUR": tracker.get_slot("price_EUR"),
            "registration_year": tracker.get_slot("registration_year"),
            "power_ps": tracker.get_slot("power_ps"),
            "odometer_km": tracker.get_slot("odometer_km"),
            "vehicle_type": extract_text_from_message(user_message, unique_vehicle_types),
            "transmission": extract_text_from_message(user_message, unique_transmissions),
            "fuel_type": extract_text_from_message(user_message, unique_fuel_types),
            "brand": extract_text_from_message(user_message, unique_brands),
        }

        # Filter the data
        filtered_data = filter_data(filters)

        if filtered_data.empty:
            dispatcher.utter_message(text="Unfortunately, I couldn't find any cars matching your criteria.")
        else:
            # Select the top 3 most popular cars
            top_cars = (
                filtered_data
                .groupby(["brand", "model"])
                .size()
                .reset_index(name="popularity")
                .sort_values(by="popularity", ascending=False)
                .head(3)
            )

            # Create the response
            response = "Here are the top 3 most popular cars based on your criteria:\n"
            for index, row in top_cars.iterrows():
                response += f"- {row['brand']} {row['model']} (popularity: {row['popularity']})\n"

            dispatcher.utter_message(text=response)

        return []
