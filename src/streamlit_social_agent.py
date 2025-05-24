import os
import openai
import tweepy
from linkedin_v2 import linkedin

# 1) Twitter client
tw_auth = tweepy.OAuth1UserHandler(
    os.getenv("TWITTER_API_KEY"),
    os.getenv("TWITTER_API_SECRET"),
    os.getenv("TWITTER_ACCESS_TOKEN"),
    os.getenv("TWITTER_ACCESS_TOKEN_SECRET"),
)
twitter = tweepy.API(tw_auth)

# 2) LinkedIn client
linkedin_client = linkedin.LinkedInApplication(
    token=os.getenv("LINKEDIN_ACCESS_TOKEN")
)

def find_on_twitter(handle_or_name: str):
    """Return the first Twitter user object matching that name/handle."""
    try:
        return twitter.get_user(handle_or_name)
    except Exception:
        # fallback to search
        results = twitter.search_users(q=handle_or_name, count=1)
        return results[0] if results else None

def find_on_linkedin(name: str):
    """Search LinkedIn for the first match (very rudimentary)."""
    res = linkedin_client.search_profile(selectors=[{"people": ["id","first-name","last-name"]}],
                                         params={"keywords": name, "count": 1})
    people = res.get("people", {}).get("values", [])
    return people[0] if people else None

def generate_message(name: str, company: str):
    """Use GPT to write a personalized outreach."""
    prompt = f"""
You are an outreach assistant. Write a warm, concise LinkedIn DM to {name} at {company}, 
introducing our services at Acme Corp, and asking if they’d be interested in a quick call.
"""
    resp = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":prompt}],
        max_tokens=200,
    )
    return resp.choices[0].message.content.strip()

def send_twitter_dm(user_id: str, text: str):
    """Send a DM on Twitter (requires elevated API access)."""
    twitter.send_direct_message(recipient_id=user_id, text=text)

def send_linkedin_message(profile_urn: str, text: str):
    """Post a LinkedIn message (organization→member) via the API."""
    linkedin_client.send_message([profile_urn], text)