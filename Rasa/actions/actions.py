from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import pandas as pd
import re
import kagglehub

# Download latest version of the dataset
path = kagglehub.dataset_download("shaunoilund/auto-sales-ebay-germany-random-50k-cleaned")
data_path = f"{path}/autos_random_50k_cleaned.csv"
try:
    car_data = pd.read_csv(data_path)
except FileNotFoundError:
    car_data = None

class ActionProvideCarRecommendation(Action):

    def name(self) -> Text:
        return "action_provide_car_recommendation"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        if car_data is None:
            dispatcher.utter_message(text="The car dataset could not be loaded. Please ensure the dataset file is available.")
            return []

        # Extract user data from slots
        budget = tracker.get_slot("budget")
        requirements = tracker.get_slot("requirements")
        fuel_type = tracker.get_slot("fuel_type")
        car_type = tracker.get_slot("car_type")

        # Debug: Log the raw slot values
        dispatcher.utter_message(text=f"DEBUG: Received budget slot value: {budget}")
        dispatcher.utter_message(text=f"DEBUG: Received fuel_type slot value: {fuel_type}")
        dispatcher.utter_message(text=f"DEBUG: Received requirements slot value: {requirements}")

        # Validate and clean budget
        try:
            if not budget:
                raise ValueError("Budget slot is empty or not set.")
            # Extract numbers from the budget slot
            extracted_budget = re.findall(r"[0-9]+(?:\\.[0-9]+)?", str(budget))
            if not extracted_budget:
                raise ValueError("No numeric value found in the budget slot.")
            budget = float(extracted_budget[0])
        except (ValueError, TypeError) as e:
            dispatcher.utter_message(text=f"DEBUG: Budget validation error: {e}")
            dispatcher.utter_message(text=f"Your budget value '{budget}' is not valid. Please provide a numeric value.")
            return []

        # Debug: Log the cleaned budget
        dispatcher.utter_message(text=f"DEBUG: Cleaned budget value: {budget}")

        # Normalize inputs
        if fuel_type:
            fuel_type = fuel_type.lower().strip()
            if fuel_type not in ['unknown', 'benzin', 'diesel', 'lpg', 'andere', 'cng', 'hybrid', 'elektro']:
                dispatcher.utter_message(text=f"The fuel type '{fuel_type}' is not recognized. Please choose from: benzin, diesel, lpg, cng, hybrid, elektro, or andere.")
                return []
        if requirements:
            requirements = requirements.lower().strip()
            if requirements not in ['cabrio', 'kleinwagen', 'suv', 'kombi', 'limousine', 'coupe', 'bus', 'andere']:
                dispatcher.utter_message(text=f"The vehicle type '{requirements}' is not recognized. Please choose from: cabrio, kleinwagen, suv, kombi, limousine, coupe, bus, or andere.")
                return []
        if car_type:
            car_type = car_type.lower().strip()

        # Filter dataset
        filtered_cars = car_data[(car_data["price_EUR"] <= budget)]
        dispatcher.utter_message(text=f"DEBUG: Cars after budget filter: {len(filtered_cars)}")

        if requirements:
            filtered_cars = filtered_cars[
                filtered_cars["vehicle_type"].str.lower().str.contains(requirements, na=False)
            ]
            dispatcher.utter_message(text=f"DEBUG: Cars after requirements filter: {len(filtered_cars)}")

        if fuel_type and len(filtered_cars) > 0:
            filtered_cars = filtered_cars[
                filtered_cars["fuel_type"].str.lower().str.contains(fuel_type, na=False)
            ]
            dispatcher.utter_message(text=f"DEBUG: Cars after fuel type filter: {len(filtered_cars)}")

        if car_type and len(filtered_cars) > 0:
            filtered_cars = filtered_cars[
                filtered_cars["vehicle_type"].str.lower().str.contains(car_type, na=False)
            ]
            dispatcher.utter_message(text=f"DEBUG: Cars after car type filter: {len(filtered_cars)}")

        # Handle no matches
        if filtered_cars.empty:
            dispatcher.utter_message(
                text="I couldn't find any exact matches. Let me show you some popular options within your budget."
            )
            filtered_cars = car_data[(car_data["price_EUR"] <= budget)].nsmallest(3, "price_EUR")

        # Generate response
        response = "Here are some cars that match your requirements:\n"
        for _, car in filtered_cars.iterrows():
            response += (
                f"- {car['brand']} {car['model']} ({car['registration_year']}): {car['price_EUR']} EUR, {car['fuel_type']}\n"
            )
        dispatcher.utter_message(text=response)

        return []