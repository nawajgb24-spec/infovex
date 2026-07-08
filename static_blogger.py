import os, random, datetime, requests, sys, time, re
from github import Github

print("🚀 Starting NYT Master Auto-Blogger (Safety Bypass Mode)...")
sys.stdout.flush()

ANTI_AI_PROMPT = """
Write like a Pulitzer-prize winning human journalist from The New York Times. 
Write a highly detailed, long-form editorial (aiming for 1000+ words).
Do NOT use robotic words like: delve, furthermore, in conclusion, testament, landscape.
Provide raw HTML ONLY (use <p> and <h3> tags). DO NOT include ```html markdown blocks.
This is a news report, NOT financial or dangerous advice.
"""

CATEGORIES = ["Anime", "Trending News", "Tech", "Sports", "Business", "Lifestyle", "Stock News", "World"]
cat = random.choice(CATEGORIES)

try:
    g = Github(os.getenv("GITHUB_TOKEN"))
    repo = g.get_repo(os.getenv("GITHUB_REPOSITORY"))
    contents = repo.get_contents("index.html")
    html = contents.decoded_content.decode("utf-8")
except Exception as e:
    print(f"❌ Repo Auth Error: {e}")
    sys.exit(1)

# Fetch Topics
titles = []
try:
    search_q = cat.replace(" ", "")
    rss = requests.get(f"[https://news.google.com/rss/search?q=](https://news.google.com/rss/search?q=){search_q}&hl=en-IN&gl=IN&ceid=IN:en", timeout=10).text
    titles = [t.split('</title>')[0] for t in rss.split('<title>')[2:20]]
except: pass

if not titles:
    titles = ["Global Market Strategies and Innovations", "World Economic Shifts", "Tech Advancements for the Future"]

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
article_html = ""
summary_text = ""
topic = ""
slug = ""

# Bypass Safety Filters Payload
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
]

for attempt in range(3):
    topic = random.choice(titles).split(' - ')[0]
    print(f"🔄 Attempt {attempt+1}: Selected Topic -> {topic} | Category: {cat}")
    sys.stdout.flush()

    slug = re.sub(r'\W+', '-', topic.lower())[:50]
    if slug in html or topic in html:
        print("⚠️ Topic already exists on website. Trying another...")
        continue

    try:
        url = f"[https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=](https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=){GEMINI_API_KEY}"
        
        main_payload = {
            "contents": [{"parts": [{"text": f"Write a massive journalistic editorial on: '{topic}'. Category: {cat}. {ANTI_AI_PROMPT}"}]}],
            "safetySettings": safety_settings
        }
        
        res = requests.post(url, json=main_payload, timeout=60)
        res_json = res.json()
        
        if 'candidates' not in res_json:
            print(f"⚠️ API Error/Block on topic '{topic}'. API Response: {res_json}")
            continue
            
        clean_text = res_json['candidates'][0]['content']['parts'][0]['text'].replace("```html", "").replace("```", "").strip()
        
        # Summary
        summary_payload = {
            "contents": [{"parts": [{"text": f"Write a 2-sentence journalistic teaser for: {topic}. No markdown."}]}],
            "safetySettings": safety_settings
        }
        res_s = requests.post(url, json=summary_payload, timeout=15)
        summary_text = res_s.json()['candidates'][0]['content']['parts'][0]['text'].strip()
        
        if len(clean_text) > 300:
            article_html = clean_text
            break
        else:
            print("⚠️ Article generated was too short. Retrying...")
            
    except Exception as e:
        print(f"⚠️ Attempt {attempt+1} Error: {e}")

if not article_html:
    print("❌ All 3 attempts failed. Exiting.")
    sys.exit(1)

time_str = datetime.datetime.now().strftime("%B %d, %Y")
slug = f"{slug}-{random.randint(100,999)}"
img_keyword = topic.replace(" ", "%20").replace('"', '').replace("'", "")
image_url = f"[https://image.pollinations.ai/prompt/professional%20news%20photography%20of%20](https://image.pollinations.ai/prompt/professional%20news%20photography%20of%20){img_keyword}?width=1200&height=650&nologo=true"

full_page_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{topic} - INFOVEX</title>
    <link href="[https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,500;0,700;0,900;1,400&family=Inter:wght@400;500;600;700&display=swap](https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,500;0,700;0,900;1,400&family=Inter:wght@400;500;600;700&display=swap)" rel="stylesheet">
    <style>
        body {{ background: #ffffff; color: #111; font-family: 'Playfair Display', Georgia, serif; line-height: 1.8; margin: 0; padding: 0; }}
        header {{ text-align: center; padding: 30px; border-bottom: 1px solid #ddd; }}
        .logo {{ font-size: 35px; font-weight: 900; text-decoration: none; color: #111; font-family: 'Inter', sans-serif; }}
        .article-container {{ max-width: 800px; margin: 50px auto; padding: 0 20px; }}
        .meta {{ font-family: 'Inter', sans-serif; font-size: 13px; color: #b80000; font-weight: bold; text-transform: uppercase; margin-bottom: 15px; }}
        h1 {{ font-size: 42px; font-weight: 700; margin-bottom: 25px; line-height: 1.2; }}
        .hero-img {{ width: 100%; height: auto; margin-bottom: 30px; border-bottom: 1px solid #eee; }}
        .content p {{ font-size: 19px; margin-bottom: 25px; color: #222; text-align: justify; }}
        .content h3 {{ font-family: 'Inter', sans-serif; font-size: 24px; margin: 40px 0 15px 0; }}
        a.back {{ display: inline-block; margin-top: 40px; font-family: 'Inter', sans-serif; color: #b80000; text-decoration: none; font-weight: bold; font-size: 14px; text-transform: uppercase; }}
        a.back:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <header><a href="../index.html" class="logo">INFOVEX</a></header>
    <div class="article-container">
        <div class="meta">{cat} • {time_str}</div>
        <h1>{topic}</h1>
        <img src="{image_url}" class="hero-img" alt="{topic}">
        <div class="content">
            {article_html}
        </div>
        <a href="../index.html" class="back">← Back to Homepage</a>
    </div>
</body>
</html>"""

try:
    repo.create_file(f"posts/{slug}.html", f"New Article: {topic}", full_page_html, branch="main")
    print(f"✅ Saved individual article: posts/{slug}.html")
except Exception as e:
    print(f"❌ Error saving article: {e}")
    sys.exit(1)

time.sleep(3) 

new_card = f"""
        <div class="post-card" data-cat="{cat}">
            <div class="post-meta">{cat} • {time_str}</div>
            <h2><a href="posts/{slug}.html">{topic}</a></h2>
            <p>{summary_text}</p>
        </div>
        """

if "" in html:
    new_html = html.replace("", new_card)
    repo.update_file(contents.path, f"Homepage Update: {cat}", new_html, contents.sha)
    print("🎉 SUCCESS: Homepage updated flawlessly!")
else:
    print("❌ Marker missing in index.html")
    sys.exit(1)
