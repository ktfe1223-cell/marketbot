import tweepy
import anthropic
import random
import requests

# ============================================
# NØKLER
# ============================================
import os

API_KEY = os.environ.get("API_KEY")
API_SECRET = os.environ.get("API_SECRET")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.environ.get("ACCESS_TOKEN_SECRET")
BEARER_TOKEN = os.environ.get("BEARER_TOKEN")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
NEWSAPI_KEY = os.environ.get("NEWSAPI_KEY")

# ============================================
# HENT NYHETER
# ============================================
def get_news():
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": "stocks OR market OR investing OR nasdaq OR fed OR inflation",
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 20,
        "apiKey": NEWSAPI_KEY
    }
    response = requests.get(url, params=params)
    data = response.json()
    headlines = []
    if data.get("articles"):
        for article in data["articles"][:10]:
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
# KJØR
# ============================================
def run_bot():
    headlines = get_news()
    if not headlines:
        print("No headlines found")
        return
    headline = random.choice(headlines)
    print(f"Using headline: {headline}")
    tweet = generate_tweet(headline)
    print(f"Generated tweet: {tweet}")
    post_tweet(tweet)

if __name__ == "__main__":
    run_bot()