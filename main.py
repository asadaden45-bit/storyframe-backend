import os
from time import time
from typing import Dict, List

import httpx
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from story_generator import generate_story


app = FastAPI(
    title="StoryFrame Backend",
    version="0.1.0",
)

# CORS (browser access)
# Keep CodePen while testing; replace YOURDOMAIN.COM later.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://codepen.io",
        "https://cdpn.io",
        "https://YOURDOMAIN.COM",
        "https://www.YOURDOMAIN.COM",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────
# Configuration
# ─────────────────────────────────────

ALLOWED_STYLES = {"default", "dark", "kids"}

RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX_REQUESTS = 10

STORYFRAME_APP_KEY = os.getenv("STORYFRAME_APP_KEY", "").strip()

client_requests: Dict[str, List[float]] = {}

# ─────────────────────────────────────
# Security & Limits
# ─────────────────────────────────────


def require_app_key(
    x_api_key: str | None = Header(None, alias="x-api-key"),
    x_storyframe_app: str | None = Header(None, alias="x-storyframe-app"),
) -> None:
    provided = (x_api_key or x_storyframe_app or "").strip()

    if not STORYFRAME_APP_KEY or provided != STORYFRAME_APP_KEY:
        raise HTTPException(status_code=403, detail

