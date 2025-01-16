# Import libraries
import weakref

import streamlit as st
import json

# Import from my own files
from DashboardManager.DashboardItem import DashboardItem
from DashboardManager.ChartItem import ChartItem
from DashboardManager.MDBoxItem import MDBoxItem
from DashboardManager.DashboardManagerEnums import DashboardItemTypes
from DashboardManager.PreprocessingItem import PreprocessingItem


class DashboardManager:
    """Class for controlling the Dashboard elements(blocks).
    This should be the only class, that the page interacts with"""

    def __new__(cls, page_number):
        # The instance of DashboardManager for every page is going to be created over and over again,
        # However it is supposed that the Manager is Singleton for every particular page. So we interrupt
        # The process of creating new instance and return the old one from the st.session_state, if we have one already.
        key = f"p{page_number}_DashboardManager"

        if key not in st.session_state:
            instance = super().__new__(cls)
            instance.amount_of_items = 0
            instance.items = {}  # The items(blocks) are stored in dict
            st.session_state[key] = instance
            instance.page_number = page_number
        return st.session_state[key]

    def __init__(self, page_number):
        pass  # Do nothing here as everything is already done in __new__()

    def is_empty(self):
        return len(self.items) == 0

    def create_item(self, item_type: DashboardItemTypes, item_pos: int, *args, **kwargs):
        """
        Factory method for creating items.

        :param item_type: The item type (e.g. DashboardItemTypes.CHART).
        :item_pos: The position of the item, after which new item will be placed.
        :param kwargs: Parameters for the constructor.
        :return: The created item instance.
        """

        manager_items = [value for key, value in sorted(self.items.items(), key=lambda x: x[0])]

        new_item: DashboardItem

        if item_type == DashboardItemTypes.CHART:
            print("Manager:", weakref.ref(kwargs["df"]))

            new_item = ChartItem(id=self.amount_of_items, *args, **kwargs)
            # self.items[self.amount_of_items] = new_chart_item

        elif item_type == DashboardItemTypes.MD_BOX:

            new_item = MDBoxItem(manager_page_number=self.page_number, **kwargs)
            # self.items[self.amount_of_items] = new_mdbox_item

        elif item_type == DashboardItemTypes.PREPROCESSING_BOX:

            new_item = PreprocessingItem(**kwargs)

        else:
            raise ValueError(f"Unknown item type: {item_type}")

        self.amount_of_items += 1
        manager_items.insert(item_pos + 1, new_item)
        self.items = {i: item for i, item in enumerate(manager_items)}
        return new_item

    def remove_item(self, item_id):
        """Remove item."""
        if item_id in self.items:
            del self.items[item_id]

    def find_next_item_from_above(self, item_id):
        # Suppose there can be situation that there will be spaces in the keys like [0, 1, 3]
        item_keys = sorted(self.items.keys())
        item_pos = item_keys.index(item_id)
        if item_pos == 0:
            return -1  # The given item is already the highest
        return item_keys[item_pos - 1]

    def find_next_item_from_below(self, item_id):
        # Suppose there can be situation that there will be spaces in the keys like [0, 1, 3]
        item_keys = sorted(self.items.keys())
        item_pos = item_keys.index(item_id)
        if item_pos == len(item_keys) - 1:
            return -1  # The given item is already the lowest
        return item_keys[item_pos + 1]

    def move_item_up(self, item_id):
        next_item_id = self.find_next_item_from_above(item_id)
        if next_item_id != -1:
            self.swap_items(item_id, next_item_id)

    def move_item_down(self, item_id):
        next_item_id = next_item_id = self.find_next_item_from_below(item_id)
        if next_item_id != -1:
            self.swap_items(item_id, next_item_id)

    def swap_items(self, item1_id, item2_id):
        """Swap two elements."""
        if item1_id not in self.items or item2_id not in self.items:
            raise ValueError("Both item IDs must exist in the items dictionary")
        self.items[item1_id], self.items[item2_id] = self.items[item2_id], self.items[item1_id]

    def save_to_json(self, filepath: str):
        """
        Saves the current state of the DashboardManager to a JSON file.

        :param filepath: Path to the JSON file.
        """
        items_data = {
            item_id: json.loads(str(item)) for item_id, item in self.items.items()
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(items_data, f, indent=4, ensure_ascii=False)

    def load_from_json(self, on_change_function, df, filepath: str):
        """
        Loads the state of the DashboardManager from a JSON file.

        :param filepath: Path to the JSON file.
        """

        with open(filepath, "r", encoding="utf-8") as f:
            items_data = json.load(f)

        self.items.clear()

        for item_id, item_data in items_data.items():
            item_type = DashboardItemTypes[item_data["type"]]  # Extract the item type
            del item_data["type"]  # Remove type from the data as it's used for initialization
            if item_type == DashboardItemTypes.CHART:
                new_item = ChartItem(id=int(item_id), on_change_function=on_change_function, df=df)
                for key, value in item_data.items():
                    new_item[key] = value
            elif item_type == DashboardItemTypes.MD_BOX:
                new_item = MDBoxItem(manager_page_number=self.page_number, on_change_function=on_change_function)
                for key, value in item_data.items():
                    new_item[key] = value
            else:
                raise ValueError(f"Unsupported item type: {item_type}")
            self.items[int(item_id)] = new_item

        st.rerun()

    def __str__(self):
        """
        Returns a JSON string representing the current state of the manager.
        """
        items_data = {item_id: json.loads(str(item)) for item_id, item in self.items.items()}
        return json.dumps(items_data, indent=4, ensure_ascii=False)
