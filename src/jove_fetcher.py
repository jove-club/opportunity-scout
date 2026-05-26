import time
import re
import requests
import feedparser

SUBREDDITS = [
    # UK general
    "CasualUK", "unitedkingdom",
    # UK outdoor & hiking
    "HikingUK", "UKhiking", "scottishhills",
    # Adventure & mountaineering
    "hiking", "Mountaineering", "alpinism", "climbharder", "bouldering",
    # Running & endurance
    "trailrunning", "ultrarunning", "running", "triathlon",
    # Travel & outdoors
    "adventuretravel", "backpacking", "camping", "ultralight",
    # Challenge & peak bagging
    "peakbagging", "wildernessbackpacking",
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
    summary = entry.get("summary", "")
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
        for feed_type, params in [("top", {"t": "week", "limit": 25}), ("hot", {"limit": 25})]:
            try:
                feed = _fetch_rss(
                    f"https://www.reddit.com/r/{sub}/{feed_type}.rss",
                    params,
                )
                for entry in feed.entries:
                    eid = entry.get("id", "")
                    if eid and eid not in seen_ids:
                        seen_ids.add(eid)
                        posts.append(_format_entry(entry, sub))
            except Exception as e:
                print(f"Error fetching r/{sub} {feed_type}: {e}")

    print(f"Fetched {len(posts)} posts from RSS feeds")
    return posts
