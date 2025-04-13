# examples/chatbot_example.py

import sys
import os

# ✅ Add parent directory to sys.path BEFORE importing expressai (for local use only)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import openai
from expressai import create_chatbot

# 🔑 Set your OpenAI API key
openai.api_key = "sk-..."  # Replace with your own OpenAI API key

# 🤖 Create a pirate-themed chatbot
pirate_bot = create_chatbot(
    system_prompt="You are a helpful pirate who always talks like a sea captain.",
    model="gpt-4o"
)

# 💬 Have a conversation
response = pirate_bot("Hello there, friend!")
print("Bot says:", response)

response = pirate_bot("What treasure lies ahead?")
print("Bot says:", response)

# 📊 Display chatbot state
print(pirate_bot)
