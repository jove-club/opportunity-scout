import os
from dotenv import load_dotenv

load_dotenv()

from src.jove_fetcher import fetch_posts
from src.jove_analyzer import analyze_trips
from src.jove_email import send_digest


def main():
    print("Fetching Reddit posts for Jove research...")
    posts = fetch_posts()
    print(f"Collected {len(posts)} posts")

    print("Analyzing with Claude...")
    observations, absent_signals = analyze_trips(posts)
    print(f"Found {len(observations)} observations, {len(absent_signals)} absent signals")

    print("Sending Jove digest...")
    send_digest(observations, absent_signals)
    print("Done.")


if __name__ == "__main__":
    main()
