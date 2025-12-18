
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

@app.post("/stories")
def create_story(prompt: str):
    return {
        "message": "Story received",
        "prompt": prompt
    }


