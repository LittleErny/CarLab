import numpy as np
import streamlit as st
from pandas import DataFrame
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from xgboost import XGBRegressor
from catboost import CatBoostRegressor

from DashboardManager.Model.ModelRelatedEnums import LossFunctions, MLModelTypes
from helpers import reverse_preprocessing


class MLModel:

    def __new__(cls,
                df: DataFrame,
                model_type: MLModelTypes = MLModelTypes.LINEAR_REGRESSION,
                target_variable: str = "price_EUR",
                ):
        # Singleton
        if "ml_model" not in st.session_state:
            instance = super().__new__(cls)
            instance.df = df
            instance.model = None  # to be assigned after training
            instance.metrics = None

            x_names = list(df.columns)
            if target_variable in x_names:
                x_names.remove(target_variable)
            else:
                raise ValueError("Got Unknown Target Variable while trying to create new MLModel.")

            instance.x_column_names = x_names
            instance.target_variable_name = target_variable

            # --- The model type ---
            instance.model_type = model_type

            # --- Common Parameters ---
            instance.random_state = 42  # Used for reproducibility (any integer or None)

            # --- Linear Models (Linear, Ridge, Lasso) ---
            instance.alpha = 1.0  # Regularization strength for Ridge/Lasso (float > 0)

            # --- Decision Tree Parameters ---
            instance.max_depth = None  # Maximum depth of the tree (int > 0 or None)
            instance.min_samples_split = 2  # Minimum samples required to split a node (int > 1)
            instance.min_samples_leaf = 1  # Minimum samples required in a leaf node (int > 0)

            # --- Random Forest Parameters ---
            instance.n_estimators = 100  # Number of trees (int > 0)
            instance.max_features = "sqrt"  # Number of features to consider for splitting ("sqrt", "log2", ..)

            # --- Gradient Boosting Parameters (XGBoost, LightGBM, CatBoost) ---
            instance.learning_rate = 0.1  # Step size shrinkage (float > 0)
            instance.n_estimators = 100  # Number of boosting stages (int > 0)
            instance.loss = LossFunctions.SQUARED_ERROR  # Loss function (use LossFunctions Enum)

            # --- CatBoost-specific Parameters ---
            instance.task_type = "CPU"  # Device to use ("CPU" or "GPU")

            st.session_state["ml_model"] = instance
        return st.session_state["ml_model"]

    def __init__(self, df: DataFrame):
        pass

    def __setitem__(self, key, value):
        setattr(self, key, value)  # Dynamic setter

    def __getitem__(self, key):
        return getattr(self, key)  # Dynamic getter

    def train_model(self, train_size: float, validation_size: float, test_size: float):
        """
        Train the model based on the current configuration.

        :param train_size: Percentage of data used for training.
        :param validation_size: Percentage of data used for validation.
        :param test_size: Percentage of data used for testing.
        """

        target_column = "price_EUR"
        X, y = self.df.drop(columns=[target_column]), self.df[target_column]

        if validation_size != 0:
            train_X, val_test_X, train_y, val_test_y = train_test_split(
                X, y, train_size=train_size, random_state=self.random_state
            )
            val_X, test_X, val_y, test_y = train_test_split(
                val_test_X, val_test_y, test_size=test_size / (test_size + validation_size),
                random_state=self.random_state
            )
        else:
            train_X, test_X, train_y, test_y = train_test_split(
                X, y, train_size=train_size, random_state=self.random_state
            )
            val_X, val_y = None, None

        model = None
        progress = st.progress(0)
        if self.model_type == MLModelTypes.LINEAR_REGRESSION:
            # print("LINEAR_REGRESSION!!!")
            model = LinearRegression()

        elif self.model_type == MLModelTypes.RIDGE_REGRESSION:
            model = Ridge(alpha=self.alpha, random_state=self.random_state)

        elif self.model_type == MLModelTypes.LASSO_REGRESSION:
            model = Lasso(alpha=self.alpha, random_state=self.random_state)

        elif self.model_type == MLModelTypes.DECISION_TREE:
            model = DecisionTreeRegressor(
                max_depth=self.max_depth if self.max_depth != 1 else 1000,
                min_samples_split=self.min_samples_split,
                min_samples_leaf=self.min_samples_leaf,
                random_state=self.random_state
            )

        elif self.model_type == MLModelTypes.RANDOM_FOREST:
            model = RandomForestRegressor(
                max_depth=self.max_depth if self.max_depth != 1 else 1000,
                n_estimators=self.n_estimators,
                max_features=self.max_features,
                random_state=self.random_state
            )

        elif self.model_type == MLModelTypes.XGBOOST:
            model = XGBRegressor(
                n_estimators=self.n_estimators,
                learning_rate=self.learning_rate,
                random_state=self.random_state
            )

        elif self.model_type == MLModelTypes.CATBOOST:
            model = CatBoostRegressor(
                iterations=self.n_estimators,
                learning_rate=self.learning_rate,
                task_type=self.task_type,
                verbose=0,
                random_state=self.random_state
            )

        # Training
        if model is not None:
            model.fit(train_X, train_y)

        # Validation and Testing
        train_mse, val_mse, test_mse = None, None, None
        train_nmse, val_nmse, test_nmse = None, None, None

        train_preds = model.predict(train_X)
        train_mse = mean_squared_error(train_y, train_preds)

        variance_target = np.var(train_y, ddof=1)  #
        train_nmse = train_mse / variance_target if variance_target != 0 else float('inf')

        if val_X is not None:
            val_preds = model.predict(val_X)
            val_mse = mean_squared_error(val_y, val_preds)

            variance_target = np.var(val_y, ddof=1)  #
            val_nmse = val_mse / variance_target if variance_target != 0 else float('inf')

        test_preds = model.predict(test_X)
        test_mse = mean_squared_error(test_y, test_preds)

        variance_target = np.var(test_y, ddof=1)  #
        test_nmse = test_mse / variance_target if variance_target != 0 else float('inf')

        # Display results
        st.success("Training complete!")

        # Combine test features, true values, and predictions into a single DataFrame
        results_df = test_X.copy()  # Copy all columns from the test set
        results_df["True_Value"] = [reverse_preprocessing("price_EUR", i) for i in test_y.values]  # Adding true values
        results_df["Prediction"] = [int(reverse_preprocessing("price_EUR", i)) for i in test_preds]  # Adding predictions

        # Display the generated dataset to the user
        st.write("Sample of Test Results:")
        st.dataframe(results_df.head(15))

        # Save the model and metrics
        self.model = model
        self.metrics = (train_mse, val_mse, test_mse, train_nmse, val_nmse, test_nmse)
        # print("Metrics: ", self.metrics)
