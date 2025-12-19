from fastapi import FastAPI
from pydantic import BaseModel
from story_generator import generate_story


app = FastAPI(
    title="StoryFrame Backend",
    version="0.1.0",
)




class StoryRequest(BaseModel):
    prompt: str


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
    story = generate_story(request.prompt)
    return {
        "story": story
    }




