from time import time
from typing import Dict

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

from story_generator import generate_story


app = FastAPI(
    title="StoryFrame Backend",
    version="0.1.0",
)


ALLOWED_STYLES = {"default", "dark", "kids"}

RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX_REQUESTS = 10

client_requests: Dict[str, list] = {}


def check_rate_limit(client_id: str) -> None:
    now = time()
    requests = client_requests.get(client_id, [])

    # keep only requests inside the window
    requests = [t for t in requests if now - t < RATE_LIMIT_WINDOW]

    if len(requests) >= RATE_LIMIT_MAX_REQUESTS:
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Please slow down.",
        )

    requests.append(now)
    client_requests[client_id] = requests


class StoryRequest(BaseModel):
    prompt: str
    style: str = "default"


class StoryResponse(BaseModel):
    story: str


@app.get("/")
def root():
    return {"status": "StoryFrame backend is running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/stories", response_model=StoryResponse)
def create_story(request: StoryRequest, http_request: Request):
    client_ip = http_request.client.host
    check_rate_limit(client_ip)

    if request.style not in ALLOWED_STYLES:
        raise HTTPException(
            status_code=400,
            detail="Invalid style. Allowed: default, dark, kids",
        )

    story = generate_story(request.prompt, request.style)
    return {"story": story}

