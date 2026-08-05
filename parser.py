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

    feed = feedparser.parse(response.content)

    posts = []

    for entry in feed.entries:
        posts.append({
            "title": entry.get("title", ""),
            "url": entry.get("link", "")
        })

    print(f"Found {len(posts)} posts", flush=True)

    return posts


if __name__ == "__main__":

    posts = get_posts()

    print("Posts:", len(posts))

    for p in posts[:5]:
        print(p["title"])
        print(p["url"])
        print("-" * 40)
