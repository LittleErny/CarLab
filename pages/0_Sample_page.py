import streamlit as st
from helpers import initialize_global_session_variables_if_not_yet
import os
from functools import partial


# In case this page was the first to be load by the user in the whole application,
# this will initialize them; and do nothing in the opposite case
initialize_global_session_variables_if_not_yet()

PAGE_NUMBER = os.path.basename(__file__).split("_")[0]  # The number in front of the filename

st.write("## This is the sample page(to be removed)")
st.write("Do not forget to use ``initialize_session_variables_if_not_yet()`` in the beginning of every page")

st.write("#### A monument to the need to read documentation more carefully")
st.write("150 lines of code..")

if f"p{PAGE_NUMBER}_editing_mode" not in st.session_state:
    st.session_state[f"p{PAGE_NUMBER}_editing_mode"] = False


# Universal decorator for functions, that render editable parts of interface, such as radiobuttons, text fields, etc.
# Using this, the new value is stored in the session state immediately, without need to make one more edit for
# the previous edit to be saved.
# ------------------------------ How it works: ------------------------------
# When we first render the graphical element, we save its unique key in the st.session_state with a negative flag,
# that this element is being edited
# When we edit element(for example, press another radiobutton), enable_editing_mode(key) is called. This changes
# the flag, indicating that this element with this key is being edited.
# Afterward, the automatic page reset is executed by streamlit, which usually prevents us from immediate save of new
# state of the element.
# When resetting the page, the state_handler(..) sees whether the flag of some element was changed. If so - saves
# new value to the session_state, cancels flag, and forces page reset with updated value.
# In such a way, all the changes are applied immediately.
def state_handler(state_key):
    def decorator(func):
        def wrapper(*args, **kwargs):

            # If the element was never rendered before, init its flag
            if f"p{PAGE_NUMBER}_{kwargs['key']}" not in st.session_state:
                st.session_state[f"p{PAGE_NUMBER}_flag_{kwargs['key']}"] = False

            # if f'p{PAGE_NUMBER}_value_{radio_res}' not in st.session_state:

            # Render the element of interface
            value = func(*args, **kwargs)

            # If editing mode is enabled, update the state
            if st.session_state[f"p{PAGE_NUMBER}_editing_mode"]:
                if st.session_state[f"p{PAGE_NUMBER}_flag_{kwargs['key']}"]:
                    # Save the value to the session state
                    # st.session_state[f"p{PAGE_NUMBER}_value_{kwargs['key']}"] = value

                    # And disable flags
                    st.session_state[f"p{PAGE_NUMBER}_editing_mode"] = False
                    st.session_state[f"p{PAGE_NUMBER}_flag_{kwargs['key']}"] = False

                    # Rerender the page with updated data
                    st.rerun()

            return value

        return wrapper

    return decorator


# Enabling Edit Mode
def enable_editing_mode(key):
    st.session_state[f"p{PAGE_NUMBER}_flag_{key}"] = True
    st.session_state[f"p{PAGE_NUMBER}_editing_mode"] = True


# Our function-replacer for st.radio()
@state_handler("radio_state")
def render_radio(label, options, index, key):
    return st.radio(label,
                    options,
                    index=index,
                    key=key,
                    on_change=partial(enable_editing_mode, key)
                    )


# Our function-replacer for st.selectbox()
@state_handler("selectbox_state")
def render_selectbox(label, options, index, key):
    return st.selectbox(label,
                        options,
                        index=index,
                        key=key,
                        on_change=partial(enable_editing_mode, key)
                        )


# Our function-replacer for st.text_input()
@state_handler("text_input_state")
def render_text_input(label, key):
    return st.text_input(label,
                         key=key,
                         on_change=partial(enable_editing_mode, key)
                         )


# if "selectbox_state" not in st.session_state:
#     st.session_state.selectbox_state = "Option 1"
#
# if "text_input_state" not in st.session_state:
#     st.session_state.text_input_state = "init"

# Рендеринг элементов с использованием универсального подхода
# Установка начальных значений состояний
radio_key = "radio_1"
radio_options = ["1", "2", "3"]
if radio_key not in st.session_state:
    st.session_state[radio_key] = "1"

radio_res = render_radio(
    "Choose an option", radio_options,
    index=radio_options.index(st.session_state[radio_key]),
    key=radio_key
)


selectbox_key = "selectbox_1"
selectbox_options = ["Option 1", "Option 2", "Option 3"]
if selectbox_key not in st.session_state:
    st.session_state[selectbox_key] = "Option 1"

selectbox_res = render_selectbox(
    "Select an option", selectbox_options,
    index=selectbox_options.index(st.session_state[selectbox_key]
    ),
    key=selectbox_key
)

text_input_key = "text_input_1"
if text_input_key not in st.session_state:
    st.session_state[text_input_key] = ""

text_input_res = render_text_input(
    "Enter some text", key=text_input_key
)


# Отображение текущих состояний
st.write(f"Radio state: {radio_res}")
st.write(f"Selectbox state: {selectbox_res}")
st.write(f"Text input state: {text_input_res}")

# st.write(st.session_state)
