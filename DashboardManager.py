# Import libraries
import io
from abc import ABC, abstractmethod
from enum import Enum
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from random import randint

# Import from my own files
from helpers import NUMERICAL_COLUMNS

# Some constants
SAMPLE_MD_TEXT = "You can edit this md text by pressing **edit** button"
LIST_GRAPHS_1_VAR = ["Boxplot", "Histogram", "KDE"]
LIST_GRAPHS_2_VAR = ["Scatter", "Line", "Bar"]
LIST_GRAPHS_3_OR_MORE_VAR = ["Correlation Heatmap", "Pairplot", "3D Scatter",
                             "Parallel Coordinates", "Pivot Table Heatmap",
                             "Missing Data Heatmap"]


class DashboardItemTypes(Enum):
    """Represents the types of DashboardItem."""
    CHART = "chart"
    MD_BOX = "md_box"  # TODO!!!!

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


# TODO!
class MdBoxModes(Enum):
    VIEW = 1
    EDIT = 2


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


class ChartItem(DashboardItem):
    """
    ChartItem, inherited from DashboardItem: represents a Chart with all these parameters.
    Chart parameters:
    on_change_function - some function that edits the elements of this chart after editing the interface elements.
                         It is supposed, that this function will use __setitem__ & __getitem__. It should have the
                         following signature: func(item_id: int, what_to_update: str, changed_field_key: str) -> None.
    chart_type: ChartTypes - the type of chart (for example Boxplot, Scatter, etc.)
    amount_of_params - the number of axis in the chart
    x - X axis name. Must be the same as the name of corresponding column in the Dataframe
    y - Y axis name. Must be the same as the name of corresponding column in the Dataframe
    z - Z axis name. Must be the same as the name of corresponding column in the Dataframe
    df: pandas.Dataframe - a link to the dataframe, the data from which is used for building a chart
    high_res_mode: Bool - a flag representing whether the chart should be shown in high resolution
    """

    def __init__(self, id, on_change_function, df):
        self.on_change_function = on_change_function
        self.title = f"Chart {id}"  # id is used only for the name of the chart, that can be changed later
        self.chart_type = ChartTypes.BOXPLOT
        self.amount_of_params = 1
        self.x = df.columns[0]
        self.y = df.columns[0]  # Initialize y and z in advance, even if they are not used
        self.z = df.columns[0]
        self.df = df
        self.high_res_mode = False

    def __repr__(self):
        """How this object is shown while debugging."""
        return str(self)

    def __str__(self):
        """A brief info about the chart"""
        return (f'ChartItem object of type **{self.chart_type}** with title '
                f'"**{self.title}**" and **{self.amount_of_params}** parameters.')

    def __setitem__(self, key, value):
        setattr(self, key, value)  # Dynamic setter for ChartItem

    def __getitem__(self, key):
        return getattr(self, key)  # Dynamic getter for ChartItem

    def render(self, pos_id):  # We take new id for rendering and do not store it in __init__(), as it might be changed
        """Renders everything about this chart in the Streamlit app."""

        def render_axis_selectbox(axis_name, axis_names, index):
            """Helper function for showing the options for choosing the axis names."""
            if axis_name == "x":
                st.selectbox("X-axis", axis_names, index=index,
                             key=f"x_{pos_id}",
                             on_change=self.on_change_function,
                             args=(pos_id, "x", f"x_{pos_id}")
                             )
            elif axis_name == "y":
                st.selectbox("Y-axis", axis_names, index=index,
                             key=f"y_{pos_id}",
                             on_change=self.on_change_function,
                             args=(pos_id, "y", f"y_{pos_id}")
                             )
            elif axis_name == "z":
                st.selectbox("Z-axis", axis_names, index=index,
                             key=f"z_{pos_id}",
                             on_change=self.on_change_function,
                             args=(pos_id, "z", f"z_{pos_id}")
                             )
            else:
                raise ValueError(f'Unknown axis_name: expected "x", "y", or "z"; but received {axis_name}.')

        # Check whether all the chart params are valid, and reset the wrong
        self.validate_chart()

        # TODO: Automatically generate the names of the graphs(LLM?..)
        # Editable title of the chart
        st.text_input(
            f"Chart Title",
            self.title,
            key=f"title_{pos_id}",
            on_change=self.on_change_function,
            args=(pos_id, "title", f"title_{pos_id}")
        )

        # Then render the graph

        chart_buffer, width = self.render_chart()  # Create graph as an image and get it width in pixels

        # st.write(f"Width of the image: {width} pixels")

        st.image(chart_buffer, width=width, use_container_width=False, output_format="PNG")  # And show it

        # Editing the parameters of the graph in the expander bar
        with st.expander("Edit Chart Parameters"):

            # Render the upper part
            col1, col2 = st.columns([1, 1])

            # Choose the number of parameters
            col1.radio("Number of Parameters", [1, 2, "more"],
                       index=[1, 2, "more"].index(self.amount_of_params),
                       key=f"amount_of_params_{pos_id}",
                       on_change=self.on_change_function,
                       args=(pos_id, "amount_of_params", f"amount_of_params_{pos_id}")
                       )
            # If we want to enable high resolution mode
            col2.checkbox("Enable high resolution mode",
                          value=self.high_res_mode,
                          key=f"high_res_mode_{pos_id}",
                          on_change=self.on_change_function,
                          args=(pos_id, "high_res_mode", f"high_res_mode_{pos_id}")
                          )

            # Then choose the type of graph
            if self.amount_of_params == 1:
                try:
                    st.selectbox("Chart Type (1 Param)", LIST_GRAPHS_1_VAR,
                                 index=LIST_GRAPHS_1_VAR.index(str(self.chart_type)),
                                 key=f"chart_type_{pos_id}",
                                 on_change=self.on_change_function,
                                 args=(pos_id, "chart_type", f"chart_type_{pos_id}")
                                 )
                except ValueError as err:
                    # There is a possible scenario when user changes the number of params, and the
                    # ValueError in the "index" param arises, as the graph types are different for
                    # 1 and 2-parameter graphs (or with even bigger amount of params)
                    # TODO: This part should be deleted after finishing implementing ChartItem.validate_chart()!!!!!!
                    new_chart_type = ChartTypes.from_string(
                        st.selectbox("Chart Type (1 Param)", LIST_GRAPHS_1_VAR,
                                     index=0,  # In such a case we just use "any"
                                     key=f"chart_type_{pos_id}",
                                     on_change=self.on_change_function,
                                     args=(pos_id, "chart_type", f"chart_type_{pos_id}")
                                     ))
                    self.chart_type = new_chart_type

                # Then choose X-axis parameter
                if self.chart_type is ChartTypes.HISTOGRAM:
                    # For Histogram any parameter can be used
                    render_axis_selectbox("x", self.df.columns, list(self.df.columns).index(self.x))

                else:
                    # However, for boxplots and KDEs only numerical parameters are accepted
                    render_axis_selectbox("x", NUMERICAL_COLUMNS, list(NUMERICAL_COLUMNS).index(self.x))

            elif self.amount_of_params == 2:
                try:
                    st.selectbox("Chart Type (2 Param)", LIST_GRAPHS_2_VAR,
                                 index=LIST_GRAPHS_2_VAR.index(str(self.chart_type)),
                                 key=f"chart_type_{pos_id}",
                                 on_change=self.on_change_function,
                                 args=(pos_id, "chart_type", f"chart_type_{pos_id}")
                                 )
                except ValueError as err:
                    # There is a possible scenario when user changes the number of params, and the
                    # ValueError in the "index" param arises, as the graph types are different for
                    # 1 and 2-parameter graphs (or with even bigger amount of params)
                    # TODO: This part should be deleted after finishing implementing ChartItem.validate_chart()!!!!!!
                    new_chart_type = ChartTypes.from_string(
                        st.selectbox("Chart Type", ["Scatter", "Line", "Bar"],
                                     index=0,  # In such a case we just use "any"
                                     key=f"chart_type_{pos_id}",
                                     on_change=self.on_change_function,
                                     args=(
                                         pos_id, "chart_type", f"chart_type_{pos_id}")
                                     )
                    )
                    self.chart_type = new_chart_type

                # Then choose X-axis parameter
                render_axis_selectbox("x", self.df.columns, list(self.df.columns).index(self.x))

                # And choose Y-axis parameter
                render_axis_selectbox("y", self.df.columns, list(self.df.columns).index(self.y))

            else:
                # If the option "more" is chosen
                try:

                    st.selectbox("Chart Type (3 or more params)",
                                 LIST_GRAPHS_3_OR_MORE_VAR,
                                 index=LIST_GRAPHS_3_OR_MORE_VAR.index(str(self.chart_type)),
                                 key=f"chart_type_{pos_id}",
                                 on_change=self.on_change_function,
                                 args=(pos_id, "chart_type", f"chart_type_{pos_id}")
                                 )
                except ValueError as err:
                    # There is a possible scenario when user changes the number of params, and the
                    # ValueError in the "index" param arises, as the graph types are different for
                    # 1 and 2-parameter graphs
                    # TODO: This part should be deleted after finishing implementing ChartItem.validate_chart()!!!!!!
                    st.selectbox("Chart Type (3 or more params)",
                                 LIST_GRAPHS_3_OR_MORE_VAR,
                                 index=0,
                                 key=f"chart_type_{pos_id}",
                                 on_change=self.on_change_function,
                                 args=(pos_id, "chart_type", f"chart_type_{pos_id}")
                                 )

                if self.chart_type == "Correlation Heatmap":
                    pass  # Nothing needed to do

                elif self.chart_type == "Pairplot":
                    pass  # Nothing needed to do

                elif self.chart_type == "3D Scatter":

                    # Choose X-axis parameter
                    render_axis_selectbox("x", self.df.columns, list(self.df.columns).index(self.x))
                    # st.selectbox("X-axis", df.columns, index=list(df.columns).index(item["x"]),
                    #                          key=f"x_{id}")
                    # Choose Y-axis parameter
                    render_axis_selectbox("y", self.df.columns, list(self.df.columns).index(self.y))
                    # item["y"] = st.selectbox("Y-axis", df.columns, index=list(df.columns).index(item["y"]),
                    #                          key=f"y_{id}")
                    # Choose Y-axis parameter
                    render_axis_selectbox("z", self.df.columns, list(self.df.columns).index(self.z))
                    # item["z"] = st.selectbox("Z-axis", df.columns, index=list(df.columns).index(item["z"]),
                    #                          key=f"z_{id}")
                    # TODO: Probably add some kind of rotator?..

                elif self.chart_type == "Parallel Coordinates":
                    pass  # TODO!!!!!

                elif self.chart_type == "Pivot Table Heatmap":
                    pass  # TODO!!!
                    # pivot_data = df.pivot_table(
                    #     values=chart_params["value_column"],
                    #     index=chart_params["row_column"],
                    #     columns=chart_params["column_column"],
                    #     aggfunc='mean'
                    # )
                    # sns.heatmap(pivot_data, annot=True, cmap="viridis")
                elif self.chart_type == "Missing Data Heatmap":
                    pass  # TODO!!!

    def get_type(self):
        return DashboardItemTypes.CHART

    def get_graph_type(self):
        return self.chart_type

    # @st.cache_data  TODO: make our own caching here for images in buffer
    def render_chart(_self):  # _self is for not to be visible for the st caching function
        """
        Render a chart based on the chart type and parameters.
        (The result is cached to avoid redundant recalculations if the chart is not modified.) not yet

        :param df: Input DataFrame used to generate the chart.
        :return: The rendered chart object.
        """

        self = _self

        if self.high_res_mode:
            fig, ax = plt.subplots(figsize=(30, 18))  # Resolution of 3000х1800 pixels
            width = 3000
        else:
            fig, ax = plt.subplots(figsize=(10, 6))  # Resolution of 1000х600 pixels
            width = 1000

        df = self.df

        if self.high_res_mode:
            # Make the names of categories vertical, so that user can read it when there are a lot of them
            if self.x in ("model", "brand"):
                plt.xticks(rotation=90)

            if self.amount_of_params == 2 and self.y in ("model", "brand"):
                plt.yticks(rotation=90)

            plt.rcParams.update({'font.size': 8})

        if self.amount_of_params == 1:

            if self.chart_type == ChartTypes.BOXPLOT:
                sns.boxplot(data=df, x=self.x)
            elif self.chart_type == ChartTypes.HISTOGRAM:
                sns.histplot(data=df, x=self.x, kde=False, ax=ax)
            elif self.chart_type == ChartTypes.KDE:
                sns.kdeplot(data=df, x=self.x, fill=True, ax=ax)
            else:
                raise ValueError(f"The chart_type of ChartItem object is unknown. Got: {self.chart_type}")

        elif self.amount_of_params == 2:
            if self.chart_type == ChartTypes.SCATTER:
                sns.scatterplot(data=df, x=self.x, y=self.y)
            elif self.chart_type == ChartTypes.LINE:
                sns.lineplot(data=df, x=self.x, y=self.y)
            elif self.chart_type == ChartTypes.BAR:
                sns.barplot(data=df, x=self.x, y=self.y)
            else:
                raise ValueError(f"The chart_type of ChartItem object is unknown. Got: {self.chart_type}")

        else:
            pass  # TODO: other types of charts

        # Save the image, close all the environment, and pass the image back
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        plt.close(fig)
        plt.rcdefaults()
        return buf, width

    def validate_chart(self):
        """Sometimes there are the cases, when some graph arguments do not correspond for each other. This can
        happen when user changes the upper parameters(for example the amount of parameters), and the type of graph
        is still old. This function will reset parameters to basic one, so that user did not see any errors.

        Some rules for chart validation:
        - The higher parameter, the more important it is. Specifically:
            - if chart_type conflicts with amount_of_params, amount_of_params has priority.
            - if chart_type conflicts with parameter type(categorical/numerical), chart_type has priority.

        """

        if self.amount_of_params == 1:

            # check if the graph type can be chosen when we have only 1 graph param
            if not any(list(map(lambda x: ChartTypes.from_string(x) == self.chart_type, LIST_GRAPHS_1_VAR))):
                print("BOXPLOT WAS SET DURING VALIDATION")
                self.chart_type = ChartTypes.BOXPLOT  # set to the basic one

            # then check the conflict btw chart_type and the type of parameter
            if self.chart_type == ChartTypes.BOXPLOT or self.chart_type == ChartTypes.KDE:

                # then only numerical type can be accepted
                if self.x not in NUMERICAL_COLUMNS:
                    # if this is not numerical, set it back to numerical
                    self.x = NUMERICAL_COLUMNS[0]

        elif self.amount_of_params == 2:

            # check if the graph type can be chosen when we have 2 graph params (axis)
            if not any(list(map(lambda x: ChartTypes.from_string(x) == self.chart_type, LIST_GRAPHS_2_VAR))):
                print("Scatter WAS SET DURING VALIDATION")
                self.chart_type = ChartTypes.SCATTER  # set to the basic one


# TODO!!!
class MDBoxItem(DashboardItem):
    def __init__(self, content=SAMPLE_MD_TEXT):
        self.content = content
        self.mode = MdBoxModes.VIEW  # No editor is shown

    def enable_editing_mode(self):
        self.mode = MdBoxModes.EDIT

    def disable_editing_mode(self):
        self.mode = MdBoxModes.VIEW

    def update_content(self, new_content):
        self.content = new_content

    def render(self):
        print("rendering..")


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
        return st.session_state[key]

    def __init__(self, page_number):
        pass  # Do nothing here as everything is already done in __new__()

    def __str__(self):
        # Just for easier debugging
        return '\n'.join([item.__dict__ for item in self.items])

    def get_items(self):
        return self.items.items()

    def is_empty(self):
        return len(self.items) == 0

    def create_item(self, item_type: DashboardItemTypes, *args, **kwargs):
        """
        Factory method for creating items.

        :param item_type: The item type (e.g. 'chart' or 'md_box').
        :param kwargs: Parameters for the constructor.
        :return: The created item instance.
        """
        # print("creating some item", item_type, args, kwargs)

        if item_type == DashboardItemTypes.CHART:
            new_chart_item = ChartItem(id=self.amount_of_items, *args, **kwargs)
            self.items[self.amount_of_items] = new_chart_item
            self.amount_of_items += 1

            return new_chart_item
        elif item_type == DashboardItemTypes.MD_BOX:
            # TODO: the process of creating MD box
            return MDBoxItem(**kwargs)
        else:
            raise ValueError(f"Unknown item type: {item_type}")

    def remove_item(self, item_id):
        """Remove item."""
        if item_id in self.items:
            del self.items[item_id]

    def move_item_up(self, item_id):
        # Suppose there can be situation that there will be spaces in the keys like [0, 1, 3]
        item_keys = sorted(self.items.keys())
        item_pos = item_keys.index(item_id)
        if item_pos == 0:
            return  # do nothing, as the position is already the highest possible
        next_item_id = item_keys[item_pos - 1]
        self.swap_items(item_id, next_item_id)

    def move_item_down(self, item_id):
        # Suppose there can be situation that there will be spaces in the keys like [0, 1, 3]
        item_keys = sorted(self.items.keys())
        item_pos = item_keys.index(item_id)
        if item_pos == len(item_keys) - 1:
            return  # do nothing, as the position is already the lowest possible
        next_item_id = item_keys[item_pos + 1]
        self.swap_items(item_id, next_item_id)

    def swap_items(self, item1_id, item2_id):
        """Swap two elements."""
        if item1_id not in self.items or item2_id not in self.items:
            raise ValueError("Both item IDs must exist in the items dictionary")
        self.items[item1_id], self.items[item2_id] = self.items[item2_id], self.items[item1_id]

    def print_items(self):
        """Print info about all the elements."""
        for item_id, item in self.items.items():
            print(f"ID: {item_id}, Type: {type(item).__name__}")
