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
    trip_ideas, trends = analyze_trips(posts)
    print(f"Found {len(trip_ideas)} trip ideas, {len(trends)} trends")

    print("Sending Jove digest...")
    send_digest(trip_ideas, trends)
    print("Done.")


if __name__ == "__main__":
    main()
