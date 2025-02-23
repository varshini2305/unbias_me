import streamlit as st
import requests
import re
# import speech_recognition as sr
from bs4 import BeautifulSoup
import tempfile
import os
import openai
import json
import yaml
from parsing_web_page import extract_content_from_url

# Load the config.yaml file
with open("models/config.yaml", "r") as file:
    config = yaml.safe_load(file)

# from pydub import AudioSegment



# Backend API URL
API_URL = "http://127.0.0.1:8000/analyze"  # Update if using Ngrok

### 🔹 Function to Parse Webpage Content ###
def parse_from_webpage(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        return soup.get_text()[:2000]  # Extracts first 2000 characters
    except Exception as e:
        return f"Error fetching content: {str(e)}"

### 🔹 Function to Process User Input ###
def unbias_me(input_text):
    # Check if input is a URL
    if re.match(r"https?://", input_text):
        input_text = extract_content_from_url(input_text)
        print(f"{input_text=}")

    # Make a request to FastAPI
    response = requests.post(API_URL, json={"paragraph": input_text})
    print(f"{response=}")
    
    if response.status_code == 200:
        return response.json().get("critical_thoughts", "No analysis found.")
    else:
        return f"Error: {response.status_code}"

# 🔹 Streamlit UI
st.title("🔍 Unbias Me: Critical Thinking Assistant")
st.markdown("Share your opinions, chat, or provide a URL for unbiased analysis.")

# 🔹 Text Input Box + Voice Button
col1, col2 = st.columns([4, 1])
with col1:
    user_input = st.text_input("Enter text or URL here:", key="input_text")
# with col2:
#     audio_file = st.file_uploader("🎤 Upload Voice", type=["wav", "mp3", "ogg"])

# # 🔹 Transcribe Audio to Text
# if audio_file:
#     temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
#     temp_audio.write(audio_file.getvalue())
#     temp_audio.close()
    
#     # transcribed_text = transcribe_audio(temp_audio.name)
#     os.unlink(temp_audio.name)  # Delete temporary file
    
    
# 🔹 "Unbias Me" Button
if st.button("🤔 Unbias Me"):
    if user_input:
        result = unbias_me(user_input)
        st.markdown("### 🧠 Critical Analysis")
        st.write(result)
    else:
        st.warning("Please enter text, a URL, or use voice input.")

