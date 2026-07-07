import os, random, datetime, requests, sys
from github import Github

print("🚀 Step 1: Starting Fast-Track Update...")
sys.stdout.flush()

try:
    g = Github(os.getenv("GITHUB_TOKEN"))
    repo = g.get_repo(os.getenv("GITHUB_REPOSITORY"))
    
    # Fast Fetch
    contents = repo.get_contents("index.html")
    html = contents.decoded_content.decode("utf-8")
    
    # Content Generation (Mini)
    cat = random.choice(["Sports", "Lifestyle", "Technology", "Business"])
    time_str = datetime.datetime.now().strftime("%B %d, %Y")
    
    new_post = f'\n<!-- INJECT_POST -->\n<div class="post-card"><div class="meta">{time_str} • {cat}</div><h2>News Update</h2><div class="full-story"><p>Latest automated update processed successfully.</p></div></div>'
    new_short = f'\n<!-- INJECT_SHORT -->\n<div class="short-card"><div class="short-tag">{cat}</div><h4>Live Update</h4><p>System operational.</p></div>'
    
    # Fast Update Logic
    if '<!-- INJECT_POST -->' in html:
        html = html.replace('<!-- INJECT_POST -->', new_post).replace('<!-- INJECT_SHORT -->', new_short)
        
        # Fast Commit
        print("🚀 Step 5: Committing via fast-track...")
        sys.stdout.flush()
        repo.update_file(contents.path, "AI Auto-Post", html, contents.sha)
        print("🎉 SUCCESS!")
    else:
        print("❌ Tags missing!")

except Exception as e:
    print(f"❌ Critical Error: {e}")
    sys.exit(1)
