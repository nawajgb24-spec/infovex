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

        main_search_term = urllib.parse.quote(f"{chosen_category} core focus")
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
            return "<p class='no-data'>Scanning live channels for incoming data streams...</p>"
        
        html = ""
        for i in items:
            safe_title = i['title'].replace("'", "\\'")
            html += f"""
            <div class="news-card">
                <div class="img-wrapper">
                    <img src="{i['image']}" alt="Infovex Media">
                    <button class="share-btn-card" onclick="shareArticle('{safe_title}', window.location.href)" title="Share Article">🔗</button>
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
        cat = s.get("category", "Trending") if isinstance(s, dict) else "LIVE"
        safe_txt = txt.replace("'", "\\'")
        
        shorts_html += f"""
        <div class="short-premium-card" onclick="shareArticle('Short Pulse: {safe_txt}', window.location.href)">
            <img class="short-card-img" src="{img}" alt="Shorts">
            <div class="short-card-overlay">
                <span class="short-tag">{cat}</span>
                <p class="short-text-p">{txt}</p>
                <span style="font-size:10px; opacity:0.6; margin-top:4px;">Tap to Share 📤</span>
            </div>
        </div>
        """

    safe_hero_title = latest_art['title'].replace("'", "\\'")

    # ESCAPED CSS BRACES FOR PYTHON SAFETY
    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Infovex Newsroom | Global Premium Intelligence</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Cabinet+Grotesk:wght@800&display=swap" rel="stylesheet">
    <style>
        :root {{
            --dark-canvas: #05070f;
            --surface-panel: #0b0f19;
            --border-glass: #1e293b;
            --font-primary: #f8fafc;
            --font-secondary: #94a3b8;
            --hyper-blue: #38bdf8;
            --neon-green: #10b981;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; scroll-behavior: smooth; }}
        body {{ background-color: var(--dark-canvas); color: var(--font-primary); font-family: 'Plus Jakarta Sans', sans-serif; overflow-x: hidden; }}
        
        /* Rigid Fitting Navigation Utilities */
        header {{ background-color: rgba(5, 7, 15, 0.95); backdrop-filter: blur(20px); border-bottom: 1px solid var(--border-glass); position: sticky; top: 0; z-index: 2000; }}
        .header-wrap {{ max-width: 1300px; margin: 0 auto; display: flex; flex-direction: column; align-items: center; padding: 14px 20px; text-align: center; }}
        .brand-box {{ margin-bottom: 10px; }}
        .brand {{ font-family: 'Cabinet Grotesk', sans-serif; font-size: 32px; font-weight: 800; text-transform: uppercase; letter-spacing: -0.5px; text-decoration: none; color: #fff; }}
        .brand span {{ color: var(--hyper-blue); }}
        .sub-tagline {{ font-size: 13px; color: var(--font-secondary); margin-top: 4px; font-weight: 500; letter-spacing: 0.2px; }}
        
        /* Functional Navigation Links */
        .nav-categories {{ display: flex; gap: 16px; overflow-x: auto; max-width: 100%; padding: 6px 0; scrollbar-width: none; }}
        .nav-categories::-webkit-scrollbar {{ display: none; }}
        .nav-categories a {{ text-decoration: none; color: var(--font-secondary); font-size: 13.5px; font-weight: 600; padding: 6px 12px; border-radius: 20px; transition: all 0.2s ease; white-space: nowrap; }}
        .nav-categories a:hover {{ color: var(--hyper-blue); background: rgba(56, 189, 248, 0.08); }}
        
        /* Clean Structural Framing Layout */
        .portal-grid {{ max-width: 1300px; margin: 24px auto; display: grid; grid-template-columns: 2.2fr 1fr; gap: 32px; padding: 0 20px; }}
        
        /* Hero Elements scaling */
        .spotlight-hero {{ background: var(--surface-panel); border-radius: 14px; border: 1px solid var(--border-glass); overflow: hidden; margin-bottom: 36px; position: relative; }}
        .spotlight-hero img {{ width: 100%; height: 380px; object-fit: cover; }}
        .hero-details {{ padding: 24px; }}
        .section-badge {{ background: rgba(56, 189, 248, 0.12); color: var(--hyper-blue); font-size: 11px; font-weight: 700; padding: 4px 10px; border-radius: 6px; text-transform: uppercase; }}
        h1 {{ font-family: 'Cabinet Grotesk', sans-serif; font-size: 28px; font-weight: 800; margin: 12px 0; line-height: 1.3; color: #fff; }}
        .hero-desc {{ font-size: 15px; color: #cbd5e1; line-height: 1.6; }}
        .hero-desc h2 {{ font-size: 18px; color: #fff; margin: 16px 0 8px 0; font-family: 'Cabinet Grotesk', sans-serif; }}
        
        /* Native Floating Share Trigger */
        .main-share-trigger {{ background: var(--hyper-blue); color: #000; border: none; padding: 8px 14px; border-radius: 6px; font-weight: 700; font-size: 12px; cursor: pointer; margin-top: 14px; display: inline-flex; align-items: center; gap: 6px; transition: opacity 0.2s; }}
        .main-share-trigger:hover {{ opacity: 0.9; }}

        /* Row blocks */
        .editorial-row {{ margin-bottom: 36px; scroll-margin-top: 140px; }}
        .row-heading {{ font-size: 17px; font-weight: 700; margin-bottom: 16px; padding-bottom: 8px; border-bottom: 1px solid var(--border-glass); display: flex; align-items: center; gap: 8px; color: #fff; font-family: 'Cabinet Grotesk', sans-serif; letter-spacing: 0.5px; }}
        .row-heading::before {{ content: ''; display: inline-block; width: 4px; height: 14px; background: var(--hyper-blue); border-radius: 2px; }}
        
        /* Grid Alignment Mechanics */
        .cards-flex-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 16px; }}
        .news-card {{ background: var(--surface-panel); border-radius: 10px; border: 1px solid var(--border-glass); overflow: hidden; display: flex; flex-direction: column; position: relative; }}
        .img-wrapper {{ width: 100%; height: 150px; overflow: hidden; position: relative; }}
        .news-card img {{ width: 100%; height: 100%; object-fit: cover; }}
        .share-btn-card {{ position: absolute; top: 10px; right: 10px; background: rgba(0,0,0,0.7); color: #fff; border: 1px solid var(--border-glass); border-radius: 50%; width: 32px; height: 32px; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 14px; transition: background 0.2s; }}
        .share-btn-card:hover {{ background: var(--hyper-blue); color: #000; }}
        .card-meta {{ padding: 14px; flex-grow: 1; }}
        .news-card h3 {{ font-size: 14px; font-weight: 600; color: #f1f5f9; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }}
        .timestamp {{ font-size: 11px; color: var(--font-secondary); margin-top: 8px; }}
        
        /* Sidebar System */
        .sidebar-shorts {{ background: #080c14; border-radius: 14px; padding: 20px; border: 1px solid var(--border-glass); height: fit-content; position: sticky; top: 130px; }}
        .sidebar-title {{ font-family: 'Cabinet Grotesk', sans-serif; font-size: 18px; font-weight: 800; color: #fff; margin-bottom: 16px; text-transform: uppercase; }}
        .short-premium-card {{ position: relative; width: 100%; height: 160px; border-radius: 10px; overflow: hidden; margin-bottom: 12px; border: 1px solid var(--border-glass); cursor: pointer; transition: transform 0.2s ease; }}
        .short-premium-card:hover {{ transform: scale(1.01); }}
        .short-card-img {{ width: 100%; height: 100%; object-fit: cover; filter: brightness(0.35); }}
        .short-card-overlay {{ position: absolute; bottom: 0; left: 0; width: 100%; padding: 12px; display: flex; flex-direction: column; justify-content: flex-end; height: 100%; }}
        .short-tag {{ background: var(--hyper-blue); color: #05070f; font-size: 8px; font-weight: 800; padding: 2px 5px; border-radius: 3px; text-transform: uppercase; width: fit-content; margin-bottom: 6px; }}
        .short-text-p {{ font-size: 12px; font-weight: 600; line-height: 1.4; color: #ffffff; }}
        .no-data {{ font-size: 12px; color: var(--font-secondary); font-style: italic; }}
        
        /* Premium Corporate Footer Components */
        footer {{ background: #03050a; border-top: 1px solid var(--border-glass); padding: 40px 20px; margin-top: 60px; text-align: center; }}
        .footer-wrap {{ max-width: 1300px; margin: 0 auto; display: flex; flex-direction: column; align-items: center; gap: 16px; }}
        .footer-logo {{ font-family: 'Cabinet Grotesk', sans-serif; font-size: 22px; font-weight: 800; color: #fff; text-decoration: none; }}
        .footer-logo span {{ color: var(--hyper-blue); }}
        .footer-links {{ display: flex; gap: 24px; flex-wrap: wrap; justify-content: center; }}
        .footer-links a {{ color: var(--font-secondary); text-decoration: none; font-size: 13px; font-weight: 500; transition: color 0.2s; }}
        .footer-links a:hover {{ color: var(--hyper-blue); }}
        .copyright {{ font-size: 12px; color: #475569; margin-top: 12px; }}

        /* Fluid Media Breakpoints */
        @media(max-width: 1024px) {{
            .portal-grid {{ grid-template-columns: 1fr; gap: 32px; }}
            .sidebar-shorts {{ position: static; }}
            .spotlight-hero img {{ height: 280px; }}
        }}
        @media(max-width: 640px) {{
            .brand {{ font-size: 26px; }}
            h1 {{ font-size: 22px; }}
            .spotlight-hero img {{ height: 200px; }}
            .cards-flex-grid {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>

<header>
    <div class="header-wrap">
        <div class="brand-box">
            <a href="#" class="brand">INFO<span>VEX</span></a>
            <div class="sub-tagline">The Pulse of Tomorrow’s Tech, Sports, and Global Intelligence.</div>
        </div>
        <div class="nav-categories">
            <a href="#electronics">🔌 Electronics</a>
            <a href="#sports">🏆 Sports</a>
            <a href="#facts">💡 Facts</a>
            <a href="#films">🎬 Films</a>
            <a href="#health">🌱 Health & Food</a>
        </div>
    </div>
</header>

<main class="portal-grid">
    <section>
        <div class="spotlight-hero">
            <img src="{latest_art['image']}" alt="Spotlight Headline">
            <div class="hero-details">
                <span class="section-badge">Live Top Story ({current_cat})</span>
                <h1>{latest_art['title']}</h1>
                <div class="hero-desc">{latest_art['content']}</div>
                <button class="main-share-trigger" onclick="shareArticle('{safe_hero_title}', window.location.href)">Share This Update 📤</button>
            </div>
        </div>

        <div class="editorial-row" id="electronics">
            <div class="row-heading">🔌 Electronics & Tech-Hardware</div>
            <div class="cards-flex-grid">{render_feed("Electronics")}</div>
        </div>

        <div class="editorial-row" id="sports">
            <div class="row-heading">🏆 Global Sports Track</div>
            <div class="cards-flex-grid">{render_feed("Sports")}</div>
        </div>

        <div class="editorial-row" id="facts">
            <div class="row-heading">💡 Interesting Facts Hub</div>
            <div class="cards-flex-grid">{render_feed("Interesting Facts")}</div>
        </div>

        <div class="editorial-row" id="films">
            <div class="row-heading">🎬 Global Film Industry</div>
            <div class="cards-flex-grid">{render_feed("Film Industry")}</div>
        </div>

        <div class="editorial-row" id="health">
            <div class="row-heading">🌱 Health & Food Insights</div>
            <div class="cards-flex-grid">{render_feed("Health & Food")}</div>
        </div>
    </section>

    <aside class="sidebar-shorts">
        <div class="sidebar-title">⚡ Google Shorts Feed</div>
        {shorts_html}
    </aside>
</main>

<footer>
    <div class="footer-wrap">
        <a href="#" class="footer-logo">INFO<span>VEX</span></a>
        <div class="footer-links">
            <a href="#">About Intelligence Hub</a>
            <a href="mailto:contact@infovex.com">📬 Contact Support: contact@infovex.com</a>
            <a href="#">Privacy Framework</a>
            <a href="#">Terms of Feed</a>
        </div>
        <div class="copyright">© 2026 Infovex Media Network. Powered by Gemini AI. All Rights Reserved.</div>
    </div>
</footer>

<script>
function shareArticle(title, url) {{
    if (navigator.share) {{
        navigator.share({{
            title: title,
            text: title + " - Read more on Infovex Network:",
            url: url
        }}).then(() => {{
            print('Successfully shared');
        }}).catch((error) => {{
            console.log('Error sharing:', error);
        }});
    }} else {{
        navigator.clipboard.writeText(title + " - " + url);
        alert("Link copied to clipboard! Share it anywhere. 🚀");
    }}
}}
</script>

</body>
</html>"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(full_html)
    print("Upgraded professional UI generated successfully.")

if __name__ == "__main__":
    generate_automated_blog()
