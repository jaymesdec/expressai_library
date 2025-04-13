# examples/vision_example.py

import sys
import os

# ✅ Add parent directory to sys.path BEFORE importing expressai (for local use only)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import openai
from expressai import create_chatbot

# 🔑 Set your OpenAI API key
openai.api_key = "sk-..."  # Replace with your own OpenAI API key

# 🧠 Create a chatbot that can describe images
bot = create_chatbot(
    system_prompt="You are a poetic scientific observer.",
    model="gpt-4o",
    max_tokens=100
)

# 🖼️ Ask the bot to describe an image
caption = bot(
    "Describe this image from a scientific perspective.",
    image="crab_nebula.jpg"  # Make sure this image is in the same folder
)

print("Bot says:", caption)
