import streamlit as st
import requests
import os
import subprocess
from helpers import initialize_global_session_variables_if_not_yet

# Function to launch the Rasa server and Action server
@st.cache_resource
def start_servers():
    rasa_path = "Rasa"
    if not os.path.exists(rasa_path):
        st.error("Rasa folder not found. Ensure the path is correct.")
        return None

    os.chdir(rasa_path)
    # Start Rasa server
    subprocess.Popen(['start', 'cmd', '/min', '/k', 'rasa run'], shell=True)
    # Start Rasa Action server
    subprocess.Popen(['start', 'cmd', '/min', '/k', 'rasa run actions'], shell=True)
    os.chdir("..")  # Return to the root directory

# Constants
RASA_SERVER_URL = "http://localhost:5005/webhooks/rest/webhook"

# Streamlit page configuration
st.set_page_config(page_title="CarLab Chatbot", page_icon="💬")
initialize_global_session_variables_if_not_yet()

# Initialize the Rasa server
start_servers()

# Page title
if "title_set" not in st.session_state:
    st.title("Chat with Manager Bot")
    st.session_state.title_set = True

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Message input field
prompt = st.chat_input("Input your message:")
if prompt:
    # Save user's message
    st.session_state.messages.append({"sender": "user", "message": prompt})

    # Send the message to the Rasa server
    with st.spinner("Waiting for bot's response..."):
        try:
            response = requests.post(RASA_SERVER_URL, json={"sender": "user", "message": prompt})
            response.raise_for_status()
            bot_responses = response.json()

            for bot_response in bot_responses:
                bot_message = bot_response.get("text", "")
                if bot_message:
                    st.session_state.messages.append({"sender": "bot", "message": bot_message})
        except Exception as e:
            error_message = "Bot is not responding. Please try again later."
            st.session_state.messages.append({"sender": "bot", "message": error_message})
            st.error(f"Error: {e}")

# Display chat history
for msg in st.session_state.messages:
    sender = "👤 You" if msg["sender"] == "user" else "🤖 Bot"
    st.markdown(f"**{sender}:** {msg['message']}")
