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
        raise HTTPException(status_code=403, detail="Unauthorized client")


def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


def check_rate_limit(client_id: str) -> None:
    now = time()
    timestamps = client_requests.get(client_id, [])

    timestamps = [t for t in timestamps if now - t < RATE_LIMIT_WINDOW]

    if len(timestamps) >= RATE_LIMIT_MAX_REQUESTS:
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Please slow down.",
        )

    timestamps.append(now)
    client_requests[client_id] = timestamps


# ─────────────────────────────────────
# Models
# ─────────────────────────────────────


class StoryRequest(BaseModel):
    prompt: str
    style: str = "default"


class StoryResponse(BaseModel):
    story: str


# ─────────────────────────────────────
# Routes
# ─────────────────────────────────────


@app.get("/")
def root():
    return {"status": "StoryFrame backend is running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post(
    "/stories",
    response_model=StoryResponse,
    dependencies=[Depends(require_app_key)],
)
def create_story(
    request: StoryRequest,
    http_request: Request,
):
    client_ip = get_client_ip(http_request)
    check_rate_limit(client_ip)

    if request.style not in ALLOWED_STYLES:
        raise HTTPException(
            status_code=400,
            detail="Invalid style. Allowed: default, dark, kids",
        )

    story = generate_story(request.prompt, request.style)
    return {"story": story}


@app.post("/web/stories", response_model=StoryResponse)
async def web_create_story(request: StoryRequest, http_request: Request):
    """
    Browser-safe endpoint:
    - No API key required from the browser
    - Backend calls the protected /stories endpoint internally with the secret key
    """
    client_ip = get_client_ip(http_request)
    check_rate_limit(client_ip)

    if request.style not in ALLOWED_STYLES:
        raise HTTPException(
            status_code=400,
            detail="Invalid style. Allowed: default, dark, kids",
        )

    if not STORYFRAME_APP_KEY:
        raise HTTPException(status_code=500, detail="Server missing STORYFRAME_APP_KEY")

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(
            "https://storyframe-backend.onrender.com/stories",
            headers={"x-api-key": STORYFRAME_APP_KEY},
            json={"prompt": request.prompt, "style": request.style},
        )

    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)

    return resp.json()
