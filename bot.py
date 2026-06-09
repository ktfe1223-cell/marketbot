import tweepy
import anthropic
import random
import requests
import time
import os
import json

# ============================================
# NØKLER
# ============================================
API_KEY = os.environ.get("API_KEY")
API_SECRET = os.environ.get("API_SECRET")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.environ.get("ACCESS_TOKEN_SECRET")
BEARER_TOKEN = os.environ.get("BEARER_TOKEN")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
NEWSAPI_KEY = os.environ.get("NEWSAPI_KEY")

SEEN_FILE = "seen_headlines.json"

# ============================================
# HENT NYHETER
# ============================================
def get_news():
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": "stocks OR market OR investing OR nasdaq OR fed OR inflation OR earnings",
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 20,
        "apiKey": NEWSAPI_KEY
    }
    response = requests.get(url, params=params)
    data = response.json()
    headlines = []
    if data.get("articles"):
        for article in data["articles"][:20]:
            headlines.append(article["title"])
    return headlines

# ============================================
# SJEKK OM NYHET ER NY
# ============================================
def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r") as f:
            return json.load(f)
    return []

def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(seen[-100:], f)

def get_new_headlines():
    all_headlines = get_news()
    seen = load_seen()
    new = [h for h in all_headlines if h not in seen]
    return new, seen

# ============================================
# GENERER TWEET
# ============================================
TONES = [
    "witty and sarcastic",
    "contrarian and thought-provoking",
    "direct and analytical",
    "motivational for investors",
    "humorous about investing",
]

def generate_tweet(headline):
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    tone = random.choice(TONES)
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        messages=[
            {
                "role": "user",
                "content": f"""You run a popular finance/investing account on X (Twitter).
Write a single tweet based on this news headline: '{headline}'
Tone: {tone}
Rules:
- Maximum 280 characters
- No hashtags
- No emojis unless it really fits
- Sound like a real human, not AI
- Be engaging and shareable
Just write the tweet, nothing else."""
            }
        ]
    )
    return message.content[0].text.strip()

# ============================================
# POST TWEET
# ============================================
def post_tweet(text):
    client = tweepy.Client(
        bearer_token=BEARER_TOKEN,
        consumer_key=API_KEY,
        consumer_secret=API_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET
    )
    client.create_tweet(text=text)
    print(f"Posted: {text}")

# ============================================
# HOVEDLØKKE
# ============================================
def run():
    print("Bot started — checking for news every 15 minutes...")
    while True:
        try:
            new_headlines, seen = get_new_headlines()
            if new_headlines:
                headline = new_headlines[0]
                print(f"New headline: {headline}")
                tweet = generate_tweet(headline)
                post_tweet(tweet)
                seen.append(headline)
                save_seen(seen)
            else:
                print("No new headlines.")
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(900)  # 15 minutter

if __name__ == "__main__":
    run()