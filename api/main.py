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

from mangum import Mangum  # add this line for ASGI-to-WSGI adapter

API_KEY = os.getenv("API_KEY")

app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if not os.path.exists("api/metadata.json"):
    raise FileNotFoundError("metadata.json not found — please run html_scraper.py first!")

if not os.path.exists("api/discourse_posts.json"):
    raise FileNotFoundError("discourse_posts.json not found — please run discourse_scraper.py first!")

with open("api/metadata.json", "r", encoding="utf-8") as f:
    metadata = json.load(f)

with open("api/discourse_posts.json", "r", encoding="utf-8") as f:
    discourse_posts = json.load(f)

class QueryRequest(BaseModel):
    question: str
    image: Optional[str] = None

class Link(BaseModel):
    url: str
    text: str

class QueryResponse(BaseModel):
    answer: str
    links: List[Link]

@app.api_route("/", methods=["GET", "POST"])
async def root(request: Request):
    return JSONResponse(
        content={"answer": "Welcome to TDS Virtual TA API!", "links": []},
        status_code=200
    )

@app.post("/api/", response_model=QueryResponse)
async def answer_question(query: QueryRequest):
    question_lower = query.question.lower()
    matching_links: List[Link] = []
    similarity_threshold = 65

    if query.image:
        try:
            image_data = base64.b64decode(query.image)
            with open("/tmp/received_image.webp", "wb") as f:
                f.write(image_data)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid image data: {str(e)}")

    keywords = re.findall(r'\w+', question_lower)

    for entry in metadata:
        title = entry.get("title", "").lower()
        filename = entry.get("filename", "").lower()
        original_url = entry.get("original_url", "").lower()

        score_title = fuzz.partial_ratio(question_lower, title)
        score_filename = fuzz.partial_ratio(question_lower, filename)
        url_match = any(kw in original_url for kw in keywords)

        if max(score_title, score_filename) >= similarity_threshold or url_match:
            matching_links.append(Link(url=entry["original_url"], text=entry["title"]))

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

    if any(kw in question_lower for kw in ["exam date", "end-term", "schedule"]):
        matching_links = []

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

# ASGI handler for Vercel
handler = Mangum(app)
