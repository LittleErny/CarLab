import pandas as pd
import re
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from kagglehub import dataset_download
from difflib import get_close_matches


# Load dataset from Kaggle
path = dataset_download("shaunoilund/auto-sales-ebay-germany-random-50k-cleaned")
data_path = f"{path}/autos_random_50k_cleaned.csv"
try:
    data = pd.read_csv(data_path)
except FileNotFoundError:
    data = None

# Normalize categorical fields
if data is not None:
    data['vehicle_type'] = data['vehicle_type'].str.lower()
    data['transmission'] = data['transmission'].str.lower()
    data['fuel_type'] = data['fuel_type'].str.lower()
    data['brand'] = data['brand'].str.lower()

# Define unique values for categorical fields
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

def extract_text_from_message_with_correction(message: str, valid_values: List[str]) -> str:
    words = re.findall(r"\w+", message.lower())
    for word in words:
        match = get_close_matches(word, valid_values, n=1, cutoff=0.8)
        if match:
            return match[0]
    return None

def filter_data(filters: Dict[Text, Any]) -> pd.DataFrame:
    if data is None:
        return pd.DataFrame()

    filtered_data = data.copy()

    # Step 1: Filter by price
    if filters.get("price_EUR") is not None:
        try:
            price = float(filters["price_EUR"])
            filtered_data = filtered_data[
                (filtered_data["price_EUR"] >= price * 0.9) & (filtered_data["price_EUR"] <= price * 1.1)
            ]
        except ValueError:
            pass

    # Step 2: Filter by registration year
    if filters.get("registration_year") is not None:
        try:
            year = int(filters["registration_year"])
            filtered_data = filtered_data[filtered_data["registration_year"] >= year]
        except ValueError:
            pass

    # Step 3: Filter by power
    if filters.get("power_ps") is not None:
        try:
            power = float(filters["power_ps"])
            filtered_data = filtered_data[
                (filtered_data["power_ps"] >= power * 0.9) & (filtered_data["power_ps"] <= power * 1.1)
            ]
        except ValueError:
            pass

    # Step 4: Filter by odometer
    if filters.get("odometer_km") is not None:
        try:
            odometer = float(filters["odometer_km"])
            filtered_data = filtered_data[
                (filtered_data["odometer_km"] >= odometer * 0.9) & (filtered_data["odometer_km"] <= odometer * 1.1)
            ]
        except ValueError:
            pass

    # Step 5: Filter by categorical fields
    for key in ["vehicle_type", "transmission", "fuel_type", "brand"]:
        if filters.get(key) is not None:
            value = filters[key].lower()
            filtered_data = filtered_data[filtered_data[key].str.lower() == value]

    return filtered_data

from rasa_sdk.events import SlotSet

class ActionProvideRecommendation(Action):

    def name(self) -> Text:
        return "action_provide_recommendation"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict) -> List[Dict[Text, Any]]:
        user_message = tracker.latest_message.get("text", "")

        # Extract and validate slot values with correction for misspellings
        filters = {
            "price_EUR": tracker.get_slot("price_EUR") or extract_text_from_message_with_correction(user_message, [str(i) for i in range(1000, 1000000, 1000)]),
            "registration_year": tracker.get_slot("registration_year"),
            "power_ps": tracker.get_slot("power_ps"),
            "odometer_km": tracker.get_slot("odometer_km"),
            "vehicle_type": tracker.get_slot("vehicle_type") or extract_text_from_message_with_correction(user_message, unique_vehicle_types),
            "transmission": tracker.get_slot("transmission") or extract_text_from_message_with_correction(user_message, unique_transmissions),
            "fuel_type": tracker.get_slot("fuel_type") or extract_text_from_message_with_correction(user_message, unique_fuel_types),
            "brand": tracker.get_slot("brand") or extract_text_from_message_with_correction(user_message, unique_brands),
        }

        events = []
        for slot_name, slot_value in filters.items():
            if slot_value and tracker.get_slot(slot_name) != slot_value:
                events.append(SlotSet(slot_name, slot_value))

        # debug_message = "Current filters based on provided slots:\n"
        # for key, value in filters.items():
        #     debug_message += f"- {key}: {value}\n"
        # dispatcher.utter_message(text=debug_message)

        filtered_data = filter_data(filters)

        if filtered_data.empty:
            dispatcher.utter_message(text="Unfortunately, I couldn't find any cars matching your criteria.")
        else:
            top_cars = (
                filtered_data
                .groupby(["brand", "model"])
                .size()
                .reset_index(name="popularity")
                .sort_values(by="popularity", ascending=False)
                .head(3)
            )

            response = "Here are the top 3 most popular cars based on your criteria:\n"
            for index, row in top_cars.iterrows():
                response += f"- {row['brand']} {row['model']} (popularity: {row['popularity']})\n"

            dispatcher.utter_message(text=response)

        return events