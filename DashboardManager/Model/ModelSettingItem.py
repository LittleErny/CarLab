import streamlit as st

from DashboardManager.DashboardItem import DashboardItem
from DashboardManager.DashboardManagerEnums import DashboardItemTypes
from DashboardManager.Model.Model import MLModel
from DashboardManager.Model.ModelRelatedEnums import LossFunctions, MLModelTypes

LIST_OF_MODEL_TYPES = [MLModelTypes.LINEAR_REGRESSION, MLModelTypes.RIDGE_REGRESSION, MLModelTypes.LASSO_REGRESSION,
                       MLModelTypes.DECISION_TREE, MLModelTypes.RANDOM_FOREST, MLModelTypes.XGBOOST,
                       MLModelTypes.CATBOOST]


class ModelSettingItem(DashboardItem):
    def __init__(self, on_change_function, ml_model):
        self.on_change_function = on_change_function
        self.ml_model: MLModel = ml_model

    def get_type(self) -> DashboardItemTypes:
        return DashboardItemTypes.MODEL_SETTING

    def render(self, pos_id):
        st.write("### Model Settings")

        # Add input for random_state (common to all models)
        st.number_input(
            "Random State",
            value=self.ml_model.random_state,
            min_value=0,
            key="input_random_state",
            help="Seed value to ensure reproducibility of results.",
            on_change=self.on_change_function,
            kwargs={"what_to_update": "random_state", "changed_field_key": "input_random_state"}
        )

        if self.ml_model.model_type == MLModelTypes.LINEAR_REGRESSION:
            st.info("Linear Regression has no additional parameters.")

        elif self.ml_model.model_type in [MLModelTypes.RIDGE_REGRESSION, MLModelTypes.LASSO_REGRESSION]:
            st.number_input(
                "Alpha (Regularization Strength)",
                value=self.ml_model.alpha,
                min_value=0.0,
                format="%.5f",
                key="input_alpha",
                help="Regularization strength: higher values mean stronger regularization to avoid overfitting.",
                on_change=self.on_change_function,
                kwargs={"what_to_update": "alpha", "changed_field_key": "input_alpha"}
            )

        elif self.ml_model.model_type == MLModelTypes.DECISION_TREE:
            st.number_input(
                "Max Depth",
                value=self.ml_model.max_depth if self.ml_model.max_depth else -1,
                min_value=-1,
                key="input_max_depth",
                help="Maximum depth of the tree. Set to -1 for unlimited depth.",
                on_change=self.on_change_function,
                kwargs={"what_to_update": "max_depth", "changed_field_key": "input_max_depth"}
            )
            st.number_input(
                "Min Samples Split",
                value=self.ml_model.min_samples_split,
                min_value=2,
                key="input_min_samples_split",
                help="The minimum number of samples required to split an internal node.",
                on_change=self.on_change_function,
                kwargs={"what_to_update": "min_samples_split", "changed_field_key": "input_min_samples_split"}
            )
            st.number_input(
                "Min Samples Leaf",
                value=self.ml_model.min_samples_leaf,
                min_value=1,
                key="input_min_samples_leaf",
                help="The minimum number of samples required to be at a leaf node.",
                on_change=self.on_change_function,
                kwargs={"what_to_update": "min_samples_leaf", "changed_field_key": "input_min_samples_leaf"}
            )

        elif self.ml_model.model_type == MLModelTypes.RANDOM_FOREST:
            st.number_input(
                "Max Depth",
                value=self.ml_model.max_depth if self.ml_model.max_depth else -1,
                min_value=-1,
                key="input_max_depth",
                help="Maximum depth of the tree. Set to -1 for unlimited depth.",
                on_change=self.on_change_function,
                kwargs={"what_to_update": "max_depth", "changed_field_key": "input_max_depth"}
            )
            st.number_input(
                "Number of Estimators",
                value=self.ml_model.n_estimators,
                min_value=1,
                key="input_n_estimators",
                help="The number of trees in the forest. Higher values improve performance but increase computation time.",
                on_change=self.on_change_function,
                kwargs={"what_to_update": "n_estimators", "changed_field_key": "input_n_estimators"}
            )
            st.selectbox(
                "Max Features",
                ["auto", "sqrt", "log2"],
                index=["sqrt", "log2"].index(self.ml_model.max_features),
                key="input_max_features",
                help="The number of features to consider when looking for the best split.",
                on_change=self.on_change_function,
                kwargs={"what_to_update": "max_features", "changed_field_key": "input_max_features"}
            )

        elif self.ml_model.model_type == MLModelTypes.XGBOOST:
            st.number_input(
                "Learning Rate",
                value=self.ml_model.learning_rate,
                min_value=0.0,
                format="%.5f",
                key="input_learning_rate",
                help="Controls the contribution of each tree to the final prediction. Lower values require more trees.",
                on_change=self.on_change_function,
                kwargs={"what_to_update": "learning_rate", "changed_field_key": "input_learning_rate"}
            )
            st.number_input(
                "Number of Estimators",
                value=self.ml_model.n_estimators,
                min_value=1,
                key="input_n_estimators_boosting",
                help="The number of boosting stages to perform.",
                on_change=self.on_change_function,
                kwargs={"what_to_update": "n_estimators", "changed_field_key": "input_n_estimators_boosting"}
            )
            st.selectbox(
                "Loss Function",
                list(LossFunctions),
                format_func=lambda x: x.value,
                index=list(LossFunctions).index(self.ml_model.loss),
                key="input_loss_function",
                help="The loss function to optimize during training.",
                on_change=self.on_change_function,
                kwargs={"what_to_update": "loss", "changed_field_key": "input_loss_function"}
            )

        elif self.ml_model.model_type == MLModelTypes.CATBOOST:
            st.selectbox(
                "Task Type",
                ["CPU", "GPU"],
                index=["CPU", "GPU"].index(self.ml_model.task_type),
                key="input_task_type",
                help="Specifies whether to train on CPU or GPU.",
                on_change=self.on_change_function,
                kwargs={"what_to_update": "task_type", "changed_field_key": "input_task_type"}
            )

        else:
            st.warning("Model type not recognized or not implemented.")
