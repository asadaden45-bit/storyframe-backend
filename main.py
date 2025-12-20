from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from story_generator import generate_story


app = FastAPI(
    title="StoryFrame Backend",
    version="0.1.0",
)


ALLOWED_STYLES = {"default", "dark", "kids"}


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
def create_story(request: StoryRequest):
    if request.style not in ALLOWED_STYLES:
        raise HTTPException(
            status_code=400,
            detail="Invalid style. Allowed: default, dark, kids",
        )

    story = generate_story(request.prompt, request.style)
    return {"story": story}


