import os
import json
import random
import urllib.parse
from google import genai
from google.genai import types
from datetime import datetime

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY missing!")
    exit(1)

client = genai.Client(api_key=api_key)

def generate_automated_blog():
    try:
        categories = [
            {"name": "Electronics", "weight": 25},
            {"name": "Sports", "weight": 25},
            {"name": "Interesting Facts", "weight": 20},
            {"name": "Film Industry", "weight": 20},
            {"name": "Health & Food", "weight": 10}
        ]
        
        chosen_category = random.choices(
            [c["name"] for c in categories], 
            weights=[c["weight"] for c in categories], 
            k=1
        )[0]
        
        date_str = datetime.now().strftime("%B %d, %Y")
        print(f"Target Category: {chosen_category}")

        config = types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())]
        )
        
        search_prompt = f"Identify the absolute highest-traffic trending news topic or viral search query right now for '{chosen_category}' in 2026. Return ONLY the plain headline text."
        topic_response = client.models.generate_content(model='gemini-2.5-flash', contents=search_prompt, config=config)
        topic = topic_response.text.strip().replace('"', '')
        print(f"Live Topic: {topic}")

        main_prompt = f"""
        Act as a chief digital news editor. Write a premium, deeply detailed, and original news report about '{topic}' specifically under the category '{chosen_category}' set in the year 2026.
        Organize using clear paragraphs. Output format: Direct clean text, no markdown backticks, no code blocks.
        """
        main_response = client.models.generate_content(model='gemini-2.5-flash', contents=main_prompt, config=config)
        main_text = main_response.text.strip().replace('\n', '<br>')

        short_prompt = f"""
        Analyze this topic: '{topic}'.
        Generate a strictly valid JSON response containing exactly two fields:
        1. 'text': An explosive news summary under 25 words.
        2. 'keyword': 2 precise English words for finding a photography image on Unsplash.
        Output ONLY raw valid JSON. No markdown wrappers or backticks.
        """
        short_response = client.models.generate_content(model='gemini-2.5-flash', contents=short_prompt)
        
        try:
            clean_json = short_response.text.strip().replace('```json', '').replace('```', '')
            short_data = json.loads(clean_json)
            short_text = short_data.get("text", f"Updates on {topic} surfaces online.")
            short_kw = short_data.get("keyword", chosen_category)
        except:
            short_text = f"Live breaking updates on {topic} surfaces globally."
            short_kw = chosen_category

        main_search_term = urllib.parse.quote(f"{chosen_category} news dynamic")
        main_image_url = f"https://images.unsplash.com/featured/1200x650?{main_search_term}&sig={random.randint(1, 9999)}"

        short_search_term = urllib.parse.quote(short_kw)
        short_image_url = f"https://images.unsplash.com/featured/400x400?{short_search_term}&sig={random.randint(1, 9999)}"

        data_file = "data.json"
        valid_cats = ["Electronics", "Sports", "Interesting Facts", "Film Industry", "Health & Food", "shorts"]
        
        if os.path.exists(data_file):
            with open(data_file, "r", encoding="utf-8") as f:
                db = json.load(f)
        else:
            db = {c: [] for c in valid_cats}

        for c in valid_cats:
            if c not in db: db[c] = []

        new_post = {
            "title": topic,
            "date": date_str,
            "content": main_text,
            "image": main_image_url
        }

        db[chosen_category].insert(0, new_post)
        db[chosen_category] = db[chosen_category][:4]
        
        new_short = {
            "text": short_text,
            "image": short_image_url,
            "category": chosen_category
        }
        db["shorts"].insert(0, new_short)
        db["shorts"] = db["shorts"][:5]

        with open(data_file, "w", encoding="utf-8") as f:
            json.dump(db, f, indent=4)

        build_magazine_portal(db, new_post, chosen_category)

    except Exception as e:
        print(f"Critical execution fault: {str(e)}")
        exit(1)

def build_magazine_portal(db, latest_art, current_cat):
    def render_feed(cat_name):
        items = db.get(cat_name, [])
        if not items:
            return "<p class='no-data'>AI sync engine processing updates...</p>"
        
        html = ""
        for i in items:
            safe_title = i['title'].replace("'", "\\'")
            html += f"""
            <div class="news-card">
                <div class="img-wrapper">
                    <img src="{i['image']}" alt="Infovex Core Media">
                    <button class="share-btn-card" onclick="shareArticle('{safe_title}', window.location.href)" title="Share">🔗</button>
                </div>
                <div class="card-meta">
                    <h3>{i['title']}</h3>
                    <p class="timestamp">🕒 {i['date']}</p>
                </div>
            </div>
            """
        return html

    shorts_html = ""
    for s in db.get("shorts", []):
        img = s.get("image") if isinstance(s, dict) else "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=400&q=80"
        txt = s.get("text", s) if isinstance(s, dict) else s
        cat = s.get("category", "Pulse") if isinstance(s, dict) else "LIVE"
        safe_txt = txt.replace("'", "\\'")
        
        shorts_html += f"""
        <div class="short-premium-card" onclick="shareArticle('Short Blast: {safe_txt}', window.location.href)">
            <img class="short-card-img" src="{img}" alt="Shorts Feed">
            <div class="short-card-overlay">
                <span class="short-tag">{cat}</span>
                <p class="short-text-p">{txt}</p>
                <span style="font-size:9px; opacity:0.5; margin-top:4px;">Tap to Share 📤</span>
            </div>
        </div>
        """

    safe_hero_title = latest_art['title'].replace("'", "\\'")
    cache_version = random.randint(100, 999) # Forces browser to instantly reload layout changes

    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Infovex Intelligence Hub</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&family=Cabinet+Grotesk:wght@800&v={cache_version}" rel="stylesheet">
    <style>
        :root {{
            --dark-canvas: #060814;
            --surface-panel: #0e1326;
            --border-glass: #1e293b;
            --font-primary: #f8fafc;
            --font-secondary: #94a3b8;
            --hyper-blue: #38bdf8;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; scroll-behavior: smooth; }}
        body {{ background-color: var(--dark-canvas); color: var(--font-primary); font-family: 'Plus Jakarta Sans', sans-serif; overflow-x: hidden; -webkit-font-smoothing: antialiased; }}
        
        header {{ background-color: rgba(6, 8, 20, 0.96); backdrop-filter: blur(20px); border-bottom: 1px solid var(--border-glass); position: sticky; top: 0; z-index: 2000; padding: 12px 16px; }}
        .header-wrap {{ max-width: 1200px; margin: 0 auto; display: flex; flex-direction: column; align-items: center; gap: 8px; }}
        .brand {{ font-family: 'Cabinet Grotesk', sans-serif; font-size: 28px; font-weight: 800; text-transform: uppercase; letter-spacing: -0.5px; text-decoration: none; color: #fff; line-height: 1; }}
        .brand span {{ color: var(--hyper-blue); }}
        .sub-tagline {{ font-size: 11.5px; color: var(--font-secondary); font-weight: 500; letter-spacing: 0.1px; margin-top: 2px; }}
        
        .nav-categories {{ display: flex; gap: 10px; overflow-x: auto; max-width: 100%; padding: 4px 0; width: 100%; justify-content: center; scrollbar-width: none; }}
        .nav-categories::-webkit-scrollbar {{ display: none; }}
        .nav-categories a {{ text-decoration: none; color: var(--font-secondary); font-size: 12.5px; font-weight: 600; padding: 5px 10px; border-radius: 20px; transition: all 0.2s; white-space: nowrap; }}
        .nav-categories a:hover {{ color: var(--hyper-blue); background: rgba(56, 189, 248, 0.08); }}
        
        .portal-grid {{ max-width: 1200px; margin: 20px auto; display: grid; grid-template-columns: 2.2fr 1fr; gap: 24px; padding: 0 16px; }}
        
        .spotlight-hero {{ background: var(--surface-panel); border-radius: 12px; border: 1px solid var(--border-glass); overflow: hidden; margin-bottom: 28px; }}
        .spotlight-hero img {{ width: 100%; height: 350px; object-fit: cover; }}
        .hero-details {{ padding: 20px; }}
        .section-badge {{ background: rgba(56, 189, 248, 0.12); color: var(--hyper-blue); font-size: 10px; font-weight: 700; padding: 4px 8px; border-radius: 4px; text-transform: uppercase; }}
        h1 {{ font-family: 'Cabinet Grotesk', sans-serif; font-size: 24px; font-weight: 800; margin: 10px 0; line-height: 1.25; color: #fff; }}
        .hero-desc {{ font-size: 14px; color: #cbd5e1; line-height: 1.55; }}
        .hero-desc h2 {{ font-size: 16px; color: #fff; margin: 14px 0 6px 0; font-family: 'Cabinet Grotesk', sans-serif; }}
        
        .main-share-trigger {{ background: var(--hyper-blue); color: #000; border: none; padding: 6px 12px; border-radius: 4px; font-weight: 700; font-size: 11px; cursor: pointer; margin-top: 12px; display: inline-flex; align-items: center; gap: 4px; }}

        .editorial-row {{ margin-bottom: 28px; scroll-margin-top: 120px; }}
        .row-heading {{ font-size: 15px; font-weight: 700; margin-bottom: 14px; padding-bottom: 6px; border-bottom: 1px solid var(--border-glass); display: flex; align-items: center; gap: 6px; color: #fff; font-family: 'Cabinet Grotesk', sans-serif; text-transform: uppercase; }}
        .row-heading::before {{ content: ''; display: inline-block; width: 3px; height: 12px; background: var(--hyper-blue); border-radius: 1px; }}
        
        .cards-flex-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 14px; }}
        .news-card {{ background: var(--surface-panel); border-radius: 8px; border: 1px solid var(--border-glass); overflow: hidden; display: flex; flex-direction: column; position: relative; }}
        .img-wrapper {{ width: 100%; height: 140px; overflow: hidden; position: relative; }}
        .news-card img {{ width: 100%; height: 100%; object-fit: cover; }}
        .share-btn-card {{ position: absolute; top: 8px; right: 8px; background: rgba(0,0,0,0.7); color: #fff; border: 1px solid var(--border-glass); border-radius: 50%; width: 28px; height: 28px; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 12px; }}
        
        .card-meta {{ padding: 12px; flex-grow: 1; }}
        .news-card h3 {{ font-size: 13.5px; font-weight: 600; color: #f1f5f9; line-height: 1.35; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }}
        .timestamp {{ font-size: 10.5px; color: var(--font-secondary); margin-top: 6px; }}
        
        .sidebar-shorts {{ background: #090d1f; border-radius: 12px; padding: 16px; border: 1px solid var(--border-glass); height: fit-content; position: sticky; top: 120px; }}
        .sidebar-title {{ font-family: 'Cabinet Grotesk', sans-serif; font-size: 16px; font-weight: 800; color: #fff; margin-bottom: 14px; text-transform: uppercase; }}
        .short-premium-card {{ position: relative; width: 100%; height: 150px; border-radius: 8px; overflow: hidden; margin-bottom: 10px; border: 1px solid var(--border-glass); cursor: pointer; }}
        .short-card-img {{ width: 100%; height: 100%; object-fit: cover; filter: brightness(0.35); }}
        .short-card-overlay {{ position: absolute; bottom: 0; left: 0; width: 100%; padding: 10px; display: flex; flex-direction: column; justify-content: flex-end; height: 100%; }}
        .short-tag {{ background: var(--hyper-blue); color: #060814; font-size: 8px; font-weight: 800; padding: 1px 4px; border-radius: 2px; text-transform: uppercase; width: fit-content; margin-bottom: 4px; }}
        .short-text-p {{ font-size: 11.5px; font-weight: 600; line-height: 1.35; color: #ffffff; }}
        
        footer {{ background: #03040a; border-top: 1px solid var(--border-glass); padding: 30px 16px; margin-top: 40px; text-align: center; }}
        .footer-wrap {{ max-width: 1200px; margin: 0 auto; display: flex; flex-direction: column; align-items: center; gap: 12px; }}
        .footer-logo {{ font-family: 'Cabinet Grotesk', sans-serif; font-size: 20px; font-weight: 800; color: #fff; text-decoration: none; }}
        .footer-logo span {{ color: var(--hyper-blue); }}
        .footer-links {{ display: flex; gap: 16px; flex-wrap: wrap; justify-content: center; }}
        .footer-links a {{ color: var(--font-secondary); text-decoration: none; font-size: 12px; transition: color 0.2s; }}
        .footer-links a:hover {{ color: var(--hyper-blue); }}
        .copyright {{ font-size: 11px; color: #475569; }}

        @media(max-width: 1024px) {{
            .portal-grid {{ grid-template-columns: 1fr; gap: 24px; }}
            .sidebar-shorts {{ position: static; }}
            .spotlight-hero img {{ height: 260px; }}
        }}
        @media(max-width: 640px) {{
            header {{ padding: 10px; }}
            .brand {{ font-size: 24px; }}
            .sub-tagline {{ font-size: 10px; }}
            .nav-categories a {{ font-size: 11.5px; padding: 4px 8px; }}
            h1 {{ font-size: 19px; }}
            .spotlight-hero img {{ height: 190px; }}
            .cards-flex-grid {{ grid-template-columns: 1fr; }}
            .news-card h3 {{ font-size: 13px; }}
        }}
    </style>
</head>
<body>

<header>
    <div class="header-wrap">
        <a href="#" class="brand">INFO<span>VEX</span></a>
        <div class="sub-tagline">The Pulse of Tomorrow’s Tech, Sports, and Global Intelligence.</div>
        <div class="nav-categories">
            <a href="#electronics">🔌 Electronics</a>
            <a href="#sports">🏆 Sports</a>
            <a href="#facts">💡 Facts</a>
            <a href="#films">🎬 Films</a>
            <a href="#health">🌱 Food</a>
        </div>
    </div>
</header>

<main class="portal-grid">
    <section>
        <div class="spotlight-hero">
            <img src="{latest_art['image']}" alt="Main Cover">
            <div class="hero-details">
                <span class="section-badge">Featured Core ({current_cat})</span>
                <h1>{latest_art['title']}</h1>
                <div class="hero-desc">{latest_art['content']}</div>
                <button class="main-share-trigger" onclick="shareArticle('{safe_hero_title}', window.location.href)">Share Update 📤</button>
            </div>
        </div>

        <div class="editorial-row" id="electronics">
            <div class="row-heading">🔌 Electronics & Tech</div>
            <div class="cards-flex-grid">{render_feed("Electronics")}</div>
        </div>

        <div class="editorial-row" id="sports">
            <div class="row-heading">🏆 Global Sports Track</div>
            <div class="cards-flex-grid">{render_feed("Sports")}</div>
        </div>

        <div class="editorial-row" id="facts">
            <div class="row-heading">💡 Interesting Facts</div>
            <div class="cards-flex-grid">{render_feed("Interesting Facts")}</div>
        </div>

        <div class="editorial-row" id="films">
            <div class="row-heading">🎬 Film Industry</div>
            <div class="cards-flex-grid">{render_feed("Film Industry")}</div>
        </div>

        <div class="editorial-row" id="health">
            <div class="row-heading">🌱 Health & Food</div>
            <div class="cards-flex-grid">{render_feed("Health & Food")}</div>
        </div>
    </section>

    <aside class="sidebar-shorts">
        <div class="sidebar-title">⚡ Shorts Feed</div>
        {shorts_html}
    </aside>
</main>

<footer>
    <div class="footer-wrap">
        <a href="#" class="footer-logo">INFO<span>VEX</span></a>
        <div class="footer-links">
            <a href="mailto:contact@infovex.com">📬 Contact: contact@infovex.com</a>
            <a href="#">Privacy Policy</a>
        </div>
        <div class="copyright">© 2026 Infovex Network. All Rights Reserved.</div>
    </div>
</footer>

<script>
function shareArticle(title, url) {{
    if (navigator.share) {{
        navigator.share({{ title: title, text: title, url: url }}).catch(console.error);
    }} else {{
        navigator.clipboard.writeText(title + " - " + url);
        alert("Link copied to clipboard! 🚀");
    }}
}}
</script>

</body>
</html>"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(full_html)
    print("Mobile scalable UI generated.")

if __name__ == "__main__":
    generate_automated_blog()
