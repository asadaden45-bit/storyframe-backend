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
# IMPORTANT: allow_credentials=False so allow_origins=["*"] works correctly.
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

client_requests: Dict[str, List[float]] = {}

# ─────────────────────────────────────
# Security & Limits
# ─────────────────────────────────────


def require_android_app(
    x_storyframe_app: str = Header(..., alias="x-storyframe-app"),
) -> None:
    if x_storyframe_app != "android":
        raise HTTPException(status_code=403, detail="Unauthorized client")


def get_client_ip(request: Request) -> str:
    # Works behind proxies too (Render/Cloudflare may set this)
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
