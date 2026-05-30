import re
import time
import os
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

# UK outdoor community forum RSS feeds
FORUM_FEEDS = [
    ("UKClimbing Forums", "https://www.ukclimbing.com/forums/rss/"),
    ("PlanetFear", "https://www.planetfear.com/feed/"),
    ("Run247", "https://www.run247.com/feed/"),
]

# Meetup groups — London outdoor/adventure communities
MEETUP_GROUPS = [
    "London-Outdoor-Adventure-Group",
    "London-Hikers",
    "London-Trail-Runners",
    "london-outdoor-adventures",
    "London-hiking-and-adventures",
]

# Eventbrite search queries (outdoor & adventure events in UK)
EVENTBRITE_QUERIES = [
    "hiking",
    "trail running",
    "mountaineering",
    "adventure weekend",
    "scrambling",
    "wild camping",
]

# YouTube search queries — what's trending in UK outdoor content
YOUTUBE_QUERIES = [
    "hiking UK 2026",
    "Scottish Highlands adventure",
    "trail running UK",
    "mountain scrambling UK",
    "outdoor adventure London",
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


def _fetch_forum_posts():
    posts = []
    seen_ids = set()
    for name, url in FORUM_FEEDS:
        try:
            feed = _fetch_rss(url)
            for entry in feed.entries[:20]:
                eid = entry.get("id", "")
                if eid and eid not in seen_ids:
                    seen_ids.add(eid)
                    posts.append(_format_entry(entry, name))
        except Exception as e:
            print(f"Error fetching {name} RSS: {e}")
    return posts


def _fetch_meetup_posts():
    posts = []
    seen_ids = set()
    for group in MEETUP_GROUPS:
        try:
            feed = _fetch_rss(f"https://www.meetup.com/{group}/events/rss/")
            for entry in feed.entries[:10]:
                eid = entry.get("id", "")
                if eid and eid not in seen_ids:
                    seen_ids.add(eid)
                    posts.append(_format_entry(entry, f"Meetup: {group}"))
        except Exception as e:
            print(f"Error fetching Meetup {group}: {e}")
    return posts


def _fetch_eventbrite_posts():
    token = os.environ.get("EVENTBRITE_TOKEN")
    if not token:
        print("Skipping Eventbrite — no EVENTBRITE_TOKEN set")
        return []

    posts = []
    seen_ids = set()
    headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    for query in EVENTBRITE_QUERIES:
        try:
            time.sleep(1)
            resp = requests.get(
                "https://www.eventbriteapi.com/v3/events/search/",
                headers=headers,
                params={
                    "q": query,
                    "location.address": "United Kingdom",
                    "location.within": "300km",
                    "categories": "17",  # Outdoor & Adventure
                    "expand": "ticket_availability",
                    "sort_by": "date",
                    "page_size": 20,
                },
                timeout=15,
            )
            resp.raise_for_status()
            for event in resp.json().get("events", []):
                eid = event.get("id", "")
                if eid and eid not in seen_ids:
                    seen_ids.add(eid)
                    avail = event.get("ticket_availability", {})
                    sold_out = avail.get("is_sold_out", False)
                    waitlist = avail.get("waitlist_available", False)
                    status_note = " [SOLD OUT]" if sold_out else (" [WAITLIST]" if waitlist else "")
                    posts.append({
                        "id": eid,
                        "title": event.get("name", {}).get("text", "") + status_note,
                        "body": (event.get("description", {}).get("text") or "")[:400],
                        "url": event.get("url", ""),
                        "source": "Eventbrite",
                    })
        except Exception as e:
            print(f"Eventbrite error for '{query}': {e}")

    return posts


def _fetch_youtube_posts():
    api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        print("Skipping YouTube — no YOUTUBE_API_KEY set")
        return []

    posts = []
    seen_ids = set()
    # Published after: 7 days ago
    from datetime import datetime, timedelta, timezone
    published_after = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")

    for query in YOUTUBE_QUERIES:
        try:
            time.sleep(1)
            resp = requests.get(
                "https://www.googleapis.com/youtube/v3/search",
                params={
                    "part": "snippet",
                    "q": query,
                    "type": "video",
                    "order": "viewCount",
                    "publishedAfter": published_after,
                    "regionCode": "GB",
                    "relevanceLanguage": "en",
                    "maxResults": 10,
                    "key": api_key,
                },
                timeout=15,
            )
            resp.raise_for_status()
            for item in resp.json().get("items", []):
                vid_id = item.get("id", {}).get("videoId", "")
                if vid_id and vid_id not in seen_ids:
                    seen_ids.add(vid_id)
                    snippet = item.get("snippet", {})
                    posts.append({
                        "id": vid_id,
                        "title": snippet.get("title", ""),
                        "body": snippet.get("description", "")[:400],
                        "url": f"https://www.youtube.com/watch?v={vid_id}",
                        "source": f"YouTube (search: {query})",
                    })
        except Exception as e:
            print(f"YouTube error for '{query}': {e}")

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
    forum_posts = _fetch_forum_posts()
    meetup_posts = _fetch_meetup_posts()
    eventbrite_posts = _fetch_eventbrite_posts()
    youtube_posts = _fetch_youtube_posts()
    trends_posts = _fetch_google_trends()

    all_posts = (
        reddit_posts + magazine_posts + forum_posts +
        meetup_posts + eventbrite_posts + youtube_posts + trends_posts
    )

    print(
        f"Fetched {len(reddit_posts)} Reddit, "
        f"{len(magazine_posts)} magazine, "
        f"{len(forum_posts)} forum, "
        f"{len(meetup_posts)} Meetup, "
        f"{len(eventbrite_posts)} Eventbrite, "
        f"{len(youtube_posts)} YouTube, "
        f"{len(trends_posts)} Trends entries "
        f"({len(all_posts)} total)"
    )
    return all_posts
