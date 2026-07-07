import os
import random
import datetime
import requests
import xml.etree.ElementTree as ET
from github import Github

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPOSITORY")

g = Github(GITHUB_TOKEN)

CATEGORIES = [
    "Sports", "Lifestyle", "Stock News", "Cooking", "Health", 
    "Film Industry", "Movie Review", "Anime Latest", "Technology", 
    "Business & Startups", "Global Facts"
]

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
    return "Market & Global Dynamic System Breakthroughs"

def generate_dual_content(topic, category):
    backup_article = f"<h2>{topic} — Key Developments Revealed</h2><p>Major dynamic changes are unfolding rapidly globally in the {category} sector. Experts suggest close monitoring of these latest structural updates moving forward.</p><p>As the situation develops further, additional operational metrics will define the next cycle of industry progress.</p>"
    backup_short = f"<h4>Quick Update on {topic}</h4><p>Latest updates regarding {topic} under {category} section are currently processing live across media networks.</p>"

    if not GEMINI_API_KEY:
        return backup_article, backup_short

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    prompt = f"Write a premium human journalistic news update for INFOVEX about '{topic}' under category '{category}'. Avoid AI phrases. Wrap inside [START_ARTICLE]...[END_ARTICLE] with h2 and p tags, and short inside [START_SHORT]...[END_SHORT] with h4 and p tags."
    
    try:
        response = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=15)
        res_json = response.json()
        raw_text = res_json['candidates'][0]['content']['parts'][0]['text']
        raw_text = raw_text.replace("```html", "").replace("```", "").strip()
        
        article = raw_text.split("[START_ARTICLE]")[1].split("[END_ARTICLE]")[0].strip()
        short = raw_text.split("[START_SHORT]")[1].split("[END_SHORT]")[0].strip()
        return article, short
    except Exception:
        return backup_article, backup_short

def update_platform(article_body, short_body, category):
    repo = g.get_repo(GITHUB_REPO)
    contents = repo.get_contents("index.html", ref="main")
    html_code = contents.decoded_content.decode("utf-8")
    
    timestamp = datetime.datetime.now().strftime("%B %d, %Y • %I:%M %p")
    
    full_post_template = f"""
    <div class="post-card">
        <div class="meta">{timestamp} • {category}</div>
        {article_body}
    </div>
    """
    
    short_template = f"""
    <div class="short-card">
        <div class="short-tag">{category}</div>
        {short_body}
    </div>
    """
    
    # Naye index.html ke sath 100% accurate match
    article_placeholder = '<div id="posts-container">'
    short_placeholder = '<div class="shorts-sticky" id="shorts-container">'
    
    if article_placeholder in html_code and short_placeholder in html_code:
        html_code = html_code.replace(article_placeholder, f"{article_placeholder}\n{full_post_template}")
        html_code = html_code.replace(short_placeholder, f"{short_placeholder}\n{short_template}")
        
        repo.update_file(contents.path, f"AI Desk Live Update: {category}", html_code, contents.sha, branch="main")
        print("🎉 Platform updated with safe fallback data!")
    else:
        print("❌ Error: Target placeholders missing in index.html structure.")

if __name__ == "__main__":
    selected_category = random.choice(CATEGORIES)
    trending_topic = get_trending_topic(selected_category)
    article_html, short_html = generate_dual_content(trending_topic, selected_category)
    update_platform(article_html, short_html, selected_category)
