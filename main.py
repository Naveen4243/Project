from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from fastapi.responses import JSONResponse
import base64
import json
import os

app = FastAPI()

# Load metadata.json on startup
if not os.path.exists("metadata.json"):
    raise FileNotFoundError("metadata.json not found — please run your scraper first!")

with open("metadata.json", "r", encoding="utf-8") as f:
    metadata = json.load(f)
print(f"Loaded {len(metadata)} metadata entries.")

# Request model
class QueryRequest(BaseModel):
    question: str
    image: Optional[str] = None  # base64 image string

# Response models
class Link(BaseModel):
    url: str
    text: str

class QueryResponse(BaseModel):
    answer: str
    links: List[Link]

@app.get("/")
def read_root():
    return JSONResponse(content={"message": "Welcome to TDS Virtual TA API!"})

@app.post("/api/", response_model=QueryResponse)
def answer_question(query: QueryRequest):
    print("Received question:", query.question)

    # Save image if present
    if query.image:
        try:
            image_data = base64.b64decode(query.image)
            with open("received_image.webp", "wb") as f:
                f.write(image_data)
            print("Image received and saved.")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid image data: {str(e)}")

    question_lower = query.question.lower()
    matching_links: List[Link] = []

    for entry in metadata:
        # Check if the question text appears in title or filename (case-insensitive)
        title_lower = entry.get("title", "").lower()
        filename_lower = entry.get("filename", "").lower()
        if question_lower in title_lower or question_lower in filename_lower:
            matching_links.append(Link(url=entry["original_url"], text=entry["title"]))

    # If no direct match, fallback: try keyword substring matching on question words
    if not matching_links:
        keywords = question_lower.split()
        for entry in metadata:
            title_lower = entry.get("title", "").lower()
            if any(kw in title_lower for kw in keywords):
                matching_links.append(Link(url=entry["original_url"], text=entry["title"]))

    if matching_links:
        answer = f"I found {len(matching_links)} relevant resource(s) based on your question."
    else:
        answer = "Sorry, no relevant resources found for your query."

    return QueryResponse(answer=answer, links=matching_links)
