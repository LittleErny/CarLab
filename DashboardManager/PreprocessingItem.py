import streamlit as st

from DashboardManager.DashboardItem import DashboardItem
from DashboardManager.DashboardManagerEnums import DashboardItemTypes, PreprocessingTypes

PREP_TYPES = [PreprocessingTypes.OUTLIER_REMOVAL, PreprocessingTypes.LABEL_ENCODING,
              PreprocessingTypes.SCALING, PreprocessingTypes.REMOVING_UNNEC_COLUMN]


class PreprocessingItem(DashboardItem):
    def __init__(self, action, preproc_type):
        self.preprocessing_type: PreprocessingTypes = preproc_type
        self.action = action

    def render(self, pos_id):
        # st.write("Rendering PreprocessingItem...")
        if self.preprocessing_type == PreprocessingTypes.OUTLIER_REMOVAL:
            column, method, threshold = self.action["column"], self.action["method"], self.action["threshold"]
            if method in ("top", "bottom"):
                st.write("#### Outlier removal")
                st.write(f"The {method} ``{threshold}%`` of ``{column}`` were removed.")
            elif method == "both":
                st.write(f"The ``{threshold}%`` from both top and bottom were removed from ``{column}``.")

        elif self.preprocessing_type == PreprocessingTypes.LABEL_ENCODING:
            column, mapping = self.action["column"], self.action["mapping"]
            st.write("#### Label Encoding")
            st.write(f"The ``{column}`` was labeled. The mapping is:")
            st.json(mapping, expanded=False)

        elif self.preprocessing_type == PreprocessingTypes.SCALING:
            column, scaling_method = self.action["column"], self.action["scaling_method"]

            st.write("#### Numerical Parameter Scaling")
            st.write(f"The ``{column}`` was scaled using ``{scaling_method}`` method.")

        elif self.preprocessing_type == PreprocessingTypes.REMOVING_UNNEC_COLUMN:
            st.write("Some column was removed")
            pass

        else:
            raise ValueError(f"PreprocessingItem.preprocessing_type is unknown. Got: {self.preprocessing_type}")



    def get_type(self) -> DashboardItemTypes:
        return DashboardItemTypes.PREPROCESSING_BOX
