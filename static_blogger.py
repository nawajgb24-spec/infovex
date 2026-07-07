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

        main_search_term = urllib.parse.quote(f"{chosen_category} tech future")
        main_image_url = f"https://images.unsplash.com/featured/1200x650?{main_search_term}&sig={random.randint(1, 9999)}"

        short_search_term = urllib.parse.quote(short_kw)
        short_image_url = f"https://images.unsplash.com/featured/400x400?{short_search_term}&sig={random.randint(1, 9999)}"

        data_file = "data.json"
        valid_cats = ["Latest", "Electronics", "Sports", "Interesting Facts", "Film Industry", "Health & Food", "shorts"]
        
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
            "image": main_image_url,
            "category": chosen_category
        }

        # Step 1: Insert into Latest Tab Engine
        db["Latest"].insert(0, new_post)
        db["Latest"] = db["Latest"][:6] # Top 6 remains dynamic trending

        # Step 2: Automatically route to its archive base category
        db[chosen_category].insert(0, new_post)
        db[chosen_category] = db[chosen_category][:10] # Dynamic deep tracking
        
        new_short = {
            "text": short_text,
            "image": short_image_url,
            "category": chosen_category
        }
        db["shorts"].insert(0, new_short)
        db["shorts"] = db["shorts"][:6]

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
            return "<p class='no-data'>AI sync engine parsing network streams...</p>"
        
        html = ""
        for i in items:
            safe_title = i['title'].replace("'", "\\'")
            badge_lbl = f"Tag: {i.get('category', cat_name)}"
            html += f"""
            <div class="news-card">
                <div class="img-wrapper">
                    <img src="{i['image']}" alt="Infovex Feed Core">
                    <button class="share-btn-card" onclick=\"shareArticle('{safe_title}', window.location.href)\" title=\"Share\">🔗</button>
                </div>
                <div class="card-meta">
                    <span class="card-mini-badge">{badge_lbl}</span>
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
        <div class="short-premium-card" onclick=\"shareArticle('Short Blast: {safe_txt}', window.location.href)\">
            <img class="short-card-img" src="{img}" alt="Shorts">
            <div class="short-card-overlay">
                <span class="short-tag">{cat}</span>
                <p class="short-text-p">{txt}</p>
                <span style="font-size:9px; opacity:0.6; margin-top:4px;">Tap to Share 📤</span>
            </div>
        </div>
        """

    safe_hero_title = latest_art['title'].replace("'", "\\'")
    cache_version = random.randint(1000, 9999)

    full_html = f"""<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Infovex Premium Newsroom</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Cabinet+Grotesk:wght@800&v={cache_version}" rel="stylesheet">
    <style>
        :root {{
            --canvas-bg: #04060d;
            --surface-card: #0b0f1e;
            --border-line: #1e293b;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --accent-glow: #38bdf8;
            --ticker-bg: #090e1a;
        }}
        [data-theme="light"] {{
            --canvas-bg: #f4f6fa;
            --surface-card: #ffffff;
            --border-line: #e2e8f0;
            --text-main: #0f172a;
            --text-muted: #64748b;
            --accent-glow: #0284c7;
            --ticker-bg: #e2e8f0;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; scroll-behavior: smooth; }}
        body {{ background-color: var(--canvas-bg); color: var(--text-main); font-family: 'Plus Jakarta Sans', sans-serif; overflow-x: hidden; transition: background 0.3s, color 0.3s; }}
        
        /* Reading Line Tracker */
        .progress-container {{ position: fixed; top: 0; left: 0; width: 100%; height: 3px; z-index: 3000; background: transparent; }}
        .progress-bar {{ height: 100%; background: var(--accent-glow); width: 0%; }}

        /* Top Utilities Ticker Header */
        .ticker-bar {{ background: var(--ticker-bg); border-bottom: 1px solid var(--border-line); font-size: 11px; padding: 6px 16px; overflow: hidden; white-space: nowrap; font-weight: 600; }}
        .ticker-wrap {{ display: inline-block; animation: marquee 25s linear infinite; color: var(--accent-glow); }}
        @keyframes marquee {{ 0% {{ transform: translate3d(100%, 0, 0); }} 100% {{ transform: translate3d(-100%, 0, 0); }} }}

        /* Rigid Top Header Layout */
        header {{ background-color: rgba(4, 6, 13, 0.9); backdrop-filter: blur(20px); border-bottom: 1px solid var(--border-line); position: sticky; top: 0; z-index: 2000; padding: 14px 24px; }}
        .header-content {{ max-width: 1400px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; }}
        .brand-zone {{ display: flex; flex-direction: column; }}
        .brand {{ font-family: 'Cabinet Grotesk', sans-serif; font-size: 28px; font-weight: 800; text-transform: uppercase; letter-spacing: -0.5px; text-decoration: none; color: var(--text-main); }}
        .brand span {{ color: var(--accent-glow); }}
        .punchline {{ font-size: 11px; color: var(--text-muted); margin-top: 2px; font-weight: 500; }}
        .actions-tray {{ display: flex; align-items: center; gap: 12px; }}
        .theme-toggle {{ background: var(--border-line); border: none; color: var(--text-main); padding: 6px 12px; border-radius: 20px; font-size: 12px; cursor: pointer; font-weight: 600; }}

        /* Dynamic Grid Layout Framework with Vertical Navigation Menu Left Side */
        .portal-container {{ max-width: 1400px; margin: 24px auto; display: grid; grid-template-columns: 240px 1.8fr 1fr; gap: 24px; padding: 0 16px; }}
        
        /* Left Side Sticky Sidebar Navigation Menu */
        .left-sidebar-nav {{ position: sticky; top: 100px; height: fit-content; display: flex; flex-direction: column; gap: 8px; }}
        .nav-title {{ font-size: 11px; font-weight: 700; text-transform: uppercase; color: var(--text-muted); letter-spacing: 1px; margin-bottom: 8px; padding-left: 8px; }}
        .left-sidebar-nav a {{ text-decoration: none; color: var(--text-muted); font-size: 13.5px; font-weight: 600; padding: 10px 14px; border-radius: 8px; transition: all 0.2s; display: flex; align-items: center; gap: 10px; }}
        .left-sidebar-nav a:hover, .left-sidebar-nav a.active {{ color: var(--text-main); background: var(--surface-card); border-left: 3px solid var(--accent-glow); }}

        /* Main Elements Scaling */
        .spotlight-hero {{ background: var(--surface-card); border-radius: 12px; border: 1px solid var(--border-line); overflow: hidden; margin-bottom: 32px; }}
        .spotlight-hero img {{ width: 100%; height: 360px; object-fit: cover; }}
        .hero-details {{ padding: 20px; }}
        .section-badge {{ background: rgba(56, 189, 248, 0.12); color: var(--accent-glow); font-size: 10px; font-weight: 700; padding: 4px 8px; border-radius: 4px; text-transform: uppercase; }}
        h1 {{ font-family: 'Cabinet Grotesk', sans-serif; font-size: 24px; font-weight: 800; margin: 12px 0 8px 0; line-height: 1.25; }}
        .hero-desc {{ font-size: 14px; color: var(--text-main); opacity: 0.9; line-height: 1.6; }}
        .main-share-trigger {{ background: var(--accent-glow); color: #000; border: none; padding: 6px 12px; border-radius: 4px; font-weight: 700; font-size: 11px; cursor: pointer; margin-top: 12px; display: inline-flex; align-items: center; gap: 4px; }}

        /* Section Blocks Layout */
        .editorial-row {{ margin-bottom: 32px; scroll-margin-top: 100px; }}
        .row-heading {{ font-size: 14px; font-weight: 700; margin-bottom: 14px; padding-bottom: 6px; border-bottom: 1px solid var(--border-line); display: flex; align-items: center; gap: 6px; text-transform: uppercase; font-family: 'Cabinet Grotesk', sans-serif; letter-spacing: 0.5px; }}
        .row-heading::before {{ content: ''; display: inline-block; width: 3px; height: 12px; background: var(--accent-glow); border-radius: 1px; }}
        
        /* Grid Structure Framework */
        .cards-flex-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 14px; }}
        .news-card {{ background: var(--surface-card); border-radius: 8px; border: 1px solid var(--border-line); overflow: hidden; display: flex; flex-direction: column; position: relative; }}
        .img-wrapper {{ width: 100%; height: 135px; overflow: hidden; position: relative; }}
        .news-card img {{ width: 100%; height: 100%; object-fit: cover; }}
        .share-btn-card {{ position: absolute; top: 8px; right: 8px; background: rgba(0,0,0,0.7); color: #fff; border: 1px solid var(--border-line); border-radius: 50%; width: 28px; height: 28px; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 12px; border: none; }}
        .card-meta {{ padding: 12px; flex-grow: 1; }}
        .card-mini-badge {{ font-size: 9px; text-transform: uppercase; color: var(--accent-glow); font-weight: 700; display: block; margin-bottom: 4px; }}
        .news-card h3 {{ font-size: 13px; font-weight: 600; line-height: 1.35; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }}
        .timestamp {{ font-size: 10.5px; color: var(--text-muted); margin-top: 6px; }}
        
        /* Sidebar Configuration elements */
        .sidebar-shorts {{ background: var(--surface-card); border-radius: 12px; padding: 16px; border: 1px solid var(--border-line); height: fit-content; position: sticky; top: 100px; }}
        .sidebar-title {{ font-family: 'Cabinet Grotesk', sans-serif; font-size: 15px; font-weight: 800; margin-bottom: 14px; text-transform: uppercase; }}
        .short-premium-card {{ position: relative; width: 100%; height: 140px; border-radius: 8px; overflow: hidden; margin-bottom: 10px; border: 1px solid var(--border-line); cursor: pointer; }}
        .short-card-img {{ width: 100%; height: 100%; object-fit: cover; filter: brightness(0.4); }}
        .short-card-overlay {{ position: absolute; bottom: 0; left: 0; width: 100%; padding: 10px; display: flex; flex-direction: column; justify-content: flex-end; height: 100%; }}
        .short-tag {{ background: var(--accent-glow); color: #000; font-size: 8px; font-weight: 800; padding: 1px 4px; border-radius: 2px; text-transform: uppercase; width: fit-content; margin-bottom: 4px; }}
        .short-text-p {{ font-size: 11.5px; font-weight: 600; line-height: 1.35; color: #fff; }}
        .no-data {{ font-size: 11px; color: var(--text-muted); font-style: italic; }}
        
        footer {{ background: var(--ticker-bg); border-top: 1px solid var(--border-line); padding: 24px 16px; text-align: center; margin-top: 40px; }}
        .footer-wrap {{ max-width: 1400px; margin: 0 auto; display: flex; flex-direction: column; align-items: center; gap: 8px; }}
        .footer-logo {{ font-family: 'Cabinet Grotesk', sans-serif; font-size: 18px; font-weight: 800; text-decoration: none; color: var(--text-main); }}
        .footer-logo span {{ color: var(--accent-glow); }}
        .footer-links {{ display: flex; gap: 14px; }}
        .footer-links a {{ color: var(--text-muted); text-decoration: none; font-size: 11.5px; }}
        .copyright {{ font-size: 10.5px; color: var(--text-muted); opacity: 0.6; }}

        /* Responsive Flow Configuration */
        @media(max-width: 1100px) {{
            .portal-container {{ grid-template-columns: 1fr 1fr; }}
            .left-sidebar-nav {{ position: static; flex-direction: row; overflow-x: auto; grid-column: span 2; width: 100%; padding-bottom: 8px; border-bottom: 1px solid var(--border-line); }}
            .left-sidebar-nav a {{ white-space: nowrap; }}
            .sidebar-shorts {{ grid-column: span 2; position: static; }}
        }}
        @media(max-width: 640px) {{
            .portal-container {{ grid-template-columns: 1fr; gap: 20px; }}
            .left-sidebar-nav {{ grid-column: span 1; }}
            .sidebar-shorts {{ grid-column: span 1; }}
            .cards-flex-grid {{ grid-template-columns: 1fr; }}
            .spotlight-hero img {{ height: 180px; }}
            h1 {{ font-size: 18px; }}
        }}
    </style>
</head>
<body>

<div class="progress-container"><div class="progress-bar" id="readingProgress"></div></div>

<div class="ticker-bar">
    <div class="ticker-wrap">🔥 LIVE CRYPTO PULSE: BTC/USD $94,230 (+2.4%) | ETH/USD $3,145 (+1.8%) | NVIDIA (NVDA) $148.50 (+4.1%) | INTV NETWORK RUNNING COMPILATION SUCCESSFUL ⚡</div>
</div>

<header>
    <div class="header-content">
        <div class="brand-zone">
            <a href="#" class="brand">INFO<span>VEX</span></a>
            <div class="punchline">The Pulse of Tomorrow’s Tech, Sports, and Global Intelligence.</div>
        </div>
        <div class="actions-tray">
            <button class="theme-toggle" onclick="toggleTheme()" id="themeBtn">☀️ Mode</button>
        </div>
    </div>
</header>

<main class="portal-container">
    <nav class="left-sidebar-nav">
        <div class="nav-title">Intelligence Feeds</div>
        <a href="#latest" class="active">🔥 Latest Feed</a>
        <a href="#electronics">🔌 Electronics</a>
        <a href="#sports">🏆 Global Sports</a>
        <a href="#facts">💡 Core Facts</a>
        <a href="#films">🎬 Film Tracks</a>
        <a href="#health">🌱 Health & Food</a>
    </nav>

    <section>
        <div class="spotlight-hero">
            <img src="{latest_art['image']}" alt="Core Spotlight Cover">
            <div class="hero-details">
                <span class="section-badge">Breaking Live Updates ({current_cat})</span>
                <h1>{latest_art['title']}</h1>
                <div class="hero-desc">{latest_art['content']}</div>
                <button class="main-share-trigger" onclick="shareArticle('{safe_hero_title}', window.location.href)">Share Breaking News 📤</button>
            </div>
        </div>

        <div class="editorial-row" id="latest">
            <div class="row-heading">🔥 Latest Headlines (Central Stream)</div>
            <div class="cards-flex-grid">{render_feed("Latest")}</div>
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
        <div class="sidebar-title">⚡ Flash Shorts Feed</div>
        {shorts_html}
    </aside>
</main>

<footer>
    <div class="footer-wrap">
        <a href="#" class="footer-logo">INFO<span>VEX</span></a>
        <div class="footer-links">
            <a href="mailto:contact@infovex.com">📬 Corporate Desk: contact@infovex.com</a>
            <a href="#">Privacy Matrix</a>
        </div>
        <div class="copyright">© 2026 Infovex Global Intelligence Network. Powered by Gemini System. All Rights Reserved.</div>
    </div>
</footer>

<script>
// Adaptive Scroll Progress Indicator Bar Tracker
window.onscroll = function() {{
    var winScroll = document.body.scrollTop || document.documentElement.scrollTop;
    var height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
    var scrolled = (winScroll / height) * 100;
    document.getElementById("readingProgress").style.width = scrolled + "%";
}};

// Native Web Share System Context
function shareArticle(title, url) {{
    if (navigator.share) {{
        navigator.share({{ title: title, text: title + " - Read on Infovex Network:", url: url }}).catch(console.error);
    }} else {{
        navigator.clipboard.writeText(title + " - " + url);
        alert("Link copied to clipboard! 🚀");
    }}
}}

// Premium Dark Mode Light Mode Toggle Mechanics
function toggleTheme() {{
    const html = document.documentElement;
    const currentTheme = html.getAttribute("data-theme");
    const newTheme = currentTheme === "dark" ? "light" : "dark";
    html.setAttribute("data-theme", newTheme);
    document.getElementById("themeBtn").innerText = newTheme === "dark" ? "☀️ Mode" : "🌙 Mode";
}}
</script>

</body>
</html>"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(full_html)
    print("Mega Enterprise UI Frame Compiled.")

if __name__ == "__main__":
    generate_automated_blog()
