import sys
import os

# ✅ Add parent directory to sys.path BEFORE importing expressai
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from expressai import create_chatbot
import openai

# 🔑 Replace with your OpenAI API key
openai.api_key = "YOUR_API_KEY_HERE"

bot = create_chatbot(
    system_prompt="You are a poetic scientific observer.",
    model="gpt-4o",
    max_tokens=100
)

# Image + text
caption = bot("Describe this image from a scientific perspective.", image="crab_nebula.jpg")
print(caption)
