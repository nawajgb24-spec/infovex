import os
import datetime
from pytrends.request import TrendReq
from openai import OpenAI
from github import Github

# GitHub Actions automatic in keys ko background se utha lega
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPOSITORY") 

openai_client = OpenAI(api_key=OPENAI_API_KEY)
g = Github(GITHUB_TOKEN)

def get_trending_topic():
    print("🔄 Fetching top trend from India...")
    pytrends = TrendReq(hl='en-US', tz=330)
    trending_searches = pytrends.realtime_trending_searches(pn='IN')
    return trending_searches['title'].iloc[0]

def generate_blog_content(topic):
    print(f"✍️ Writing completely unique article for: {topic}...")
    
    prompt = f"""
    Write a high-quality, 100% unique, and human-like news article about: '{topic}'.
    
    Guidelines to prevent AdSense Ban & Copyright Issues:
    - Write like a professional human journalist. 
    - Never use standard AI words (e.g., delve, testament, furthermore, revolutionized).
    - Rely purely on factual data and rewrite it in your own words to ensure 0% plagiarism.
    - Structure it beautifully using clean HTML card format:
      <div class="post-card">
          <div class="meta">{datetime.datetime.now().strftime("%B %d, %Y")} • Trending Update</div>
          <h2>Catchy Title for {topic}</h2>
          <p>Paragraph 1 explaining the core news news clearly...</p>
          <p>Paragraph 2 covering background details or implications...</p>
      </div>
    """
    
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a safe, professional, and unique news writer."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.6 # Safe zone for realistic writing
    )
    return response.choices[0].message.content

def update_homepage(new_post_html):
    print("📤 Injecting new post into index.html...")
    repo = g.get_repo(GITHUB_REPO)
    
    # Existing index.html ko read karna
    contents = repo.get_contents("index.html", ref="main")
    current_html = contents.decoded_content.decode("utf-8")
    
    # Naye post ko placeholder ke niche fit karna
    placeholder = 'id="posts-container">'
    if placeholder in current_html:
        updated_html = current_html.replace(placeholder, f'{placeholder}\n{new_post_html}')
        
        # GitHub par file update karna
        repo.update_file(contents.path, "AI Bot: Added New Trending Post", updated_html, contents.sha, branch="main")
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
      
