import os
import json
import random
from datetime import datetime

# Import the official Google GenAI SDK
try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None

# ==========================================
# 1. AI CONTENT FETCHING LOGIC
# ==========================================

def get_fallback_data():
    """Provides fallback data to ensure the build never fails."""
    return {
        "quote": {
            "text": "The best error message is the one that never shows up.",
            "author": "Thomas Fuchs"
        },
        "articles": [
            {
                "id": f"art_{i}",
                "title": f"The Evolution of Tech Landscape {2026 - i}",
                "category": random.choice(["Tech", "Sports", "Facts", "Film", "Health"]),
                "snippet": "An in-depth look at how emerging trends are reshaping our daily workflows and industry standards globally.",
                "image": f"https://picsum.photos/seed/info{i}/800/400",
                "date": f"2026-10-{24-i:02d}",
                "url": f"#article-url-{i}"
            } for i in range(10)
        ],
        "shorts": [
            {
                "id": f"short_{i}",
                "title": f"Quick Insight {i+1}",
                "content": "Fascinating facts and quick tips to keep you informed on the go. Swipe for more.",
                "image": f"https://picsum.photos/seed/short{i}/400/600"
            } for i in range(5)
        ]
    }

def fetch_ai_content():
    """Fetches AI-generated content using the google.genai SDK and saves it to data.json."""
    api_key = os.environ.get("GEMINI_API_KEY")
    
    if not genai or not api_key:
        print("Warning: Google GenAI SDK missing or GEMINI_API_KEY not set. Using fallback data.")
        data = get_fallback_data()
    else:
        print("Connecting to Google GenAI...")
        client = genai.Client(api_key=api_key)
        
        prompt = """
        Generate JSON data for a news portal named 'Infovex'. Include:
        1. "quote": A daily motivational or tech-related quote with "text" and "author".
        2. "articles": An array of exactly 10 latest news articles. Each object needs: "id", "title", "category" (Tech, Sports, Facts, Film, or Health), "snippet" (2 sentences max), "image" (use random realistic unsplash image URLs or placeholders), "date" (YYYY-MM-DD), and "url" (a dummy hash link).
        3. "shorts": An array of exactly 5 flash shorts. Each object needs: "id", "title", "content" (brief text), and "image" (vertical placeholder image URL).
        Output strictly valid JSON matching this schema.
        """
        
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.7
                )
            )
            data = json.loads(response.text)
            print("Successfully fetched AI content.")
        except Exception as e:
            print(f"Error fetching AI content: {e}. Falling back to default data.")
            data = get_fallback_data()

    # Save to data.json
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


# ==========================================
# 2. UI BUILDER LOGIC
# ==========================================

def get_css():
    """Returns the CSS string."""
    return """
    :root {
        --bg-main: #04060d;
        --text-main: #f8fafc;
        --text-muted: #94a3b8;
        --accent: #38bdf8;
        --glass-bg: rgba(255, 255, 255, 0.03);
        --glass-border: rgba(255, 255, 255, 0.05);
        --glass-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
        --nav-bg: rgba(4, 6, 13, 0.8);
    }

    [data-theme="light"] {
        --bg-main: #f1f5f9;
        --text-main: #0f172a;
        --text-muted: #475569;
        --accent: #0284c7;
        --glass-bg: rgba(255, 255, 255, 0.7);
        --glass-border: rgba(255, 255, 255, 1);
        --glass-shadow: 0 4px 30px rgba(0, 0, 0, 0.05);
        --nav-bg: rgba(241, 245, 249, 0.8);
    }

    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { background: var(--bg-main); color: var(--text-main); font-family: 'Inter', system-ui, sans-serif; transition: background 0.3s, color 0.3s; line-height: 1.6; overflow-x: hidden; }
    a { text-decoration: none; color: inherit; }
    ul { list-style: none; }

    /* HEADER */
    header { position: sticky; top: 0; z-index: 100; background: var(--nav-bg); backdrop-filter: blur(12px); border-bottom: 1px solid var(--glass-border); padding: 1rem 5%; display: flex; justify-content: space-between; align-items: center; }
    .logo { font-size: 1.5rem; font-weight: 800; letter-spacing: -0.5px; }
    .logo span { color: var(--accent); }
    .header-actions { display: flex; align-items: center; gap: 1rem; }
    .theme-toggle { background: transparent; border: 1px solid var(--glass-border); color: var(--text-main); padding: 0.5rem 1rem; border-radius: 20px; cursor: pointer; transition: all 0.2s; backdrop-filter: blur(5px); }
    .theme-toggle:hover { border-color: var(--accent); }
    .mobile-menu-btn { display: none; font-size: 1.5rem; background: none; border: none; color: var(--text-main); cursor: pointer; }

    /* LAYOUT GRID */
    .layout-grid { display: grid; grid-template-columns: 220px 1fr 300px; gap: 2rem; max-width: 1500px; margin: 0 auto; padding: 2rem 5%; align-items: start; }
    .sidebar-sticky { position: sticky; top: 90px; }
    .sidebar-title { font-size: 0.875rem; text-transform: uppercase; letter-spacing: 1px; color: var(--text-muted); margin-bottom: 1.5rem; }

    /* LEFT SIDEBAR (CATEGORIES) */
    .left-sidebar { transition: transform 0.3s ease; }
    .category-list { display: flex; flex-direction: column; gap: 0.5rem; }
    .cat-link { display: block; padding: 0.8rem 1rem; border-radius: 8px; color: var(--text-muted); transition: all 0.2s; font-weight: 500; border: 1px solid transparent; }
    .cat-link:hover { background: var(--glass-bg); color: var(--accent); border-color: var(--glass-border); transform: translateX(5px); }

    /* GLASSMORPHISM SHARED */
    .glass-panel { background: var(--glass-bg); backdrop-filter: blur(12px); border: 1px solid var(--glass-border); border-radius: 16px; box-shadow: var(--glass-shadow); }

    /* MAIN FEED & QUOTE */
    .main-feed { display: flex; flex-direction: column; gap: 2rem; min-width: 0; }
    .daily-quote { padding: 2.5rem 2rem; text-align: center; position: relative; overflow: hidden; }
    .quote-icon { font-size: 5rem; color: var(--accent); opacity: 0.1; position: absolute; top: -20px; left: 10px; font-family: serif; line-height: 1; }
    .daily-quote blockquote { font-size: 1.25rem; font-weight: 500; font-style: italic; margin-bottom: 1rem; position: relative; z-index: 1; }
    .daily-quote cite { color: var(--accent); font-weight: 600; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px; }

    /* ARTICLE CARDS */
    .articles-container { display: flex; flex-direction: column; gap: 1.5rem; }
    .block-link { display: block; transition: transform 0.3s ease, border-color 0.3s ease; overflow: hidden; }
    .block-link:hover { transform: translateY(-4px); border-color: var(--accent); }
    .card-img-wrapper { position: relative; height: 240px; }
    .card-img-wrapper img { width: 100%; height: 100%; object-fit: cover; }
    .badge { position: absolute; top: 1rem; left: 1rem; background: var(--accent); color: #fff; padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.75rem; font-weight: bold; text-transform: uppercase; box-shadow: 0 2px 10px rgba(0,0,0,0.3); }
    .card-content { padding: 1.5rem; }
    .card-title { font-size: 1.3rem; margin-bottom: 0.75rem; line-height: 1.4; }
    .card-snippet { color: var(--text-muted); font-size: 0.95rem; margin-bottom: 1rem; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
    .card-meta { font-size: 0.85rem; color: var(--text-muted); opacity: 0.8; }

    /* RIGHT SIDEBAR (SHORTS) */
    .shorts-grid { display: flex; flex-direction: column; gap: 1.25rem; }
    .short-card { position: relative; height: 350px; border-radius: 12px; overflow: hidden; cursor: pointer; transition: transform 0.2s, border-color 0.2s; border: 1px solid var(--glass-border); }
    .short-card:hover { transform: scale(1.02); border-color: var(--accent); }
    .short-card img { width: 100%; height: 100%; object-fit: cover; }
    .short-overlay { position: absolute; bottom: 0; left: 0; width: 100%; padding: 2.5rem 1rem 1rem; background: linear-gradient(transparent, rgba(0,0,0,0.95)); display: flex; align-items: flex-end; }
    .short-title { font-weight: 600; color: #fff; text-shadow: 0 2px 4px rgba(0,0,0,0.8); }

    /* MODAL */
    .modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.85); backdrop-filter: blur(8px); z-index: 1000; display: none; justify-content: center; align-items: center; opacity: 0; transition: opacity 0.3s ease; }
    .modal-overlay.active { display: flex; opacity: 1; }
    .modal-glass-content { background: var(--glass-bg); backdrop-filter: blur(25px); border: 1px solid var(--glass-border); width: 90%; max-width: 420px; border-radius: 20px; overflow: hidden; position: relative; transform: scale(0.95); transition: transform 0.3s ease; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.8); }
    .modal-overlay.active .modal-glass-content { transform: scale(1); }
    .modal-close { position: absolute; top: 15px; right: 15px; background: rgba(0,0,0,0.6); color: #fff; border: 1px solid rgba(255,255,255,0.2); width: 32px; height: 32px; border-radius: 50%; cursor: pointer; font-size: 1.2rem; z-index: 10; display: flex; justify-content: center; align-items: center; transition: background 0.2s; }
    .modal-close:hover { background: rgba(0,0,0,0.9); }
    .modal-img { width: 100%; height: 450px; object-fit: cover; }
    .modal-body { padding: 1.5rem; }
    .modal-title { font-size: 1.25rem; margin-bottom: 0.75rem; font-weight: 700; }
    .modal-text { color: var(--text-muted); font-size: 0.95rem; margin-bottom: 1.5rem; line-height: 1.5; }
    .btn-share { width: 100%; padding: 0.875rem; background: var(--accent); color: #fff; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; display: flex; justify-content: center; align-items: center; gap: 0.5rem; transition: background 0.2s, transform 0.1s; }
    .btn-share:hover { filter: brightness(1.1); transform: translateY(-2px); }
    .btn-share:active { transform: translateY(0); }

    /* RESPONSIVE DESIGN */
    @media (max-width: 1100px) {
        .layout-grid { grid-template-columns: 200px 1fr; }
        .right-sidebar { display: none; }
    }
    @media (max-width: 768px) {
        .layout-grid { grid-template-columns: 1fr; padding: 1rem 5%; gap: 1.5rem; }
        
        /* Mobile Hamburger & Sidebar Logic */
        .mobile-menu-btn { display: block; }
        .left-sidebar { position: fixed; top: 70px; left: -100%; width: 250px; height: calc(100vh - 70px); background: var(--nav-bg); backdrop-filter: blur(15px); border-right: 1px solid var(--glass-border); z-index: 90; padding: 2rem; transition: left 0.3s ease; }
        .left-sidebar.active { left: 0; }
        .theme-toggle span { display: none; }
    }
    """

def get_js():
    """Returns the JavaScript string."""
    return """
    // Theme Toggle Logic
    const themeBtn = document.getElementById('themeToggle');
    const root = document.documentElement;
    
    if (localStorage.getItem('theme') === 'light') {
        root.setAttribute('data-theme', 'light');
        themeBtn.innerHTML = '🌙';
    }

    themeBtn.addEventListener('click', () => {
        if (root.getAttribute('data-theme') === 'light') {
            root.removeAttribute('data-theme');
            localStorage.setItem('theme', 'dark');
            themeBtn.innerHTML = '☀️ <span style="font-family:inherit;font-size:0.9rem">Light Mode</span>';
        } else {
            root.setAttribute('data-theme', 'light');
            localStorage.setItem('theme', 'light');
            themeBtn.innerHTML = '🌙 <span style="font-family:inherit;font-size:0.9rem">Dark Mode</span>';
        }
    });

    // Mobile Menu Logic
    const mobileBtn = document.getElementById('mobileMenuBtn');
    const sidebar = document.getElementById('leftSidebar');
    
    mobileBtn.addEventListener('click', () => {
        sidebar.classList.toggle('active');
        mobileBtn.innerHTML = sidebar.classList.contains('active') ? '✕' : '☰';
    });

    // Shorts Modal & Native Share Logic
    const modal = document.getElementById('shortModal');
    const modalImg = document.getElementById('modalImg');
    const modalTitle = document.getElementById('modalTitle');
    const modalContent = document.getElementById('modalContent');
    let currentShareData = {};

    function openShortModal(title, content, imgUrl) {
        modalImg.src = imgUrl;
        modalTitle.textContent = title;
        modalContent.textContent = content;
        
        currentShareData = {
            title: 'Infovex Shorts: ' + title,
            text: content,
            url: window.location.href 
        };

        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    function closeShortModal(event, force = false) {
        if (force || event.target === modal) {
            modal.classList.remove('active');
            document.body.style.overflow = 'auto';
        }
    }

    async function shareShort() {
        if (navigator.share) {
            try {
                await navigator.share(currentShareData);
            } catch (err) {
                console.log('Share canceled or failed:', err);
            }
        } else {
            alert("Web Share API is not supported in this browser. Link ready to be copied manually.");
        }
    }
    """

def build_ui(data):
    """Compiles JSON data into a full HTML template."""
    
    # 1. Left Sidebar
    categories = ["Tech", "Sports", "Facts", "Film", "Health"]
    cat_links = "".join([f'<li><a href="#{c.lower()}" class="cat-link">{c}</a></li>' for c in categories])
    
    sidebar_html = f"""
    <aside class="left-sidebar" id="leftSidebar">
        <div class="sidebar-sticky">
            <h3 class="sidebar-title">Categories</h3>
            <ul class="category-list">
                {cat_links}
            </ul>
        </div>
    </aside>
    """

    # 2. Main Feed (Quote + 10 Articles)
    quote = data.get("quote", {"text": "Stay curious.", "author": "Infovex"})
    quote_html = f"""
    <div class="daily-quote glass-panel">
        <span class="quote-icon">“</span>
        <blockquote>{quote['text']}</blockquote>
        <cite>— {quote['author']}</cite>
    </div>
    """

    articles = data.get("articles", [])[:10]
    articles_html = ""
    for art in articles:
        articles_html += f"""
        <a href="{art.get('url', '#')}" class="article-card glass-panel block-link">
            <div class="card-img-wrapper">
                <img src="{art.get('image', '')}" alt="{art.get('title', '')}" loading="lazy">
                <span class="badge">{art.get('category', 'News')}</span>
            </div>
            <div class="card-content">
                <h2 class="card-title">{art.get('title', '')}</h2>
                <p class="card-snippet">{art.get('snippet', '')}</p>
                <div class="card-meta">Published: {art.get('date', '')}</div>
            </div>
        </a>
        """

    main_feed_html = f"""
    <main class="main-feed">
        {quote_html}
        <div class="articles-container">
            {articles_html}
        </div>
    </main>
    """

    # 3. Right Sidebar (Shorts)
    shorts = data.get("shorts", [])[:5]
    shorts_html = ""
    for short in shorts:
        safe_title = short.get('title', '').replace("'", "\\'")
        safe_content = short.get('content', '').replace("'", "\\'")
        img_url = short.get('image', '')
        shorts_html += f"""
        <div class="short-card" onclick="openShortModal('{safe_title}', '{safe_content}', '{img_url}')">
            <img src="{img_url}" alt="{safe_title}" loading="lazy">
            <div class="short-overlay">
                <span class="short-title">{short.get('title', '')}</span>
            </div>
        </div>
        """

    right_sidebar_html = f"""
    <aside class="right-sidebar">
        <div class="sidebar-sticky">
            <h3 class="sidebar-title">Flash Shorts</h3>
            <div class="shorts-grid">
                {shorts_html}
            </div>
        </div>
    </aside>
    """

    # 4. Modal
    modal_html = """
    <div class="modal-overlay" id="shortModal" onclick="closeShortModal(event)">
        <div class="modal-glass-content" onclick="event.stopPropagation()">
            <button class="modal-close" onclick="closeShortModal(event, true)">×</button>
            <img src="" alt="Short Content" class="modal-img" id="modalImg" loading="lazy">
            <div class="modal-body">
                <h3 class="modal-title" id="modalTitle"></h3>
                <p class="modal-text" id="modalContent"></p>
                <button class="btn-share" onclick="shareShort()">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"></circle><circle cx="6" cy="12" r="3"></circle><circle cx="18" cy="19" r="3"></circle><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"></line><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"></line></svg>
                    Share Short
                </button>
            </div>
        </div>
    </div>
    """

    # Assemble HTML
    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Infovex | Professional News Portal</title>
    <style>{get_css()}</style>
</head>
<body>
    <header>
        <div class="logo">Info<span>vex</span></div>
        <div class="header-actions">
            <button class="theme-toggle" id="themeToggle">☀️ <span style="font-family:inherit;font-size:0.9rem">Light Mode</span></button>
            <button class="mobile-menu-btn" id="mobileMenuBtn">☰</button>
        </div>
    </header>

    <div class="layout-grid">
        {sidebar_html}
        {main_feed_html}
        {right_sidebar_html}
    </div>

    {modal_html}

    <script>{get_js()}</script>
</body>
</html>
"""
    return full_html


# ==========================================
# 3. MAIN ORCHESTRATION
# ==========================================

def main():
    print("Starting Infovex Static Site Generator...")
    
    # 1. Fetch data via API or fallback
    fetch_ai_content()
    
    # 2. Load the data
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Error: data.json not found. Using fallback.")
        data = get_fallback_data()

    # 3. Build UI
    html_content = build_ui(data)
    
    # 4. Save to index.html
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print("Build Successful! 'index.html' is ready for production deployment.")

if __name__ == "__main__":
    main()
