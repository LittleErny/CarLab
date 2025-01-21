from enum import Enum


class LossFunctions(Enum):  # For gradient boosting models
    SQUARED_ERROR = "squared_error"
    ABSOLUTE_ERROR = "absolute_error"


class MLModelTypes(Enum):
    LINEAR_REGRESSION = 'Linear Regression'
    RIDGE_REGRESSION = 'Ridge Regression'
    LASSO_REGRESSION = 'Lasso Regression'
    DECISION_TREE = 'Decision Tree Regressor'
    RANDOM_FOREST = 'Random Forest Regressor'
    XGBOOST = 'XGBoost Regressor'
    # LIGHTGBM = 'LightGBM Regressor'
    CATBOOST = 'CatBoost Regressor'
    # NEURAL_NETWORK = 'Neural Network (Feedforward)'

    @staticmethod
    def from_string(label: str):
        """Receive the type of chart from its name."""
        for item in MLModelTypes:
            if item.value == label:
                return item
        raise ValueError(f"'{label}' is not a valid PreprocessingTypes value")

    def __eq__(self, other):
        # Due to Streamlit behavior with lots of reloading & reinitializing of some pages, this class is recreated
        # several times, although it should be Singleton. This is why Enum-s should not be used with "is" operator,
        # instead the __eq__() method (which is just "==" operator) should be used.
        return str(self) == str(other)