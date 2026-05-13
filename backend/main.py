from fastapi import FastAPI, HTTPException


app = FastAPI(
    title="StoryBook Agent Backend",
    version="0.1.0",
)

@app.get("/")
def healthcheck():
    return {
        "status": "ok",
        "service": "StoryBook Agent Backend",
    }

@app.post("/initialize")
def initialize_story():
    