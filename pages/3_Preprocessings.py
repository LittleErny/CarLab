import os
import streamlit as st

from DashboardManager.ChartItem import ChartItem
from DashboardManager.DashboardItem import DashboardItem
from DashboardManager.DashboardManagerEnums import ChartTypes, DashboardItemTypes, PreprocessingTypes
from DashboardManager.MDBoxItem import MDBoxItem
from DashboardManager.DashboardManager import DashboardManager
from helpers import initialize_global_session_variables_if_not_yet, NUMERICAL_COLUMNS, execute_preprocessing_action

PAGE_NUMBER = os.path.basename(__file__).split("_")[0]  # The number in front of the filename
PREPROCESSING_OPTIONS = [PreprocessingTypes.OUTLIER_REMOVAL, PreprocessingTypes.LABEL_ENCODING,
                         PreprocessingTypes.SCALING, PreprocessingTypes.REMOVING_UNNEC_COLUMN]

st.set_page_config(page_title="CarLab Preprocessing", page_icon="✏️")


# Functions to handle changes for each input element
def update_item_state(item_id: int, what_to_update: str, changed_field_key: str) -> None:
    if what_to_update == "chart_type":
        manager.items[item_id][what_to_update] = ChartTypes.from_string(st.session_state[changed_field_key])
    elif what_to_update == "preprocessing_type":
        manager.items[item_id][what_to_update] = PreprocessingTypes.from_string(st.session_state[changed_field_key])
    else:
        manager.items[item_id][what_to_update] = st.session_state[changed_field_key]


def update_item_state_in_preproc_manager(item_id: int, what_to_update: str, changed_field_key: str) -> None:
    if what_to_update == "chart_type":
        preproc_manager.items[item_id][what_to_update] = ChartTypes.from_string(st.session_state[changed_field_key])
    elif what_to_update == "preprocessing_type":
        preproc_manager.items[item_id][what_to_update] = PreprocessingTypes.from_string(
            st.session_state[changed_field_key])
    else:
        preproc_manager.items[item_id][what_to_update] = st.session_state[changed_field_key]


def create_some_item(item_type: DashboardItemTypes, manager: DashboardManager, item_pos: int, *args, **kwargs):
    manager.create_item(item_type, item_pos, *args, **kwargs)


def reload_charts():
    # Assuming charts are only in the 2nd manager:
    manager.reload_items(update_item_state, st.session_state.df2)


def render_sidebar_preprocessing_config_bar():
    global df

    st.sidebar.button("🔄 Update Charts",
                      on_click=reload_charts)

    # Uncomment this to be able to edit saved manager states
    # st.sidebar.write("- - -")
    #
    # if st.sidebar.button("Save current page state"):
    #     preproc_manager.save_to_json("dashboard_manager_saves/beginner_level_data_page_3_1.json")
    #     manager.save_to_json("dashboard_manager_saves/beginner_level_data_page_3_2.json")
    #
    # if st.sidebar.button("Load page from json"):
    #     preproc_manager.load_from_json(update_item_state_in_preproc_manager,
    #                                    df,
    #                                    "dashboard_manager_saves/beginner_level_data_page_3_1.json",
    #                                    skip_rerun=True  # as we need to load one more manager
    #                                    )
    #
    #     manager.load_from_json(update_item_state,
    #                            df,
    #                            "dashboard_manager_saves/beginner_level_data_page_3_2.json")
    #
    # st.sidebar.write("- - -")

    st.sidebar.selectbox(
        "Please select the type of Preprocessing action:", PREPROCESSING_OPTIONS,
        format_func=lambda x: x.value,
        key="p3_preproc_type", index=PREPROCESSING_OPTIONS.index(st.session_state["p3_preproc_type"]),
    )
    selected_type = st.session_state['p3_preproc_type']
    # st.sidebar.write(selected_type)

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

        if st.sidebar.button("Apply", key="apply_preproc_action"):
            execute_preprocessing_action(
                action_type=PreprocessingTypes.OUTLIER_REMOVAL,
                df=df,
                manager=preproc_manager,
                column=selected_column,
                method=selected_method,
                threshold=selected_threshold
            )

    elif selected_type == PreprocessingTypes.LABEL_ENCODING:
        st.sidebar.selectbox("Select column to encode", st.session_state.categorical_columns,
                             key="p3_preprocessing_column")
        selected_column = st.session_state["p3_preprocessing_column"]

        if st.sidebar.button("Apply", key="apply_preproc_action"):
            execute_preprocessing_action(
                action_type=PreprocessingTypes.LABEL_ENCODING,
                manager=preproc_manager,
                df=df,
                column=selected_column
            )

    elif selected_type == PreprocessingTypes.SCALING:
        st.sidebar.selectbox("Select column", NUMERICAL_COLUMNS, key="p3_preprocessing_column")
        selected_column = st.session_state["p3_preprocessing_column"]

        st.sidebar.selectbox("Select scaling method", ["Min-Max Scaling", "Standard Scaling"],
                             key="p3_scaling_method")
        selected_scaling_method = st.session_state["p3_scaling_method"]

        if st.sidebar.button("Apply", key="apply_preproc_action"):
            execute_preprocessing_action(
                action_type=PreprocessingTypes.SCALING,
                manager=preproc_manager,
                df=df,
                column=selected_column,
                scaling_method=selected_scaling_method
            )

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

if not st.session_state.hardcore_mode and not st.session_state.page_3_was_ever_rendered:
    st.session_state.page_3_was_ever_rendered = True

    preproc_manager.load_from_json(update_item_state_in_preproc_manager, df,
                                   "dashboard_manager_saves/beginner_level_data_page_3_1.json",
                                   skip_rerun=True)

    manager.load_from_json(update_item_state, df,
                           "dashboard_manager_saves/beginner_level_data_page_3_2.json",
                           skip_rerun=True)

render_sidebar_preprocessing_config_bar()

# If we do not have any items to show, let the user create the first one
st.write("# Preprocessing Tool")

with st.expander("Brief Instructions", expanded=False):
    st.markdown("""
### How works this page?

This page is very similar to the previous one, however has some differences. The page is split into the 2 parts - 
Executing preprocessing actions, and Visualizing the result of preprocessing actions. So, it means that you first should
execute all the preprocessing actions, and only then try to visualize them. 

Note: Here and further the copy of initial dataset is used. You will not see any changes in Parameters Visualisation 
page. 

Note: The same dataset is used on this and Faker page. So, for example, if you create 1000 fake rows on the Faker page
and press `🔄 Update Charts` button, it will have impact on the graphs on this page also. 
So I recommend applying Scaling only after you create additional Fake Data and study it sufficiently.

Note: In current version there is no way to discard particular preprocessing action or mix their order 
after they were executed. So please make sure to do it in the correct order.
""")

with st.expander("Brief theory", expanded=False):
    st.markdown("""### Data Preprocessing Overview

#### Outliers Removal
Outliers are data points that differ significantly from other observations in the dataset. Removing or handling outliers can:

- Enhance visualization and interpretation of data.
- Improve the accuracy of machine learning models.
- Prevent bias in statistical analyses.

#### Label Encoding
Label Encoding is the process of converting categorical variables into numerical values. It is useful for preparing data for machine learning models that require numerical inputs.

#### Scaling
Scaling is the process of normalizing or standardizing numerical features. It ensures that all features contribute equally to the model and avoids bias caused by differing feature magnitudes.
""")

st.write("## Preprocessing History")

# Generate the upper part of the page
if preproc_manager.is_empty():
    st.write("*No preprocessing actions to show.*")
    st.write("*In order to initiate a new preprocessing action, have a look at the sidebar from the left.*")
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
st.write("## Post-Preprocessing Data Visualisation")

# If we do not have any items to show, let the user create the first one
if manager.is_empty():
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
