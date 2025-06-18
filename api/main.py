from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import base64
import json
import os
from rapidfuzz import fuzz
import re

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Locate JSON files relative to this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
metadata_path = os.path.join(BASE_DIR, "metadata.json")
discourse_path = os.path.join(BASE_DIR, "discourse_posts.json")

# Load metadata and discourse posts at startup
if not os.path.exists(metadata_path):
    raise FileNotFoundError("metadata.json not found — please upload it.")

if not os.path.exists(discourse_path):
    raise FileNotFoundError("discourse_posts.json not found — please upload it.")

with open(metadata_path, "r", encoding="utf-8") as f:
    metadata = json.load(f)

with open(discourse_path, "r", encoding="utf-8") as f:
    discourse_posts = json.load(f)

# Pydantic models
class QueryRequest(BaseModel):
    question: str
    image: Optional[str] = None

class Link(BaseModel):
    url: str
    text: str

class QueryResponse(BaseModel):
    answer: str
    links: List[Link]

# Root endpoint
@app.api_route("/", methods=["GET", "POST"])
async def root(request: Request):
    return JSONResponse(
        content={
            "answer": "Welcome to TDS Virtual TA API!",
            "links": []
        },
        status_code=200
    )

# /api/ endpoint — POST only
@app.post("/api/", response_model=QueryResponse)
async def answer_question(query: QueryRequest):
    question_lower = query.question.lower()
    matching_links: List[Link] = []
    similarity_threshold = 65  # tuning threshold

    # If image is included, save it (optional)
    if query.image:
        try:
            image_data = base64.b64decode(query.image)
            image_path = os.path.join(BASE_DIR, "received_image.webp")
            with open(image_path, "wb") as f:
                f.write(image_data)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid image data: {str(e)}")

    # Tokenize question for keyword matching
    keywords = re.findall(r'\w+', question_lower)

    # Match against metadata
    for entry in metadata:
        title = entry.get("title", "").lower()
        filename = entry.get("filename", "").lower()
        original_url = entry.get("original_url", "").lower()

        score_title = fuzz.partial_ratio(question_lower, title)
        score_filename = fuzz.partial_ratio(question_lower, filename)
        url_match = any(kw in original_url for kw in keywords)

        if max(score_title, score_filename) >= similarity_threshold or url_match:
            matching_links.append(Link(url=entry["original_url"], text=entry["title"]))

    # Match against Discourse posts
    for post in discourse_posts:
        topic_title = post.get("topic_title", "").lower()
        content = post.get("content", "").lower()

        score_title = fuzz.partial_ratio(question_lower, topic_title)
        score_content = fuzz.partial_ratio(question_lower, content)

        keyword_boost = 0
        for kw in ["ga3", "llm", "docker"]:
            if kw in topic_title or kw in content:
                keyword_boost += 20

        final_score = max(score_title, score_content) + keyword_boost

        if final_score >= similarity_threshold:
            matching_links.append(Link(url=post["url"], text=post["topic_title"]))

    # Special rule: If query mentions exam dates / schedule — skip matches
    if any(kw in question_lower for kw in ["exam date", "end-term", "schedule"]):
        matching_links = []

    # Build final response
    answer_text = (
        f"I found {len(matching_links)} relevant resource(s) based on your question."
        if matching_links else
        "Sorry, no relevant resources found for your query."
    )

    return JSONResponse(
        content={
            "answer": answer_text,
            "links": [link.dict() for link in matching_links]
        },
        status_code=200
    )
