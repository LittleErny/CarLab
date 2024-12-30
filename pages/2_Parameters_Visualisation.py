import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from helpers import initialize_global_session_variables_if_not_yet, NUMERICAL_COLUMNS, create_quantitative_dataset

LIST_GRAPHS_1_VAR = []
LIST_GRAPHS_2_VAR = []
LIST_GRAPHS_3_OR_MORE_VAR = ["Correlation Heatmap", "Pairplot", "3D Scatter",
                             "Parallel Coordinates", "Pivot Table Heatmap",
                             "Missing Data Heatmap"]


# TODO: fix the problem with re-rendering heavy charts if they are not edited or created in the first time

# Functions to handle changes for each input element
def update_chart_state(graph_id, what_to_update, changed_field_key):
    st.session_state.p2_items[graph_id][what_to_update] = st.session_state[changed_field_key]


# Whenever we need to create a new graph, this sample is created and s
def generate_sample_graph():
    id = st.session_state.p2_chart_counter
    # print(id, st.session_state.p2_items)
    sample_graph = {
        "container_type": "graph",
        "title": f"Chart {st.session_state.p2_chart_counter + 1}",
        "type": "Scatter",
        "x": df.columns[0],
        "y": df.columns[0],  # Initialize y and z in advance
        "z": df.columns[0],
        "params": 1
    }
    st.session_state.p2_items[id] = sample_graph
    st.session_state.p2_chart_counter += 1


def generate_sample_md_container():
    id = st.session_state.p2_chart_counter
    sample_md_box = {
        "container_type": "md",
        "mode": "view",
        "text": "You can edit this md text by pressing **edit** button"
    }
    st.session_state.p2_items[id] = sample_md_box
    st.session_state.p2_chart_counter += 1


def disable_edit_mode_in_md_boxes():
    # Just run through all the boxes and change their mode
    for id, item in st.session_state.p2_items.items():
        if item["container_type"] == "md" and item["mode"] == "edit":
            st.session_state.p2_items[id]["mode"] = "view"
    print("disable_edit_mode_in_md_boxes")


def enable_editing_mode():
    # print("change_editing_mode: now is " + str(-st.session_state.p2_editing_mode))
    st.session_state.p2_editing_mode = True


# In case this page was the first to be load by the user in the whole application,
# this will initialize them; and do nothing in the opposite case
initialize_global_session_variables_if_not_yet()

df = st.session_state.df


# Graph render function
def render_chart(chart_params):
    plt.figure(figsize=(10, 6))

    # If we have only 1 parameter
    if chart_params["params"] == 1:
        # Choose from graphs with 1 parameter
        if chart_params["type"] == "Boxplot":
            sns.boxplot(data=df, x=chart_params["x"])
        elif chart_params["type"] == "Histogram":
            sns.histplot(data=df, x=chart_params["x"], kde=False)
        elif chart_params["type"] == "KDE":
            sns.kdeplot(data=df, x=chart_params["x"], fill=True)

    elif chart_params["params"] == 2:
        # Choose from graphs with 2 parameters
        if chart_params["type"] == "Scatter":
            sns.scatterplot(data=df, x=chart_params["x"], y=chart_params["y"])
        elif chart_params["type"] == "Line":
            sns.lineplot(data=df, x=chart_params["x"], y=chart_params["y"])
        elif chart_params["type"] == "Bar":
            sns.barplot(data=df, x=chart_params["x"], y=chart_params["y"])
        # TODO: Add boxplots for (categorical+non-categorical)

    else:
        # Choose from graphs with more parameters
        if chart_params["type"] == "Correlation Heatmap":
            df_quantitative = create_quantitative_dataset(df)
            corr_matrix = df_quantitative.corr()
            sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="coolwarm")
        elif chart_params["type"] == "Pairplot":
            df_quantitative = create_quantitative_dataset(df)
            sns.pairplot(data=df_quantitative)  # Отображает парные графики для всех численных переменных
        elif chart_params["type"] == "3D Scatter":
            from mpl_toolkits.mplot3d import Axes3D
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')
            ax.scatter(
                df[chart_params["x"]],
                df[chart_params["y"]],
                df[chart_params["z"]]
            )
            ax.set_xlabel(chart_params["x"])
            ax.set_ylabel(chart_params["y"])
            ax.set_zlabel(chart_params["z"])
        elif chart_params["type"] == "Parallel Coordinates":
            from pandas.plotting import parallel_coordinates
            parallel_coordinates(data=df, class_column=chart_params["class_column"])
        elif chart_params["type"] == "Pivot Table Heatmap":
            pivot_data = df.pivot_table(
                values=chart_params["value_column"],
                index=chart_params["row_column"],
                columns=chart_params["column_column"],
                aggfunc='mean'
            )
            sns.heatmap(pivot_data, annot=True, cmap="viridis")
        elif chart_params["type"] == "Missing Data Heatmap":
            sns.heatmap(df.isnull(), cbar=False, cmap="viridis")

    # Draw the graph
    st.pyplot(plt)


# If we do not have any charts to show, let the user create the first one
if not st.session_state.p2_items:
    if st.button("➕ Add First Chart", key=f"add_first_chart"):
        generate_sample_graph()
        st.rerun()
    st.button("Add First Text", key=f"add_first_md_box", on_click=generate_sample_md_container)

# Render all the items(graphs or MD-boxes) that we have
for id, item in st.session_state.p2_items.items():

    # Each item interface is inside the container
    with st.container(border=True):

        # Split the container to 2 parts - left & right in a ratio of 15 to 1
        main, arrows = st.columns([15, 1])

        with main:

            if item["container_type"] == "graph":

                # TODO: Automatically generate the names of the graphs(LLM?..)
                # Editable title of the chart
                item["title"] = st.text_input(
                    f"Chart Title",
                    item["title"],
                    key=f"title_{id}",
                    on_change=update_chart_state,
                    args=(id, "title", f"title_{id}")
                )

                # Placeholder for the graph, as the rendering should take place after the parameters initialization
                placeholder = st.empty()

                # Editing the parameters of the graph
                with st.expander("Edit Chart Parameters"):
                    # Choose the number of parameters
                    item["params"] = st.radio("Number of Parameters", [1, 2, "more"],
                                              index=[1, 2, "more"].index(item["params"]),
                                              key=f"params_{id}",
                                              on_change=update_chart_state,
                                              args=(id, "params", f"params_{id}")
                                              )

                    # Then choose the type of graph
                    if item["params"] == 1:
                        try:
                            item["type"] = st.selectbox("Chart Type (1 Param)", ["Boxplot", "Histogram", "KDE"],
                                                        index=["Boxplot", "Histogram", "KDE"].index(item["type"]),
                                                        key=f"type_1_{id}",
                                                        on_change=update_chart_state,
                                                        args=(id, "type", f"type_1_{id}")
                                                        )
                        except ValueError as err:
                            # There is a possible scenario when user changes the number of params, and the
                            # ValueError in the "index" param arises, as the graph types are different for
                            # 1 and 2-parameter graphs (or with even bigger amount of params)
                            item["type"] = st.selectbox("Chart Type (1 Param)", ["Boxplot", "Histogram", "KDE"],
                                                        index=0,  # In such a case we just use "any"
                                                        key=f"type_1_{id}",
                                                        on_change=update_chart_state,
                                                        args=(id, "type", f"type_1_{id}")
                                                        )

                        # Then choose X-axis parameter
                        if item["type"] == "Histogram":
                            # For Histogram any parameter can be used
                            item["x"] = st.selectbox("X-axis", df.columns, index=list(df.columns).index(item["x"]),
                                                     key=f"x_{id}",
                                                     on_change=update_chart_state,
                                                     args=(id, "x", f"x_{id}")
                                                     )
                        else:
                            # However, for boxplots and KDEs only numerical parameters are accepted
                            item["x"] = st.selectbox("X-axis", NUMERICAL_COLUMNS,
                                                     index=NUMERICAL_COLUMNS.index(item["x"]),
                                                     key=f"x_{id}",
                                                     on_change=update_chart_state,
                                                     args=(id, "x", f"x_{id}")
                                                     )


                    elif item["params"] == 2:
                        try:
                            item["type"] = st.selectbox("Chart Type (2 Param)", ["Scatter", "Line", "Bar"],
                                                        index=["Scatter", "Line", "Bar"].index(item["type"]),
                                                        key=f"type_{id}",
                                                        on_change=update_chart_state,
                                                        args=(id, "type", f"type_{id}")
                                                        )
                        except ValueError as err:
                            # There is a possible scenario when user changes the number of params, and the
                            # ValueError in the "index" param arises, as the graph types are different for
                            # 1 and 2-parameter graphs (or with even bigger amount of params)
                            item["type"] = st.selectbox("Chart Type", ["Scatter", "Line", "Bar"],
                                                        index=0,  # In such a case we just use "any"
                                                        key=f"type_{id}",
                                                        on_change=update_chart_state,
                                                        args=(id, "type", f"type_{id}")
                                                        )

                        # Then choose X-axis parameter

                        item["x"] = st.selectbox("X-axis", df.columns, index=list(df.columns).index(item["x"]),
                                                 key=f"x_{id}",
                                                 on_change=update_chart_state,
                                                 args=(id, "x", f"x_{id}")
                                                 )

                        # And choose Y-axis parameter
                        item["y"] = st.selectbox("Y-axis", df.columns, index=list(df.columns).index(item["y"]),
                                                 key=f"y_{id}",
                                                 on_change=update_chart_state,
                                                 args=(id, "y", f"y_{id}")
                                                 )

                    else:
                        # If the option "more" is chosen
                        try:

                            item["type"] = st.selectbox("Chart Type (3 or more params)",
                                                        LIST_GRAPHS_3_OR_MORE_VAR,
                                                        index=LIST_GRAPHS_3_OR_MORE_VAR.index(item["type"]),
                                                        key=f"type_{id}",
                                                        on_change=update_chart_state,
                                                        args=(id, "type", f"type_{id}")
                                                        )
                        except ValueError as err:
                            # There is a possible scenario when user changes the number of params, and the
                            # ValueError in the "index" param arises, as the graph types are different for
                            # 1 and 2-parameter graphs
                            item["type"] = st.selectbox("Chart Type", LIST_GRAPHS_3_OR_MORE_VAR,
                                                        index=0,  # In such a case we just use "any"
                                                        key=f"type_{id}",
                                                        on_change=update_chart_state,
                                                        args=(id, "type", f"type_{id}")
                                                        )

                        if item["type"] == "Correlation Heatmap":
                            pass  # Nothing needed to do

                        elif item["type"] == "Pairplot":
                            pass  # Nothing needed to do

                        elif item["type"] == "3D Scatter":

                            # Choose X-axis parameter
                            item["x"] = st.selectbox("X-axis", df.columns, index=list(df.columns).index(item["x"]),
                                                     key=f"x_{id}")
                            # Choose Y-axis parameter
                            item["y"] = st.selectbox("Y-axis", df.columns, index=list(df.columns).index(item["y"]),
                                                     key=f"y_{id}")
                            # Choose Y-axis parameter
                            item["z"] = st.selectbox("Z-axis", df.columns, index=list(df.columns).index(item["z"]),
                                                     key=f"z_{id}")


                        elif item["type"] == "Parallel Coordinates":
                            pass  # TODO!!!!!

                        elif item["type"] == "Pivot Table Heatmap":
                            pass  # TODO!!!
                            # pivot_data = df.pivot_table(
                            #     values=chart_params["value_column"],
                            #     index=chart_params["row_column"],
                            #     columns=chart_params["column_column"],
                            #     aggfunc='mean'
                            # )
                            # sns.heatmap(pivot_data, annot=True, cmap="viridis")
                        elif item["type"] == "Missing Data Heatmap":
                            pass

                # Now, after the editing the params, render the graph in the placeholder
                with placeholder:
                    render_chart(item)

            else:  # If we have a md box

                if st.button("\U0001F58B\ufe0f Edit"):
                    st.session_state.p2_items[id]["mode"] = "edit"

                if item["mode"] == "view":
                    # Just show the text if we want to just watch it
                    st.markdown(item["text"])
                else:
                    # Show the editable field
                    input_text = st.text_area("Markdown Input", item["text"],
                                              key=f"editor_{id}",
                                              on_change=enable_editing_mode)
                    # print(input_text)
                    # print(st.session_state.p2_editing_mode)
                    if st.session_state.p2_editing_mode:
                        print("f is true")
                        st.session_state.p2_items[id]["text"] = input_text
                        st.session_state.p2_editing_mode = False
                        disable_edit_mode_in_md_boxes()
                        st.rerun()

        # Draw arrows on the right
        with arrows:
            # Make a little gap from above
            # for _ in range(13):
            #     st.write("")

            # Moves the graph up in the list
            if st.button("⬆️", key=f"up_{id}") and id > 0:
                st.session_state.p2_items[id], st.session_state.p2_items[id - 1] = st.session_state.p2_items[id - 1], \
                    st.session_state.p2_items[id]
                st.rerun()

            # Moves the graph down in the list
            if st.button("⬇️", key=f"down_{id}") and id < len(st.session_state.p2_items) - 1:
                st.session_state.p2_items[id], st.session_state.p2_items[id + 1] = st.session_state.p2_items[id + 1], \
                    st.session_state.p2_items[id]
                st.rerun()

        # The bottom of Container
        col1, col2, col3 = st.columns([2, 2, 2])  # The ratio 2:2:2 so that the buttons look good
        with col1:
            # Deletes the graph
            if st.button("❌ Delete Chart", key=f"delete_{id}"):
                st.session_state.p2_items.pop(id)
                st.rerun()
        with col2:
            # Creates a new sample graph below
            if st.button("➕ Add New Chart Below", key=f"add_chart_{id}"):
                generate_sample_graph()
                st.rerun()
        with col3:
            if st.button("➕ Add New MD Text Below", key=f"add_md_{id}"):
                generate_sample_md_container()
                st.rerun()

# De-comment for debugging
# st.write(st.session_state.p2_items)
