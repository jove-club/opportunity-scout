import os
from dotenv import load_dotenv

load_dotenv()

from src.reddit_fetcher import fetch_posts
from src.analyzer import analyze_opportunities
from src.email_sender import send_digest


def main():
    print("Fetching Reddit posts...")
    posts = fetch_posts()
    print(f"Collected {len(posts)} posts")

    print("Analyzing with Claude...")
    opportunities = analyze_opportunities(posts)
    print(f"Found {len(opportunities)} opportunities scoring 7+")

    print("Sending digest...")
    send_digest(opportunities)
    print("Done.")


if __name__ == "__main__":
    main()
