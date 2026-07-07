import os, random, datetime, requests
from github import Github

g = Github(os.getenv("GITHUB_TOKEN"))
repo = g.get_repo(os.getenv("GITHUB_REPOSITORY"))
contents = repo.get_contents("index.html")
html = contents.decoded_content.decode("utf-8")

# Fresh Content
cat = random.choice(["Sports", "Lifestyle", "Technology", "Business"])
topic = "Market Updates"
time = datetime.datetime.now().strftime("%B %d, %Y")

post = f'\n<div class="post-card"><div class="meta">{time} • {cat}</div><h2>{topic}</h2><div class="preview-text">Latest editorial report.</div></div>'
short = f'\n<div class="short-card"><div class="short-tag">{cat}</div><h4>{topic}</h4></div>'

# Clean Logic: Replace only the placeholder
new_html = html.replace('', f'{post}\n')
new_html = new_html.replace('', f'{short}\n')

repo.update_file(contents.path, "Update Content", new_html, contents.sha)
