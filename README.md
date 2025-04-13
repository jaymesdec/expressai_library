# 🧠 expressai

**expressai** is a creative Python library for expressive AI-based projects in chat, vision, and voice.  
It’s designed to make powerful AI tools feel accessible, engaging, and playful—perfect for learning, prototyping, and teaching.

Created for workshops, classrooms, and creative developers.

---

## ✨ Features

- 🧑‍🏫 **Create AI chatbots** with custom personalities and memory
- 🖼️ **Analyze images** using OpenAI’s GPT-4o vision capabilities
- 🔊 **Speak responses aloud** with realistic ElevenLabs text-to-speech
- 🎛️ Thoughtfully designed for use in Google Colab and student-friendly settings

---

## 📦 Installation

### 📍 Local (for development)

```bash
git clone https://github.com/jaymesdec/expressai.git
cd expressai
pip install -e .
📍 Google Colab (quick setup)
In your first code cell:

!pip install openai elevenlabs pillow ipython

Then:

from expressai import create_chatbot, speak_text

🧪 Quick Examples

🤖 Create a chatbot
import openai
from expressai import create_chatbot

openai.api_key = "sk-..."  # Set your OpenAI API key

bot = create_chatbot(
    system_prompt="You are a friendly pirate who answers in rhymes.",
    model="gpt-4o"
)

print(bot("What is the square root of 16?"))

🖼️ Show a chatbot an image

description = bot("Describe this image like a scientist.", image="my_photo.jpg")
print(description)

🔊 Speak the output

import elevenlabs
from expressai import speak_text

elevenlabs.api_key = "sk-..."  # Your ElevenLabs key

speak_text("The stars are not silent—they sing in fusion.")

________ADD LIST OF VOICE IDs___________

🔐 API Keys Required
To use this library, you’ll need:
An OpenAI API key
An ElevenLabs API key
Set them in your notebook or script:

openai.api_key = "your-openai-key"
elevenlabs.api_key = "your-elevenlabs-key"

🛠️ Requirements
Python 3.8+
openai ≥ 1.14.0
elevenlabs ≥ 1.1.0
pillow ≥ 10.0.0
ipython ≥ 8.0.0

Install dependencies with:

pip install -r requirements.txt

🧑‍🎓 For Educators and Students
expressai was designed to be expressive, intuitive, and empowering for learners. 

🪪 License
MIT License
Created by Jaymes Dec

