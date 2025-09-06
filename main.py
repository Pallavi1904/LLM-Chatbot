import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as gen_ai
from google.api_core.exceptions import ResourceExhausted

# Load environment variables
load_dotenv()

# Configure Streamlit page settings
st.set_page_config(
    page_title="Chat with Gemini!",
    page_icon=":brain:",  # Favicon emoji
    layout="centered",    # Page layout option
)

# Load Google API Key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Configure Google Generative AI
gen_ai.configure(api_key=GOOGLE_API_KEY)

# ✅ Try Pro first, fallback to Flash if quota is hit
def get_model(preferred="gemini-1.5-pro"):
    try:
        return gen_ai.GenerativeModel(preferred)
    except Exception:
        return gen_ai.GenerativeModel("gemini-1.5-flash")

model = get_model()

# Function to translate roles between Gemini and Streamlit terminology
def translate_role_for_streamlit(user_role):
    if user_role == "model":
        return "assistant"
    else:
        return user_role

# Initialize chat session if not already present
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

# Display the chatbot's title
st.title("🤖 Gemini ChatBot")

# Display chat history
for message in st.session_state.chat_session.history:
    with st.chat_message(translate_role_for_streamlit(message.role)):
        st.markdown(message.parts[0].text)

# Input field for user's message
user_prompt = st.chat_input("Ask Gemini...")

if user_prompt:
    # Add user's message to chat and display it
    st.chat_message("user").markdown(user_prompt)

    try:
        # Try with current model
        gemini_response = st.session_state.chat_session.send_message(user_prompt)
    except ResourceExhausted:
        # If quota exceeded, switch to flash model
        st.warning("⚠️ Quota exceeded for gemini-1.5-pro. Switching to gemini-1.5-flash...")
        flash_model = gen_ai.GenerativeModel("gemini-1.5-flash")
        st.session_state.chat_session = flash_model.start_chat(history=st.session_state.chat_session.history)
        gemini_response = st.session_state.chat_session.send_message(user_prompt)

    # Display Gemini's response
    with st.chat_message("assistant"):
        st.markdown(gemini_response.text)
