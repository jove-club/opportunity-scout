import re
import time
import requests
import feedparser
from pytrends.request import TrendReq

SUBREDDITS = [
    "CasualUK", "unitedkingdom",
    "HikingUK", "UKhiking", "scottishhills",
    "hiking", "Mountaineering", "alpinism", "climbharder", "bouldering",
    "trailrunning", "ultrarunning", "running", "triathlon",
    "adventuretravel", "backpacking", "camping", "ultralight",
    "peakbagging", "wildernessbackpacking",
]

# Outdoor & adventure magazine/blog RSS feeds
MAGAZINE_FEEDS = [
    ("Trail Magazine", "https://www.trailrunningmag.co.uk/feed/"),
    ("The Great Outdoors", "https://www.tgomagazine.co.uk/feed/"),
    ("Outdoor Enthusiast", "https://www.outdoorenthusiast.co.uk/feed/"),
    ("Adventure Travel Magazine", "https://www.adventuretravelmag.co.uk/feed/"),
    ("Sidetracked", "https://sidetracked.com/feed/"),
    ("Alpinist", "https://www.alpinist.com/feed/"),
]

# Google Trends keywords to track
TRENDS_KEYWORDS = [
    ["guided hiking UK", "hiking holiday UK", "adventure weekend UK"],
    ["Scottish Highlands trip", "Snowdonia hike", "Lake District guided"],
    ["trail running UK", "fell running", "mountain running"],
    ["alpine climbing beginner", "mountaineering course UK"],
]

HEADERS = {"User-Agent": "opportunity-scout/1.0 (personal research tool)"}


def _fetch_rss(url, params=None):
    time.sleep(1.5)
    resp = requests.get(url, headers=HEADERS, params=params, timeout=15)
    resp.raise_for_status()
    return feedparser.parse(resp.content)


def _format_entry(entry, source):
    summary = entry.get("summary", "")
    body = re.sub(r"<[^>]+>", " ", summary).strip()[:400]
    return {
        "id": entry.get("id", ""),
        "title": entry.get("title", ""),
        "body": body,
        "url": entry.get("link", ""),
        "source": source,
    }


def _fetch_reddit_posts():
    posts = []
    seen_ids = set()
    for sub in SUBREDDITS:
        for feed_type, params in [("top", {"t": "week", "limit": 25}), ("hot", {"limit": 25})]:
            try:
                feed = _fetch_rss(f"https://www.reddit.com/r/{sub}/{feed_type}.rss", params)
                for entry in feed.entries:
                    eid = entry.get("id", "")
                    if eid and eid not in seen_ids:
                        seen_ids.add(eid)
                        posts.append(_format_entry(entry, f"Reddit r/{sub}"))
            except Exception as e:
                print(f"Error fetching r/{sub} {feed_type}: {e}")
    return posts


def _fetch_magazine_posts():
    posts = []
    seen_ids = set()
    for name, url in MAGAZINE_FEEDS:
        try:
            feed = _fetch_rss(url)
            for entry in feed.entries[:15]:
                eid = entry.get("id", "")
                if eid and eid not in seen_ids:
                    seen_ids.add(eid)
                    posts.append(_format_entry(entry, name))
        except Exception as e:
            print(f"Error fetching {name} RSS: {e}")
    return posts


def _fetch_google_trends():
    trends = []
    try:
        pytrends = TrendReq(hl="en-GB", tz=0)
        for keywords in TRENDS_KEYWORDS:
            try:
                time.sleep(2)
                pytrends.build_payload(keywords, timeframe="now 7-d", geo="GB")
                data = pytrends.interest_over_time()
                if data.empty:
                    continue
                # Summarise as a pseudo-post so the analyzer can include it
                week_avg = data[keywords].mean().to_dict()
                top_keyword = max(week_avg, key=week_avg.get)
                score = int(week_avg[top_keyword])
                trends.append({
                    "id": f"trends-{''.join(keywords)}",
                    "title": f"Google Trends (UK, past 7 days): '{top_keyword}' scored {score}/100",
                    "body": "Relative search interest this week (UK): " + ", ".join(
                        f"{k}: {int(v)}/100" for k, v in sorted(week_avg.items(), key=lambda x: -x[1])
                    ),
                    "url": "https://trends.google.com",
                    "source": "Google Trends",
                })
            except Exception as e:
                print(f"Trends error for {keywords}: {e}")
    except Exception as e:
        print(f"Google Trends init error: {e}")
    return trends


def fetch_posts():
    reddit_posts = _fetch_reddit_posts()
    magazine_posts = _fetch_magazine_posts()
    trends_posts = _fetch_google_trends()

    all_posts = reddit_posts + magazine_posts + trends_posts

    print(
        f"Fetched {len(reddit_posts)} Reddit, "
        f"{len(magazine_posts)} magazine, "
        f"{len(trends_posts)} Trends entries "
        f"({len(all_posts)} total)"
    )
    return all_posts
