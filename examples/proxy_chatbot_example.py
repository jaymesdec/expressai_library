# examples/proxy_chatbot_example.py
#
# Student-style usage: talk to the classroom proxy with NO OpenAI API key.
# (Adults using OpenAI directly should see chatbot_example.py instead.)

import sys
import os

# ✅ Add parent directory to sys.path BEFORE importing expressai (local use only)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from expressai import create_chatbot

# 🏫 Values your teacher provides — no "sk-..." key required.
PROXY_URL = "https://franklin-ai-proxy-c953cd639dde.herokuapp.com/v1"  # your class proxy
CLASSROOM_PASSWORD = "ASK-YOUR-TEACHER"     # <-- your teacher gives you this password
MY_NAME = "alice"

bot = create_chatbot(
    system_prompt="You are a friendly study buddy who explains things simply.",
    base_url=PROXY_URL,
    classroom_token=CLASSROOM_PASSWORD,
    student_id=MY_NAME,
)

print(bot)
print("Bot:", bot.ask("Explain what a function is, using a pizza analogy."))
print("Bot:", bot.ask("Now give me a tiny example in Python."))  # remembers context
