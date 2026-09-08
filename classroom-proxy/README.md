# Classroom AI Proxy

A tiny FastAPI service that lets middle-school students use AI in Google Colab
**without ever touching a real API key**. It holds one OpenAI key server-side and
gives students a shared classroom token instead.

## What it protects against

- **Leaked credentials** — no `sk-...` key ever lives in a shared/pushed notebook.
- **Cost runaway** — every request is forced to a cheap model (`gpt-4o-mini`),
  `max_tokens` is hard-capped, and each student is rate-limited.
- **Unauthorized use** — requests without the correct classroom token get `401`.

## Endpoints

| Method | Path                   | Purpose                                   |
|--------|------------------------|-------------------------------------------|
| GET    | `/health`              | Uptime / monitoring check                 |
| POST   | `/v1/chat/completions` | OpenAI-compatible chat completions        |

Authentication: send the classroom token as either
`Authorization: Bearer <token>` **or** `X-Classroom-Token: <token>`.
Optionally send `X-Student-ID: <name>` for per-student rate limiting.

## Run locally

```bash
cd classroom-proxy
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # then edit .env with your real OPENAI_API_KEY
uvicorn main:app --reload --port 8000
```

Test it:

```bash
# Health check
curl http://localhost:8000/health

# A chat request (use the CLASSROOM_SECRET from your .env)
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-class-password" \
  -H "X-Student-ID: alice" \
  -d '{"messages":[{"role":"user","content":"Say hello like a pirate"}]}'

# Wrong token -> 401
curl -i -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer wrong" \
  -d '{"messages":[{"role":"user","content":"hi"}]}'
```

## Deploy to Heroku

The included `Procfile` (`web: uvicorn main:app --host 0.0.0.0 --port $PORT`),
`.python-version`, and `app.json` are Heroku-ready. **A cloud URL is required** — a
localhost proxy is unreachable from Google Colab, which runs on Google's servers.

This proxy lives in the `classroom-proxy/` subfolder of the `expressai_library` repo,
but Heroku expects the app at the repo root. Use a **subtree push** to deploy just this
folder:

```bash
# Run these from the repo ROOT (expressai_library/), not from classroom-proxy/
heroku login
heroku create franklin-ai-proxy          # pick your own app name

# Set secrets (students never see these)
heroku config:set OPENAI_API_KEY=sk-your-real-key --app franklin-ai-proxy
heroku config:set CLASSROOM_SECRET=your-class-password --app franklin-ai-proxy
# Optional overrides:
# heroku config:set MAX_TOKENS_CAP=400 RATE_LIMIT_MAX=15 --app franklin-ai-proxy

# Deploy ONLY the classroom-proxy/ subfolder as the app root
git subtree push --prefix classroom-proxy heroku main

# Make sure a web dyno is running, then health-check
heroku ps:scale web=1 --app franklin-ai-proxy
curl https://franklin-ai-proxy-c953cd639dde.herokuapp.com/health
```

Notes:
- Use a **Basic** dyno (~$7/mo) if you want it always-on. **Eco** dynos (~$5/mo pooled)
  sleep after 30 min idle, so the first request each class period is slow (~10–20s cold start).
- If the subtree push is ever rejected after history changes, force it with:
  `git push heroku \`git subtree split --prefix classroom-proxy main\`:refs/heads/main --force`
- Alternative (no subtree): copy `classroom-proxy/`'s contents into their own repo and
  `git push heroku main` normally.

Then give students the public URL + the classroom token. They connect with:

```python
bot = expressai.create_chatbot(
    system_prompt="You are a friendly study buddy.",
    base_url="https://franklin-ai-proxy-c953cd639dde.herokuapp.com/v1",  # note the /v1
    classroom_token="your-class-password",
    student_id="alice",
)
```

## Notes / limits

- The rate limiter is **in-memory**, so it resets on restart and is per-process.
  For a single classroom instance that's fine; for multiple replicas you'd want a
  shared store (e.g. Redis).
- Only chat completions are proxied. Image generation (DALL·E) and ElevenLabs
  voice are **not** routed through this proxy — vision (image analysis) works
  because it uses the chat completions endpoint.
