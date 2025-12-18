
from fastapi import FastAPI

app = FastAPI(
    title="StoryFrame Backend",
    version="0.1.0",
)


@app.get("/")
def root():
    return {"status": "StoryFrame backend is running"}

@app.get("/health")
def health():
    return {"status": "ok"}

from pydantic import BaseModel


class StoryRequest(BaseModel):
    prompt: str


@app.post("/stories")
def create_story(request: StoryRequest):
    return {
        "message": "Story received",
        "prompt": request.prompt
    }



