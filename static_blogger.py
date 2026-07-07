import os
import sys
import random
import datetime
import requests
import xml.etree.ElementTree as ET
from github import Github
from github import Auth

print("🚀 Step 1: Script start ho gayi hai...")
sys.stdout.flush()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPOSITORY")

print("🚀 Step 2: GitHub se connect kar rahe hain...")
sys.stdout.flush()

# Naya Auth system taaki koi warning na aaye
if GITHUB_TOKEN:
    auth = Auth.Token(GITHUB_TOKEN)
    g = Github(auth=auth)
else:
    g = Github()

CATEGORIES = ["Sports", "Lifestyle", "Stock News", "Cooking", "Technology", "Business"]

GLOBAL_STABLE_IMAGES = [
    "https://images.unsplash.com/photo-1504711434969-e33886168f5c?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1495020689067-958852a6565d?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1505373877841-8d25f7d46678?auto=format&fit=crop&w=1200&q=80"
]

def get_trending_topic(selected_category):
    print(f"🚀 Step 3: Google News se '{selected_category}' ki news dhoondh rahe hain...")
    sys.stdout.flush()
    try:
        url = "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en"
        response = requests.get(url, timeout=10)
        root = ET.fromstring(response.content)
        titles = [item.find('title').text for item in root.findall('.//item')]
        if titles:
            print(f"✅ Topic mil gaya: {titles[0][:30]}...")
            return random.choice(titles[:15]).split(" - ")[0]
    except Exception as e:
        print(f"⚠️ RSS Error: {e}")
    return "Market & Global Dynamic System Breakthroughs"

def generate_dual_content(topic, category):
    print("🚀 Step 4: Content setup kar rahe hain...")
    sys.stdout.flush()
    selected_pics = random.sample(GLOBAL_STABLE_IMAGES, 3)
    img1 = f'<img src="{selected_pics[0]}" alt="Header">'
    img2 = f'<img src="{selected_pics[1]}" alt="Mid">'
    img3 = f'<img src="{selected_pics[2]}" alt="Bottom">'
    
    backup_article = f"{img1}<p>Latest developments surrounding <b>{topic}</b> have captured immediate attention.</p>{img2}<p>Execution teams advise tracking authorized portals.</p>{img3}<p>Observers continue to watch this scenario closely.</p>"
    backup_short = f"<h4>Update on {topic}</h4><p>Operational framework is expanding.</p>"

    if not GEMINI_API_KEY:
        print("⚠️ Gemini API Key nahi mili! Backup text use kar rahe hain.")
        sys.stdout.flush()
        return backup_article, backup_short

    print("🚀 Step 5: Gemini AI ko likhne bol rahe hain...")
    sys.stdout.flush()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    prompt = f"Act as a journalist. Write 4 paragraphs about '{topic}' for category '{category}'. Wrap main text in [START_ARTICLE] and [END_ARTICLE] tags with <p>. Wrap short summary in [START_SHORT] and [END_SHORT] tags."
    
    try:
        response = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=15)
        response.raise_for_status() # Agar API atki toh yahan pakdi jayegi
        raw_text = response.json()['candidates'][0]['content']['parts'][0]['text']
        article = raw_text.split("[START_ARTICLE]")[1].split("[END_ARTICLE]")[0].strip()
        short = raw_text.split("[START_SHORT]")[1].split("[END_SHORT]")[0].strip()
        print("✅ Gemini ne article likh diya!")
        sys.stdout.flush()
        
        paras = article.split("</p>")
        if len(paras) >= 4:
            article = f"{img1}\n{paras[0]}</p>\n{paras[1]}</p>\n{img2}\n{paras[2]}</p>\n{img3}\n" + "\n".join(paras[3:])
        else:
            article = f"{img1}\n{article}\n{img2}"
        return article, short
    except Exception as e:
        print(f"⚠️ Gemini API fail ho gayi: {e}. Backup use kar rahe hain.")
        sys.stdout.flush()
        return backup_article, backup_short

def update_platform(article_body, short_body, category, topic):
    print("🚀 Step 6: Website (index.html) ko update kar rahe hain...")
    sys.stdout.flush()
    try:
        repo = g.get_repo(GITHUB_REPO)
        contents = repo.get_contents("index.html", ref="main")
        html_code = contents.decoded_content.decode("utf-8")
        
        timestamp = datetime.datetime.now().strftime("%B %d, %Y • %I:%M %p")
        
        full_post = f'\n\n<div class="post-card"><div class="meta">{timestamp} • {category}</div><h2>{topic}</h2><div class="preview-text">Latest comprehensive editorial report released.</div><div class="full-story">{article_body}</div></div>'
        short_post = f'\n\n<div class="short-card"><div class="short-tag">{category}</div>{short_body}</div>'
        
        if '' in html_code:
            html_code = html_code.replace('', full_post)
            html_code = html_code.replace('', short_post)
            
        repo.update_file(contents.path, f"AI Auto-Post: {category}", html_code, contents.sha, branch="main")
        print("🎉 Step 7: SUCCESS! Naya article website par upload ho gaya.")
        sys.stdout.flush()
    except Exception as e:
        print(f"❌ Upload Error: {e}")
        sys.stdout.flush()

if __name__ == "__main__":
    cat = random.choice(CATEGORIES)
    top = get_trending_topic(cat)
    art, shrt = generate_dual_content(top, cat)
    update_platform(art, shrt, cat, top)
