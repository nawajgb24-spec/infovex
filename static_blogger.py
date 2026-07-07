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
    img1 = '<img src="https://images.unsplash.com/photo-1504711434969-e33886168f5c?auto=format&fit=crop&w=1200&q=80" alt="News Image 1" style="width:100%; display:block; max-height:450px; object-fit:cover; margin:25px 0; border-radius:4px; border:1px solid #eee;">'
    img2 = '<img src="https://images.unsplash.com/photo-1495020689067-958852a6565d?auto=format&fit=crop&w=1200&q=80" alt="News Image 2" style="width:100%; display:block; max-height:400px; object-fit:cover; margin:25px 0; border-radius:4px; border:1px solid #eee;">'
    img3 = '<img src="https://images.unsplash.com/photo-1505373877841-8d25f7d46678?auto=format&fit=crop&w=1200&q=80" alt="News Image 3" style="width:100%; display:block; max-height:400px; object-fit:cover; margin:25px 0; border-radius:4px; border:1px solid #eee;">'

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
    
    STRICT ANTI-AI RULES (To bypass Google AI Detectors):
    1. NEVER use cliché AI transitions or buzzwords like: furthermore, moreover, in conclusion, testament, delve, rapidly evolving, landscape, crucial, paramount, underscore, pivotal, look no further, ripples, or world of.
    2. Write with variable sentence lengths (burstiness)—some sentences should be short and punchy, others detailed. This is how real humans write.
    3. Use a direct, informative, objective, and gripping journalistic tone. Start straight with the breaking news hook.
    4. Let the weight of the topic decide the length naturally. If it is a major global event, explain the deep impact extensively (up to 2000-3000 letters). If it is a crisp rule update, keep it tight and informative (around 1000 letters).
    
    STRUCTURE REQUIREMENT:
    - Write exactly 4 fully-developed human paragraphs.
    - Wrap the main story paragraphs inside [START_ARTICLE]...[END_ARTICLE] tags using standard HTML p tags.
    - Wrap a sharp Google Short summary inside [START_SHORT]...[END_SHORT] tags using an h4 headline and a single paragraph.
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
    
    # Precise character stripping matcher
    article_placeholder = '<div id="posts-container"></div>'
    short_placeholder = '<div class="shorts-sticky" id="shorts-container"></div>'
    
    # Check alternate format case if spaces are created by hand
    if article_placeholder not in html_code:
        article_placeholder = '<div id="posts-container">\n            \n            </div>'
    if short_placeholder not in html_code:
        short_placeholder = '<div class="shorts-sticky" id="shorts-container">\n                \n            </div>'

    # Fallback to pure string tag check
    if '<div id="posts-container">' in html_code and '<div class="shorts-sticky" id="shorts-container">' in html_code:
        html_code = html_code.replace('<div id="posts-container">', f'<div id="posts-container">\n{full_post_template}')
        html_code = html_code.replace('<div class="shorts-sticky" id="shorts-container">', f'<div class="shorts-sticky" id="shorts-container">\n{short_template}')
        
        repo.update_file(contents.path, f"AI Desk Update: Premium Deep-Content {category}", html_code, contents.sha, branch="main")
        print("🎉 Platform updated successfully with deep structures!")
    else:
        print("❌ Error: Target placeholders missing in index.html structure.")

if __name__ == "__main__":
    selected_category = random.choice(CATEGORIES)
    trending_topic = get_trending_topic(selected_category)
    article_html, short_html = generate_dual_content(trending_topic, selected_category)
    update_platform(article_html, short_html, selected_category, trending_topic)
