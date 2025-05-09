import hashlib

import streamlit as st
from matplotlib import pyplot as plt
import pandas as pd
import seaborn as sns
import io
import weakref

from DashboardManager.DashboardItem import DashboardItem
from DashboardManager.DashboardManagerEnums import ChartTypes, DashboardItemTypes
from helpers import NUMERICAL_COLUMNS, CATEGORICAL_COLUMNS

# Some constants
LIST_GRAPHS_1_VAR = [ChartTypes.BOXPLOT, ChartTypes.HISTOGRAM, ChartTypes.KDE]
LIST_GRAPHS_2_VAR = [ChartTypes.SCATTER, ChartTypes.LINE, ChartTypes.BAR, ChartTypes.CATEGORICAL_BOXPLOTS]
LIST_GRAPHS_3_OR_MORE_VAR = [ChartTypes.CORRELATION_HEATMAP,
                             # ChartTypes.PAIRPLOT, ChartTypes.THREE_D_SCATTER,  # NOT IMPLEMENTED YET
                             # "Parallel Coordinates", "Pivot Table Heatmap",    # DO NOT UNCOMMENT
                             # "Missing Data Heatmap"
                             ]


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
        self.df_ref = weakref.ref(df)
        self.high_res_mode = False

    def __repr__(self):
        """How this object is shown while debugging."""
        return str(self)

    # def __str__(self):
    #     """A brief info about the chart"""
    #     return (f'ChartItem object of type **{self.chart_type}** with title '
    #             f'"**{self.title}**" and **{self.amount_of_params}** parameters.')

    def _calculate_hash(self):
        """
        Calculates a hash for the current graph parameters to use for caching.
        """
        # Hashing data from a DataFrame to track data changes
        df = self.df_ref()
        df_hash = hashlib.md5(pd.util.hash_pandas_object(df, index=True).values.tobytes()).hexdigest()

        # Collecting parameters for hashing
        params = (
            df_hash,
            self.chart_type,
            self.amount_of_params,
            self.x,
            self.y,
            self.z,
            self.high_res_mode
        )

        # Create hash from the parameters
        return hashlib.md5(str(params).encode('utf-8')).hexdigest()

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
        df = self.df_ref()
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
                st.selectbox("Chart Type (1 Param)",
                             [i.value for i in LIST_GRAPHS_1_VAR],
                             index=LIST_GRAPHS_1_VAR.index(self.chart_type),
                             key=f"chart_type_{pos_id}",
                             on_change=self.on_change_function,
                             args=(pos_id, "chart_type", f"chart_type_{pos_id}")
                             )

                # Then choose X-axis parameter
                if self.chart_type == ChartTypes.HISTOGRAM:
                    # For Histogram any parameter can be used
                    render_axis_selectbox("x", df.columns, list(df.columns).index(self.x))

                else:
                    # However, for boxplots and KDEs only numerical parameters are accepted
                    render_axis_selectbox("x", NUMERICAL_COLUMNS, list(NUMERICAL_COLUMNS).index(self.x))

            elif self.amount_of_params == 2:

                st.selectbox("Chart Type (2 Param)",
                             [i.value for i in LIST_GRAPHS_2_VAR],
                             index=LIST_GRAPHS_2_VAR.index(self.chart_type),
                             key=f"chart_type_{pos_id}",
                             on_change=self.on_change_function,
                             args=(pos_id, "chart_type", f"chart_type_{pos_id}")
                             )

                # Then choose X-axis parameter
                if self.chart_type == ChartTypes.CATEGORICAL_BOXPLOTS:
                    render_axis_selectbox("x", CATEGORICAL_COLUMNS, CATEGORICAL_COLUMNS.index(self.x))
                else:
                    render_axis_selectbox("x", df.columns, list(df.columns).index(self.x))

                # And choose Y-axis parameter
                if self.chart_type == ChartTypes.CATEGORICAL_BOXPLOTS:
                    render_axis_selectbox("y", NUMERICAL_COLUMNS, NUMERICAL_COLUMNS.index(self.y))
                else:
                    render_axis_selectbox("y", df.columns, list(df.columns).index(self.y))

            else:
                # If the option "more" is chosen

                st.selectbox("Chart Type (3 or more params)",
                             [i.value for i in LIST_GRAPHS_3_OR_MORE_VAR],
                             index=LIST_GRAPHS_3_OR_MORE_VAR.index(self.chart_type),
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
                render_axis_selectbox("x", df.columns, list(df.columns).index(self.x))
                # st.selectbox("X-axis", df.columns, index=list(df.columns).index(item["x"]),
                #                          key=f"x_{id}")
                # Choose Y-axis parameter
                render_axis_selectbox("y", df.columns, list(df.columns).index(self.y))
                # item["y"] = st.selectbox("Y-axis", df.columns, index=list(df.columns).index(item["y"]),
                #                          key=f"y_{id}")
                # Choose Y-axis parameter
                render_axis_selectbox("z", df.columns, list(df.columns).index(self.z))
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

    # @st.cache_data
    def render_chart(_self):  # _self is for not to be visible for the st caching function
        """
        Render a chart based on the chart type and parameters.
        (The result is cached to avoid redundant recalculations if the chart is not modified.) not yet

        :return: The rendered chart object.
        """

        self = _self

        # If the hash is already in the cache, return the saved image and width
        current_hash = self._calculate_hash()
        if current_hash in st.session_state["chart_hashes"]:
            return (st.session_state["chart_hashes"][current_hash]['buffer'],
                    st.session_state["chart_hashes"][current_hash]['width'])

        if self.high_res_mode:
            fig, ax = plt.subplots(figsize=(30, 18))  # Resolution of 3000х1800 pixels
            width = 3000
        else:
            fig, ax = plt.subplots(figsize=(10, 6))  # Resolution of 1000х600 pixels
            width = 1000

        df = self.df_ref()

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
            elif self.chart_type == ChartTypes.CATEGORICAL_BOXPLOTS:
                # Assume that X is categorical and Y is not
                cat_groups = df.groupby(self.x)[self.y].median().sort_values(ascending=False)
                # Sort the categories on the graph - from the highest median to lowest
                sns.boxplot(
                    data=df,
                    x=self.x,
                    y=self.y,
                    order=cat_groups.index,  # order
                    showfliers=False
                )
            else:
                raise ValueError(f"The chart_type of ChartItem object is unknown. Got: {self.chart_type}")

        else:
            if self.chart_type == ChartTypes.CORRELATION_HEATMAP:
                corr_matrix = df[NUMERICAL_COLUMNS].corr()  # Only numerical params can be used here
                sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="coolwarm", ax=ax)
                plt.title("Correlation Heatmap")
            else:
                raise ValueError(
                    f"The chart_type of ChartItem object is unknown or unsupported for more than 2 parameters. Got: {self.chart_type}")
            # pass  # TODO: other types of charts

        # Save the image, close all the environment, and pass the image back
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        plt.close(fig)
        plt.rcdefaults()

        # Save the result in the Kache
        st.session_state['chart_hashes'][current_hash] = {
            'buffer': buf,
            'width': width
        }

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
            if not any(list(map(lambda x: x == self.chart_type, LIST_GRAPHS_1_VAR))):
                self.chart_type = ChartTypes.BOXPLOT  # set to the basic one

            # then check the conflict btw chart_type and the type of parameter
            if self.chart_type == ChartTypes.BOXPLOT or self.chart_type == ChartTypes.KDE:

                # then only numerical type can be accepted
                if self.x not in NUMERICAL_COLUMNS:
                    # if this is not numerical, set it back to numerical
                    self.x = NUMERICAL_COLUMNS[0]

        elif self.amount_of_params == 2:

            # check if the graph type can be chosen when we have 2 graph params (axis)
            if not any(list(map(lambda x: x == self.chart_type, LIST_GRAPHS_2_VAR))):
                self.chart_type = ChartTypes.SCATTER  # set to the basic one

            if self.chart_type == ChartTypes.CATEGORICAL_BOXPLOTS:

                # Only (cat + non-cat) are accepted
                if (self.x in NUMERICAL_COLUMNS and self.y not in NUMERICAL_COLUMNS) or (
                        self.x not in NUMERICAL_COLUMNS and self.y in NUMERICAL_COLUMNS):

                    # For better picture, X-axis is available for categorical parameter only
                    if self.y not in NUMERICAL_COLUMNS:
                        self.x, self.y = self.y, self.x

                elif self.x in NUMERICAL_COLUMNS and self.y in NUMERICAL_COLUMNS:
                    self.x = CATEGORICAL_COLUMNS[0]

                elif self.x not in NUMERICAL_COLUMNS and self.y not in NUMERICAL_COLUMNS:
                    self.y = NUMERICAL_COLUMNS[0]

        elif self.amount_of_params == "more":
            # check if the current graph type can be chosen when we have 3 or more graph params (axis)
            if not any(list(map(lambda x: x == self.chart_type, LIST_GRAPHS_3_OR_MORE_VAR))):
                # Set the 1st possible option
                self.chart_type = ChartTypes.CORRELATION_HEATMAP

        else:
            raise ValueError(f"Unexpected amount of params during Chart validation: "
                             f"expected 1, 2, or 'more'; got {self.amount_of_params}")
