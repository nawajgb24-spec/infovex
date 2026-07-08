#!/usr/bin/env python3

"""
==========================================================
INFOVEX V3
Next Generation AI News Engine
Development Branch
==========================================================
"""

import json
import logging
import random
import re
import sys
from datetime import datetime

logger = logging.getLogger("INFOVEX_V3")

ARTICLES_DB = "articles.json"
CATEGORIES_DB = "categories.json"
CONFIG_FILE = "config.json"

HOME_LIMIT = 30
HOT_LIMIT = 10
TRENDING_LIMIT = 30

def load_json(path):

    try:

        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    except FileNotFoundError:

        logger.error(f"{path} not found.")
        return {}

    except json.JSONDecodeError:

        logger.error(f"{path} contains invalid JSON.")
        return {}

    except Exception as e:

        logger.exception(e)
        return {}

def save_json(path, data):

    try:

        with open(path, "w", encoding="utf-8") as f:

            json.dump(
                data,
                f,
                indent=4,
                ensure_ascii=False
            )

    except Exception as e:

        logger.exception(e)

 def load_config():

    config = load_json(CONFIG_FILE)

    if not config:

        logger.warning("Using default configuration.")

        config = {

            "homepage_limit": 30,

            "hot_limit": 10,

            "trending_limit": 30,

            "default_category": "World",

            "development": True

        }

    return config

         CONFIG = load_config()

         HOME_LIMIT = CONFIG["homepage_limit"]

         HOT_LIMIT = CONFIG["hot_limit"]

         TRENDING_LIMIT = CONFIG["trending_limit"]

 def load_articles():

    data = load_json(ARTICLES_DB)

    if not data:

        return []

    if isinstance(data, list):

        return data

    if "articles" in data:

        return data["articles"]

    return []

def save_articles(articles):

    save_json(

        ARTICLES_DB,

        {

            "articles": articles

        }

    )

def article_exists(slug):

    articles = load_articles()

    for article in articles:

        if article.get("slug") == slug:

            return True

    return False

def add_article(article):

    articles = load_articles()

    slug = article.get("slug")

    if article_exists(slug):

        logger.info(f"Article already exists: {slug}")

        return False

    article["published"] = datetime.utcnow().isoformat()

    articles.insert(0, article)

    save_articles(articles)

    logger.info(f"Article added: {slug}")

    return True

def latest_articles(limit=HOME_LIMIT):

    articles = load_articles()

    return articles[:limit]

def homepage_articles():

    articles = latest_articles(HOME_LIMIT)

    return articles

def hot_news():

    articles = latest_articles()


def trending_news():

    articles = latest_articles()

    return articles[:TRENDING_LIMIT]
    return articles[:HOT_LIMIT]



