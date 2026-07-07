import os
import json
import random
from datetime import datetime

# Google GenAI SDK (Optional - will use fallbacks if missing)
try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None

# ==========================================
# 1. HD IMAGE FALLBACKS (Guarantees No Blank Images)
# ==========================================
HD_IMAGES = [
    "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1531297172864-459c7accc8e6?auto=format&fit=crop&w=1200&q=80"
]

def get_fallback_data():
    return {
        "quote": {
            "text": "The future belongs to those who learn more skills and combine them in creative ways.",
            "author": "Robert Greene"
        },
        "articles": [
            {
                "id": f"art_{i}",
                "title": f"The Evolution of Technology and Lifestyle {2026 - i}",
                "category": random.choice(["Tech", "Sports", "Facts", "Film", "Health"]),
                "snippet": "An in-depth look at how emerging trends are reshaping our daily workflows and industry standards globally. Read more to find out.",
                "content": "<p>This is the full article content. In a real scenario, the AI generates detailed paragraphs here. Technology continues to evolve at an unprecedented pace, changing how we work, live, and communicate.</p><p>Stay tuned for more updates on this developing story.</p>",
                "image": random.choice(HD_IMAGES),
                "date": f"2026-10-{24-i:02d}"
            } for i in range(10) # Strictly 10 blogs
        ],
        "shorts": [
            {
                "id": f"short_{i}",
                "title": f"Quick Insight {i+1}",
                "content": "Fascinating facts and quick tips to keep you informed on the go. Swipe for more.",
                "image": f"https://images.unsplash.com/photo-1587393855524-087f83d95bc9?auto=format&fit=crop&w=600&q=80"
            } for i in range(5)
        ]
    }

def fetch_ai_content():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not genai or not api_key:
        print("Using HD Fallback Data (No API Key found)...")
        data = get_fallback_data()
    else:
        print("Connecting to Google GenAI...")
        client = genai.Client(api_key=api_key)
        prompt = """
        Generate JSON data for a news portal named 'Infovex'. Include:
        1. "quote": Motivation text and author.
        2. "articles": Exactly 10 articles. Each needs: "title", "category" (Tech, Sports, Facts, Film, Health), "snippet", "content" (HTML paragraphs), "image" (use random words), and "date" (YYYY-MM-DD).
        3. "shorts": Exactly 5 flash shorts. "title", "content", "image".
        Output strictly valid JSON.
        """
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0.7)
            )
            data = json.loads(response.text)
            
            # Ensure images are HD and not blank
            for art in data.get("articles", []):
                if not art.get("image") or "unsplash" not in art.get("image", ""):
                    art["image"] = random.choice(HD_IMAGES)
        except Exception as e:
            print(f"Error fetching AI: {e}. Using fallback.")
            data = get_fallback_data()

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


# ==========================================
# 2. CSS & JS (Shared)
# ==========================================
def get_css():
    return """
    :root {
        --bg-main: #04060d; --text-main: #f8fafc; --text-muted: #94a3b8;
        --accent: #38bdf8; --glass-bg: rgba(255, 255, 255, 0.03);
        --glass-border: rgba(255, 255, 255, 0.05); --nav-bg: rgba(4, 6, 13, 0.9);
    }
    [data-theme="light"] {
        --bg-main: #f1f5f9; --text-main: #0f172a; --text-muted: #475569;
        --accent: #0284c7; --glass-bg: rgba(255, 255, 255, 0.7);
        --glass-border: rgba(255, 255, 255, 1); --nav-bg: rgba(241, 245, 249, 0.9);
    }
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { background: var(--bg-main); color: var(--text-main); font-family: 'Inter', sans-serif; transition: 0.3s; line-height: 1.6; }
    a { text-decoration: none; color: inherit; }
    
    /* HEADER & TAGLINE */
    header { position: sticky; top: 0; z-index: 100; background: var(--nav-bg); backdrop-filter: blur(15px); border-bottom: 1px solid var(--glass-border); padding: 1rem 5%; display: flex; justify-content: space-between; align-items: center; }
    .logo-container { display: flex; flex-direction: column; }
    .logo { font-size: 1.8rem; font-weight: 900; letter-spacing: -0.5px; line-height: 1; }
    .logo span { color: var(--accent); }
    .tagline { font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 2px; margin-top: 4px; font-weight: 600; }
    .theme-toggle { background: transparent; border: 1px solid var(--glass-border); color: var(--text-main); padding: 0.5rem 1rem; border-radius: 20px; cursor: pointer; }

    /* LAYOUT */
    .layout-grid { display: grid; grid-template-columns: 200px 1fr 300px; gap: 2.5rem; max-width: 1500px; margin: 0 auto; padding: 2rem 5%; align-items: start; }
    
    /* LEFT SIDEBAR (COMPACT) */
    .sidebar-sticky { position: sticky; top: 100px; }
    .sidebar-title { font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; color: var(--text-muted); margin-bottom: 1rem; }
    .category-list { list-style: none; display: flex; flex-direction: column; gap: 0.3rem; }
    .cat-link { display: block; padding: 0.6rem 1rem; border-radius: 6px; color: var(--text-muted); font-size: 0.95rem; font-weight: 500; transition: 0.2s; }
    .cat-link:hover { background: var(--glass-bg); color: var(--accent); transform: translateX(4px); }

    /* CARDS */
    .glass-panel { background: var(--glass-bg); backdrop-filter: blur(12px); border: 1px solid var(--glass-border); border-radius
