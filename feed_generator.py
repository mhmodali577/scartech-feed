import os
import xml.etree.ElementTree as ET

from parser import get_posts
from merchant import extract_product
from local_inventory import build_local_inventory
from config import (
    OUTPUT_XML,
    STORE_NAME,
    STORE_URL
)

G = "http://base.google.com/ns/1.0"

ET.register_namespace("g", G)


def g(tag):
    return "{%s}%s" % (G, tag)


def add(parent, tag, value):
    el = ET.SubElement(parent, g(tag))
    el.text = str(value)
    return el


def build_feed():

    print("Starting Google Merchant Feed...", flush=True)

    rss = ET.Element("rss", version="2.0")

    channel = ET.SubElement(rss, "channel")

    ET.SubElement(channel, "title").text = STORE_NAME
    ET.SubElement(channel, "link").text = STORE_URL
    ET.SubElement(channel, "description").text = "ScarTech Google Merchant Feed"

    print("Loading posts...", flush=True)

    posts = get_posts()

    print(f"Found {len(posts)} products", flush=True)

    for index, post in enumerate(posts, start=1):

        try:

            print(
                f"[{index}/{len(posts)}] {post['title']}",
                flush=True
            )

            product = extract_product(post["url"])

            item = ET.SubElement(channel, "item")

            # ID
            add(
                item,
                "id",
                product.get("mpn")
                or product.get("sku")
                or product["url"].split("/")[-1].replace(".html", "")
            )

            add(item, "title", product["title"])
            add(item, "description", product["description"])
            add(item, "link", product["url"])
            add(item, "image_link", product["image"])

            add(item, "availability", product["availability"])
            add(item, "condition", product["condition"])
            add(item, "brand", product["brand"])

            add(item, "identifier_exists", "yes")
            add(item, "adult", "no")
            add(item, "google_product_category", "121")
            add(item, "product_type", "Projector Lamps")

            if product.get("mpn"):

                add(item, "mpn", product["mpn"])

            else:

                add(
                    item,
                    "mpn",
                    product["url"].split("/")[-1].replace(".html", "")
                )

            if product.get("sku"):
                add(item, "sku", product["sku"])

            price = product.get("price", "").strip()

            if price:
                add(item, "price", f"{price} EGP")

            if product.get("weight"):
                add(
                    item,
                    "shipping_weight",
                    f'{product["weight"]} kg'
                )

        except Exception as e:

            print()
            print("=" * 60, flush=True)
            print("ERROR", flush=True)
            print(post["url"], flush=True)
            print(e, flush=True)
            print("=" * 60, flush=True)

    print("Writing XML...", flush=True)

    os.makedirs("output", exist_ok=True)

    tree = ET.ElementTree(rss)

    tree.write(
        OUTPUT_XML,
        encoding="utf-8",
        xml_declaration=True
    )

    print()
    print("=" * 60, flush=True)
    print("Feed Generated Successfully", flush=True)
    print(OUTPUT_XML, flush=True)
    print("=" * 60, flush=True)

    print()
    print("=" * 60, flush=True)
    print("Generating Local Inventory Feed...", flush=True)
    print("=" * 60, flush=True)

    build_local_inventory()

    print()
    print("=" * 60, flush=True)
    print("DONE", flush=True)
    print("=" * 60, flush=True)


if __name__ == "__main__":
    build_feed()
