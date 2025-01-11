import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from helpers import initialize_global_session_variables_if_not_yet, NUMERICAL_COLUMNS, create_quantitative_dataset
from DashboardManager import *
import os

PAGE_NUMBER = os.path.basename(__file__).split("_")[0]  # The number in front of the filename


# TODO: fix the problem with re-rendering heavy charts if they are not edited or created in the first time

# Functions to handle changes for each input element
def update_item_state(item_id: int, what_to_update: str, changed_field_key: str) -> None:
    # print("error here:", item_id, what_to_update, changed_field_key, manager.items, st.session_state)
    # print("Before update:", manager.items, st.session_state[changed_field_key])

    if what_to_update == "chart_type":
        manager.items[item_id][what_to_update] = ChartTypes.from_string(st.session_state[changed_field_key])
    else:
        manager.items[item_id][what_to_update] = st.session_state[changed_field_key]
    # print("After update:", manager.items)


def create_some_item(item_type, item_pos, *args, **kwargs):
    # print("create_some_item")
    manager.create_item(item_type, item_pos, *args, **kwargs)


# In case this page was the first to be load by the user in the whole application,
# this will initialize them; and do nothing in the opposite case
initialize_global_session_variables_if_not_yet()

# Get some variables from session_state
df = st.session_state.df
manager = DashboardManager(PAGE_NUMBER)

# If we do not have any items to show, let the user create the first one
if manager.is_empty():
    # print("Manager is empty", id(manager))
    col1, col2, _ = st.columns([1, 1, 2])
    col1.button(
        "➕ **Add First Chart**",
        key=f"add_first_chart",
        on_click=create_some_item,
        args=(DashboardItemTypes.CHART, 0),  # Needed to be passes for any item we create
        kwargs={"on_change_function": update_item_state, "df": df}  # Pass item-specific parameters(except item id)
    )

    col2.button(
        "➕ **Add First Text**",
        key=f"add_first_md_box",
        on_click=create_some_item,
        args=(DashboardItemTypes.MD_BOX, 0),
        kwargs={"on_change_function": update_item_state}
    )


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
                args=(DashboardItemTypes.CHART, item_id),
                kwargs={"on_change_function": update_item_state, "df": df}
            )

        with col3:
            # Creates a sample MD Box below
            st.button(
                "➕ **Add New Text Below**",
                key=f"add_md_text_below_{item_id}",
                on_click=create_some_item,
                args=(DashboardItemTypes.MD_BOX, item_id),
                kwargs={"on_change_function": update_item_state}
            )

if st.sidebar.button("Save current page state"):
    manager.save_to_json("beginner_level_data.json")

if st.sidebar.button("Load page from json"):
    manager.load_from_json(update_item_state, df, "beginner_level_data.json")

# De-comment for debugging
# st.write(str(manager))
