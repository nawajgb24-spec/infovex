import os
import datetime
import requests
from pytrends.request import TrendReq
from github import Github

# Background se keys aur tokens uthana
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPOSITORY") 

g = Github(GITHUB_TOKEN)

def get_trending_topic():
    print("🔄 Fetching top trend from India...")
    pytrends = TrendReq(hl='en-US', tz=330)
    trending_searches = pytrends.realtime_trending_searches(pn='IN')
    return trending_searches['title'].iloc[0]

def generate_blog_content(topic):
    print(f"✍️ Writing completely unique article using Gemini for: {topic}...")
    
    # Gemini API Call URL
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    prompt = f"""
    Write a high-quality, 100% unique, and human-like news article about the trending topic: '{topic}'.
    
    Guidelines to prevent AdSense Ban & Copyright Issues:
    - Write like a professional human journalist. 
    - Never use standard AI words (e.g., delve, testament, furthermore, revolutionized).
    - Rely purely on factual data and rewrite it in your own words to ensure 0% plagiarism.
    - Structure it beautifully using clean HTML card format exactly like this:
      <div class="post-card">
          <div class="meta">{datetime.datetime.now().strftime("%B %d, %Y")} • Trending Update</div>
          <h2>Catchy Title for {topic}</h2>
          <p>Paragraph 1 explaining the core news clearly...</p>
          <p>Paragraph 2 covering background details or implications...</p>
      </div>
    """
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    response = requests.post(url, json=payload)
    result = response.json()
    
    # Gemini se text response nikalna
    try:
        article_text = result['candidates'][0]['content']['parts'][0]['text']
        # Agar Gemini ne markdown (```html) laga diya ho toh use saaf karna
        article_text = article_text.replace("```html", "").replace("```", "").strip()
        return article_text
    except KeyError:
        raise Exception(f"Gemini API Error: {result}")

def update_homepage(new_post_html):
    print("📤 Injecting new post into index.html...")
    repo = g.get_repo(GITHUB_REPO)
    
    contents = repo.get_contents("index.html", ref="main")
    current_html = contents.decoded_content.decode("utf-8")
    
    placeholder = 'id="posts-container">'
    if placeholder in current_html:
        updated_html = current_html.replace(placeholder, f'{placeholder}\n{new_post_html}')
        repo.update_file(contents.path, "AI Bot: Added New Gemini Trending Post", updated_html, contents.sha, branch="main")
        print("🎉 Successfully published to the website!")
    else:
        print("❌ Error: Placeholder not found in HTML.")

if __name__ == "__main__":
    try:
        trend = get_trending_topic()
        new_post = generate_blog_content(trend)
        update_homepage(new_post)
    except Exception as e:
        print(f"❌ Automation Error: {e}")
        
