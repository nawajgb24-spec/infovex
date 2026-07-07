import os
import random
import datetime
import requests
import json
import xml.etree.ElementTree as ET
from github import Github

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPOSITORY")

g = Github(GITHUB_TOKEN)

CATEGORIES = ["Sports", "Lifestyle", "Stock News", "Cooking", "Health", "Film Industry", "Movie Review", "Anime Latest", "Technology", "Business & Startups", "Global Facts"]

def get_trending_topic(selected_category):
    try:
        url = "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en"
        response = requests.get(url, timeout=10)
        root = ET.fromstring(response.content)
        titles = [item.find('title').text for item in root.findall('.//item')]
        if titles:
            return random.choice(titles[:15]).split(" - ")[0]
    except Exception:
        pass
    return f"Latest Updates on {selected_category} Ecosystem"

def generate_dual_content(topic, category):
    backup_article = f"<h2>{topic} — Fresh Editorial Analysis</h2><p>Critical structural shifts are currently taking place globally within the {category} landscape. Observers emphasize monitoring these recent events closely.</p>"
    backup_short = f"<h4>The Core of {topic}</h4><p>Latest dynamic points regarding {topic} have been filed directly under the {category} tracker desk.</p>"

    if not GEMINI_API_KEY:
        return backup_article, backup_short

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    prompt = f"Write a human news report for INFOVEX about '{topic}' under category '{category}'. Wrap full report inside [START_ARTICLE]...[END_ARTICLE] with h2 and p tags, and short snippet inside [START_SHORT]...[END_SHORT] with h4 and p tags."
    
    try:
        response = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=15)
        raw_text = response.json()['candidates'][0]['content']['parts'][0]['text']
        article = raw_text.split("[START_ARTICLE]")[1].split("[END_ARTICLE]")[0].strip()
        short = raw_text.split("[START_SHORT]")[1].split("[END_SHORT]")[0].strip()
        return article, short
    except Exception:
        return backup_article, backup_short

def update_platform(article_body, short_body, category):
    repo = g.get_repo(GITHUB_REPO)
    timestamp = datetime.datetime.now().strftime("%B %d, %Y • %I:%M %p")
    
    # 1. Existing Data Read Mode
    try:
        contents = repo.get_contents("data.js", ref="main")
        raw_js = contents.decoded_content.decode("utf-8")
        json_str = raw_js.replace("const blogData = ", "").strip()
        db = json.loads(json_str)
    except Exception:
        db = {"articles": [], "shorts": []}
        contents = None

    # 2. Append fresh streams to data arrays
    db["articles"].insert(0, {"date": timestamp, "category": category, "content": article_body})
    db["shorts"].insert(0, {"category": category, "content": short_body})

    # Limit to keep top 30 to stay lightning fast
    db["articles"] = db["articles"][:30]
    db["shorts"] = db["shorts"][:30]

    new_js_content = f"const blogData = {json.dumps(db, indent=2)};"

    # 3. Write data state back to GitHub
    if contents:
        repo.update_file(contents.path, f"Data stream: {category}", new_js_content, contents.sha, branch="main")
    else:
        repo.create_file("data.js", "Data stream initializing", new_js_content, branch="main")
    print("🎉 Data file synchronised successfully!")

if __name__ == "__main__":
    cat = random.choice(CATEGORIES)
    topic = get_trending_topic(cat)
    art, sh = generate_dual_content(topic, cat)
    update_platform(art, sh, cat)
