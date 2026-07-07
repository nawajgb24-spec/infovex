import os
import json
import random
import urllib.parse
from google import genai
from google.genai import types
from datetime import datetime

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

def generate_automated_blog():
    # ... (Keep logic same as before, focusing on the build_magazine_portal function below) ...
    pass 

# REPLACE YOUR build_magazine_portal FUNCTION WITH THIS ONE:
def build_magazine_portal(db, latest_art, current_cat):
    # SHORTS MODAL LOGIC ( FIXED )
    shorts_html = ""
    for s in db.get("shorts", []):
        img = s.get("image")
        txt = s.get("text", s)
        safe_txt = txt.replace("'", "\\'").replace('"', '\\"')
        
        shorts_html += f'''
        <div class="short-premium-card" onclick="openShort('{safe_txt}', '{img}')" style="cursor:pointer;">
            <img class="short-card-img" src="{img}" alt="Shorts">
            <div class="short-card-overlay">
                <p class="short-text-p">{txt}</p>
            </div>
        </div>
        '''

    # FULL HTML WRAPPER ( STABLE DESIGN )
    full_html = f"""
    <!DOCTYPE html>
    <html lang="en" data-theme="dark">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Infovex Premium Newsroom</title>
        <style>
            body {{ background: #04060d; color: #fff; font-family: sans-serif; margin: 0; }}
            .portal-container {{ display: grid; grid-template-columns: 240px 1fr 300px; gap: 20px; padding: 20px; }}
            .card {{ background: #0b0f1e; border-radius: 12px; overflow: hidden; margin-bottom: 20px; }}
            .card img {{ width: 100%; height: 200px; object-fit: cover; }}
            
            /* FIXED MODAL STYLE */
            .modal {{ display: none; position: fixed; z-index: 9999; left: 0; top: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.95); }}
            .modal-content {{ position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 90%; max-width: 400px; background: #111; padding: 20px; border-radius: 12px; text-align: center; }}
        </style>
    </head>
    <body>
        <div class="portal-container">
            <nav><h3>Categories</h3><a href="#latest" style="color:white; display:block;">Latest</a></nav>
            <main>
                <h1>{latest_art['title']}</h1>
                <div class="card"><img src="{latest_art['image']}"></div>
                <p>{latest_art['content']}</p>
            </main>
            <aside>
                <h3>Flash Shorts</h3>
                {shorts_html}
            </aside>
        </div>

        <div id="shortModal" class="modal" onclick="this.style.display='none'">
            <div class="modal-content">
                <img id="modalImg" style="width:100%; border-radius:8px;">
                <p id="modalText" style="margin-top:15px;"></p>
            </div>
        </div>

        <script>
            function openShort(text, img) {{
                document.getElementById('modalText').innerText = text;
                document.getElementById('modalImg').src = img;
                document.getElementById('shortModal').style.display = 'block';
            }}
        </script>
    </body>
    </html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(full_html)
