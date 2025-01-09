import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from helpers import initialize_global_session_variables_if_not_yet, NUMERICAL_COLUMNS, create_quantitative_dataset
from DashboardManager import *
import os

PAGE_NUMBER = os.path.basename(__file__).split("_")[0]  # The number in front of the filename


# TODO: fix the problem with re-rendering heavy charts if they are not edited or created in the first time

# Functions to handle changes for each input element
def update_chart_state(item_id: int, what_to_update: str, changed_field_key: str) -> None:
    # print("error here:", item_id, what_to_update, changed_field_key, manager.items, st.session_state)
    # print("Before update:", manager.items, st.session_state[changed_field_key])

    if what_to_update == "chart_type":
        manager.items[item_id][what_to_update] = ChartTypes.from_string(st.session_state[changed_field_key])
    else:
        manager.items[item_id][what_to_update] = st.session_state[changed_field_key]
    # print("After update:", manager.items)
    # st.session_state.p2_items[graph_id][what_to_update] = st.session_state[changed_field_key]


def create_some_item(item_type, *args, **kwargs):
    manager.create_item(item_type, *args, **kwargs)


# In case this page was the first to be load by the user in the whole application,
# this will initialize them; and do nothing in the opposite case
initialize_global_session_variables_if_not_yet()

df = st.session_state.df

manager = DashboardManager(PAGE_NUMBER)

# If we do not have any items to show, let the user create the first one
if manager.is_empty():
    # print("Manager is empty", id(manager))
    st.button(
        "➕ Add First Chart",
        key=f"add_first_chart",
        on_click=create_some_item,
        args=[DashboardItemTypes.CHART],  # Needed to be passes for any item we create
        kwargs={"on_change_function": update_chart_state, "df": df}  # Pass item-specific parameters(except item id)
    )
    if st.button("Add First Text", key=f"add_first_md_box"):
        manager.create_item(DashboardItemTypes.MD_BOX, )  # TODO!!

# print(list(*manager.get_items().items()))
# Render all the items(graphs or MD-boxes) that we have
for item_id, item in manager.get_items():

    # Declare the types for IDE
    item_id: int
    item: DashboardItem

    # Each item interface is inside the container
    with st.container(border=True):

        # Split the container to 2 parts - left & right in a ratio of 15 to 1
        main, arrows = st.columns([15, 1])

        with main:
            if item.get_type() == DashboardItemTypes.CHART:

                item: ChartItem  # Declare for IDE that item is ChartItem

                item.render(item_id)

            else:  # If we have a md box
                st.write("Still in development!")
                st.write(manager.items[0].get_type(), manager.items[0].__dict__)

                break

                if st.button("\U0001F58B\ufe0f Edit", key=f"md_edit_{item_id}"):
                    st.session_state.p2_items[item_id]["mode"] = "edit"

                if item["mode"] == "view":
                    # Just show the text if we want to just watch it
                    st.markdown(item["text"])
                else:
                    # Show the editable field
                    input_text = st.text_area("Markdown Input", item["text"],
                                              key=f"editor_{item_id}",
                                              on_change=enable_editing_mode)
                    # print(input_text)
                    # print(st.session_state.p2_editing_mode)
                    if st.session_state.p2_editing_mode:
                        # print("f is true")
                        st.session_state.p2_items[item_id]["text"] = input_text
                        st.session_state.p2_editing_mode = False
                        disable_edit_mode_in_md_boxes()
                        st.rerun()

        # Draw arrows on the right
        with arrows:
            # Make a little gap from above
            # for _ in range(13):
            #     st.write("")

            # Moves the item up in the list
            if st.button("⬆️", key=f"up_{item_id}") and item_id > 0:
                manager.move_item_up(item_id)
                st.rerun()

            # Moves the item down in the list
            if st.button("⬇️", key=f"down_{item_id}") and item_id < len(st.session_state.p2_items) - 1:
                manager.move_item_down(item_id)
                st.rerun()

        # The bottom of Container
        col1, col2, col3 = st.columns([2, 2, 2])  # The ratio 2:2:2 so that the buttons look good
        with col1:
            # Deletes the graph
            if st.button("❌ Delete Block", key=f"delete_{item_id}"):
                manager.remove_item(item_id)
                st.rerun()
        with col2:
            # Creates a new sample graph below
            st.button(
                "➕ Add New Chart Below",
                key=f"add_chart_{item_id}",
                on_click=create_some_item,
                args=[DashboardItemTypes.CHART],
                kwargs={"on_change_function": update_chart_state, "df": df}
            )
            # create_some_item(DashboardItemTypes.CHART, on_change_function=update_chart_state, df=df)

        with col3:
            if st.button("➕ Add New MD Text Below", key=f"add_md_{item_id}"):
                generate_sample_md_container()
                st.rerun()

# De-comment for debugging
st.write(str(manager))
