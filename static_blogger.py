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
    "Anime",
    "Trending News",
    "Tech",
    "Sports",
    "Business",
    "Lifestyle",
    "Stock News",
    "World",
]

HOME_MARKER = "<!-- BLOG_INSERT_MARKER -->"
MAX_HOME_POSTS = 30

NEWS_RSS_URL = "https://news.google.com/rss/search"
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/"
    "v1beta/models/gemini-1.5-flash:generateContent"
)

ANTI_AI_PROMPT = """
Write an original, well-structured editorial news article.

Requirements:

- Output raw HTML only.
- Use <h3> and <p>.
- Do not use markdown.
- Do not wrap inside ``` blocks.
- Keep a natural journalistic tone.
- Avoid repetitive wording.
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
