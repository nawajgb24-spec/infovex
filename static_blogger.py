import os
import json
import random
import urllib.parse
from google import genai
from google.genai import types
from datetime import datetime

# API Initialization
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

def generate_automated_blog():
    categories = ["Electronics", "Sports", "Interesting Facts", "Film Industry", "Health & Food"]
    chosen_category = random.choice(categories)
    date_str = datetime.now().strftime("%B %d, %Y")

    config = types.GenerateContentConfig(tools=[types.Tool(google_search=types.GoogleSearch())])
    
    # Generate Content
    topic_res = client.models.generate_content(model='gemini-2.5-flash', contents=f"Top trending news for {chosen_category} in 2026", config=config)
    topic = topic_res.text.strip().replace('"', '')
    
    main_res = client.models.generate_content(model='gemini-2.5-flash', contents=f"Write a professional news report on {topic} for category {chosen_category}. No markdown, plain text only.", config=config)
    main_text = main_res.text.strip().replace('\n', '<br>')
    
    # Generate Short
    short_res = client.models.generate_content(model='gemini-2.5-flash', contents=f"Summarize {topic} in under 20 words for a news short. Output as JSON: {{\"text\": \"...\"}}")
    try:
        short_json = json.loads(short_res.text.strip().replace('```json', '').replace('```', ''))
        short_text = short_json['text']
    except:
        short_text = topic

    # Images
    main_img = f"https://images.unsplash.com/featured/1200x650?{urllib.parse.quote(chosen_category)}&sig={random.randint(1,9999)}"
    short_img = f"https://images.unsplash.com/featured/400x400?{urllib.parse.quote(chosen_category)}&sig={random.randint(1,9999)}"

    # Update Data
    db_file = "data.json"
    db = json.load(open(db_file)) if os.path.exists(db_file) else {c: [] for c in ["Latest", "Electronics", "Sports", "Interesting Facts", "Film Industry", "Health & Food", "shorts"]}
    
    new_post = {"title": topic, "date": date_str, "content": main_text, "image": main_img, "category": chosen_category}
    db["Latest"].insert(0, new_post)
    db[chosen_category].insert(0, new_post)
    db["shorts"].insert(0, {"text": short_text, "image": short_img, "category": chosen_category})

    # Trim lists
    for key in db: db[key] = db[key][:10]
    json.dump(db, open(db_file, "w"), indent=4)
    
    # Render HTML
    render_html(db, new_post)

def render_html(db, latest):
    html = f"""<!DOCTYPE html>
<html data-theme="dark">
<head>
    <style>
        :root {{ --bg: #04060d; --card: #0b0f1e; --accent: #38bdf8; --text: #fff; }}
        body {{ background: var(--bg); color: var(--text); font-family: sans-serif; margin:0; }}
        .portal {{ display: grid; grid-template-columns: 240px 1fr 300px; gap: 20px; padding: 20px; }}
        .nav a {{ display: block; color: #94a3b8; padding: 10px; text-decoration: none; }}
        .card {{ background: var(--card); border-radius: 10px; overflow: hidden; margin-bottom: 20px; }}
        .card img {{ width: 100%; height: 200px; object-fit: cover; }}
        .modal {{ display: none; position: fixed; top:0; left:0; width:100%; height:100%; background: rgba(0,0,0,0.9); justify-content: center; align-items: center; }}
        .modal-content {{ background: #111; padding: 20px; border-radius: 15px; width: 90%; max-width: 400px; text-align: center; }}
    </style>
</head>
<body>
    <div class="portal">
        <nav class="nav"><h3>Categories</h3><a href="#latest">Latest</a><a href="#electronics">Electronics</a></nav>
        <main>
            <div class="card">
                <img src="{latest['image']}">
                <div style="padding:15px;"><h1>{latest['title']}</h1><p>{latest['content']}</p></div>
            </div>
            <div id="latest"><h2>Latest News</h2>""" + "".join([f"<div class='card'><h3>{item['title']}</h3></div>" for item in db['Latest']]) + """</div>
        </main>
        <aside>
            <h3>Shorts</h3>""" + "".join([f"<div class='card' onclick='openModal(\"{s['text']}\", \"{s['image']}\")' style='cursor:pointer'><img src='{s['image']}'><p>{s['text']}</p></div>" for s in db['shorts']]) + """
        </aside>
    </div>
    <div id="modal" class="modal" onclick="this.style.display='none'">
        <div class="modal-content"><img id="mImg" style="width:100%;"><p id="mText"></p></div>
    </div>
    <script>
        function openModal(t, i) {{ document.getElementById('mText').innerText=t; document.getElementById('mImg').src=i; document.getElementById('modal').style.display='flex'; }}
    </script>
</body>
</html>"""
    with open("index.html", "w") as f: f.write(html)

if __name__ == "__main__":
    generate_automated_blog()
