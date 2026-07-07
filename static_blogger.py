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
    # 🌟 Multi-Image Dynamic Stock Base
    img1 = '<img src="https://images.unsplash.com/photo-1504711434969-e33886168f5c?auto=format&fit=crop&w=1200&q=80" alt="News Image 1" style="width:100%; display:block; max-height:450px; object-fit:cover; margin:20px 0; border-radius:4px; border:1px solid #eee;">'
    img2 = '<img src="https://images.unsplash.com/photo-1495020689067-958852a6565d?auto=format&fit=crop&w=1200&q=80" alt="News Image 2" style="width:100%; display:block; max-height:400px; object-fit:cover; margin:20px 0; border-radius:4px; border:1px solid #eee;">'
    img3 = '<img src="https://images.unsplash.com/photo-1505373877841-8d25f7d46678?auto=format&fit=crop&w=1200&q=80" alt="News Image 3" style="width:100%; display:block; max-height:400px; object-fit:cover; margin:20px 0; border-radius:4px; border:1px solid #eee;">'

    # 🌟 Premium 1500+ Letters Guaranteed Long-Form Backups
    backup_article = f"""
    {img1}
    <p>In a groundbreaking shift that has sent ripples through regional and international observation circles, the unexpected developments surrounding <b>{topic}</b> have rapidly taken center stage. Government departments, independent regulatory committees, and core public stakeholders are evaluating the immediate administrative consequences of this sudden strategic pivot. Leading voices within the {category} landscape highlight that these structural changes will require immediate operational transformations, fundamentally altering traditional workflows and established frameworks across both urban grids and commercial sectors uniformally.</p>
    
    <p>As industry analysts dig deeper into the core logistics of this milestone, recently gathered data lists a series of compliance challenges that require swift attention from administrative channels. Media platforms and economic advisory councils warn that lingering process delays could create significant backlogs, especially during the transition into the upcoming policy cycles. Emergency summits are being convened among localized integration teams to safeguard structural integrity and guarantee a smooth layout adaptation without breaking standard protocols.</p>
    
    {img2}
    <p>Furthermore, execution experts strongly suggest that keeping a strict eye on regional distribution changes and performance metrics will be absolutely essential to sustain the momentum sparked by this update. Representatives have issued critical notices advising the general public to follow verified portals and official reports closely, rather than relying on unofficial channels. Specific guidelines detailing step-by-step compliance routines are expected to roll out across all designated networks sequentially over the coming weeks.</p>
    
    {img3}
    <p>Ultimately, the long-term impact of this decision will depend heavily on the adaptability of localized systems and baseline operations. Initial assessments point toward a steady transformation, though localized friction remains highly probable in areas lacking sufficient integration tools. As structural entities adjust their long-term strategies, the broader market continues to monitor this evolving scenario with intense scrutiny, awaiting secondary structural announcements from high-level management committees.</p>
    """
    
    backup_short = f"<h4>Quick Update on {topic}</h4><p>The operational framework for {topic} is expanding rapidly under the {category} matrix. Observers highlight strong regulatory metrics taking place immediately across regional channels.</p>"

    if not GEMINI_API_KEY:
        return backup_article, backup_short

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    prompt = f"""
    Write a massive, deep-dive human news summary for INFOVEX about '{topic}' in category '{category}'.
    Avoid any AI cliché words. Write exactly 4 very long, detailed paragraphs analyzing background, impact, prediction, and solutions.
    Overall text length MUST exceed 1500 to 2000 letters.
    Wrap the paragraphs inside [START_ARTICLE]...[END_ARTICLE] tags (use standard HTML p tags).
    Wrap a sharp short summary inside [START_SHORT]...[END_SHORT] tags using an h4 title and a single paragraph.
    """
    
    try:
        response = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=15)
        res_json = response.json()
        raw_text = res_json['candidates'][0]['content']['parts'][0]['text']
        raw_text = raw_text.replace("```html", "").replace("```", "").strip()
        
        article = raw_text.split("[START_ARTICLE]")[1].split("[END_ARTICLE]")[0].strip()
        short = raw_text.split("[START_SHORT]")[1].split("[END_SHORT]")[0].strip()
        
        # Injects images between AI paragraphs dynamically
        paras = article.split("</p>")
        if len(paras) >= 4:
            article = f"{img1}\n{paras[0]}</p>\n{paras[1]}</p>\n{img2}\n{paras[2]}</p>\n{img3}\n" + "\n".join(paras[3:])
        else:
            article = f"{img1}\n{article}\n{img2}"
            
        return article, short
    except Exception:
        return backup_article, backup_short

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
    
    article_placeholder = '<div id="posts-container">'
    short_placeholder = '<div class="shorts-sticky" id="shorts-container">'
    
    if article_placeholder in html_code and short_placeholder in html_code:
        html_code = html_code.replace(article_placeholder, f"{article_placeholder}\n{full_post_template}")
        html_code = html_code.replace(short_placeholder, f"{short_placeholder}\n{short_template}")
        
        repo.update_file(contents.path, f"AI Desk Update: Full Multi-View {category}", html_code, contents.sha, branch="main")
        print("🎉 Platform updated successfully with deep structures!")

if __name__ == "__main__":
    selected_category = random.choice(CATEGORIES)
    trending_topic = get_trending_topic(selected_category)
    article_html, short_html = generate_dual_content(trending_topic, selected_category)
    update_platform(article_html, short_html, selected_category, trending_topic)
