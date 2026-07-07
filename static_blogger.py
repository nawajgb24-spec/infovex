import os, random, datetime, requests, sys
from github import Github

print("🚀 Step 1: Detective Script Started...")
sys.stdout.flush()

try:
    # Auth & Repo Setup
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(os.getenv("GITHUB_REPOSITORY"))
    print(f"✅ Step 2: Connected to Repo -> {repo.name}")
    sys.stdout.flush()

    CATEGORIES = ["Sports", "Lifestyle", "Technology", "Business"]
    cat = random.choice(CATEGORIES)
    topic = "Global Market Updates"

    # RSS Fetch
    try:
        rss = requests.get("https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en", timeout=5).text
        titles = [t.split('</title>')[0] for t in rss.split('<title>')[2:10]]
        if titles: topic = random.choice(titles).split(' - ')[0]
    except: pass
    print(f"✅ Step 3: Topic Selected -> {topic}")
    sys.stdout.flush()

    # Images
    imgs = random.sample([
        "https://images.unsplash.com/photo-1504711434969-e33886168f5c?auto=format&fit=crop&w=1200&q=80",
        "https://images.unsplash.com/photo-1495020689067-958852a6565d?auto=format&fit=crop&w=1200&q=80",
        "https://images.unsplash.com/photo-1505373877841-8d25f7d46678?auto=format&fit=crop&w=1200&q=80"
    ], 3)
    i_tag = [f'<img src="{i}" style="width:100% !important; max-width:100%; display:block; margin:20px 0; border-radius:5px;">' for i in imgs]

    article_html = f'{i_tag[0]}<p>Breaking updates regarding <b>{topic}</b> have captured global attention today.</p>{i_tag[1]}<p>Experts are closely analyzing the impacts in the {cat} sector.</p>{i_tag[2]}<p>More detailed reports are expected soon.</p>'
    short_html = f'<h4>Update: {topic}</h4><p>Latest developments are shifting trends globally.</p>'

    # GitHub File Fetch (Bina branch hardcode kiye)
    print("⏳ Step 4: Fetching index.html from GitHub...")
    sys.stdout.flush()
    contents = repo.get_contents("index.html")
    html = contents.decoded_content.decode("utf-8")
    print("✅ Step 4 Done: index.html read successfully.")
    sys.stdout.flush()

    time_str = datetime.datetime.now().strftime("%B %d, %Y • %I:%M %p")
    new_post = f'\n\n<div class="post-card"><div class="meta">{time_str} • {cat}</div><h2>{topic}</h2><div class="preview-text">Latest verified editorial report.</div><div class="full-story">{article_html}</div></div>'
    new_short = f'\n\n<div class="short-card"><div class="short-tag">{cat}</div>{short_html}</div>'

    if '' in html:
        html = html.replace('', new_post).replace('', new_short)
        print("⏳ Step 5: Saving changes to GitHub...")
        sys.stdout.flush()
        # Bina branch naam ke save karega taaki 404 error na aaye
        repo.update_file(contents.path, f"AI Auto-Post: {cat}", html, contents.sha)
        print("🎉 SUCCESS: File updated on GitHub!")
    else:
        print("❌ ERROR: tags missing in index.html!")
        sys.exit(1)

except Exception as e:
    # Asli error yahan pakda jayega
    print(f"\n🔥🔥 CRITICAL ERROR TRAPPED: {str(e)} 🔥🔥\n")
    sys.exit(1)
