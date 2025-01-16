import os
import weakref

import streamlit as st

from DashboardManager.ChartItem import ChartItem
from DashboardManager.DashboardItem import DashboardItem
from DashboardManager.DashboardManagerEnums import ChartTypes, DashboardItemTypes, PreprocessingTypes
from DashboardManager.MDBoxItem import MDBoxItem
from DashboardManager.DashboardManager import DashboardManager
from helpers import initialize_global_session_variables_if_not_yet, NUMERICAL_COLUMNS

PAGE_NUMBER = os.path.basename(__file__).split("_")[0]  # The number in front of the filename
PREPROCESSING_OPTIONS = [PreprocessingTypes.OUTLIER_REMOVAL, PreprocessingTypes.LABEL_ENCODING,
                         PreprocessingTypes.SCALING, PreprocessingTypes.REMOVING_UNNEC_COLUMN]


# TODO: fix the problem with re-rendering heavy charts if they are not edited or created in the first time

# Functions to handle changes for each input element
def update_item_state(item_id: int, what_to_update: str, changed_field_key: str) -> None:
    # print("error here:", item_id, what_to_update, changed_field_key, manager.items, st.session_state)
    # print("Before update:", manager.items, st.session_state[changed_field_key])

    if what_to_update == "chart_type":
        manager.items[item_id][what_to_update] = ChartTypes.from_string(st.session_state[changed_field_key])
    elif what_to_update == "preprocessing_type":
        manager.items[item_id][what_to_update] = PreprocessingTypes.from_string(st.session_state[changed_field_key])
    else:
        manager.items[item_id][what_to_update] = st.session_state[changed_field_key]


def update_item_state_in_preproc_manager(item_id: int, what_to_update: str, changed_field_key: str) -> None:
    # print("error here:", item_id, what_to_update, changed_field_key, manager.items, st.session_state)
    # print("Before update:", manager.items, st.session_state[changed_field_key])

    if what_to_update == "chart_type":
        preproc_manager.items[item_id][what_to_update] = ChartTypes.from_string(st.session_state[changed_field_key])
    elif what_to_update == "preprocessing_type":
        preproc_manager.items[item_id][what_to_update] = PreprocessingTypes.from_string(
            st.session_state[changed_field_key])
    else:
        preproc_manager.items[item_id][what_to_update] = st.session_state[changed_field_key]


def create_some_item(item_type: DashboardItemTypes, manager: DashboardManager, item_pos: int, *args, **kwargs):
    # print("create_some_item")
    # if "df" in kwargs:
    #     print("create_some_item", weakref.ref(kwargs["df"]))
    manager.create_item(item_type, item_pos, *args, **kwargs)


def render_sidebar_preprocessing_config_bar():
    def remove_outliers(column, method, threshold):

        global df
        if method == 'top':
            # print("remove_outliers1", id(df), len(df), threshold)
            df.drop(df[df[column] > df[column].quantile(1 - threshold / 100)].index, inplace=True)
            # print("remove_outliers2", id(df), len(df))
        elif method == 'bottom':
            df.drop(df[df[column] < df[column].quantile(threshold / 100)].index, inplace=True)
        elif method == 'both':
            lower_bound = df[column].quantile(threshold / 100)
            upper_bound = df[column].quantile(1 - threshold / 100)
            # Удаление значений вне диапазона (нижний и верхний порог)
            df.drop(df[(df[column] < lower_bound) | (df[column] > upper_bound)].index, inplace=True)
        else:
            raise ValueError()

    global df
    # print("render_sidebar_preprocessing_config_bar:", id(df))

    st.sidebar.selectbox(
        "Please select the type of Preprocessing action:", PREPROCESSING_OPTIONS,
        format_func=lambda x: x.value,
        key="p3_preproc_type", index=PREPROCESSING_OPTIONS.index(st.session_state["p3_preproc_type"]),
    )
    selected_type = st.session_state['p3_preproc_type']
    st.sidebar.write(selected_type)

    if selected_type == PreprocessingTypes.OUTLIER_REMOVAL:
        st.sidebar.selectbox("Select column", NUMERICAL_COLUMNS, key="p3_preprocessing_column")
        selected_column = st.session_state["p3_preprocessing_column"]

        st.sidebar.selectbox("Select method", ["top", "bottom", "both"], key="p3_outlier_method")
        selected_method = st.session_state["p3_outlier_method"]

        st.sidebar.slider("Threshold (in %)", min_value=0.25, max_value=25.0, value=5.0, step=0.25,
                          key="p3_outlier_threshold")
        selected_threshold = st.session_state["p3_outlier_threshold"]
        st.sidebar.write(
            f"So, {int(len(df) * float(selected_threshold) * 0.01)} of {selected_method} lines will be removed")

        # Apply button
        if st.sidebar.button("Apply", key="apply_preproc_action"):
            action = {
                "column": selected_column,
                "method": selected_method,
                "threshold": selected_threshold
            }
            preproc_manager.create_item(item_pos=len(preproc_manager.items),
                                        item_type=DashboardItemTypes.PREPROCESSING_BOX,
                                        action=action,
                                        preproc_type=PreprocessingTypes.OUTLIER_REMOVAL)
            # print("calling remove_outliers", len(df))
            remove_outliers(selected_column, selected_method, selected_threshold)
            # print("remove_outliers was called", len(df))
            # st.session_state.df2  # Update the editable version of df

    elif selected_type == PreprocessingTypes.LABEL_ENCODING:
        st.sidebar.selectbox("Select column to encode", st.session_state.categorical_columns,
                             key="p3_preprocessing_column")
        selected_column = st.session_state["p3_preprocessing_column"]

        if st.sidebar.button("Apply", key="apply_preproc_action"):
            encoded_mapping = dict(enumerate(df[selected_column].astype('category').cat.categories))
            st.session_state.df2[selected_column] = st.session_state.df2[selected_column].astype('category').cat.codes
            # df[selected_column] = df[selected_column].astype('category').cat.codes
            action = {
                "column": selected_column,
                "action": "label_encoding",
                "mapping": encoded_mapping
            }
            preproc_manager.create_item(item_pos=len(preproc_manager.items),  # add on the end of the list
                                        item_type=DashboardItemTypes.PREPROCESSING_BOX,
                                        action=action,
                                        preproc_type=PreprocessingTypes.LABEL_ENCODING)

    elif selected_type == PreprocessingTypes.SCALING:
        st.sidebar.selectbox("Select column", NUMERICAL_COLUMNS, key="p3_preprocessing_column")
        selected_column = st.session_state["p3_preprocessing_column"]

        st.sidebar.selectbox("Select scaling method", ["Min-Max Scaling", "Standard Scaling"],
                             key="p3_scaling_method")

        scaling_method = st.session_state["p3_scaling_method"]

        if st.sidebar.button("Apply", key="apply_preproc_action"):
            if scaling_method == "Min-Max Scaling":
                df[selected_column] = ((df[selected_column] - df[selected_column].min()) /
                                       (df[selected_column].max() - df[selected_column].min()))
            elif scaling_method == "Standard Scaling":
                df[selected_column] = (df[selected_column] - df[selected_column].mean()) / df[selected_column].std()

            else:
                raise ValueError(f"Unknown scaling_method while applying scaling: got: {scaling_method}")

            action = {
                "column": selected_column,
                "action": "scaling",
                "scaling_method": scaling_method
            }

            preproc_manager.create_item(item_pos=len(preproc_manager.items),  # add on the end of the list
                                        item_type=DashboardItemTypes.PREPROCESSING_BOX,
                                        action=action,
                                        preproc_type=PreprocessingTypes.SCALING)

    elif selected_type == PreprocessingTypes.REMOVING_UNNEC_COLUMN:
        pass


# In case this page was the first to be load by the user in the whole application,
# this will initialize them; and do nothing in the opposite case
initialize_global_session_variables_if_not_yet()
# Initiate local session state variables for some items in the sidebar
if "p3_preproc_type" not in st.session_state:
    st.session_state.p3_preproc_type = PREPROCESSING_OPTIONS[0]

# Get some variables from session_state
df = st.session_state.df2  # The 2nd version that can (and should) be updated

# Manager for showing preprocessing history & MD-Boxes
preproc_manager = DashboardManager(PAGE_NUMBER + ".5")

# And manager for showing the Graphs & MD-Boxes
manager = DashboardManager(PAGE_NUMBER)

render_sidebar_preprocessing_config_bar()

# print("Main:", weakref.ref(st.session_state.df2), len(st.session_state.df2))
# If we do not have any items to show, let the user create the first one
st.write("## Preprocessing History")
st.write("Here you can see all the preprocessing actions that were executed.")
st.write("In order to initiate a new preprocessing action, have a look at the sidebar from the left.")

# Generate the upper part of the page
if preproc_manager.is_empty():
    st.write("*No preprocessing actions to show.*")
    st.button(
        "➕ **Add New Text Below**",
        key=f"add_preproc_md_text_below_{0}",
        on_click=create_some_item,
        args=(DashboardItemTypes.MD_BOX, preproc_manager, 0),
        kwargs={"on_change_function": update_item_state_in_preproc_manager}
    )

else:
    for item_id, item in preproc_manager.items.items():
        # Declare the types for IDE
        item_id: int
        item: DashboardItem  # In reality, it is actually always PreprocessingItem or MDBoxItem

        # Each item interface is inside the container
        with st.container(border=True):

            main, arrows = st.columns([15, 1], vertical_alignment="center")
            with main:
                # Render the content
                item.render(item_id)

            with arrows:
                # Moves the item up in the list
                if st.button("⬆️", key=f"preproc_up_{item_id}"):
                    # We are not allowed to swap two preprocessing actions
                    next_item_from_above_id = preproc_manager.find_next_item_from_above(item_id)
                    if (next_item_from_above_id != -1 and preproc_manager.items[item_id].get_type()
                            == preproc_manager.items[next_item_from_above_id].get_type()
                            == DashboardItemTypes.PREPROCESSING_BOX):

                        st.toast('You are not allowed to mix Preprocessing Actions', icon='⚠️')
                    else:
                        preproc_manager.move_item_up(item_id)
                        st.rerun()

                # Moves the item down in the list
                if st.button("⬇️", key=f"preproc_down_{item_id}"):
                    # We are not allowed to swap two preprocessing actions
                    next_item_from_below_id = preproc_manager.find_next_item_from_below(item_id)
                    if (next_item_from_below_id != -1 and preproc_manager.items[item_id].get_type()
                            == preproc_manager.items[next_item_from_below_id].get_type()
                            == DashboardItemTypes.PREPROCESSING_BOX):

                        st.toast('You are not allowed to mix Preprocessing Actions', icon='⚠️')
                    else:
                        preproc_manager.move_item_down(item_id)
                        st.rerun()
            # with main:
            # The bottom of Container
            if item.get_type() == DashboardItemTypes.MD_BOX:
                # If so, we can both delete it and create new MD Box below
                col1, _, col2 = st.columns([2, 2, 2])

                if col1.button("❌ **Delete Block**", key=f"preproc_delete_{item_id}"):
                    preproc_manager.remove_item(item_id)
                    st.rerun()

                col2.button(
                    "➕ **Add New Text Below**",
                    key=f"add_preproc_md_text_below_{item_id}",
                    on_click=create_some_item,
                    args=(DashboardItemTypes.MD_BOX, preproc_manager, item_id),
                    kwargs={"on_change_function": update_item_state_in_preproc_manager}
                )
            elif item.get_type() == DashboardItemTypes.PREPROCESSING_BOX:
                # If so, we cannot delete this item(the preprocessing actions are irreversible
                _, _, col = st.columns([2, 2, 2])

                col.button(
                    "➕ **Add New Text Below**",
                    key=f"add_preproc_md_text_below_{item_id}",
                    on_click=create_some_item,
                    args=(DashboardItemTypes.MD_BOX, preproc_manager, item_id),
                    kwargs={"on_change_function": update_item_state_in_preproc_manager}
                )
            else:
                raise ValueError(f"Unknown item type while attempting to render bottom buttons. Got: {item.get_type()}")

# Divide the page on 2 parts - the upper is for preprocessing logging, the lower for graphs
# However, MDBoxes are accepted in both parts
st.write("- - -")

# If we do not have any items to show, let the user create the first one
if manager.is_empty():
    # print("Manager is empty", id(manager))
    col1, col2, _ = st.columns([1, 1, 2])
    col1.button(
        "➕ **Add First Chart**",
        key=f"add_first_chart",
        on_click=create_some_item,
        args=(DashboardItemTypes.CHART, manager, 0),  # Needed to be passes for any item we create
        kwargs={"on_change_function": update_item_state, "df": df}  # Pass item-specific parameters(except item id)
    )

    col2.button(
        "➕ **Add First Text**",
        key=f"add_first_md_box",
        on_click=create_some_item,
        args=(DashboardItemTypes.MD_BOX, manager, 0),
        kwargs={"on_change_function": update_item_state}
    )

# Render the second part of the page - visualisations after preprocessing actions
# Render all the items(graphs or MD-boxes) that we have
for item_id, item in manager.items.items():

    # Declare the types for IDE
    item_id: int
    item: DashboardItem

    # Each item interface is inside the container
    with st.container(border=True):

        # Split the container to 2 parts - left & right in a ratio of 15 to 1
        main, arrows = st.columns([15, 1], vertical_alignment="center")

        # Main container(column) is used for main item content
        with main:
            if item.get_type() == DashboardItemTypes.CHART:

                item: ChartItem  # Declare for IDE that item is ChartItem

                item.render(item_id)

            elif item.get_type() == DashboardItemTypes.MD_BOX:  # If we have a md box

                item: MDBoxItem  # Declare for IDE that item is MDBoxItem

                item.render(item_id)

            else:
                raise ValueError(f"Unknown Item Type while attempting to render page {PAGE_NUMBER}: {item.get_type()}")
                # st.write(manager.items[0].get_type(), manager.items[0].__dict__)
                # break

        # Draw arrows on the right
        with arrows:
            # Make a little gap from above
            # for _ in range(13):
            #     st.write("")

            # Moves the item up in the list
            if st.button("⬆️", key=f"up_{item_id}"):
                manager.move_item_up(item_id)
                st.rerun()

            # Moves the item down in the list
            if st.button("⬇️", key=f"down_{item_id}"):
                manager.move_item_down(item_id)
                st.rerun()

        # The bottom of Container
        col1, col2, col3 = st.columns([2, 2, 2])  # The ratio 2:2:2 so that the buttons look good
        with col1:
            # Deletes the graph
            if st.button("❌ **Delete Block**", key=f"delete_{item_id}"):
                manager.remove_item(item_id)
                st.rerun()
        with col2:
            # Creates a new sample graph below
            st.button(
                "➕ **Add New Chart Below**",
                key=f"add_chart_{item_id}",
                on_click=create_some_item,
                args=(DashboardItemTypes.CHART, manager, item_id),
                kwargs={"on_change_function": update_item_state, "df": df}
            )

        with col3:
            # Creates a sample MD Box below
            st.button(
                "➕ **Add New Text Below**",
                key=f"add_md_text_below_{item_id}",
                on_click=create_some_item,
                args=(DashboardItemTypes.MD_BOX, manager, item_id),
                kwargs={"on_change_function": update_item_state}
            )
