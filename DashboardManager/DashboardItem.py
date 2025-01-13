import json
from abc import ABC, abstractmethod

from DashboardManager.DashboardManagerEnums import DashboardItemTypes


class DashboardItem(ABC):
    """Abstract class for all the Dashboard elements."""

    @abstractmethod
    def get_type(self) -> DashboardItemTypes:
        """Should return the type of current Item."""
        pass

    @abstractmethod
    def render(self, pos_id):
        """Renders this item from the very beginning to the very end."""
        pass

    def __setitem__(self, key, value):
        setattr(self, key, value)  # Dynamic setter for DashboardItem

    def __getitem__(self, key):
        return getattr(self, key)  # Dynamic getter for DashboardItem

    def __str__(self):
        # Include type in the serialized JSON
        return json.dumps(
            {
                "type": self.get_type().name,
                **{k: v for k, v in self.__dict__.items() if k not in ["on_change_function", "df"]},
            },
            default=str,  # Handle non-serializable types
        )
