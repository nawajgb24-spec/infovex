import os, random, datetime, requests, sys
from github import Github

# Initialize
try:
    g = Github(os.getenv("GITHUB_TOKEN"))
    repo = g.get_repo(os.getenv("GITHUB_REPOSITORY"))
    contents = repo.get_contents("index.html")
    html = contents.decoded_content.decode("utf-8")
except Exception as e:
    print(f"Error initializing: {e}")
    sys.exit(1)

# Topic & Content
cat = random.choice(["Sports", "Lifestyle", "Technology", "Business", "Stock News"])
topic = "Market Updates"
try:
    rss = requests.get("https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en", timeout=5).text
    titles = [t.split('</title>')[0] for t in rss.split('<title>')[2:10]]
    if titles: topic = random.choice(titles).split(' - ')[0]
except: pass

time_str = datetime.datetime.now().strftime("%B %d, %Y")
post_html = f'<div class="post-card"><div class="meta">{time_str} • {cat}</div><h2>{topic}</h2><div class="preview-text">Latest verified editorial report.</div><div class="full-story"><p>Comprehensive coverage of {topic} is now live.</p></div></div>'
short_html = f'<div class="short-card"><div class="short-tag">{cat}</div><h4>{topic}</h4></div>'

# SAFE INJECTION (Duplicate Check)
if post_html not in html:
    print("Updating content...")
    new_html = html.replace('', f'{post_html}\n')
    new_html = new_html.replace('', f'{short_html}\n')
    
    repo.update_file(contents.path, f"AI Auto-Post: {cat}", new_html, contents.sha)
    print("SUCCESS: Content injected safely.")
else:
    print("Content already exists, skipping to avoid bloat.")
