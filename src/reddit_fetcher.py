import time
import requests
import feedparser

SUBREDDITS = [
    # General opportunity hunting
    "SaaS", "entrepreneur", "startups", "sidehustle", "smallbusiness", "nocode",
    # Fitness & health
    "fitness", "running", "hiking", "climbing", "bodyweightfitness", "triathlon",
    # Travel & outdoors
    "travel", "solotravel", "backpacking", "camping", "adventuretravel", "ultralight",
]

HEADERS = {
    "User-Agent": "opportunity-scout/1.0 (personal research tool)"
}


def _fetch_rss(url, params=None):
    time.sleep(1.5)
    resp = requests.get(url, headers=HEADERS, params=params, timeout=15)
    resp.raise_for_status()
    return feedparser.parse(resp.content)


def _format_entry(entry, subreddit):
    # Extract plain text from RSS summary (contains HTML)
    summary = entry.get("summary", "")
    # Strip basic HTML tags for cleanliness
    import re
    body = re.sub(r"<[^>]+>", " ", summary).strip()[:400]
    return {
        "id": entry.get("id", ""),
        "title": entry.get("title", ""),
        "body": body,
        "url": entry.get("link", ""),
        "subreddit": subreddit,
    }


def fetch_posts():
    posts = []
    seen_ids = set()

    for sub in SUBREDDITS:
        # Top posts of the week
        try:
            feed = _fetch_rss(
                f"https://www.reddit.com/r/{sub}/top.rss",
                {"t": "week", "limit": 25},
            )
            for entry in feed.entries:
                eid = entry.get("id", "")
                if eid and eid not in seen_ids:
                    seen_ids.add(eid)
                    posts.append(_format_entry(entry, sub))
        except Exception as e:
            print(f"Error fetching top posts from r/{sub}: {e}")

        # Hot posts
        try:
            feed = _fetch_rss(
                f"https://www.reddit.com/r/{sub}/hot.rss",
                {"limit": 25},
            )
            for entry in feed.entries:
                eid = entry.get("id", "")
                if eid and eid not in seen_ids:
                    seen_ids.add(eid)
                    posts.append(_format_entry(entry, sub))
        except Exception as e:
            print(f"Error fetching hot posts from r/{sub}: {e}")

    print(f"Fetched {len(posts)} posts from RSS feeds")
    return posts
