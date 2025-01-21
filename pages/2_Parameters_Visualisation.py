import os
import streamlit as st

from DashboardManager.ChartItem import ChartItem
from DashboardManager.DashboardItem import DashboardItem
from DashboardManager.DashboardManagerEnums import ChartTypes, DashboardItemTypes
from DashboardManager.MDBoxItem import MDBoxItem
from DashboardManager.DashboardManager import DashboardManager
from helpers import initialize_global_session_variables_if_not_yet


# Functions to handle changes for each input element
def update_item_state(item_id: int, what_to_update: str, changed_field_key: str) -> None:
    # print("error here:", item_id, what_to_update, changed_field_key, manager.items, st.session_state)
    # print("Before update:", manager.items, st.session_state[changed_field_key])

    if what_to_update == "chart_type":
        manager.items[item_id][what_to_update] = ChartTypes.from_string(st.session_state[changed_field_key])
    else:
        manager.items[item_id][what_to_update] = st.session_state[changed_field_key]


def create_some_item(item_type, item_pos, *args, **kwargs):
    # print("create_some_item")
    manager.create_item(item_type, item_pos, *args, **kwargs)


# -------- Start of the page execution --------

st.set_page_config(page_title="CarLab Parameters Visualisation", page_icon="📊")
PAGE_NUMBER = os.path.basename(__file__).split("_")[0]  # The number in front of the filename

# In case this page was the first to be load by the user in the whole application,
# this will initialize them; and do nothing in the opposite case
initialize_global_session_variables_if_not_yet()

st.write("# Parameters Visualisation")
st.write("Here you can study the dataset in (almost) every possible way.")
with st.expander("Brief Instruction:", expanded=False):
    st.markdown(
        """
This page is implemented with ``DashboardManager``, which provides you similar functionality, 
as the Jupiter Notebook.
Here you can manage 2 types of blocks - ``Charts`` & ``Markdown Boxes``. 

Don't worry - all the information that you put in is saved - you can safely leave this page and return here later. 
- - -

#### Charts:

This block let you see and edit charts, that let you see the initial data "from the box". 
All the graphs you render during the session are also cached - so even if some graph took forever to generate,
it will not happen at the second time.
Note that some graphs are not perfect (because of outliers), and it is fixed on the next page.

What you can do:
- Edit chart title
- See the chart
- Edit the number of axis (the number of visualizing parameters)
- Choose the type of graph
- Edit the axis selection
- Set the flag for higher resolution (appr. 3 times higher per dimension)

Note that the higher resolution is, the higher is the rendering time. 
Also, note that the higher parameters have higher priority in case of conflicts. 
So, if you choose categorical parameter and then change the graph type to one that accepts only numerical parameters,
your choice of parameter will be automatically reset. So fill in all the graph information from top to bottom.

- - -

#### MarkDown Boxes:

Probably, the simplest thing ever. It has 2 states - ``edit`` and ``view`` (the 2nd is chosen by default).
Whenever you want to edit the text, just press **Edit** button. 
And yeah, the text you input supports Markdown (pretty obvious, I guess).

- - -

#### Common buttons:
##### Up & Down buttons:
 
You can swap the boxes in the ``DashboardManager`` by pressing the arrows from the right.
Note that some items are impossible to swap - you will see the notification about this if you try.

- - -

##### Other buttons:

- ``Remove`` - reduces the current box to atoms 
- ``➕ Add New Chart Below`` - creates new Chart below the current box
- ``➕ Add New Text Below`` - creates new MarkDown box below the current box
"""
    )

# Get some variables from session_state
df = st.session_state.df
manager = DashboardManager(PAGE_NUMBER)

if not st.session_state.hardcore_mode and not st.session_state.page_2_was_ever_rendered:
    st.session_state.page_2_was_ever_rendered = True
    manager.load_from_json(update_item_state, df,
                           "dashboard_manager_saves/beginner_level_data_page_2.json",
                           skip_rerun=False)

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

# De-comment for debugging
# st.write(str(manager))
