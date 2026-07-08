import os
import re
import sys
import time
import random
import logging
import datetime
from urllib.parse import quote

import requests
import xml.etree.ElementTree as ET
from github import Github
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ==========================================================
# Configuration
# ==========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("INFOVEX")

CATEGORIES = [
     "World",
    "Trending News",
    "Business",
    "Stock News",
    "Tech",
    "Sports",
    "Lifestyle",
    "Anime",
    "Food & Nutrition",
]

HOME_MARKER = "<!-- BLOG_INSERT_MARKER -->"
MAX_HOME_POSTS = 30

NEWS_RSS_URL = "https://news.google.com/rss/search"
GEMINI_MODEL = "gemini-2.5-flash"

GEMINI_URL = (
     f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

)

ANTI_AI_PROMPT = """
Write an original, deeply researched editorial news article.

Requirements:

- Output RAW HTML only.
- Use only <h3> and <p>.
- Never output Markdown.
- Never output ``` blocks.
- Write between 3000 and 5000 words.
- Every section must be detailed.
- Include historical background.
- Include current developments.
- Include expert analysis.
- Include future outlook.
- Use natural newspaper language.

Never use these words:

delve
furthermore
in conclusion
testament
landscape
bespoke
underscore
paradigm
moreover
intricate
tapestry
vital
beacon

Do not mention AI.

Do not mention language models.

Everything must be completely original.
"""


SAFETY_SETTINGS = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE",
    },
]

# ==========================================================
# HTTP Session
# ==========================================================

def build_session() -> requests.Session:
    session = requests.Session()

    retries = Retry(
        total=3,
        backoff_factor=2,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST"],
    )

    adapter = HTTPAdapter(max_retries=retries)

    session.mount("https://", adapter)
    session.mount("http://", adapter)

    session.headers.update(
        {
            "User-Agent": (
                "INFOVEX News Bot/2.0 "
                "(GitHub Actions)"
            )
        }
    )

    return session


session = build_session()

# ==========================================================
# Utilities
# ==========================================================

def slugify(text: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", text.lower())
    slug = slug.strip("-")

    if len(slug) > 70:
        slug = slug[:70]

    return slug


def word_count(text: str) -> int:
    return len(re.findall(r"\w+", text))


def today_string() -> str:
    return datetime.datetime.utcnow().strftime("%B %d, %Y")


def pollinations_image(topic: str) -> str:
    prompt = quote(f"professional news photography of {topic}")

    return (
        "https://image.pollinations.ai/prompt/"
        f"{prompt}"
        "?width=1200&height=650&nologo=true"
    )


logger.info("INFOVEX Auto Blogger v2 starting...")

# ==========================================================
# GitHub Repository
# ==========================================================

def github_repo():
    token = os.getenv("GITHUB_TOKEN")
    repo_name = os.getenv("GITHUB_REPOSITORY")

    if not token:
        raise RuntimeError("GITHUB_TOKEN not found.")

    if not repo_name:
        raise RuntimeError("GITHUB_REPOSITORY not found.")

    gh = Github(token)
    return gh.get_repo(repo_name)


# ==========================================================
# Homepage
# ==========================================================

def load_homepage(repo):
    file = repo.get_contents("index.html")
    html = file.decoded_content.decode("utf-8")

    if HOME_MARKER not in html:
        raise RuntimeError("BLOG_INSERT_MARKER missing in index.html")

    return file, html


# ==========================================================
# Google News RSS
# ==========================================================

def fetch_topics(category):

    logger.info(f"Fetching topics for {category}")

    response = session.get(
        NEWS_RSS_URL,
        params={
            "q": category,
            "hl": "en-IN",
            "gl": "IN",
            "ceid": "IN:en"
        },
        timeout=20,
    )

    response.raise_for_status()

    root = ET.fromstring(response.text)

    topics = []

    for item in root.findall(".//item"):

        title = item.findtext("title")

        if not title:
            continue

        title = title.split(" - ")[0].strip()

        if title not in topics:
            topics.append(title)

    logger.info(f"Found {len(topics)} topics")

    return topics


# ==========================================================
# Duplicate Detection
# ==========================================================

def slug_exists(repo, slug):
    try:
        repo.get_contents(f"posts/{slug}.html")
        return True
    except Exception:
        return False


def choose_topic(repo, topics):

    random.shuffle(topics)

    for topic in topics:

        slug = slugify(topic)

        if slug_exists(repo, slug):
            continue

        return topic, slug

    raise RuntimeError("No new topic available.")


# ==========================================================
# Homepage Helpers
# ==========================================================



def inject_card(html, card):

    start = html.find('<div id="posts-container">')

    if start == -1:
        raise RuntimeError("posts-container not found.")

    marker = html.find(HOME_MARKER)

    if marker == -1:
        raise RuntimeError("BLOG_INSERT_MARKER missing.")

    existing = html[start:marker]

    cards = re.findall(
        r'<div class="post-card".*?</div>\s*</div>',
        existing,
        re.DOTALL
    )

    cards.insert(0, card)

    cards = cards[:MAX_HOME_POSTS]

    new_posts = "\n\n".join(cards)

    before = html[:start]

    after = html[marker:]

    return (
        before
        + '<div id="posts-container">\n'
        + new_posts
        + "\n\n"
        + after
    )

# ==========================================================
# Gemini API
# ==========================================================

def gemini_request(prompt):

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not found.")

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "safetySettings": SAFETY_SETTINGS
    }

    response = session.post(
        GEMINI_URL,
        params={"key": api_key},
        json=payload,
        timeout=120
    )

    response.raise_for_status()

    data = response.json()

    if "candidates" not in data:
        raise RuntimeError(f"Gemini Error: {data}")

    return (
        data["candidates"][0]["content"]["parts"][0]["text"]
        .replace("```html", "")
        .replace("```", "")
        .strip()
    )


# ==========================================================
# Generate Article
# ==========================================================

def generate_article(topic, category):

    prompt = f"""
Topic:
{topic}

Category:
{category}

{ANTI_AI_PROMPT}
"""

    article = gemini_request(prompt)

    if word_count(article) < 3000:
        raise RuntimeError("Generated article is too short.")

    return article


# ==========================================================
# Generate Summary
# ==========================================================

def generate_summary(topic):

    prompt = f"""
Write exactly two newsroom-style sentences summarizing:

{topic}

No markdown.
"""

    return gemini_request(prompt)


# ==========================================================
# Image
# ==========================================================

def article_image(topic):
    return pollinations_image(topic)

# ==========================================================
# HTML Builder
# ==========================================================

SITE_NAME = "INFOVEX"
SITE_URL =  "https://infovex.vercel.app"


def article_html(topic, category, article, image_url, slug):

    date = today_string()

    canonical = f"{SITE_URL}/posts/{slug}.html"

    description = re.sub(r"<[^>]+>", "", article)
    description = " ".join(description.split())[:180]

    return f"""<!DOCTYPE html>
<html lang="en">
<head>

<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">

<title>{topic} | {SITE_NAME}</title>

<meta name="description" content="{description}">
<meta name="robots" content="index,follow">

<link rel="canonical" href="{canonical}">

<meta property="og:type" content="article">
<meta property="og:title" content="{topic}">
<meta property="og:description" content="{description}">
<meta property="og:image" content="{image_url}">
<meta property="og:url" content="{canonical}">

<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{topic}">
<meta name="twitter:description" content="{description}">
<meta name="twitter:image" content="{image_url}">

<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;700;900&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">

<style>

body{{
background:#fff;
margin:0;
font-family:'Playfair Display',serif;
color:#111;
line-height:1.8;
}}

header{{
padding:30px;
text-align:center;
border-bottom:1px solid #ddd;
}}

.logo{{
font-family:Inter,sans-serif;
font-size:34px;
font-weight:900;
text-decoration:none;
color:#111;
}}

.container{{
max-width:850px;
margin:60px auto;
padding:0 24px;
}}

.meta{{
font-family:Inter,sans-serif;
font-size:13px;
font-weight:700;
color:#b80000;
margin-bottom:20px;
text-transform:uppercase;
}}

.hero{{
width:100%;
height:auto;
margin-bottom:35px;
}}

.content p{{
font-size:20px;
margin-bottom:24px;
text-align:justify;
}}

.content h3{{
font-family:Inter,sans-serif;
margin-top:40px;
}}

.back{{
display:inline-block;
margin-top:40px;
font-family:Inter,sans-serif;
font-weight:700;
color:#b80000;
text-decoration:none;
}}

</style>

</head>

<body>

<header>
<a href="../index.html" class="logo">INFOVEX</a>
</header>

<div class="container">

<div class="meta">
{category} • {date}
</div>

<h1>{topic}</h1>

<img src="{image_url}" class="hero" alt="{topic}">

<div class="content">

{article}

</div>

<a href="../index.html" class="back">
← Back to Homepage
</a>

</div>

</body>
</html>
"""

# ==========================================================
# 
# ==========================================================

def build_card(topic, category, summary, slug):

    date = today_string()

    return f"""
<div class="post-card" data-cat="{category}">
    <div class="post-meta">
        {category} • {date}
    </div>

    <h2>
        <a href="posts/{slug}.html">
            {topic}
        </a>
    </h2>

    <p>
        {summary}
    </p>
</div>
"""


# ==========================================================
# Homepage Update
# ==========================================================

def update_homepage(
    repo,
    homepage_file,
    homepage_html,
    card
):

    updated_html = inject_card(
        homepage_html,
        card
    )

    repo.update_file(
        path=homepage_file.path,
        message="Homepage Update",
        content=updated_html,
        sha=homepage_file.sha,
        branch=BRANCH
    )

    logger.info("Homepage Updated Successfully.")


# ==========================================================
# Publish Story
# ==========================================================


def create_article_object(
    topic,
    category,
    summary,
    slug,
    image
):

def create_article_object
    return {
        "title": topic,
        "slug": slug,
        "category": category,
        "summary": summary,
        "image": image,
        "published": today_string(),
        "hot": False,
        "trending": True
        "url": f"posts/{slug}.html"
    }
    
    def load_articles_database(repo):

    try:

        file = repo.get_contents("articles.json")

        content = file.decoded_content.decode("utf-8")

        return file, json.loads(content)

    except Exception:

        return None, {
            "articles": []
        }

    def load_articles_database(
    repo
):
    ...
    return ...



def save_articles_database(
    repo,
    database_file,
    database
):

    content = json.dumps(
        database,
        indent=4,
        ensure_ascii=False
    )

    if database_file is None:

        repo.create_file(
            path="articles.json",
            message="Create articles database",
            content=content,
            branch=BRANCH
        )

    else:

        repo.update_file(
            path=database_file.path,
            message="Update articles database",
            content=content,
            sha=database_file.sha,
            branch=BRANCH
        )


  def publish_story(
    repo,
    homepage_file,
    homepage_html,
    topic,
    category,
    slug
):

    article = generate_article(
        topic,
        category
    )

    summary = generate_summary(
        topic
    )

    image = article_image(
        topic
    )
       
    article_data = create_article_object(
        topic,
        category,
        summary,
        slug,
        image
    )

        database_file, database = load_articles_database(
        repo
    )

    database["articles"].insert(
        0,
        article_data
    )
   
    save_articles_database(
      repo,
      database_file,
      database
)


     html_page = article_html(
        topic,
        category,
        article,
        image,
        slug
    )
     
    save_article(
       repo,
       slug,
       topic,
       html_page

    )

    database["articles"] = database["articles"][:500]

    save_articles_database(
        repo,
        database_file,
        database
        
    )

    card = build_card(
        topic,
        category,
        summary,
        slug
    )

    update_homepage(
        repo,
        homepage_file,
        homepage_html,
        card
    )

    logger.info("Story Published Successfully.")

    # ==========================================================
# Main
# ==========================================================

def main():

    logger.info("=" * 60)
    logger.info("INFOVEX Auto Blogger Started")
    logger.info("=" * 60)

    category = random.choice(CATEGORIES)

    logger.info(f"Selected Category: {category}")

    repo = github_repo()

    homepage_file, homepage_html = load_homepage(repo)

    topics = fetch_topics(category)

    if not topics:
        raise RuntimeError("No topics found.")

    topic, slug = choose_topic(repo, topics)

    logger.info(f"Selected Topic: {topic}")

    success = False

    for attempt in range(1, 4):

        try:

            logger.info(f"Attempt {attempt}/3")

            publish_story(
                repo,
                homepage_file,
                homepage_html,
                topic,
                category,
                slug
            )

            success = True

            break

        except Exception as e:

            logger.exception(e)

            time.sleep(5)

    if not success:
        raise RuntimeError("Publishing failed after 3 attempts.")

    logger.info("=" * 60)
    logger.info("INFOVEX Finished Successfully")
    logger.info("=" * 60)


# ==========================================================
# Entry Point
# ==========================================================

if __name__ == "__main__":

    try:
        main()

    except Exception as e:
        logger.exception(e)
        sys.exit(1)
