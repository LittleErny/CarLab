import streamlit as st

from DashboardManager.DashboardItem import DashboardItem
from DashboardManager.DashboardManagerEnums import DashboardItemTypes

from DashboardManager.Model.ModelRelatedEnums import MLModelTypes

LIST_OF_MODEL_TYPES = [MLModelTypes.LINEAR_REGRESSION, MLModelTypes.RIDGE_REGRESSION, MLModelTypes.LASSO_REGRESSION,
                       MLModelTypes.DECISION_TREE, MLModelTypes.RANDOM_FOREST, MLModelTypes.XGBOOST,
                       MLModelTypes.CATBOOST]


class ModelTrainingItem(DashboardItem):
    def __init__(self, on_change_function, ml_model):
        self.on_change_function = on_change_function
        self.ml_model = ml_model

    def get_type(self) -> DashboardItemTypes:
        return DashboardItemTypes.MODEL_TRAINING

    def render(self, pos_id):
        st.write("### Model Training")

        # Display the selected model type
        st.write(f"**Selected Model:** {self.ml_model.model_type.value}")

        # Slider for train, validation, and test split percentages
        st.write("#### Dataset Split Configuration")
        split_values = st.slider(
            "Adjust dataset split percentages:",
            min_value=0,
            max_value=100,
            value=(70, 85),  # Default values: 70% train, 15% validation, 15% test
            step=1,
            help="If you do not want to use validation data then connect two sliders together."
        )

        train_percent = split_values[0]
        validation_percent = split_values[1] - split_values[0]
        test_percent = 100 - train_percent - validation_percent

        st.write(f"**Train:** {train_percent}% | **Validation:** {validation_percent}% | **Test:** {test_percent}%")

        # Checkbox for using validation data
        use_validation_data = validation_percent != 0

        # Button to start training
        if st.button("Start Training"):
            try:
                # print("Training model of type:", self.ml_model.model_type)
                # print("max_depth", self.ml_model.max_depth)
                with (st.spinner("Training in progress...")):
                    # Call the training method
                    self.ml_model.train_model(
                        train_size=train_percent / 100,
                        validation_size=validation_percent / 100,
                        test_size=test_percent / 100,
                    )
            except Exception as e:
                st.error("Some Error occurred when trying to train model. Please make sure that all the preprocessing"
                         "actions are done. If the error still occurs, refer to error stack below")

                with st.expander("Error Stack:"):
                    st.error(e.with_traceback())

        # If we have trained the model already, then show its metrics
        if self.ml_model.model is not None:

            train_mse, val_mse, test_mse, train_nmse, val_nmse, test_nmse = self.ml_model.metrics

            # Display results in an expander
            with st.expander("Training Results", expanded=True):
                col1, col2 = st.columns([1, 1])

                col1.write("##### Mean Square Error (MSE)")
                col1.write("One **should not** use it for comparing models with "
                           "different types of numerical parameter scaling")

                col1.write(f"**Training MSE:** `{train_mse:.6f}`")
                if use_validation_data:
                    col1.write(f"**Validation MSE:** `{val_mse:.6f}`")
                col1.write(f"**Test MSE:** `{test_mse:.6f}`")

                col2.write("##### Normalized MSE")
                col2.write("Is used for comparing models with "
                           "different types of numerical parameter scaling")

                col2.write(f"**Training MSE:** `{train_nmse:.6f}`")
                if use_validation_data:
                    col2.write(f"**Validation MSE:** `{val_nmse:.6f}`")
                col2.write(f"**Test MSE:** `{test_nmse:.6f}`")
