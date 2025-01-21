import streamlit as st

from DashboardManager.DashboardItem import DashboardItem
from DashboardManager.DashboardManagerEnums import DashboardItemTypes, MLModelTypes

LIST_OF_MODEL_TYPES = [MLModelTypes.LINEAR_REGRESSION, MLModelTypes.RIDGE_REGRESSION, MLModelTypes.LASSO_REGRESSION,
                       MLModelTypes.DECISION_TREE, MLModelTypes.RANDOM_FOREST, MLModelTypes.XGBOOST,
                       MLModelTypes.LIGHTGBM, MLModelTypes.CATBOOST, MLModelTypes.NEURAL_NETWORK]


class ModelSelectionItem(DashboardItem):
    def __init__(self, on_change_function, ml_model):
        self.on_change_function = on_change_function
        self.ml_model = ml_model

    def get_type(self) -> DashboardItemTypes:
        return DashboardItemTypes.MODEL_SELECTION

    def render(self, pos_id):
        st.write("### Model Type Selection")

        with st.expander("Model Selection Theory", expanded=False):
            with open("DashboardManager/Model/theory_text/model_selection_theory.md", "r") as f:
                st.markdown(f.read())

        st.selectbox("Please choose the type of model",
                     LIST_OF_MODEL_TYPES,
                     format_func=lambda x: x.value,
                     key="selectbox_model_type",  # No dynamic key as this item is expected to be in only 1 instance
                     index=LIST_OF_MODEL_TYPES.index(self.ml_model.model_type),
                     on_change=self.on_change_function,
                     args=(),
                     kwargs={"what_to_update": "model_type", "changed_field_key": "selectbox_model_type"}
                     ),
