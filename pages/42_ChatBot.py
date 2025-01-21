import streamlit as st
import requests
import os
import subprocess

# TODO:
# Fix title duplication on first user input.
# Train the model for our dataset (currently working on the default one).
# Create a system persona.
# Define bot use cases.
# Design dialog flow.

# Function to launch the Rasa server
@st.cache_resource
def start_server():
    if not os.path.exists("Rasa"):
        st.error("Rasa folder not found. Ensure the path is correct.")
        return None
    os.chdir("Rasa")
    subprocess.Popen(['start', 'cmd', '/k', 'rasa run'], shell=True)
    os.chdir("..")  # Return to the root directory

# Initialize the server
start_server()

# Rasa server URL
RASA_SERVER_URL = "http://localhost:5005/webhooks/rest/webhook"

# App title
st.title("Chat with Manager Bot")  # Ensure the title is displayed every time

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Message input field
prompt = st.chat_input("Input your message:")
if prompt:
    # Save the user's message
    st.session_state.messages.append({"sender": "user", "message": prompt})

    # Send the message to the Rasa server
    try:
        response = requests.post(RASA_SERVER_URL, json={"sender": "user", "message": prompt})
        response.raise_for_status()
        bot_responses = response.json()
        for bot_response in bot_responses:
            bot_message = bot_response.get("text", "")
            st.session_state.messages.append({"sender": "bot", "message": bot_message})
    except Exception as e:
        error_message = "Bot is not responding. Please try again later."
        st.session_state.messages.append({"sender": "bot", "message": error_message})
        st.error(f"Error: {e}")

# Display chat history
for msg in st.session_state.messages:
    sender = "👤 You" if msg["sender"] == "user" else "🤖 Bot"
    st.markdown(f"**{sender}:** {msg['message']}")
