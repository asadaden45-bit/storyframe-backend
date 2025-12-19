from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI(
    title="StoryFrame Backend",
    version="0.1.0",
)


def generate_story(prompt: str) -> str:
    return f"Once upon a time, {prompt}. And they lived happily ever after."


class StoryRequest(BaseModel):
    prompt: str


@app.get("/")
def root():
    return {"status": "StoryFrame backend is running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/stories")
def create_story(request: StoryRequest):
    story = generate_story(request.prompt)
    return {
        "story": story
    }




