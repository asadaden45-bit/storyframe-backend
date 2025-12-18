from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"status": "StoryFrame backend is running"}

@app.get("/health")
def health():
    return {"status": "ok"}

