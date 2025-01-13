import streamlit as st

from DashboardManager.DashboardItem import DashboardItem
from DashboardManager.DashboardManagerEnums import MdBoxModes, DashboardItemTypes

SAMPLE_MD_TEXT = "You can edit this md text by pressing **edit** button"


class MDBoxItem(DashboardItem):
    def __init__(self, on_change_function, content=SAMPLE_MD_TEXT):

        self.content: str = content
        self.mode: MdBoxModes = MdBoxModes.VIEW  # No editor is shown
        self.on_change_function = on_change_function

    def enable_editing_mode(self):
        self.mode = MdBoxModes.EDIT

    def disable_editing_mode(self):
        self.mode = MdBoxModes.VIEW

    def get_editing_mode_state(self):
        return self.mode

    def update_content(self, new_content):
        self.content = new_content

    def render(self, pos_id):

        def disable_edit_mode_before_saving_res(on_change_function, *args):
            self.disable_editing_mode()
            on_change_function(*args)

        if st.button("\U0001F58B\ufe0f Edit", key=f"md_enable_edit_button_{pos_id}"):
            self.enable_editing_mode()

        if self.mode == MdBoxModes.VIEW:
            # Just show the text if we want to just watch it
            st.markdown(self.content)

        elif self.mode == MdBoxModes.EDIT:
            # Show the editable field
            st.text_area("Markdown Input", self.content,
                         key=f"content_{pos_id}",
                         on_change=disable_edit_mode_before_saving_res,
                         args=(self.on_change_function, pos_id, "content", f"content_{pos_id}")
                         )

        else:
            raise ValueError(f"Unknown mode of MDBox on position {pos_id}: {self.mode}")

    def get_type(self) -> DashboardItemTypes:
        return DashboardItemTypes.MD_BOX
