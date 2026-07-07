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

CATEGORIES = ["Sports", "Lifestyle", "Stock News", "Cooking", "Technology", "Business"]

GLOBAL_STABLE_IMAGES = [
    "https://images.unsplash.com/photo-1504711434969-e33886168f5c?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1495020689067-958852a6565d?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1505373877841-8d25f7d46678?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1511512578047-dfb367046420?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1508098682722-e99c43a406b2?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1200&q=80"
]

def get_trending_topic(selected_category):
    try:
        url = "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en"
        response = requests.get(url, timeout=10)
        root = ET.fromstring(response.content)
        titles = [item.find('title').text for item in root.findall('.//item')]
        if titles:
            return random.choice(titles[:15]).split(" - ")[0]
    except:
        pass
    return "Market & Global Dynamic System Breakthroughs"

def generate_dual_content(topic, category):
    selected_pics = random.sample(GLOBAL_STABLE_IMAGES, 3)
    img1 = f'<img src="{selected_pics[0]}" alt="Breaking Header">'
    img2 = f'<img src="{selected_pics[1]}" alt="Core Analysis">'
    img3 = f'<img src="{selected_pics[2]}" alt="Editorial Context">'
    
    backup_article = f"""
    {img1}
    <p>In a notable shift for regional observation circles, the latest developments surrounding <b>{topic}</b> have captured immediate attention.</p>
    <p>As experts study the core logistics, initial updates highlight a series of process compliance milestones that demand focus over the coming transition cycle.</p>
    {img2}
    <p>Furthermore, execution teams advise tracking authorized portals and official releases closely for direct instructions rather than unofficial bulletins.</p>
    {img3}
    <p>Ultimately, the long-term path will depend heavily on how smoothly localized platforms integrate these updates.</p>
    """
    
    backup_short = f"<h4>Quick Update on {topic}</h4><p>The operational framework for {topic} is expanding under the {category} matrix.</p>"

    if not GEMINI_API_KEY:
        return backup_article, backup_short

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    prompt = f"Act as a journalist. Write 4 paragraphs about '{topic}' for category '{category}'. Avoid AI buzzwords. Wrap main text in [START_ARTICLE] and [END_ARTICLE] tags with <p>. Wrap short summary in [START_SHORT] and [END_SHORT] tags."
    
    try:
        response = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=15)
        raw_text = response.json()['candidates'][0]['content']['parts'][0]['text']
        article = raw_text.split("[START_ARTICLE]")[1].split("[END_ARTICLE]")[0].strip()
        short = raw_text.split("[START_SHORT]")[1].split("[END_SHORT]")[0].strip()
        
        paras = article.split("</p>")
        if len(paras) >= 4:
            article = f"{img1}\n{paras[0]}</p>\n{paras[1]}</p>\n{img2}\n{paras[2]}</p>\n{img3}\n" + "\n".join(paras[3:])
        else:
            article = f"{img1}\n{article}\n{img2}"
        return article, short
    except:
        return backup_article, backup_short

def update_platform(article_body, short_body, category, topic):
    repo = g.get_repo(GITHUB_REPO)
    contents = repo.get_contents("index.html", ref="main")
    html_code = contents.decoded_content.decode("utf-8")
    
    timestamp = datetime.datetime.now().strftime("%B %d, %Y • %I:%M %p")
    
    # 100% SAFE INJECTION STRINGS (No Replace Empty)
    full_post = f'\n\n<div class="post-card"><div class="meta">{timestamp} • {category}</div><h2>{topic}</h2><div class="preview-text">Latest comprehensive editorial report released.</div><div class="full-story">{article_body}</div></div>'
    short_post = f'\n\n<div class="short-card"><div class="short-tag">{category}</div>{short_body}</div>'
    
    if '' in html_code:
        html_code = html_code.replace('', full_post)
    elif '<div id="posts-container">' in html_code:
        html_code = html_code.replace('<div id="posts-container">', f'<div id="posts-container">{full_post}')
        
    if '' in html_code:
        html_code = html_code.replace('', short_post)
    elif '<div class="shorts-sticky" id="shorts-container">' in html_code:
        html_code = html_code.replace('<div class="shorts-sticky" id="shorts-container">', f'<div class="shorts-sticky" id="shorts-container">{short_post}')

    repo.update_file(contents.path, f"AI Auto-Post: {category}", html_code, contents.sha, branch="main")

if __name__ == "__main__":
    cat = random.choice(CATEGORIES)
    top = get_trending_topic(cat)
    art, shrt = generate_dual_content(top, cat)
    update_platform(art, shrt, cat, top)
