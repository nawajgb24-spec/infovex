import os
import json
import random
import urllib.parse
from google import genai
from google.genai import types
from datetime import datetime

# API Key validation
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY environment variable is missing!")
    exit(1)

client = genai.Client(api_key=api_key)

def generate_automated_blog():
    try:
        # 1. Categories Pool with specific weightage mapping
        # High demand categories run more frequently. Health & Food runs occasionally (approx 3 times a week)
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
        print(f"Target Category for this run: {chosen_category}")

        # 2. Google Search Grounding for Real-Time High-Traffic Topics
        config = types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())]
        )
        
        search_prompt = f"Identify the absolute highest-traffic trending news topic, viral search query or major global breakthrough right now for '{chosen_category}' in 2026. Return ONLY the plain headline text without quotes or markdown."
        topic_response = client.models.generate_content(model='gemini-2.5-flash', contents=search_prompt, config=config)
        topic = topic_response.text.strip().replace('"', '')
        print(f"Live Searched Topic: {topic}")

        # 3. Main Analytical Article Generation (Clean HTML Output)
        main_prompt = f"""
        Act as a chief digital news editor. Write a premium, deeply detailed, and original news report about '{topic}' specifically under the category '{chosen_category}' set in the year 2026.
        Focus on high user-intent traffic keywords. Organize using explicit <h2> sub-headings and short clear paragraphs. 
        Output format: Direct clean HTML strings inside text, no markdown backticks, no markdown code blocks.
        """
        main_response = client.models.generate_content(model='gemini-2.5-flash', contents=main_prompt, config=config)
        main_text = main_response.text.strip().replace('\n', '<br>')

        # 4. JSON Prompt for Premium Google Shorts Text + Relevant Image Keyword
        short_prompt = f"""
        Analyze this topic: '{topic}'.
        Generate a strictly valid JSON response containing exactly two fields:
        1. 'text': An explosive, engaging bullet news summary under 25 words for a Google Short card.
        2. 'keyword': 2 or 3 precise English words to find a stunning photography image representing this short on Unsplash.
        Output ONLY raw valid JSON code. No markdown formatting, no backticks.
        """
        short_response = client.models.generate_content(model='gemini-2.5-flash', contents=short_prompt)
        
        try:
            short_data = json.loads(short_response.text.strip().replace('```json', '').replace('```', ''))
            short_text = short_data.get("text", f"Massive search surge reported for {topic} online.")
            short_kw = short_data.get("keyword", chosen_category)
        except:
            short_text = f"Live breaking updates on {topic} surfaces globally."
            short_kw = chosen_category

        # 5. Dynamic High-Quality Cover Images via Unsplash Featured API
        main_search_term = urllib.parse.quote(f"{chosen_category} high tech trend")
        main_image_url = f"https://images.unsplash.com/featured/1200x650?{main_search_term}&sig={random.randint(1, 9999)}"

        short_search_term = urllib.parse.quote(short_kw)
        short_image_url = f"https://images.unsplash.com/featured/400x400?{short_search_term}&sig={random.randint(1, 9999)}"

        # 6. Database Serialization (JSON File Management)
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
        db[chosen_category] = db[chosen_category][:4]  # Restrict history layout to 4 cards max
        
        new_short = {
            "text": short_text,
            "image": short_image_url,
            "category": chosen_category
        }
        db["shorts"].insert(0, new_short)
        db["shorts"] = db["shorts"][:5]  # Display top 5 premium shorts

        with open(data_file, "w", encoding="utf-8") as f:
            json.dump(db, f, indent=4)

        # 7. Compile Advanced UI Layout Portal
        build_magazine_portal(db, new_post, chosen_category)

    except Exception as e:
        print(f"Critical execution fault: {str(e)}")
        exit(1)

def build_magazine_portal(db, latest_art, current_cat):
    def render_feed(cat_name):
        items = db.get(cat_name, [])
        if not items:
            return "<p class='no-data'>AI system actively scanning live search feeds for upcoming updates...</p>"
        
        html = ""
        for i in items:
            html += f"""
            <div class="news-card">
                <div class="img-wrapper">
                    <img src="{i['image']}" alt="Infovex Media Core">
                </div>
                <div class="card-meta">
                    <h3>{i['title']}</h3>
                    <p class="timestamp">🕒 {i['date']}</p>
                </div>
            </div>
            """
        return html

    # Compile Premium Shorts Feed with Background Imagery and Translucent Filters
    shorts_html = ""
    for s in db.get("shorts", []):
        img = s.get("image") if isinstance(s, dict) else "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=400&q=80"
        txt = s.get("text", s) if isinstance(s, dict) else s
        cat = s.get("category", "Live Network") if isinstance(s, dict) else "BREAKING"
        
        shorts_html += f"""
        <div class="short-premium-card">
            <img class="short-card-img" src="{img}" alt="Shorts Network">
            <div class="short-card-overlay">
                <span class="short-tag">{cat}</span>
                <p class="short-text-p">{txt}</p>
            </div>
        </div>
        """

    # Ultra-Premium Magazine-Style Frontend Layout
    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Infovex Premium Newsroom | Intelligence Hub</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Cabinet+Grotesk:wght@800&display=swap" rel="stylesheet">
    <style>
        :root {{
            --dark-canvas: #060913;
            --surface-panel: #0d1222;
            --border-glass: #1e293b;
            --font-primary: #f8fafc;
            --font-secondary: #94a3b8;
            --hyper-blue: #38bdf8;
            --neon-green: #10b981;
        }}
        
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ background-color: var(--dark-canvas); color: var(--font-primary); font-family: 'Plus Jakarta Sans', sans-serif; overflow-x: hidden; }}
        
        header {{
            background-color: rgba(6, 9, 19, 0.9);
            backdrop-filter: blur(20px);
            border-bottom: 1px solid var(--border-glass);
            position: sticky; top: 0; z-index: 2000;
        }}
        .header-wrap {{
            max-width: 1400px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; padding: 18px 24px;
        }}
        .brand {{ font-family: 'Cabinet Grotesk', sans-serif; font-size: 28px; font-weight: 800; text-transform: uppercase; letter-spacing: -0.5px; text-decoration: none; color: #fff; }}
        .brand span {{ color: var(--hyper-blue); }}
        .live-tag {{ background: rgba(239, 68, 68, 0.12); color: #f87171; font-size: 11px; font-weight: 700; padding: 5px 12px; border-radius: 20px; text-transform: uppercase; display: flex; align-items: center; gap: 6px; }}
        .live-dot {{ width: 6px; height: 6px; background: #ef4444; border-radius: 50%; animation: pulse 1.2s infinite; }}
        
        @keyframes pulse {{ 0%{{opacity:0.4;}} 50%{{opacity:1;}} 100%{{opacity:0.4;}} }}

        .portal-grid {{
            max-width: 1400px; margin: 32px auto; display: grid; grid-template-columns: 2.3fr 1fr; gap: 36px; padding: 0 24px;
        }}
        
        .spotlight-hero {{ background: var(--surface-panel); border-radius: 16px; border: 1px solid var(--border-glass); overflow: hidden; margin-bottom: 48px; box-shadow: 0 20px 40px -15px rgba(0,0,0,0.6); }}
        .spotlight-hero img {{ width: 100%; height: 420px; object-fit: cover; }}
        .hero-details {{ padding: 28px; }}
        .section-badge {{ background: rgba(56, 189, 248, 0.12); color: var(--hyper-blue); font-size: 11px; font-weight: 700; padding: 5px 10px; border-radius: 6px; text-transform: uppercase; }}
        h1 {{ font-family: 'Cabinet Grotesk', sans-serif; font-size: 34px; font-weight: 800; margin: 16px 0 12px 0; line-height: 1.2; color: #fff; letter-spacing: -0.5px; }}
        .hero-desc {{ font-size: 16px; color: #cbd5e1; line-height: 1.7; }}
        .hero-desc h2 {{ font-size: 20px; color: #fff; margin: 20px 0 10px 0; }}

        .editorial-row {{ margin-bottom: 44px; }}
        .row-heading {{ font-size: 19px; font-weight: 700; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 1px solid var(--border-glass); display: flex; align-items: center; gap: 10px; color: #fff; text-transform: uppercase; font-family: 'Cabinet Grotesk', sans-serif; letter-spacing: 0.5px; }}
        .row-heading::before {{ content: ''; display: inline-block; width: 4px; height: 16px; background: var(--hyper-blue); border-radius: 2px; }}
        
        .cards-flex-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 20px; }}
        .news-card {{ background: var(--surface-panel); border-radius: 12px; border: 1px solid var(--border-glass); overflow: hidden; display: flex; flex-direction: column; transition: transform 0.2s ease, border-color 0.2s ease; }}
        .news-card:hover {{ transform: translateY(-3px); border-color: var(--hyper-blue); }}
        .img-wrapper {{ width: 100%; height: 160px; overflow: hidden; }}
        .news-card img {{ width: 100%; height: 100%; object-fit: cover; transition: transform 0.4s ease; }}
        .news-card:hover img {{ transform: scale(1.04); }}
        .card-meta {{ padding: 16px; flex-grow: 1; display: flex; flex-direction: column; justify-content: space-between; }}
        .news-card h3 {{ font-size: 15px; font-weight: 600; color: #f1f5f9; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }}
        .timestamp {{ font-size: 12px; color: var(--font-secondary); margin-top: 10px; }}

        /* SHORTS GRID IMPLEMENTATION WITH SMOOTH ADAPTIVE RADIAL GRADIENTS */
        .sidebar-shorts {{ background: #090e1a; border-radius: 16px; padding: 24px; border: 1px solid var(--border-glass); height: fit-content; position: sticky; top: 100px; }}
        .sidebar-title {{ font-family: 'Cabinet Grotesk', sans-serif; font-size: 20px; font-weight: 800; color: #fff; margin-bottom: 20px; display: flex; align-items: center; gap: 8px; letter-spacing: 0.5px; text-transform: uppercase; }}
        
        .short-premium-card {{
            position: relative; width: 100%; height: 190px; border-radius: 14px; overflow: hidden; margin-bottom: 16px;
            border: 1px solid var(--border-glass); box-shadow: 0 4px 20px rgba(0,0,0,0.5); transition: transform 0.2s ease, border-color 0.2s ease;
        }}
        .short-premium-card:hover {{ transform: scale(1.02); border-color: var(--hyper-blue); }}
        .short-card-img {{ width: 100%; height: 100%; object-fit: cover; filter: brightness(0.4) contrast(1.1); }}
        
        .short-card-overlay {{
            position: absolute; bottom: 0; left: 0; width: 100%; padding: 16px;
            background: linear-gradient(0deg, rgba(6,9,19,1) 0%, rgba(6,9,19,0.4) 70%, rgba(6,9,19,0) 100%);
            display: flex; flex-direction: column; justify-content: flex-end; height: 100%;
        }}
        .short-tag {{
            background: var(--hyper-blue); color: #060913; font-size: 9px; font-weight: 800; 
            padding: 2px 6px; border-radius: 4px; text-transform: uppercase; width: fit-content; margin-bottom: 8px; letter-spacing: 0.5px;
        }}
        .short-text-p {{ font-size: 13.5px; font-weight: 600; line-height: 1.45; color: #ffffff; text-shadow: 0 2px 4px rgba(0,0,0,0.6); }}

        .no-data {{ font-size: 13px; color: var(--font-secondary); font-style: italic; }}

        /* Responsive Breakpoints */
        @media(max-width: 1024px) {{
            .portal-grid {{ grid-template-columns: 1fr; gap: 40px; }}
            .sidebar-shorts {{ position: static; }}
        }}
        @media(max-width: 640px) {{
            .header-wrap {{ padding: 16px; }}
            .brand {{ font-size: 23px; }}
            h1 {{ font-size: 26px; }}
            .spotlight-hero img {{ height: 240px; }}
        }}
    </style>
</head>
<body>

<header>
    <div class="header-wrap">
        <a href="#" class="brand">INFO<span>VEX</span></a>
        <div class="live-tag"><span class="live-dot"></span> SEARCH PULSE NETWORK</div>
    </div>
</header>

<main class="portal-grid">
    <section>
        <div class="spotlight-hero">
            <img src="{latest_art['image']}" alt="Spotlight Analytics">
            <div class="hero-details">
                <span class="section-badge">Featured Update ({current_cat})</span>
                <h1>{latest_art['title']}</h1>
                <div class="hero-desc">{latest_art['content']}</div>
            </div>
        </div>

        <div class="editorial-row">
            <div class="row-heading">🔌 Electronics & Hardware</div>
            <div class="cards-flex-grid">{render_feed("Electronics")}</div>
        </div>

        <div class="editorial-row">
            <div class="row-heading">🏆 Global Sports Track</div>
            <div class="cards-flex-grid">{render_feed("Sports")}</div>
        </div>

        <div class="editorial-row">
            <div class="row-heading">💡 Interesting Facts Hub</div>
            <div class="cards-flex-grid">{render_feed("Interesting Facts")}</div>
        </div>

        <div class="editorial-row">
            <div class="row-heading">🎬 Global Film Industry</div>
            <div class="cards-flex-grid">{render_feed("Film Industry")}</div>
        </div>

        <div class="editorial-row">
            <div class="row-heading">🌱 Health & Food Insights</div>
            <div class="cards-flex-grid">{render_feed("Health & Food")}</div>
        </div>
    </section>

    <aside class="sidebar-shorts">
        <div class="sidebar-title">⚡ Google Shorts Feed</div>
        {shorts_html}
    </aside>
</main>

</body>
</html>"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(full_html)
    print("Multi-category news portal built successfully.")

if __name__ == "__main__":
    generate_automated_blog()
