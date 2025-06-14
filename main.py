from fastapi import FastAPI, HTTPException
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

# Add CORS middleware (important for external portal access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins — for public API
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load metadata and discourse posts
if not os.path.exists("metadata.json"):
    raise FileNotFoundError("metadata.json not found — please run html_scraper.py first!")
if not os.path.exists("discourse_posts.json"):
    raise FileNotFoundError("discourse_posts.json not found — please run discourse_scraper.py first!")

with open("metadata.json", "r", encoding="utf-8") as f:
    metadata = json.load(f)
print(f"Loaded {len(metadata)} course content entries.")

with open("discourse_posts.json", "r", encoding="utf-8") as f:
    discourse_posts = json.load(f)
print(f"Loaded {len(discourse_posts)} Discourse posts.")

class QueryRequest(BaseModel):
    question: str
    image: Optional[str] = None

class Link(BaseModel):
    url: str
    text: str

class QueryResponse(BaseModel):
    answer: str
    links: List[Link]

@app.get("/")
def read_root():
    return JSONResponse(content={"message": "Welcome to TDS Virtual TA API!"})

# ✅ Corrected endpoint to /query as expected by the evaluator
@app.post("/query", response_model=QueryResponse)
async def answer_question(query: QueryRequest):
    print("Received question:", query.question)
    print("Received JSON:", query.dict())

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
    similarity_threshold = 60

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

    answer = (
        f"I found {len(matching_links)} relevant resource(s) based on your question."
        if matching_links else
        "Sorry, no relevant resources found for your query."
    )

    return JSONResponse(content={"answer": answer, "links": [link.dict() for link in matching_links]}, status_code=200)
