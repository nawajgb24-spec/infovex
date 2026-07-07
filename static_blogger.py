import os
import random
import datetime
import requests
import xml.etree.ElementTree as ET
import re
from github import Github

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPOSITORY")

g = Github(GITHUB_TOKEN) if GITHUB_TOKEN else Github()

CATEGORIES = [
    "Sports", "Lifestyle", "Stock News", "Cooking", "Health", 
    "Film Industry", "Movie Review", "Anime Latest", "Technology", 
    "Business & Startups", "Global Facts"
]

GLOBAL_STABLE_IMAGES = [
    "https://images.unsplash.com/photo-1504711434969-e33886168f5c?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1495020689067-958852a6565d?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1505373877841-8d25f7d46678?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1511512578047-dfb367046420?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1508098682722-e99c43a406b2?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=1200&q=80"
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
    selected_pics = random.sample(GLOBAL_STABLE_IMAGES, min(len(GLOBAL_STABLE_IMAGES), 3))
    img1 = f'<img src="{selected_pics[0]}" alt="Breaking Header">'
    img2 = f'<img src="{selected_pics[1]}" alt="Core Analysis">'
    img3 = f'<img src="{selected_pics[2]}" alt="Editorial Context">'
    
    backup_article = f"""
    {img1}
    <p>In a notable shift for regional observation circles, the latest developments surrounding <b>{topic}</b> have captured immediate attention. Administrative departments and public stakeholders are analyzing the practical consequences of this adjustment. Frontline voices in the {category} sector suggest that these newly introduced parameters will require strategic updates across both localized networks and broader operational frameworks.</p>
    <p>As experts study the core logistics, initial updates highlight a series of process compliance milestones that demand focus over the coming transition cycle. Media platforms and panels indicate that maintaining consistency across regional distribution channels will be essential to sustain steady momentum moving forward.</p>
    {img2}
    <p>Furthermore, execution teams advise tracking authorized portals and official releases closely for direct instructions rather than unofficial bulletins. Specific operational adjustments are expected to roll out sequentially across designated systems over the next few weeks.</p>
    {img3}
    <p>Ultimately, the long-term path will depend heavily on how smoothly localized platforms integrate these updates. As administrative groups realign their approaches, observers continue to watch this scenario closely, awaiting subsequent updates from management committees.</p>
    """
    
    backup_short = f"<h4>Quick Update on {topic}</h4><p>The operational framework for {topic} is expanding under the {category} matrix. Observers highlight key metrics taking effect across regional channels.</p>"

    if not GEMINI_API_KEY:
        return backup_article, backup_short

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    prompt = f"""
    Act as a senior investigative journalist writing for a premium mainstream newspaper. Write a natural, human-written style news analysis report for INFOVEX about '{topic}' under the category '{category}'.
    
    STRUCTURE REQUIREMENT:
    - Write exactly 4 fully-developed human paragraphs.
    - Wrap main story inside [START_ARTICLE]...[END_ARTICLE] tags using standard HTML p tags.
    - Wrap short summary inside [START_SHORT]...[END_SHORT] tags using an h4 headline and a single paragraph.
    """
    
    try:
        response = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=15)
        res_json = response.json()
        raw_text = res_json['candidates'][0]['content']['parts'][0]['text']
        raw_text = raw_text.replace("```html", "").replace("```", "").strip()
        
        article = raw_text.split("[START_ARTICLE]")[1].split("[END_ARTICLE]")[0].strip()
        short = raw_text.split("[START_SHORT]")[1].split("[END_SHORT]")[0].strip()
        
        paras = article.split("</p>")
        if len(paras) >= 4:
            article = f"{img1}\n{paras[0]}</p>\n{paras[1]}</p>\n{img2}\n{paras[2]}</p>\n{img3}\n" + "\n".join(paras[3:])
        else:
            article = f"{img1}\n{article}\n{img2}"
            
        return article, short
    except Exception:
        return backup_article, backup_short

def update_sitemap(repo):
    today_date = datetime.datetime.now().strftime("%Y-%m-%d")
    sitemap_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://infovex.vercel.app/</loc>
        <lastmod>{today_date}</lastmod>
        <changefreq>always</changefreq>
        <priority>1.0</priority>
    </url>
</urlset>"""
    try:
        try:
            contents = repo.get_contents("sitemap.xml", ref="main")
            repo.update_file(contents.path, "AI Desk: Regenerate Sitemap", sitemap_content, contents.sha, branch="main")
        except Exception:
            repo.create_file("sitemap.xml", "AI Desk: Initialize Sitemap XML", sitemap_content, branch="main")
    except Exception:
        pass

def update_platform(article_body, short_body, category, topic):
    repo = g.get_repo(GITHUB_REPO)
    contents = repo.get_contents("index.html", ref="main")
    html_code = contents.decoded_content.decode("utf-8")
    
    timestamp = datetime.datetime.now().strftime("%B %d, %Y • %I:%M %p")
    
    full_post_template = f"""
    <div class="post-card">
        <div class="meta">{timestamp} • {category}</div>
        <h2>{topic}</h2>
        <div class="preview-text">Latest comprehensive editorial report on {topic} has been released. Click to read the full analysis.</div>
        <div class="full-story">
            {article_body}
        </div>
    </div>
    """
    
    short_template = f"""
    <div class="short-card">
        <div class="short-tag">{category}</div>
        {short_body}
    </div>
    """
    
    # 🌟 ADVANCED REGEX PARSING ENGINE (Bina matching dependencies ke safely append karega)
    if '' in html_code and '' in html_code:
        html_code = html_code.replace('', f'\n{full_post_template}')
        html_code = html_code.replace('', f'\n{short_template}')
    else:
        # Standard structural backup split using target div blocks
        if '<div id="posts-container">' in html_code:
            html_code = html_code.replace('<div id="posts-container">', f'<div id="posts-container">\n{full_post_template}')
        if '<div class="shorts-sticky" id="shorts-container">' in html_code:
            html_code = html_code.replace('<div class="shorts-sticky" id="shorts-container">', f'<div class="shorts-sticky" id="shorts-container">\n{short_template}')

    repo.update_file(contents.path, f"AI Desk Update: Append Article {category}", html_code, contents.sha, branch="main")
    update_sitemap(repo)
    print("🎉 Platform updated successfully via fail-proof stack logic!")

if __name__ == "__main__":
    selected_category = random.choice(CATEGORIES)
    trending_topic = get_trending_topic(selected_category)
    article_html, short_html = generate_dual_content(trending_topic, selected_category)
    update_platform(article_html, short_html, selected_category, trending_topic)
