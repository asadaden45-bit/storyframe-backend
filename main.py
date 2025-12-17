from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"status": "StoryFrame backend is running"}
