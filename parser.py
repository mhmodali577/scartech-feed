import feedparser
from config import FEED_URL

def get_posts():
    feed = feedparser.parse(FEED_URL)

    posts = []

    for entry in feed.entries:
        posts.append({
            "title": entry.get("title", ""),
            "url": entry.get("link", "")
        })

    return posts


if __name__ == "__main__":
    posts = get_posts()

    print("Posts:", len(posts))

    for p in posts[:5]:
        print(p["title"])
        print(p["url"])
        print("-" * 40)