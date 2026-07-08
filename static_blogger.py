import os, random, datetime, requests, sys, time, re
from github import Github

print("🚀 Starting NYT Master Auto-Blogger...")
sys.stdout.flush()

ANTI_AI_PROMPT = """
CRITICAL RULES FOR HUMAN-LIKE WRITING:
1. DO NOT use words like: delve, furthermore, in conclusion, testament, landscape, bespoke, underscore, paradigm, moreover, intricate, tapestry, vital, beacon.
2. Write like a Pulitzer-prize winning human journalist from The New York Times.
3. Vary sentence lengths. Use natural journalistic flow. No robotic transitions.
4. The article MUST be extremely detailed, aiming for 2500 to 5000 words.
5. Do not include markdown code blocks. Return RAW HTML ONLY.
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

# 1. Fetch Trending Topic safely
topic = "Global Market Strategies and Innovations"
try:
    search_q = cat.replace(" ", "")
    rss = requests.get(f"https://news.google.com/rss/search?q={search_q}&hl=en-IN&gl=IN&ceid=IN:en", timeout=10).text
    titles = [t.split('</title>')[0] for t in rss.split('<title>')[2:15]]
    if titles: 
        topic = random.choice(titles).split(' - ')[0]
except: pass

print(f"✅ Selected Topic: {topic} | Category: {cat}")
sys.stdout.flush()

# DUPLICATE CHECK: Agar topic pehle se front page par hai toh yahin rok do
slug = re.sub(r'\W+', '-', topic.lower())[:50]
if slug in html or topic in html:
    print("⚠️ Topic already exists on website. Skipping to avoid duplicates.")
    sys.exit(0)

# 2. HD Image URL (Copyright Free)
img_keyword = topic.replace(" ", "%20").replace('"', '').replace("'", "")
image_url = f"https://image.pollinations.ai/prompt/professional%20news%20photography%20of%20{img_keyword}?width=1200&height=650&nologo=true"

# 3. Generate Content
article_html = f"<p>Breaking detailed coverage on {topic}.</p>"
summary_text = f"An in-depth look at {topic}."

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        main_prompt = f"Write a massive 2500-word editorial on: '{topic}'. Category: {cat}. Structure with engaging introduction, <h3> subheadings, factual analysis, and strong closing. {ANTI_AI_PROMPT}"
        
        res = requests.post(url, json={"contents":[{"parts":[{"text": main_prompt}]}]}, timeout=60)
        clean_text = res.json()['candidates'][0]['content']['parts'][0]['text'].replace("```html", "").replace("```", "").strip()
        if len(clean_text) > 100: article_html = clean_text
            
        res_s = requests.post(url, json={"contents":[{"parts":[{"text": f"Write a 2-sentence teaser for: {topic}. No markdown."}]}]}, timeout=15)
        summary_text = res_s.json()['candidates'][0]['content']['parts'][0]['text'].strip()
    except Exception as e:
        print(f"⚠️ Content Gen Error: {e}")

time_str = datetime.datetime.now().strftime("%B %d, %Y")
slug = f"{slug}-{random.randint(100,999)}"

# 4. Create Individual Article Page (Safe in /posts/ folder)
full_page_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{topic} - INFOVEX</title>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,500;0,700;0,900;1,400&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body {{ background: #ffffff; color: #111; font-family: 'Playfair Display', Georgia, serif; line-height: 1.8; margin: 0; padding: 0; }}
        header {{ text-align: center; padding: 30px; border-bottom: 1px solid #ddd; }}
        .logo {{ font-size: 35px; font-weight: 900; text-decoration: none; color: #111; font-family: 'Inter', sans-serif; }}
        .article-container {{ max-width: 800px; margin: 50px auto; padding: 0 20px; }}
        .meta {{ font-family: 'Inter', sans-serif; font-size: 13px; color: #b80000; font-weight: bold; text-transform: uppercase; margin-bottom: 15px; }}
        h1 {{ font-size: 42px; font-weight: 700; margin-bottom: 25px; line-height: 1.2; }}
        .hero-img {{ width: 100%; height: auto; margin-bottom: 30px; border-bottom: 3px solid #111; }}
        .content p {{ font-size: 19px; margin-bottom: 25px; color: #222; text-align: justify; }}
        .content h3 {{ font-family: 'Inter', sans-serif; font-size: 22px; margin: 40px 0 15px 0; }}
        a.back {{ display: inline-block; margin-top: 40px; font-family: 'Inter', sans-serif; color: #b80000; text-decoration: none; font-weight: bold; }}
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

time.sleep(3) 

# 5. Safely Update Homepage
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
