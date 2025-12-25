import os
from time import time
from typing import Dict, List

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from story_generator import generate_story


app = FastAPI(
    title="StoryFrame Backend",
    version="0.1.0",
)

# CORS (for browser tests like CodePen)
# IMPORTANT: allow_credentials must be False if allow_origins uses specific sites or "*".
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://codepen.io",
        "https://cdpn.io",
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

def require_android_app(
    x_storyframe_app: str = Header(..., alias="x-storyframe-app"),
) -> None:
    # Allow BOTH during transition:
    # 1) old value "android"
    # 2) secret key from STORYFRAME_APP_KEY env var
    allowed = {"android"}
    if STORYFRAME_APP_KEY:
        allowed.add(STORYFRAME_APP_KEY)

    if x_storyframe_app not in allowed:
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

    # Keep only requests inside the window
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


@app.post("/stories", response_model=StoryResponse)
def create_story(
    request: StoryRequest,
    http_request: Request,
    _: None = Depends(require_android_app),
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
