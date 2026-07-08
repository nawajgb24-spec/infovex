import os, random, datetime, requests, sys, time # time add kiya hai
from github import Github

try:
    g = Github(os.getenv("GITHUB_TOKEN"))
    repo = g.get_repo(os.getenv("GITHUB_REPOSITORY"))
    
    # Thoda wait karte hain taaki server load na ho
    time.sleep(5) 
    
    contents = repo.get_contents("index.html")
    html = contents.decoded_content.decode("utf-8")
    
    cat = random.choice(["Sports", "Lifestyle", "Technology", "Business", "Stock News"])
    topic = "Market Updates"
    try:
        rss = requests.get("https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en", timeout=10).text
        titles = [t.split('</title>')[0] for t in rss.split('<title>')[2:10]]
        if titles: topic = random.choice(titles).split(' - ')[0]
    except: pass

    time_str = datetime.datetime.now().strftime("%B %d, %Y")
    post_html = f'<div class="post-card"><div class="meta">{time_str} • {cat}</div><h2>{topic}</h2><div class="preview-text">Latest verified editorial report.</div><div class="full-story"><p>Comprehensive coverage of {topic} is now live.</p></div></div>'
    short_html = f'<div class="short-card"><div class="short-tag">{cat}</div><h4>{topic}</h4></div>'

    if post_html not in html:
        new_html = html.replace('<!-- INJECT_POST -->', f'{post_html}\n<!-- INJECT_POST -->')
        new_html = new_html.replace('<!-- INJECT_SHORT -->', f'{short_html}\n<!-- INJECT_SHORT -->')
        
        # Ek aur baar wait, taaki update fail na ho
        time.sleep(2) 
        repo.update_file(contents.path, f"AI Auto-Post: {cat}", new_html, contents.sha)
        print("SUCCESS!")
    else:
        print("Content already updated.")

except Exception as e:
    print(f"Server Error (GitHub side issue): {e}")
    sys.exit(1)
