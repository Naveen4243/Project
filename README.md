# 📚 TDS Virtual TA Scraper

A simple scraper tool to extract content from the **Tools of Data Science (TDS)** course website and Discourse forum, saving them as markdown files with metadata for offline study and analysis.  
This project was built as part of the **IIT Madras BSc Data Science program.**

---

## 📌 Project Repository

🔗 [GitHub Repository](https://github.com/Naveen4243/Project)  
👤 GitHub: [Naveen4243](https://github.com/Naveen4243)

---

## 📁 Project Structure
project/

├── scrapers/

│ ├── discourse_scraper.py

│ └── html_scraper.py

├── markdown_files/

│ └── Tools_in_Data_Science.md

├── discourse_posts.json

├── metadata.json

├── requirements.txt

├── auth.json

├── main.py

├── sample.webp

├── image.txt

├── received_image.webp

├── LICENSE

└── README.md


---

## 📦 Installation

1. **Clone this repository**

```bash
git clone https://github.com/Naveen4243/Project.git
cd Project

```
2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Install Playwright Browsers (only needed once)

```bash
playwright install
```

---

## 🚀 How to Use
### 1. Scrape Discourse Posts
Run:
```bash
python scrapers/discourse_scraper.py
```
❗ On first run — it will launch a browser window.

👉 Login with your Google IITM student email.

👉 Then click ▶️ Resume in the Playwright control bar.

👉 It’ll save your session to auth.json for future runs.


After login, it’ll scrape and create:

discourse_posts.json — containing clean structured posts from 01 Jan 2025 to 14 Apr 2025.


### 2. Scrape TDS Course Pages
Run:

```bash
python scrapers/html_scraper.py
```

This will:

👉 Visit each page in the TDS course site

👉 Convert content to Markdown

👉 Save it in the markdown_files/ folder

👉 Log metadata into metadata.json

---

## Create and Run the FastAPI-based Virtual TA API
The API serves as a question-answer interface using the scraped metadata and supports optional image upload.

1. Start the API server

```bash
uvicorn main:app --reload
```

2. API Endpoints

👉 GET /
    Returns a welcome message.

👉 POST /api/
    Accepts JSON body with:
```bash
{

  "question": "Your question here",
  
  "image": "Optional base64-encoded image string"
  
}
```

3. API Behavior

👉 The API searches the metadata entries for keywords matching the question text.

👉 If an image is provided (base64 encoded), it saves the image locally as received_image.webp.

👉 Responds with a JSON object containing:

  👉 answer: a summary of relevant resources found

  👉 links: list of matched metadata URLs and titles

Example JSON response:
```bash
{
  "answer": "I found 1 relevant resource(s) based on your question.",
  "links": [
    {
      "url": "https://tds.s-anand.net/#/2025-01",
      "text": "Tools in Data Science"
    }
  ]
}
```
---

## 📖 License
This project is for educational use as part of the IIT Madras BSc Data Science - Tools of Data Science course.

---

## ✨ Author
Naveen Raj R
