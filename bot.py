import tweepy
import anthropic
import random
import requests
import time
import os

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

# Holder styr på sette nyheter i minnet (nullstilles bare ved restart)
seen_headlines = set()

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
    global seen_headlines
    print("Bot started — checking for news every 15 minutes...")

    # Ved oppstart — last inn eksisterende nyheter uten å poste
    print("Loading existing headlines on startup...")
    existing = get_news()
    seen_headlines = set(existing)
    print(f"Loaded {len(seen_headlines)} existing headlines. Now watching for new ones...")

    while True:
        time.sleep(900)  # Vent 15 min
        try:
            all_headlines = get_news()
            new = [h for h in all_headlines if h not in seen_headlines]
            if new:
                headline = new[0]
                print(f"New headline: {headline}")
                tweet = generate_tweet(headline)
                post_tweet(tweet)
                seen_headlines.add(headline)
            else:
                print("No new headlines.")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    run()