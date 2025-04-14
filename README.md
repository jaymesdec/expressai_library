# 🧠 expressai

**expressai** is a creative Python library for expressive AI-based projects in **chat**, **vision**, and **voice**.  
It empowers you to:

- Create conversational AI chatbots with memory
- Speak responses aloud using ElevenLabs voices
- Analyze images with GPT-4o’s vision capabilities
- Generate new images using DALL·E 3
- Respond in different languages

Perfect for **teaching, workshops, project-based learning**, or anyone who wants to explore the expressive potential of AI in a simple, straightforward way.

---

## ✨ Features

1. **Chat Mode**  
   Create chatbots with distinct personalities.
2. **Voice Support**  
   Give each bot a voice and speak responses out loud using ElevenLabs.
3. **Image Analysis**  
   Show a bot an image, and it will describe or analyze it using GPT-4o.
4. **Image Generation**  
   Ask a bot to generate an image with DALL·E 2 and display/save the result.
5. **Multilingual**  
   Request responses in a specific language with a simple command.

---

## 📦 Installation in Google Colab
!pip install --upgrade --no-deps git+https://github.com/jaymesdec/expressai_library.git
!pip install openai elevenlabs pillow
import openai, elevenlabs
openai.api_key = "sk-..."   # Your OpenAI API key
elevenlabs.api_key = "sk-..."  # Your ElevenLabs API key
from expressai import create_chatbot, speak_text

🧑‍🏫 Quick Examples
1. Create a Chatbot
from expressai import create_chatbot
import openai

openai.api_key = "sk-..."  # OpenAI API key

# A friendly pirate chatbot
pirate_bot = create_chatbot(
    system_prompt="You are a helpful pirate who always talks like a sea captain.",
    model="gpt-4o"
)

response = pirate_bot("Avast! What's the best treasure map strategy?")
print("Bot says:", response)

2. Give the Chatbot a Voice
import elevenlabs

elevenlabs.api_key = "sk-..."  # ElevenLabs API key

# Create a bot with a voice ID
pirate_bot = create_chatbot(
    system_prompt="You are a jolly pirate who loves to tell sea stories.",
    model="gpt-4o",
    voice_id="Myn1LuZgd2qPMOg9BNtC"  # Example voice ID
)

# Ask it something and speak the answer
answer = pirate_bot("Tell me about the biggest sea monster ye ever saw!", speak=True)
print(answer)
This will generate text and save an audio file in output_audio/ with a unique timestamped filename.

3. Respond in a Different Language
answer_spanish = pirate_bot(
    "What is the nature of treasure hunting?",
    language="Spanish"
)
print(answer_spanish)
Here, your prompt gets prefixed with Please respond in Spanish. so the bot replies in Spanish.

4. Analyze Images (Vision)
caption = pirate_bot(
    "Describe this image from a scientific perspective.",
    image="sea_creature.jpg"
)
print("Bot's analysis:", caption)
The bot sees the image and responds with GPT-4o’s vision capabilities. In Google Colab, just upload sea_creature.jpg to your workspace.

5. Generate an Image (DALL·E 2)
file_path = pirate_bot(
    "Draw a treasure map with dragons and mountains",
    generate_image=True
)
print("Generated image saved to:", file_path)
The image is displayed inline if you’re in Colab
And a copy is saved to output_images/ with a name derived from your prompt

🔊 ElevenLabs Voice Tips
Find or create voices in ElevenLabs.
Copy the Voice ID from your dashboard.
Pass it as voice_id when creating a chatbot.

Example Voice IDs:

Character	Voice ID
Feynman	dDO88mp6NlmgMvxIk8kV
Pirate	Myn1LuZgd2qPMOg9BNtC
Herzog	N9Q6FLY8ILw7lPey10SP

🛠 Requirements
Python 3.8+
openai >= 1.14.0
elevenlabs >= 1.1.0
pillow >= 10.0.0

🧠 Educator Notes
Encourage students to experiment with prompts and see how tone or language changes the results.

Use voice to make the interaction more playful and accessible.

Combining image analysis and generation can spark creativity (e.g., analyze a real photo, then generate a fictional variation).

The logs in output_audio/ and output_images/ can be shared or reviewed.

🪪 License
MIT License
Created by Jaymes Dec (with massive help from chatGPT)

Contributions welcome!
Enjoy exploring the expressive possibilities of AI with expressai.