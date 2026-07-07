import os
import json
from datetime import datetime

# ==========================================
# 1. DATA MOCKUP (Backend Logic Simulation)
# ==========================================

ARTICLES = [
    {
        "title": "The Future of Quantum Computing in 2027",
        "category": "Tech",
        "snippet": "Researchers have just crossed a major threshold in qubit stability, paving the way for commercial quantum systems.",
        "image": "https://images.unsplash.com/photo-1635070041078-e363dbe005cb?auto=format&fit=crop&w=800&q=80",
        "date": "Oct 24, 2026"
    },
    {
        "title": "Global Football: New Tournament Formats Announced",
        "category": "Sports",
        "snippet": "FIFA reveals a controversial but highly anticipated structure for the upcoming club competitions.",
        "image": "https://images.unsplash.com/photo-1579952363873-27f3bade9f55?auto=format&fit=crop&w=800&q=80",
        "date": "Oct 23, 2026"
    },
    {
        "title": "Why the James Webb Space Telescope is Redefining Time",
        "category": "Facts",
        "snippet": "Recent deep-field captures show galaxies formed much earlier than standard cosmological models predicted.",
        "image": "https://images.unsplash.com/photo-1614730321146-b6fa6a46bcb4?auto=format&fit=crop&w=800&q=80",
        "date": "Oct 22, 2026"
    },
    {
        "title": "Indie Films Sweeping the Autumn Festivals",
        "category": "Film",
        "snippet": "Big studios take a backseat as independent directors showcase groundbreaking narratives this season.",
        "image": "https://images.unsplash.com/photo-1485846234645-a62644f84728?auto=format&fit=crop&w=800&q=80",
        "date": "Oct 21, 2026"
    },
    {
        "title": "Optimizing Sleep: The Science of Circadian Rhythms",
        "category": "Health",
        "snippet": "New studies suggest that micro-adjustments to light exposure can drastically improve deep sleep phases.",
        "image": "https://images.unsplash.com/photo-1541781774459-bb2af2f05b55?auto=format&fit=crop&w=800&q=80",
        "date": "Oct 20, 2026"
    }
]

SHORTS = [
    {
        "id": "short_1",
        "title": "Did you know?",
        "content": "Bananas are berries, but strawberries aren't! Botanically speaking, a berry has seeds on the inside.",
        "image": "https://images.unsplash.com/photo-1528825871115-3581a5387919?auto=format&fit=crop&w=400&q=80"
    },
    {
        "id": "short_2",
        "title": "Tech Tip",
        "content": "You can use 'window.structuredClone()' in modern JS for deep copying objects without external libraries.",
        "image": "https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&w=400&q=80"
    },
    {
        "id": "short_3",
        "title": "Quick Workout",
        "content": "The 4-7-8 breathing technique: Inhale for 4s, hold for 7s, exhale for 8s. Instantly lowers heart rate.",
        "image": "https://images.unsplash.com/photo-1518611012118-696072aa579a?auto=format&fit=crop&w=400&q=80"
    }
]

# ==========================================
# 2. GENERATOR FUNCTIONS
# ==========================================

def generate_automated_blog(article):
    """Generates the HTML for a single standard article card."""
    return f"""
    <article class="card">
        <div class="card-img-wrapper">
            <img src="{article['image']}" alt="{article['title']}" loading="lazy">
            <span class="category-badge">{article['category']}</span>
        </div>
        <div class="card-content">
            <h3 class="card-title">{article['title']}</h3>
            <p class="card-snippet">{article['snippet']}</p>
            <span class="card-meta">{article['date']}</span>
        </div>
    </article>
    """

def generate_short_card(short):
    """Generates the HTML for a Shorts thumbnail that triggers the modal."""
    # Escaping quotes for inline JS function call
    escaped_title = short['title'].replace("'", "\\'")
    escaped_content = short['content'].replace("'", "\\'")
    return f"""
    <div class="short-card" onclick="openModal('{escaped_title}', '{escaped_content}', '{short['image']}')">
        <img src="{short['image']}" alt="{short['title']}" loading="lazy">
        <div class="short-overlay">
            <svg viewBox="0 0 24 24" fill="currentColor" class="play-icon"><path d="M8 5v14l11-7z"/></svg>
            <span class="short-title">{short['title']}</span>
        </div>
    </div>
    """

# ==========================================
# 3. CORE BUILDER LOGIC
# ==========================================

def build_magazine_portal():
    """Compiles the static site into an index.html file."""
    
    # Process Data
    articles_html = "\n".join([generate_automated_blog(a) for a in ARTICLES])
    shorts_html = "\n".join([generate_short_card(s) for s in SHORTS])
    
    # HTML Template
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Infovex | Premium News Portal</title>
    <meta name="description" content="High-performance news portal covering Tech, Sports, Facts, Film, and Health.">
    
    <style>
        /* CSS VARIABLES */
        :root {{
            --bg-dark: #04060d;
            --bg-card: #0d111a;
            --bg-hover: #161c2b;
            --accent: #38bdf8;
            --text-main: #f1f5f9;
            --text-muted: #94a3b8;
            --border-color: #1e293b;
            --font-sans: 'Inter', system-ui, -apple-system, sans-serif;
            --transition: all 0.2s ease-in-out;
        }}

        /* RESET & BASE */
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            background-color: var(--bg-dark);
            color: var(--text-main);
            font-family: var(--font-sans);
            line-height: 1.6;
            -webkit-font-smoothing: antialiased;
        }}
        a {{ text-decoration: none; color: inherit; }}
        ul {{ list-style: none; }}

        /* STICKY HEADER */
        header {{
            position: sticky;
            top: 0;
            z-index: 100;
            background: rgba(4, 6, 13, 0.85);
            backdrop-filter: blur(12px);
            border-bottom: 1px solid var(--border-color);
            padding: 1rem 5%;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .logo {{ font-size: 1.5rem; font-weight: 800; color: var(--text-main); letter-spacing: -0.5px; }}
        .logo span {{ color: var(--accent); }}
        .nav-links {{ display: flex; gap: 2rem; }}
        .nav-links a:hover {{ color: var(--accent); transition: var(--transition); }}

        /* MAIN LAYOUT GRID */
        .container {{
            display: grid;
            grid-template-columns: 200px 1fr 300px;
            gap: 2rem;
            padding: 2rem 5%;
            max-width: 1600px;
            margin: 0 auto;
        }}

        /* SIDEBAR (Categories) */
        .sidebar h3 {{ color: var(--text-muted); font-size: 0.875rem; text-transform: uppercase; margin-bottom: 1rem; letter-spacing: 1px; }}
        .cat-list li {{ margin-bottom: 0.5rem; }}
        .cat-list a {{
            display: block; padding: 0.5rem 1rem; border-radius: 6px;
            color: var(--text-muted); transition: var(--transition);
        }}
        .cat-list a:hover {{ background: var(--bg-card); color: var(--accent); }}

        /* MAIN FEED */
        .main-feed {{ display: flex; flex-direction: column; gap: 2rem; }}
        .section-title {{ font-size: 1.75rem; font-weight: 700; margin-bottom: 1rem; border-left: 4px solid var(--accent); padding-left: 1rem; }}
        
        .card {{
            background: var(--bg-card);
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid var(--border-color);
            transition: var(--transition);
        }}
        .card:hover {{ transform: translateY(-4px); border-color: var(--accent); box-shadow: 0 10px 30px rgba(0,0,0,0.5); }}
        .card-img-wrapper {{ position: relative; height: 240px; }}
        .card-img-wrapper img {{ width: 100%; height: 100%; object-fit: cover; }}
        .category-badge {{
            position: absolute; top: 1rem; left: 1rem;
            background: var(--accent); color: #000;
            font-size: 0.75rem; font-weight: 700; padding: 0.25rem 0.75rem;
            border-radius: 20px; text-transform: uppercase;
        }}
        .card-content {{ padding: 1.5rem; }}
        .card-title {{ font-size: 1.25rem; margin-bottom: 0.75rem; line-height: 1.4; }}
        .card-snippet {{ color: var(--text-muted); font-size: 0.95rem; margin-bottom: 1rem; }}
        .card-meta {{ font-size: 0.85rem; color: #64748b; }}

        /* SHORTS FEED */
        .shorts-sidebar {{ display: flex; flex-direction: column; gap: 1rem; }}
        .short-card {{
            position: relative; height: 350px; border-radius: 12px; overflow: hidden;
            cursor: pointer; transition: var(--transition);
        }}
        .short-card img {{ width: 100%; height: 100%; object-fit: cover; }}
        .short-card:hover {{ transform: scale(1.02); }}
        .short-overlay {{
            position: absolute; bottom: 0; left: 0; width: 100%;
            background: linear-gradient(transparent, rgba(0,0,0,0.9));
            padding: 1.5rem 1rem 1rem; display: flex; align-items: flex-end; gap: 0.5rem;
        }}
        .play-icon {{ width: 20px; height: 20px; fill: var(--text-main); }}
        .short-title {{ font-weight: 600; font-size: 0.95rem; text-shadow: 0 2px 4px rgba(0,0,0,0.8); }}

        /* SHORTS MODAL OVERLAY */
        .modal-overlay {{
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(4, 6, 13, 0.95); backdrop-filter: blur(8px);
            z-index: 1000; display: none; justify-content: center; align-items: center;
            opacity: 0; transition: opacity 0.3s ease;
        }}
        .modal-overlay.active {{ display: flex; opacity: 1; }}
        .modal-content {{
            background: var(--bg-card); width: 100%; max-width: 400px;
            border-radius: 16px; overflow: hidden; border: 1px solid var(--border-color);
            position: relative; transform: translateY(20px); transition: transform 0.3s ease;
            box-shadow: 0 25px 50px -12px rgba(0,0,0,0.8);
        }}
        .modal-overlay.active .modal-content {{ transform: translateY(0); }}
        .modal-img {{ width: 100%; height: 450px; object-fit: cover; }}
        .modal-body {{ padding: 1.5rem; }}
        .modal-title {{ font-size: 1.25rem; margin-bottom: 0.5rem; }}
        .modal-text {{ color: var(--text-muted); font-size: 0.95rem; margin-bottom: 1.5rem; }}
        
        .modal-actions {{ display: flex; gap: 1rem; }}
        .btn {{
            flex: 1; padding: 0.75rem; border: none; border-radius: 8px;
            font-weight: 600; cursor: pointer; transition: var(--transition);
            display: flex; justify-content: center; align-items: center; gap: 0.5rem;
        }}
        .btn-share {{ background: var(--accent); color: #000; }}
        .btn-share:hover {{ background: #2ea4db; }}
        .btn-close {{ background: var(--bg-hover); color: var(--text-main); }}
        .btn-close:hover {{ background: var(--border-color); }}

        /* RESPONSIVE DESIGN */
        @media (max-width: 1024px) {{
            .container {{ grid-template-columns: 1fr 300px; }}
            .sidebar {{ display: none; }} /* Hide sidebar on tablet */
        }}
        @media (max-width: 768px) {{
            .container {{ grid-template-columns: 1fr; padding: 1rem; }}
            .nav-links {{ display: none; }} /* Hamburger menu placeholder */
            .card-img-wrapper {{ height: 200px; }}
            .shorts-sidebar {{ flex-direction: row; overflow-x: auto; padding-bottom: 1rem; scroll-snap-type: x mandatory; }}
            .short-card {{ min-width: 200px; height: 300px; scroll-snap-align: start; }}
        }}
    </style>
</head>
<body>

    <header>
        <div class="logo">Info<span>vex</span></div>
        <nav class="nav-links">
            <a href="#">Tech</a>
            <a href="#">Sports</a>
            <a href="#">Facts</a>
            <a href="#">Film</a>
            <a href="#">Health</a>
        </nav>
    </header>

    <div class="container">
        <aside class="sidebar">
            <h3>Discover</h3>
            <ul class="cat-list">
                <li><a href="#">Technology</a></li>
                <li><a href="#">Sports Arena</a></li>
                <li><a href="#">Fascinating Facts</a></li>
                <li><a href="#">Film Industry</a></li>
                <li><a href="#">Health & Wellness</a></li>
            </ul>
        </aside>

        <main class="main-feed">
            <h2 class="section-title">Latest Updates</h2>
            {articles_html}
        </main>

        <aside class="shorts-sidebar">
            <h2 class="section-title">Shorts</h2>
            {shorts_html}
        </aside>
    </div>

    <div class="modal-overlay" id="shortModal" onclick="closeModal(event)">
        <div class="modal-content" onclick="event.stopPropagation()">
            <img src="" alt="" class="modal-img" id="modalImg">
            <div class="modal-body">
                <h3 class="modal-title" id="modalTitle"></h3>
                <p class="modal-text" id="modalContent"></p>
                <div class="modal-actions">
                    <button class="btn btn-share" onclick="shareShort()">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"></circle><circle cx="6" cy="12" r="3"></circle><circle cx="18" cy="19" r="3"></circle><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"></line><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"></line></svg>
                        Share
                    </button>
                    <button class="btn btn-close" onclick="closeModal(event, true)">Close</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        const modal = document.getElementById('shortModal');
        const modalImg = document.getElementById('modalImg');
        const modalTitle = document.getElementById('modalTitle');
        const modalContent = document.getElementById('modalContent');
        
        let currentShareData = {{}};

        // Open Modal and Populate Data
        function openModal(title, content, imgUrl) {{
            modalImg.src = imgUrl;
            modalTitle.textContent = title;
            modalContent.textContent = content;
            
            // Setup data for sharing
            currentShareData = {{
                title: 'Infovex Shorts: ' + title,
                text: content,
                url: window.location.href 
            }};

            modal.classList.add('active');
            document.body.style.overflow = 'hidden'; // Prevent background scrolling
        }}

        // Close Modal
        function closeModal(event, force = false) {{
            // Close if background is clicked or close button is clicked
            if (force || event.target === modal) {{
                modal.classList.remove('active');
                document.body.style.overflow = 'auto'; // Restore scrolling
            }}
        }}

        // Native Web Share API
        async function shareShort() {{
            if (navigator.share) {{
                try {{
                    await navigator.share(currentShareData);
                    console.log('Content shared successfully');
                }} catch (err) {{
                    console.log('Error sharing:', err);
                }}
            }} else {{
                // Fallback for browsers that don't support Web Share API
                alert("Sharing is not supported on this browser. Copy the URL to share!");
            }}
        }}
    </script>
</body>
</html>
"""
    
    # Write to File
    output_filename = "index.html"
    try:
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"Success: Built '{output_filename}' dynamically. Ready for deployment.")
    except Exception as e:
        print(f"Error building portal: {e}")

if __name__ == "__main__":
    build_magazine_portal()
