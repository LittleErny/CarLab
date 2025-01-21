from enum import Enum


class DashboardItemTypes(Enum):
    """Represents the types of DashboardItem."""
    CHART = "chart"
    MD_BOX = "md_box"
    PREPROCESSING_BOX = "preproc_box"
    MODEL_SELECTION = "model_selection"
    MODEL_SETTING = "model_setting"
    MODEL_TRAINING = "model_training"
    MODEL_SCORING = "model_scoring"

    def __eq__(self, other):
        # Due to Streamlit behavior with lots of reloading & reinitializing of some pages, this class is recreated
        # several times, although it should be Singleton. This is why Enum-s should not be used with "is" operator,
        # instead the __eq__() method (which is just "==" operator) should be used.
        return str(self) == str(other)


class ChartTypes(Enum):
    """Represents the types of possible charts."""
    # Charts with one axis
    BOXPLOT = "Boxplot"
    HISTOGRAM = "Histogram"
    KDE = "KDE"

    # Charts with two axis
    SCATTER = "Scatter"
    LINE = "Line"
    BAR = "Bar"
    CATEGORICAL_BOXPLOTS = "Categorical_Boxplots"

    # Charts with three or more axis
    CORRELATION_HEATMAP = "Correlation Heatmap"
    PAIRPLOT = "Pairplot"
    THREE_D_SCATTER = "3D Scatter"
    PARALLEL_COORDINATES = "Parallel Coordinates"
    PIVOT_TABLE_HEATMAP = "Pivot Table Heatmap"
    MISSING_DATA_HEATMAP = "Missing Data Heatmap"

    @staticmethod
    def from_string(label: str):
        """Receive the type of chart from its name."""
        for item in ChartTypes:
            if item.value == label:
                return item
        raise ValueError(f"'{label}' is not a valid ChartTypes value")

    def __eq__(self, other):
        # Due to Streamlit behavior with lots of reloading & reinitializing of some pages, this class is recreated
        # several times, although it should be Singleton. This is why Enum-s should not be used with "is" operator,
        # instead the __eq__() method (which is just "==" operator) should be used.
        return str(self) == str(other)


class MdBoxModes(Enum):
    VIEW = 1
    EDIT = 2

    def __eq__(self, other):
        # Due to Streamlit behavior with lots of reloading & reinitializing of some pages, this class is recreated
        # several times, although it should be Singleton. This is why Enum-s should not be used with "is" operator,
        # instead the __eq__() method (which is just "==" operator) should be used.
        return str(self) == str(other)


class PreprocessingTypes(Enum):
    OUTLIER_REMOVAL = "Remove Outlier"
    LABEL_ENCODING = "Encode Label"
    SCALING = "Scale Numerical Parameter"
    REMOVING_UNNEC_COLUMN = "Remove Unnecessary Column"

    @staticmethod
    def from_string(label: str):
        """Receive the type of chart from its name."""
        for item in PreprocessingTypes:
            if item.value == label:
                return item
        raise ValueError(f"'{label}' is not a valid PreprocessingTypes value")

    def __eq__(self, other):
        # Due to Streamlit behavior with lots of reloading & reinitializing of some pages, this class is recreated
        # several times, although it should be Singleton. This is why Enum-s should not be used with "is" operator,
        # instead the __eq__() method (which is just "==" operator) should be used.
        return str(self) == str(other)




