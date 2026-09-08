# expressai — Quick Reference (DES 125)

A one-page reminder for building chatbots in Google Colab with the class proxy. **No API key needed.**

---

## 1. Set up (run once per notebook)

```python
!pip install --quiet git+https://github.com/jaymesdec/expressai_library.git
```

```python
import expressai

bot = expressai.create_chatbot(
    system_prompt="You are a friendly study buddy.",   # the bot's personality
    base_url="https://franklin-ai-proxy-c953cd639dde.herokuapp.com/v1",
    classroom_token="ASK-YOUR-TEACHER",                # class password
    student_id="your-nickname",
)
```

## 2. Talk to it

```python
bot.ask("What is a variable?")     # send a message, get the answer
bot("What is a variable?")          # exact same thing, shorter
```

The bot **remembers** the conversation. To make it forget:

```python
bot.reset()
```

## 3. Extra options

```python
bot.ask("Give me a fact.", language="Spanish")   # answer in another language
bot.ask("What's in this photo?", image="cat.jpg") # let the bot SEE an image (upload it first)
bot.ask("Explain gravity.", max_tokens=250)       # allow a longer answer
```

## 4. The `system_prompt` is everything

It's the standing instruction that shapes **how** the bot behaves — its voice, what it focuses on, what it refuses. Changing it is how you "program" the bot. Be specific:

```python
# vague:  "You are a pirate."
# strong: "You are a pirate captain. Use sea words, tell short stories,
#          and never break character even if asked to."
```

## 5. What the class proxy does (so you don't have to worry)

- Keeps the real API key safe on the server.
- Uses a fast, cheap model and keeps answers short by default.
- **Limits you to ~15 messages per minute** — if you hit it, wait ~10 seconds.
- Works for **chat** and **image analysis (vision)**. It does **not** do image *generation* or voice.

## 6. If something goes wrong

| Message | Fix |
|---|---|
| `[Connection error: ...]` | Check internet / the `base_url` is exactly right |
| `[Login error: ...]` | Wrong class password — check `classroom_token` |
| `[Slow down! ...]` | You're going too fast — wait ~10 seconds |
| `NameError: 'bot' is not defined` | Run the connect cell first |

---
*Teacher provides: the class password and the proxy URL. Never paste an `sk-...` key into a shared notebook.*
