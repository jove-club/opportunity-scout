import os
import praw

SUBREDDITS = [
    # General opportunity hunting
    "SaaS", "entrepreneur", "startups", "sidehustle", "smallbusiness", "nocode",
    # Fitness & health
    "fitness", "running", "hiking", "climbing", "bodyweightfitness", "triathlon",
    # Travel & outdoors
    "travel", "solotravel", "backpacking", "camping", "adventuretravel", "ultralight",
]

OPPORTUNITY_PHRASES = [
    "I wish there was",
    "why isn't there",
    "I'd pay for",
    "does anyone know of a tool",
    "looking for an app",
    "there should be an app",
    "nobody has built",
    "I hate that there's no",
    "frustrated with",
    "pain point",
    "I can't find a",
    "why is it so hard to",
]


def _get_client():
    return praw.Reddit(
        client_id=os.environ["REDDIT_CLIENT_ID"],
        client_secret=os.environ["REDDIT_CLIENT_SECRET"],
        user_agent=f"opportunity-scout/1.0 by u/{os.environ['REDDIT_USERNAME']}",
    )


def _format_post(post):
    return {
        "id": post.id,
        "title": post.title,
        "body": post.selftext[:400] if post.selftext else "",
        "url": f"https://reddit.com{post.permalink}",
        "subreddit": post.subreddit.display_name,
        "score": post.score,
        "num_comments": post.num_comments,
    }


def fetch_posts():
    reddit = _get_client()
    posts = []
    seen_ids = set()

    combined = "+".join(SUBREDDITS)

    # Keyword search for explicit opportunity signals
    for phrase in OPPORTUNITY_PHRASES:
        try:
            results = reddit.subreddit(combined).search(phrase, time_filter="week", limit=20)
            for post in results:
                if post.id not in seen_ids and post.score >= 3:
                    seen_ids.add(post.id)
                    posts.append(_format_post(post))
        except Exception as e:
            print(f"Search error for '{phrase}': {e}")

    # Top posts of the week — catches viral complaints not using keyword phrases
    try:
        top = reddit.subreddit(combined).top(time_filter="week", limit=75)
        for post in top:
            if post.id not in seen_ids:
                seen_ids.add(post.id)
                posts.append(_format_post(post))
    except Exception as e:
        print(f"Error fetching top posts: {e}")

    return posts
