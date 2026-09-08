# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

`expressai` is a small, pip-installable Python library that gives students and workshop
participants a one-line interface to AI chat, vision, image generation, and voice. The
primary runtime target is **Google Colab** (with free-tier ElevenLabs in mind), not a local
server. Simplicity for beginners is the guiding design constraint — favor readable, obvious
code over cleverness or abstraction.

This repo has two parts:
- `expressai/` — the student-facing library (this is the pip package).
- `classroom-proxy/` — a standalone FastAPI server that lets students use AI **without an
  API key**. It holds the real `OPENAI_API_KEY` server-side, authenticates students with a
  shared classroom token, forces a cheap model, caps tokens, and rate-limits per student.
  Deployed separately to Heroku via `Procfile` + `.python-version` + `app.json` (from the
  repo root: `git subtree push --prefix classroom-proxy heroku main`, since the proxy is a
  subfolder). Not part of the pip package. See `classroom-proxy/README.md`.

The two connect through the OpenAI-compatible wire protocol: the library points its OpenAI
client at the proxy's `base_url` and sends the classroom token as the bearer key plus
`X-Classroom-Token` / `X-Student-ID` headers; the proxy validates and forwards to OpenAI.

## Install / run

There is no build step, no linter config, and no test suite in this repo.

```bash
# Local editable install (from repo root)
pip install -e .

# How students install it (in Colab), per README:
!pip install --upgrade --no-deps git+https://github.com/jaymesdec/expressai_library.git
!pip install openai elevenlabs pillow
```

Run an example locally (examples inject the parent dir into `sys.path`, so no install needed):

```bash
python examples/chatbot_example.py   # edit the file to add a real API key first
```

Version lives in `setup.py` (`version=`); bump it there when publishing.

## Architecture

Three modules under `expressai/`, re-exported from `expressai/__init__.py`:

- `chatbot.py` — the `Chatbot` class, the heart of the library.
- `tts.py` — `speak_text()`, standalone ElevenLabs text-to-speech.
- `vision.py` — `analyze_image()`, a standalone image-analysis helper.

The public API is `create_chatbot(...)` (a factory returning a `Chatbot`), plus `speak_text`
and `analyze_image`. `ChatBot` is an alias of `Chatbot`, and `.ask()`/`.chat()` are aliases
of `__call__` — all added for spec/ergonomic compatibility; the underlying implementation is
still the single-callable dispatch below.

### Client resolution / proxy routing

`Chatbot` builds its OpenAI client **lazily** in `_ensure_client()` (cached after first
success), so a key set *after* construction still works:

- If `base_url` is set (proxy mode): the api_key becomes `api_key or classroom_token or
  DUMMY_CLASSROOM_KEY` (the OpenAI SDK refuses an empty key), and `classroom_token` /
  `student_id` are attached as `X-Classroom-Token` / `X-Student-ID` default headers.
- Otherwise (direct OpenAI): key resolves `api_key` → `os.getenv("OPENAI_API_KEY")` →
  `openai.api_key` (the last preserves original behavior). If none, methods return the
  friendly `_missing_key_message()` string instead of raising.

All three capability methods (`_chat`, `_analyze_image`, `_generate_image`) now take the
resolved `client` as an argument rather than each building their own — thread `base_url`
through this single client, never construct a bare `openai.OpenAI()` inside a method.

### The single-callable dispatch pattern

`Chatbot` is invoked by *calling the instance* (`Chatbot.__call__`). The keyword arguments
decide which capability runs — this is the central design idiom, so preserve it when adding
features:

- `generate_image=True` → DALL·E 3 generation (`_generate_image`); note this hits OpenAI's
  images endpoint, which the classroom proxy does **not** implement, so it only works in
  direct-OpenAI mode
- `image="path.jpg"` → vision via `_analyze_image` (works through the proxy — it's chat completions)
- otherwise → chat completion with conversation memory (`_chat`)
- `speak=True` speaks the result afterward, but only if the bot was created with a `voice_id`
- `language="Spanish"` simply prepends `"Please respond in {language}."` to the prompt

Chat history is kept in `self.history` and replayed on every `_chat` call (so the bot has
memory); `reset()` clears it. Image and generation paths do **not** touch history.

### Conventions to follow

- **API keys can come from args, env, or module globals.** `Chatbot` resolves them in
  `_ensure_client()` (see above). The original `openai.api_key` / `elevenlabs.api_key`
  module-global convention still works as the final fallback — keep it. `tts.py` (ElevenLabs)
  still reads `elevenlabs.api_key` directly; TTS is never proxied.
- **Errors are returned as bracketed strings, not raised** (e.g. `"[Chat error: {e}]"`,
  `"[Image load error: {e}]"`). `Chatbot._friendly_error()` maps common failures
  (`APIConnectionError`, `AuthenticationError`, `RateLimitError`) to beginner-friendly
  messages — prefer routing new API-call failures through it. A missing key returns
  `_missing_key_message()`; `analyze_image`/`speak_text` still raise `ValueError` for a
  missing key. Match the return-string style inside `Chatbot`.
- **Colab detection is duplicated** in both `chatbot.py` and `tts.py` via a
  `try: import google.colab` block setting `IN_COLAB`. When `IN_COLAB`, results display
  inline (`IPython.display`); otherwise they save/play to disk. Any new output feature should
  respect this same branch.
- **Generated files land in the current working directory**: audio in `output_audio/`
  (timestamped `response_YYYYMMDD_HHMMSS.mp3`), images in `output_images/` (named from the
  first 40 chars of the prompt). Directories are created on demand with `os.makedirs(...,
  exist_ok=True)`.

### Vision paths (now unified)

Both vision code paths use `client.chat.completions.create` with `image_url` content blocks:
`Chatbot._analyze_image` (chatbot.py) and the standalone `vision.analyze_image` (vision.py).
The latter was migrated off the newer `responses` API specifically so it works through the
classroom proxy, which only implements chat completions. Keep both on chat completions.

## Default model

The default model is **`gpt-4o-mini`** (changed from `gpt-4o` in 0.2.0) for cost safety —
it is vision-capable, so image analysis still works. In proxy mode the server overrides the
model regardless of what the client sends.

## Dependencies

`openai>=1.14.0`, `elevenlabs>=1.1.0`, `pillow>=10.0.0`, `requests>=2.25.0`, Python 3.8+.
(`requests` downloads the DALL·E result in `_generate_image`; it is now a declared dependency.)
TTS defaults to model `eleven_multilingual_v2` and MP3 output (`mp3_44100_128`), chosen so it
works on ElevenLabs' free tier.

The proxy (`classroom-proxy/`) has its own `requirements.txt` (`fastapi`, `uvicorn[standard]`,
`openai`, `python-dotenv`, `pydantic`) and is deployed independently of the pip package.
