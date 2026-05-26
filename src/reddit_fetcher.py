import re
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

# Hacker News "Ask HN" search terms — people posting problems they want solved
HN_SEARCH_TERMS = [
    "ask HN who wants",
    "ask HN I need",
    "ask HN is there a tool",
    "ask HN why isn't there",
    "ask HN looking for",
    "show HN",
]

HEADERS = {"User-Agent": "opportunity-scout/1.0 (personal research tool)"}


def _fetch_rss(url, params=None):
    time.sleep(1.5)
    resp = requests.get(url, headers=HEADERS, params=params, timeout=15)
    resp.raise_for_status()
    return feedparser.parse(resp.content)


def _format_reddit_entry(entry, subreddit):
    summary = entry.get("summary", "")
    body = re.sub(r"<[^>]+>", " ", summary).strip()[:400]
    return {
        "id": entry.get("id", ""),
        "title": entry.get("title", ""),
        "body": body,
        "url": entry.get("link", ""),
        "source": f"Reddit r/{subreddit}",
    }


def _fetch_hn_posts():
    posts = []
    seen_ids = set()

    # HN Algolia search API — free, no auth
    for term in HN_SEARCH_TERMS:
        try:
            time.sleep(1)
            resp = requests.get(
                "https://hn.algolia.com/api/v1/search",
                params={"query": term, "tags": "story", "numericFilters": "created_at_i>{}".format(
                    int(time.time()) - 7 * 24 * 3600  # last 7 days
                ), "hitsPerPage": 20},
                timeout=10,
            )
            resp.raise_for_status()
            for hit in resp.json().get("hits", []):
                oid = hit.get("objectID", "")
                if oid and oid not in seen_ids:
                    seen_ids.add(oid)
                    posts.append({
                        "id": oid,
                        "title": hit.get("title", ""),
                        "body": (hit.get("story_text") or "")[:400],
                        "url": hit.get("url") or f"https://news.ycombinator.com/item?id={oid}",
                        "source": "Hacker News",
                    })
        except Exception as e:
            print(f"HN search error for '{term}': {e}")

    # Also grab top Ask HN stories of the week via RSS
    try:
        feed = _fetch_rss("https://hnrss.org/ask?points=10")
        for entry in feed.entries:
            eid = entry.get("id", "")
            if eid and eid not in seen_ids:
                seen_ids.add(eid)
                body = re.sub(r"<[^>]+>", " ", entry.get("summary", "")).strip()[:400]
                posts.append({
                    "id": eid,
                    "title": entry.get("title", ""),
                    "body": body,
                    "url": entry.get("link", ""),
                    "source": "Hacker News",
                })
    except Exception as e:
        print(f"HN RSS error: {e}")

    return posts


def fetch_posts():
    posts = []
    seen_ids = set()

    # Reddit
    for sub in SUBREDDITS:
        for feed_type, params in [("top", {"t": "week", "limit": 25}), ("hot", {"limit": 25})]:
            try:
                feed = _fetch_rss(f"https://www.reddit.com/r/{sub}/{feed_type}.rss", params)
                for entry in feed.entries:
                    eid = entry.get("id", "")
                    if eid and eid not in seen_ids:
                        seen_ids.add(eid)
                        posts.append(_format_reddit_entry(entry, sub))
            except Exception as e:
                print(f"Error fetching r/{sub} {feed_type}: {e}")

    reddit_count = len(posts)

    # Hacker News
    hn_posts = _fetch_hn_posts()
    for p in hn_posts:
        if p["id"] not in seen_ids:
            seen_ids.add(p["id"])
            posts.append(p)

    print(f"Fetched {reddit_count} Reddit posts, {len(posts) - reddit_count} HN posts ({len(posts)} total)")
    return posts
