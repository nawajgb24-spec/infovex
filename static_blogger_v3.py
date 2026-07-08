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
