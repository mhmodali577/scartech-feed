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

    rss = ET.Element("rss", version="2.0")

    channel = ET.SubElement(rss, "channel")

    ET.SubElement(channel, "title").text = STORE_NAME
    ET.SubElement(channel, "link").text = STORE_URL
    ET.SubElement(channel, "description").text = "ScarTech Google Merchant Feed"

    posts = get_posts()

    print(f"Found {len(posts)} products")

    for index, post in enumerate(posts, start=1):

        try:

            print(f"[{index}/{len(posts)}] {post['title']}")

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

            # Google Merchant
            add(item, "identifier_exists", "yes")
            add(item, "adult", "no")
            add(item, "google_product_category", "121")
            add(item, "product_type", "Projector Lamps")

            # MPN
            if product.get("mpn"):
                add(item, "mpn", product["mpn"])
            else:
                add(
                    item,
                    "mpn",
                    product["url"].split("/")[-1].replace(".html", "")
                )

            # SKU
            if product.get("sku"):
                add(item, "sku", product["sku"])

            # Price
            price = product.get("price", "").strip()

            if price:
                add(item, "price", f"{price} EGP")

            # Weight (اختياري)
            if product.get("weight"):
                add(item, "shipping_weight", f'{product["weight"]} kg')

        except Exception as e:

            print()
            print("=" * 60)
            print("ERROR")
            print(post["url"])
            print(e)
            print("=" * 60)

    os.makedirs("output", exist_ok=True)

    tree = ET.ElementTree(rss)

    tree.write(
        OUTPUT_XML,
        encoding="utf-8",
        xml_declaration=True
    )

    print()
    print("=" * 60)
    print("Feed Generated Successfully")
    print(OUTPUT_XML)
    print("=" * 60)

    print()
    print("=" * 60)
    print("Generating Local Inventory Feed...")
    print("=" * 60)

    build_local_inventory()


if __name__ == "__main__":
    build_feed()