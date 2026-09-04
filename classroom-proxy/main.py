"""
Classroom AI Proxy
==================

A tiny, kid-safe FastAPI service that sits between student Google Colab notebooks
and OpenAI. Students authenticate with a shared classroom token instead of a real
OpenAI API key, so no billable credentials are ever exposed in a notebook.

What it does:
  * Holds the real OPENAI_API_KEY server-side (never sent to clients).
  * Exposes an OpenAI-compatible POST /v1/chat/completions endpoint.
  * Requires a shared classroom token (Authorization: Bearer <token> or
    X-Classroom-Token: <token>) matching CLASSROOM_SECRET.
  * Forces a cheap model and hard-caps max_tokens to prevent runaway cost.
  * Rate-limits per student (X-Student-ID) or per client IP.
  * Allows CORS from anywhere so Colab can reach it.

Run locally:
    uvicorn main:app --reload --port 8000
"""

import os
import time
from collections import defaultdict, deque

from dotenv import load_dotenv
from fastapi import FastAPI, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from openai import OpenAI

load_dotenv()

# --------------------------------------------------------------------------- #
# Configuration (all overridable via environment variables)
# --------------------------------------------------------------------------- #
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CLASSROOM_SECRET = os.getenv("CLASSROOM_SECRET", "change-me")
ALLOWED_MODEL = os.getenv("ALLOWED_MODEL", "gpt-4o-mini")
MAX_TOKENS_CAP = int(os.getenv("MAX_TOKENS_CAP", "400"))
RATE_LIMIT_MAX = int(os.getenv("RATE_LIMIT_MAX", "15"))          # requests...
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))    # ...per this many seconds

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

app = FastAPI(title="Classroom AI Proxy", version="1.0.0")

# Colab notebooks and web apps run from many origins; allow all.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------------------------------- #
# In-memory sliding-window rate limiter
# --------------------------------------------------------------------------- #
# Maps an identifier -> deque of recent request timestamps. This is per-process
# and resets on restart, which is fine for a single-instance classroom proxy.
_request_log: "defaultdict[str, deque]" = defaultdict(deque)


def _is_rate_limited(identifier: str) -> bool:
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW
    hits = _request_log[identifier]

    # Drop timestamps that have aged out of the window.
    while hits and hits[0] < window_start:
        hits.popleft()

    if len(hits) >= RATE_LIMIT_MAX:
        return True

    hits.append(now)
    return False


def _extract_token(authorization: str, x_classroom_token: str) -> str:
    """Pull the classroom token from either the Bearer header or X-Classroom-Token."""
    if x_classroom_token:
        return x_classroom_token.strip()
    if authorization and authorization.lower().startswith("bearer "):
        return authorization[7:].strip()
    return ""


# --------------------------------------------------------------------------- #
# Routes
# --------------------------------------------------------------------------- #
@app.get("/health")
def health():
    """Lightweight uptime/monitoring check."""
    return {
        "status": "ok",
        "model": ALLOWED_MODEL,
        "openai_key_configured": client is not None,
    }


@app.post("/v1/chat/completions")
async def chat_completions(
    request: Request,
    authorization: str = Header(default=""),
    x_classroom_token: str = Header(default=""),
    x_student_id: str = Header(default=""),
):
    # 1. Server misconfiguration guard
    if client is None:
        return JSONResponse(
            status_code=500,
            content={"error": {"message": "Proxy is missing OPENAI_API_KEY.", "type": "config_error"}},
        )

    # 2. Authentication
    token = _extract_token(authorization, x_classroom_token)
    if token != CLASSROOM_SECRET:
        return JSONResponse(
            status_code=401,
            content={"error": {"message": "Invalid or missing classroom token.", "type": "auth_error"}},
        )

    # 3. Rate limiting (per student if we know who they are, else per IP)
    identifier = x_student_id.strip() or (request.client.host if request.client else "unknown")
    if _is_rate_limited(identifier):
        return JSONResponse(
            status_code=429,
            content={
                "error": {
                    "message": (
                        f"Rate limit reached ({RATE_LIMIT_MAX} requests per "
                        f"{RATE_LIMIT_WINDOW}s). Please wait a moment and try again."
                    ),
                    "type": "rate_limit_error",
                }
            },
        )

    # 4. Parse the incoming OpenAI-style body
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(
            status_code=400,
            content={"error": {"message": "Request body must be valid JSON.", "type": "invalid_request"}},
        )

    messages = body.get("messages")
    if not isinstance(messages, list) or not messages:
        return JSONResponse(
            status_code=400,
            content={"error": {"message": "'messages' is required and must be a non-empty list.", "type": "invalid_request"}},
        )

    # 5. Enforce guardrails: force cheap model, cap tokens, block streaming.
    requested_max = body.get("max_tokens")
    if isinstance(requested_max, int) and requested_max > 0:
        max_tokens = min(requested_max, MAX_TOKENS_CAP)
    else:
        max_tokens = MAX_TOKENS_CAP

    safe_params = {
        "model": ALLOWED_MODEL,          # ignore whatever the client asked for
        "messages": messages,
        "max_tokens": max_tokens,
        "stream": False,                 # keep responses simple for students
    }
    # Pass through a few harmless, well-behaved tuning knobs if present.
    if isinstance(body.get("temperature"), (int, float)):
        safe_params["temperature"] = body["temperature"]

    # 6. Forward to OpenAI and return an OpenAI-compatible response
    try:
        completion = client.chat.completions.create(**safe_params)
        return JSONResponse(content=completion.model_dump())
    except Exception as e:
        return JSONResponse(
            status_code=502,
            content={"error": {"message": f"Upstream AI request failed: {e}", "type": "upstream_error"}},
        )
