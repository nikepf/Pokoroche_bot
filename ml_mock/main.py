from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI(title="Mock ML API")

class ImportanceRequest(BaseModel):
    text: str
    context: dict | None = None

class ImportanceResponse(BaseModel):
    importance: float

class TopicsRequest(BaseModel):
    text: str

class TopicsResponse(BaseModel):
    topics: List[str]


@app.post("/importance", response_model=ImportanceResponse)
async def importance(_: ImportanceRequest):
    return {"importance": 0.5}


@app.post("/topics", response_model=TopicsResponse)
async def topics(_: TopicsRequest):
    return {"topics": ["mock", "test", "demo"]}


@app.get("/health")
async def health():
    return {"status": "ok"}
