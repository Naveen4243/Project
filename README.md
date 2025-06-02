# 📚 TDS Virtual TA Scraper

A simple scraper tool to extract content from the **Tools of Data Science (TDS)** course website and Discourse forum, saving them as markdown files with metadata for offline study and analysis.  
This project was built as part of the **IIT Madras BSc Data Science program.**

---

## 📌 Project Repository

🔗 [GitHub Repository](https://github.com/Naveen4243/Project)  
👤 GitHub: [Naveen4243](https://github.com/Naveen4243)

---

## 📁 Project Structure
tds-virtual-ta-scraper/

├── scrapers/

│ ├── discourse_scraper.py

│ └── html_scraper.py

├── markdown_files/

│ └── Tools_in_Data_Science.md

├── discourse_posts.json

├── metadata.json

├── requirements.txt

├── auth.json

└── README.md


---

## 📦 Installation

1. **Clone this repository**

```bash
git clone https://github.com/Naveen4243/Project.git
cd Project
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Install Playwright Browsers (only needed once)**

```bash
playwright install
```

---

## 🚀 How to Use
### ✅ Scrape Discourse Posts
Run:
```bash
python scrapers/discourse_scraper.py
```
❗ On first run — it will launch a browser window.

👉 Login with your Google IITM student email.

👉 Then click ▶️ Resume in the Playwright control bar.

👉 It’ll save your session to auth.json for future runs.


After login, it’ll scrape and create:

✅ discourse_posts.json — containing clean structured posts from 01 Jan 2025 to 14 Apr 2025.


### ✅ Scrape TDS Course Pages
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

## 📑 Configuration
👉 BASE_URL and BASE_ORIGIN are set in html_scraper.py.

👉 Output folder: markdown_files/

👉 Metadata file: metadata.json

👉 Auth config (optional for Discourse API): auth.json

---

## 📝 Dependencies
Listed in requirements.txt:

```bash
playwright
beautifulsoup4
markdownify
```

---

## 📌 Notes
👉 Make sure to manually create the markdown_files/ folder if it doesn't exist. The script will auto-create it if missing.

👉 Discourse scraper (discourse_scraper.py) is under development.

---

## 📖 License
This project is for educational use as part of the IIT Madras BSc Data Science - Tools of Data Science course.

---

## ✨ Author
Naveen Raj R
