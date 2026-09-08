# Teacher Setup — Classroom AI Proxy

Everything you need to stand up (and check) the proxy so students can build chatbots with `expressai` in Colab **without ever seeing an API key**. Do the one-time deploy once; run the 30-second pre-class check each period.

---

## What this is (and why)

The proxy is a tiny server that holds your real `OPENAI_API_KEY` **server-side**. Students authenticate with a shared **class password** instead. It also forces a cheap model, caps response length, and rate-limits each student — so a shared notebook can't leak your key or run up a bill.

- Repo folder: `expressai_library/classroom-proxy/`
- Students connect to: `https://<your-app>.herokuapp.com/v1`  ← note the `/v1`
- Students send: the class password (as `classroom_token`) + a nickname (`student_id`)

---

## One-time deploy (Heroku)

Run these **from the repo root** (`expressai_library/`), not from inside `classroom-proxy/`. The proxy is a subfolder, so it deploys via a **subtree push**.

```bash
heroku login
heroku create franklin-ai-proxy            # pick your own app name

# Secrets — students never see these:
heroku config:set OPENAI_API_KEY=sk-your-real-key   --app franklin-ai-proxy
heroku config:set CLASSROOM_SECRET=your-class-password --app franklin-ai-proxy

# Deploy ONLY the classroom-proxy/ subfolder as the app root:
git subtree push --prefix classroom-proxy heroku main

heroku ps:scale web=1 --app franklin-ai-proxy       # make sure a dyno is running
```

If a later subtree push is rejected after history changes, force it:

```bash
git push heroku `git subtree split --prefix classroom-proxy main`:refs/heads/main --force
```

**Dyno choice:** a **Basic** dyno (~$7/mo) stays always-on. An **Eco** dyno (~$5/mo pooled) **sleeps after 30 min idle**, so the first request each class period is a slow (~10–20s) cold start — fine if you wake it before class (see the pre-class check).

---

## Verify it's working

```bash
# 1. Health check — should say status ok and openai_key_configured: true
curl https://franklin-ai-proxy.herokuapp.com/health

# 2. A real chat request with your class password:
curl -X POST https://franklin-ai-proxy.herokuapp.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-class-password" \
  -H "X-Student-ID: teacher-test" \
  -d '{"messages":[{"role":"user","content":"Say hello like a pirate"}]}'

# 3. Wrong password should return 401:
curl -i -X POST https://franklin-ai-proxy.herokuapp.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer wrong" \
  -d '{"messages":[{"role":"user","content":"hi"}]}'
```

If #1 shows `openai_key_configured: false`, your `OPENAI_API_KEY` config var isn't set.

---

## What to give students

Two things — put them on the board:

1. **Proxy URL:** `https://franklin-ai-proxy.herokuapp.com/v1`  *(exactly, including `/v1`)*
2. **Class password:** whatever you set as `CLASSROOM_SECRET`

They paste these into the connect cell (`base_url` and `classroom_token`) in the playground notebook. **Never** hand out the `sk-...` key.

---

## 30-second pre-class check

1. Run the **health check** curl above (this also **wakes an Eco dyno** so the first student request isn't slow).
2. Confirm the password on the board matches the current `CLASSROOM_SECRET`.
3. If you rotated the password, tell students the new one.

---

## Tuning knobs (optional)

Set any of these as Heroku config vars; defaults are sensible for a class.

| Config var | Default | What it does |
|---|---|---|
| `CLASSROOM_SECRET` | `change-me` | The class password students use. **Set this.** |
| `OPENAI_API_KEY` | — | Your real key. **Set this.** |
| `ALLOWED_MODEL` | `gpt-4o-mini` | The model every request is forced to use (ignores what the client asks) |
| `MAX_TOKENS_CAP` | `400` | Hard ceiling on response length — keeps answers short and cheap |
| `RATE_LIMIT_MAX` | `15` | Max requests per student per window |
| `RATE_LIMIT_WINDOW` | `60` | The window, in seconds (so 15 requests / 60s by default) |

```bash
heroku config:set MAX_TOKENS_CAP=400 RATE_LIMIT_MAX=15 --app franklin-ai-proxy
```

Raise `RATE_LIMIT_MAX` if students hit "Slow down!" during legitimate work; raise `MAX_TOKENS_CAP` if you want longer answers (costs more).

---

## Troubleshooting

| Symptom (student sees) | Cause | Fix |
|---|---|---|
| `[Login error: ... token was rejected]` (401) | Wrong/blank class password | Check the password on the board matches `CLASSROOM_SECRET` |
| `[Slow down! ...]` (429) | Student passed the rate limit | Normal guardrail; wait ~10s, or raise `RATE_LIMIT_MAX` |
| First request of the day hangs ~15s | Eco dyno cold start | Run the health check before class to wake it, or use a Basic dyno |
| `[Connection error ...]` | Wrong `base_url`, or app is down | Verify the URL includes `/v1`; run `heroku ps` / health check |
| Everyone gets a 500 config error | `OPENAI_API_KEY` not set on Heroku | `heroku config:set OPENAI_API_KEY=...` |

Logs: `heroku logs --tail --app franklin-ai-proxy`

---

## Updating the proxy later

After editing anything in `classroom-proxy/`, redeploy with the same subtree push:

```bash
git subtree push --prefix classroom-proxy heroku main
```

## Notes / limits

- The rate limiter is **in-memory and per-process** — it resets on restart. Fine for one classroom instance; you'd need a shared store (Redis) only if you scale to multiple dynos.
- Only **chat + vision** (image analysis) go through the proxy. **Image generation (DALL·E) and voice (ElevenLabs) do not** — those need a direct key and are teacher/demo-only.
- Rotate `CLASSROOM_SECRET` each term (or if it leaks): set the new value, redeploy is **not** needed for a config change, just update the board.
- Cost = the Heroku dyno (~$5–7/mo) + your OpenAI usage (tiny with `gpt-4o-mini` + the token cap).
