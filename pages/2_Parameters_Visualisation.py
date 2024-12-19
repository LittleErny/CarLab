import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from helpers import initialize_session_variables_if_not_yet, NUMERICAL_COLUMNS


# TODO: Automatically generate the names of the graphs(LLM?..)

# Whenever we need to create a new graph, this sample is created and s
def generate_sample_graph():
    id = st.session_state.p2_chart_counter
    sample_graph = {
        "id": id,
        "container_type": "graph",
        "title": f"Chart {st.session_state.p2_chart_counter + 1}",
        "type": "Scatter",
        "x": df.columns[0],
        "y": df.columns[1],
        "params": 1
    }
    st.session_state.p2_charts.insert(id + 1, sample_graph)
    st.session_state.p2_chart_counter += 1


def generate_sample_md_container():
    id = st.session_state.p2_chart_counter
    sample_md_box = {
        "id": id,
        "container_type": "md",
        "mode": "view",
        "text": "You can edit this md text by pressing **edit** button"
    }
    st.session_state.p2_charts.insert(id + 1, sample_md_box)
    st.session_state.p2_chart_counter += 1


def disable_edit_mode_in_md_boxes():
    # Just run through all the boxes and change their mode
    for i, graph in enumerate(st.session_state.p2_charts):
        if graph["container_type"] == "md" and graph["mode"] == "edit":
            st.session_state.p2_charts[i]["mode"] = "view"
    print("disable_edit_mode_in_md_boxes")


def change_editing_mode():
    print("change_editing_mode: now is " + str(-st.session_state.p2_editing_mode))
    st.session_state.p2_editing_mode = True

# In case this page was the first to be load by the user in the whole application,
# this will initialize them; and do nothing in the opposite case
initialize_session_variables_if_not_yet()

# if "charts" not in st.session_state or "chart_counter" not in st.session_state:
#     st.session_state.p2_charts = []
#     st.session_state.p2_chart_counter = 0

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

    else:
        # Choose from graphs with 2 parameters
        if chart_params["type"] == "Scatter":
            sns.scatterplot(data=df, x=chart_params["x"], y=chart_params["y"])
        elif chart_params["type"] == "Line":
            sns.lineplot(data=df, x=chart_params["x"], y=chart_params["y"])
        elif chart_params["type"] == "Bar":
            sns.barplot(data=df, x=chart_params["x"], y=chart_params["y"])
        # TODO: Add boxplots for (categorical+non-categorical)

    # Draw the graph
    st.pyplot(plt)


# If we do not have any charts to show, let the user create the first one
if not st.session_state.p2_charts:
    st.button("➕ Add First Chart", key=f"add_first_chart", on_click=generate_sample_graph)
    st.button("Add First Text", key=f"add_first_md_box", on_click=generate_sample_md_container)


# Render all the graphs that we have
for i, chart in enumerate(st.session_state.p2_charts):

    # Each graph interface is inside the container
    with st.container(border=True):

        # Split the container to 2 parts - left & right in a ratio of 15 to 1
        main, arrows = st.columns([15, 1])

        with main:

            if chart["container_type"] == "graph":
                # Editable title of the chart
                chart["title"] = st.text_input(f"Chart Title", chart["title"], key=f"title_{i}")

                # Placeholder for the graph, as the rendering should take place after the parameters initialization
                placeholder = st.empty()

                # Editing the parameters of the graph
                with st.expander("Edit Chart Parameters"):
                    # Choose the number of parameters
                    chart["params"] = st.radio("Number of Parameters", [1, 2], index=[1, 2].index(chart["params"]),
                                               key=f"params_{i}")

                    # Then choose the type of graph
                    if chart["params"] == 1:
                        try:
                            chart["type"] = st.selectbox("Chart Type (1 Param)", ["Boxplot", "Histogram", "KDE"],
                                                         index=["Boxplot", "Histogram", "KDE"].index(chart["type"]),
                                                         key=f"type_1_{i}")
                        except ValueError as err:
                            # There is a possible scenario when user changes the number of params, and the
                            # ValueError in the "index" param arises, as the graph types are different for
                            # 1 and 2-parameter graphs
                            chart["type"] = st.selectbox("Chart Type (1 Param)", ["Boxplot", "Histogram", "KDE"],
                                                         index=0,  # In such a case we just use "any"
                                                         key=f"type_1_{i}")

                        # Then choose X-axis parameter
                        if chart["type"] == "Histogram":
                            # For Histogram any parameter can be used
                            chart["x"] = st.selectbox("X-axis", df.columns, index=list(df.columns).index(chart["x"]),
                                                      key=f"x_{i}")
                        else:
                            # However, for boxplots and KDEs only numerical parameters are accepted
                            chart["x"] = st.selectbox("X-axis", NUMERICAL_COLUMNS,
                                                      index=NUMERICAL_COLUMNS.index(chart["x"]),
                                                      key=f"x_{i}")


                    else:
                        try:
                            chart["type"] = st.selectbox("Chart Type (2 Param)", ["Scatter", "Line", "Bar"],
                                                         index=["Scatter", "Line", "Bar"].index(chart["type"]),
                                                         key=f"type_{i}")
                        except ValueError as err:
                            # There is a possible scenario when user changes the number of params, and the
                            # ValueError in the "index" param arises, as the graph types are different for
                            # 1 and 2-parameter graphs
                            chart["type"] = st.selectbox("Chart Type", ["Scatter", "Line", "Bar"],
                                                         index=0,  # In such a case we just use "any"
                                                         key=f"type_{i}")

                        # Then choose X-axis parameter

                        chart["x"] = st.selectbox("X-axis", df.columns, index=list(df.columns).index(chart["x"]),
                                                  key=f"x_{i}")

                        # And choose Y-axis parameter
                        chart["y"] = st.selectbox("Y-axis", df.columns, index=list(df.columns).index(chart["y"]),
                                                  key=f"y_{i}")

                # Now, after the editing the params, render the graph in the placeholder
                with placeholder:
                    render_chart(chart)

            else:  # If we have a md box

                if st.button("\U0001F58B\ufe0f Edit"):
                    st.session_state.p2_charts[i]["mode"] = "edit"

                if chart["mode"] == "view":
                    # Just show the text if we want to just watch it
                    st.markdown(chart["text"])
                else:
                    input_text = st.text_area("Markdown Input", chart["text"],
                                              key=f"editor_{i}",
                                              on_change=change_editing_mode)
                    print(input_text)
                    print(st.session_state.p2_editing_mode)
                    if st.session_state.p2_editing_mode:
                        print("f is true")
                        st.session_state.p2_charts[i]["text"] = input_text
                        st.session_state.p2_editing_mode = False
                        disable_edit_mode_in_md_boxes()
                        st.rerun()

                    # print(input_text)
                    # print(st.session_state.p2_charts[i]["text"])
                    # st.session_state.p2_charts[i]["text"] = input_text
                    # print(st.session_state.p2_charts[i]["text"])

        # Draw arrows on the right
        with arrows:
            # Make a little gap from above
            # for _ in range(13):
            #     st.write("")

            # Moves the graph up in the list
            if st.button("⬆️", key=f"up_{i}") and i > 0:
                st.session_state.p2_charts[i], st.session_state.p2_charts[i - 1] = st.session_state.p2_charts[i - 1], \
                    st.session_state.p2_charts[i]
                st.rerun()

            # Moves the graph down in the list
            if st.button("⬇️", key=f"down_{i}") and i < len(st.session_state.p2_charts) - 1:
                st.session_state.p2_charts[i], st.session_state.p2_charts[i + 1] = st.session_state.p2_charts[i + 1], \
                    st.session_state.p2_charts[i]
                st.rerun()

        # The bottom of Container
        col1, col2, col3 = st.columns([2, 2, 2])  # The ratio 2:2:4:1 so that the buttons look good
        with col1:
            # Deletes the graph
            if st.button("❌ Delete Chart", key=f"delete_{i}"):
                st.session_state.p2_charts.pop(i)
                st.rerun()
        with col2:
            # Creates a new sample graph below
            if st.button("➕ Add New Chart Below", key=f"add_chart_{i}"):
                generate_sample_graph()
                st.rerun()
        with col3:
            if st.button("➕ Add New MD Text Below", key=f"add_md_{i}"):
                generate_sample_md_container()
                st.rerun()

# st.write(st.session_state.p2_charts)
