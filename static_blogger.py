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
    print(f"🔄 Fetching latest live news for category: {selected_category}...")
    try:
        url = "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en"
        response = requests.get(url, timeout=10)
        root = ET.fromstring(response.content)
        
        titles = [item.find('title').text for item in root.findall('.//item')]
        if titles:
            clean_title = random.choice(titles[:15]).split(" - ")[0]
            return clean_title
    except Exception as e:
        print(f"⚠️ RSS Fetch error, using category smart baseline: {e}")
    
    backups = {
        "Sports": "India Cricket Team Match Strategy and Upcoming Tournament Updates",
        "Stock News": "Stock Market Highlights Today Nifty Sensex Top Gainers and Losers",
        "Technology": "Latest AI Breakthroughs and New Smartphone Launches This Week",
        "Anime Latest": "Trending Anime Episodes Streaming Updates and Manga Releases",
        "Health": "Top Wellness Habits and Balanced Diet Guidelines for Longevity",
        "Cooking": "Viral Food Recipes and New Global Fusion Culinary Trends",
        "Lifestyle": "Modern Fashion Trends and Minimalist Living Design Tips",
        "Film Industry": "Box Office Collection Records and Upcoming Cinema Teasers",
        "Movie Review": "Honest Critique of the Latest Trending Over-The-Top Web Series Release",
        "Business & Startups": "Innovative Startup Models Changing Indian Ecosystem Economy",
        "Global Facts": "Deep Mind Mysteries and Incredible Historical Unexplained Facts"
    }
    return backups.get(selected_category, "Global Trending Breakthrough Updates")

def generate_dual_content(topic, category):
    print(f"🧠 Gemini AI generating unique News Article + Google Short for: '{topic}'...")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    prompt = f"""
    You are a premium human journalist writing for INFOVEX. Write a 100% unique, human-like news update about '{topic}' under the category '{category}'.
    
    CRITICAL ANTI-BAN RULES:
    - Never use robotic AI filler words (e.g., delve, testament, furthermore, revolutionized, landscape, beacon).
    - Write in a natural, straight-to-the-point journalistic tone.
    - Zero plagiarism. Content must be fresh.
    
    You must output EXACTLY two clear parts enclosed in tags, like this:
    
    [START_ARTICLE]
    <h2>An Catchy, Organic Title Relating to {topic}</h2>
    <p>A comprehensive and deeply factual first paragraph about the core event...</p>
    <p>A second detailed paragraph describing the future impacts or background context...</p>
    [END_ARTICLE]
    
    [START_SHORT]
    <h4>Fast Snippet Headline for {topic}</h4>
    <p>A brief 2-3 sentence engaging fact or sharp summary that works perfectly as a Google Short story format.</p>
    [END_SHORT]
    """
    
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    response = requests.post(url, json=payload)
    res_json = response.json()
    
    try:
        raw_text = res_json['candidates'][0]['content']['parts'][0]['text']
        raw_text = raw_text.replace("```html", "").replace("```", "").strip()
        
        article = raw_text.split("[START_ARTICLE]")[1].split("[END_ARTICLE]")[0].strip()
        short = raw_text.split("[START_SHORT]")[1].split("[END_SHORT]")[0].strip()
        
        return article, short
    except Exception:
        raise Exception(f"AI Generation Failed or Parser Mismatch. Response: {res_json}")

def update_platform(article_body, short_body, category):
    print("📤 Injecting data streams safely into index.html placeholders...")
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
    
    # Exact tag string match clean strategy
    article_placeholder = '<div id="posts-container">'
    short_placeholder = '<div class="shorts-sticky" id="shorts-container">'
    
    if article_placeholder in html_code and short_placeholder in html_code:
        html_code = html_code.replace(article_placeholder, f"{article_placeholder}\n{full_post_template}")
        html_code = html_code.replace(short_placeholder, f"{short_placeholder}\n{short_template}")
        
        repo.update_file(
            contents.path, 
            f"AI Desk: Updated {category} Feed & Google Shorts Stream", 
            html_code, 
            contents.sha, 
            branch="main"
        )
        print("🎉 Platform updated live successfully!")
    else:
        print("❌ Error: Target placeholders missing in index.html structure.")

if __name__ == "__main__":
    try:
        selected_category = random.choice(CATEGORIES)
        trending_topic = get_trending_topic(selected_category)
        
        article_html, short_html = generate_dual_content(trending_topic, selected_category)
        update_platform(article_html, short_html, selected_category)
    except Exception as e:
        print(f"❌ Execution Fault: {e}")
