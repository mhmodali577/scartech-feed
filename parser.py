import feedparser
import requests

from config import FEED_URL, REQUEST_TIMEOUT


def get_posts():

    print(f"Loading feed: {FEED_URL}", flush=True)

    response = requests.get(
        FEED_URL,
        timeout=REQUEST_TIMEOUT,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )

    response.raise_for_status()

    print("Feed downloaded successfully", flush=True)

    print("Parsing feed...", flush=True)

    feed = feedparser.parse(response.content)

    print("Feed parsed successfully", flush=True)

    print(f"Entries found: {len(feed.entries)}", flush=True)

    posts = []

    for index, entry in enumerate(feed.entries, start=1):

        if index % 10 == 0:
            print(f"Loaded {index} feed entries...", flush=True)

        posts.append({
            "title": entry.get("title", ""),
            "url": entry.get("link", "")
        })

    print(f"Found {len(posts)} posts", flush=True)

    return posts


if __name__ == "__main__":

    posts = get_posts()

    print()
    print("=" * 60)
    print(f"Posts: {len(posts)}")
    print("=" * 60)

    for p in posts[:5]:
        print(p["title"])
        print(p["url"])
        print("-" * 40)
