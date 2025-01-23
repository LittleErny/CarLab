import os

import streamlit as st

from DashboardManager.ChartItem import ChartItem
from DashboardManager.DashboardItem import DashboardItem
from DashboardManager.DashboardManager import DashboardManager
from DashboardManager.DashboardManagerEnums import DashboardItemTypes, ChartTypes
from DashboardManager.MDBoxItem import MDBoxItem
from DashboardManager.Model.Model import MLModel
from helpers import initialize_global_session_variables_if_not_yet

st.set_page_config(page_title="CarLab Model", page_icon="🤖")

initialize_global_session_variables_if_not_yet()
PAGE_NUMBER = os.path.basename(__file__).split("_")[0]  # The number in front of the filename


def update_model_item_state(what_to_update: str, changed_field_key: str) -> None:
    ml_model[what_to_update] = st.session_state[changed_field_key]


def update_non_model_item_state(item_id: int, what_to_update: str, changed_field_key: str) -> None:
    if what_to_update == "chart_type":
        manager.items[item_id][what_to_update] = ChartTypes.from_string(st.session_state[changed_field_key])
    else:
        manager.items[item_id][what_to_update] = st.session_state[changed_field_key]


def create_some_item(item_type: DashboardItemTypes, manager: DashboardManager, item_pos: int, *args, **kwargs):
    manager.create_item(item_type, item_pos, *args, **kwargs)


manager = DashboardManager(PAGE_NUMBER)
df = st.session_state.df2

st.write("# Model")
st.write("Here you can choose, set up, and train your model.")

if manager.is_empty():
    ml_model = MLModel(df)

    manager.create_item(DashboardItemTypes.MD_BOX,
                        item_pos=0,
                        on_change_function=update_non_model_item_state,
                        content="""
Now it's time to train some model to be able to do predictions. If you are not in the hardcore mode,
 you can see the table with my results in the bottom of this page. Good luck! 
 
Note: It's better to do some preprocessing actions before model training - especially labelling😉
""")

    manager.create_item(DashboardItemTypes.MODEL_SELECTION,
                        item_pos=1,
                        ml_model=ml_model,
                        on_change_function=update_model_item_state
                        )

    manager.create_item(DashboardItemTypes.MODEL_SETTING,
                        item_pos=2,
                        ml_model=ml_model,
                        on_change_function=update_model_item_state
                        )

    manager.create_item(DashboardItemTypes.MODEL_TRAINING,
                        item_pos=3,
                        ml_model=ml_model,
                        on_change_function=update_model_item_state
                        )
    if not st.session_state.hardcore_mode:
        manager.create_item(DashboardItemTypes.MD_BOX,
                            item_pos=4,
                            on_change_function=update_non_model_item_state,
                            content="""
Here is the rating of all the tried models in 
their best configurations, as I succeed to achieve.

| Model              | MSE (Min-Max) | MSE (Standard) | NMSE (Min-Max)  | NMSE (Standard)  |
|--------------------|---------------|----------------|-----------------|------------------|
| Linear Reg.        | 0.0094        | 0.4133         | 0.4158          | 0.4158           |
| Ridge Reg.         | 0.0094        | 0.4133         | 0.4158          | 0.4158           |
| Lasso Reg.         | 0.0220        | 0.9768         | 0.9930          | 0.9827           |
| Decision Tree*     | 0.0045        | 0.1984         | 0.1987          | 0.1996           |
| Random Forest**    | 0.0033        | 0.1534         | 0.1536          | 0.1543           |
| XGBoost***         | 0.0030        | 0.1355         | 0.1364          | 0.1364           |
| CatBoost           | 0.0036        | 0.1723         | 0.1734          | 0.1734           |

*- Decision Tree with max_depth=10

**- Random Forest with max_depth=10 and number_of_estimators=20

***- XGBoost with learning_rate=0.2, number_of_estimators=20, loss_func="Squared Error"

Note: The random_state=42 for each model.
""")


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

            elif item.get_type() == DashboardItemTypes.MODEL_SELECTION:

                item.render(item_id)

            elif item.get_type() == DashboardItemTypes.MODEL_SETTING:

                item.render(item_id)

            elif item.get_type() == DashboardItemTypes.MODEL_TRAINING:

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
            # Deletes the block
            if item.get_type() == DashboardItemTypes.MD_BOX:
                if st.button("❌ **Delete Block**", key=f"delete_{item_id}"):
                    manager.remove_item(item_id)
                    st.rerun()
        with col2:
            pass
            # Creates a new sample graph below
            # st.button(
            #     "➕ **Add New Chart Below**",
            #     key=f"add_chart_{item_id}",
            #     on_click=create_some_item,
            #     args=(DashboardItemTypes.CHART, manager, item_id),
            #     kwargs={"on_change_function": update_non_model_item_state, "df": df}
            # )

        with col3:
            # Creates a sample MD Box below
            st.button(
                "➕ **Add New Text Below**",
                key=f"add_md_text_below_{item_id}",
                on_click=create_some_item,
                args=(DashboardItemTypes.MD_BOX, manager, item_id),
                kwargs={"on_change_function": update_non_model_item_state}
            )
