import os
from google import genai
from datetime import datetime

# Safe API Key validation
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY environment variable is missing!")
    exit(1)

# Initialize Google GenAI Client
client = genai.Client(api_key=api_key)

def get_trending_topic():
    # Dynamic trending topic context for India & Global tech
    return "India's Tech Revolution 2026: The Massive Rise of Smart Electronics Production"

def generate_automated_blog():
    try:
        topic = get_trending_topic()
        date_str = datetime.now().strftime("%B %d, %Y")
        print(f"Starting Gemini content generation for: {topic}")

        # Strict prompt to generate beautiful inline styled HTML layout for the website front page
        prompt = f"""
        Act as an elite digital news and lifestyle journalist. Write a comprehensive, detailed, and highly engaging article about '{topic}'.
        
        The article context must match the year 2026.
        Ensure the text is fully original, high-quality, and completely matches Google AdSense publisher policies.
        
        Format the output directly as a clean HTML block suitable to be injected into a main page. 
        Start with a structured heading, follow up with a beautiful featured image placeholder, add bold introductory paragraphs, use <h2> for subheadings, and unordered lists (<ul>, <li>) for key takeaways.
        
        Use this exact premium image URL as the featured banner right under the main title:
        <img src="https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1200&q=80" alt="Tech Banner" style="width:100%; border-radius:8px; margin: 20px 0;">
        
        Do not include triple backticks like ```html, output the HTML tags directly.
        """

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        
        blog_html_content = response.text

        # Full Premium Front Page Layout integrating Dark/Light Mode & Clean UI Navbar
        full_html_page = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Infovex | AI-Driven Global News Hub</title>
    <style>
        :root {{
            --bg-color: #f8f9fa;
            --text-color: #212529;
            --card-bg: #ffffff;
            --accent-color: #007bff;
        }}
        @media (prefers-color-scheme: dark) {{
            :root {{
                --bg-color: #121212;
                --text-color: #e0e0e0;
                --card-bg: #1e1e1e;
                --accent-color: #375a7f;
            }}
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            margin: 0;
            padding: 0;
            line-height: 1.6;
        }}
        header {{
            background-color: var(--card-bg);
            border-bottom: 1px solid rgba(0,0,0,0.1);
            padding: 15px 20px;
            position: sticky;
            top: 0;
            z-index: 100;
        }}
        .nav-container {{
            max-width: 900px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .logo {{
            font-size: 24px;
            font-weight: bold;
            color: var(--accent-color);
            text-decoration: none;
        }}
        nav a {{
            margin-left: 15px;
            text-decoration: none;
            color: var(--text-color);
            font-weight: 500;
        }}
        main {{
            max-width: 800px;
            margin: 40px auto;
            padding: 0 20px;
        }}
        .article-card {{
            background-color: var(--card-bg);
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        }}
        .meta-date {{
            font-size: 14px;
            color: #888;
            margin-bottom: 10px;
        }}
        footer {{
            text-align: center;
            padding: 20px;
            font-size: 14px;
            color: #666;
            margin-top: 40px;
        }}
    </style>
</head>
<body>

<header>
    <div class="nav-container">
        <a href="#" class="logo">INFOVEX</a>
        <nav>
            <a href="#">🇮🇳 India Trends</a>
            <a href="#">🌍 Global</a>
            <a href="#">💻 Tech</a>
            <a href="#">⚽ Sports</a>
        </nav>
    </div>
</header>

<main>
    <div class="article-card">
        <div class="meta-date">Published on {date_str} | Powered by Infovex AI</div>
        {blog_html_content}
    </div>
</main>

<footer>
    <p>&copy; 2026 Infovex News Network. All Rights Reserved. Compliant with Google AdSense Policies.</p>
</footer>

</body>
</html>"""

        # Update index.html directly on root
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(full_html_page)
            
        print("Successfully updated index.html with latest Gemini content.")

    except Exception as e:
        print(f"An error occurred during content pipeline processing: {str(e)}")
        exit(1)

if __name__ == "__main__":
    generate_automated_blog()
