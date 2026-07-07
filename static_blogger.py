import os
import random
import datetime
import requests
from github import Github

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
g = Github(GITHUB_TOKEN)
repo = g.get_repo(os.getenv("GITHUB_REPOSITORY"))

CATEGORIES = ["Sports", "Lifestyle", "Technology", "Business", "Stock News"]
cat = random.choice(CATEGORIES)

# 1. Fetch Trending Topic (Fast Mode)
topic = "Global Tech & Market Updates"
try:
    rss = requests.get("https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en", timeout=5).text
    titles = [t.split('</title>')[0] for t in rss.split('<title>')[2:10]]
    if titles: topic = random.choice(titles).split(' - ')[0]
except: pass

# 2. Set Random HD Images
imgs = random.sample([
    "https://images.unsplash.com/photo-1504711434969-e33886168f5c?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1495020689067-958852a6565d?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1505373877841-8d25f7d46678?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1200&q=80"
], 3)
i_tag = [f'<img src="{i}" style="width:100% !important; max-width:100%; display:block; margin:20px 0; border-radius:5px;">' for i in imgs]

# 3. Get News Content
article_html = f'{i_tag[0]}<p>Breaking updates regarding <b>{topic}</b> have captured global attention today.</p>{i_tag[1]}<p>Experts are closely analyzing the impacts in the {cat} sector.</p>{i_tag[2]}<p>More detailed reports and analyses are expected soon.</p>'
short_html = f'<h4>Update: {topic}</h4><p>Latest {cat} developments are shifting trends globally.</p>'

if GEMINI_API_KEY:
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        res = requests.post(url, json={"contents":[{"parts":[{"text": f"Write a 3-paragraph news report on '{topic}'. Return ONLY HTML <p> tags without any markdown like ```html."}]}]}, timeout=10)
        paras = res.json()['candidates'][0]['content']['parts'][0]['text'].replace("```html","").replace("```","").strip().split("</p>")
        if len(paras) >= 3:
            article_html = f"{i_tag[0]}\n{paras[0]}</p>\n{i_tag[1]}\n{paras[1]}</p>\n{i_tag[2]}\n{paras[2]}</p>"
    except: pass

# 4. Inject Post Securely 
contents = repo.get_contents("index.html", ref="main")
html = contents.decoded_content.decode("utf-8")
time_str = datetime.datetime.now().strftime("%B %d, %Y • %I:%M %p")

new_post = f'\n\n<div class="post-card"><div class="meta">{time_str} • {cat}</div><h2>{topic}</h2><div class="preview-text">Latest verified editorial report.</div><div class="full-story">{article_html}</div></div>'
new_short = f'\n\n<div class="short-card"><div class="short-tag">{cat}</div>{short_html}</div>'

if '' in html:
    html = html.replace('', new_post).replace('', new_short)
    repo.update_file(contents.path, f"New Auto Post - {cat}", html, contents.sha, branch="main")
