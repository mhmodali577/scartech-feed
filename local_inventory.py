import xml.etree.ElementTree as ET

from parser import get_posts
from merchant import extract_product

G = "http://base.google.com/ns/1.0"

ET.register_namespace("g", G)


def g(tag):
    return "{%s}%s" % (G, tag)


def add(parent, tag, value):
    el = ET.SubElement(parent, g(tag))
    el.text = str(value)
    return el


OUTPUT_XML = "local-inventory.xml"

STORE_CODE = "08657209231339284488"


def build_local_inventory():

    rss = ET.Element("rss", version="2.0")

    channel = ET.SubElement(rss, "channel")

    ET.SubElement(channel, "title").text = "ScarTech Local Inventory"

    posts = get_posts()

    print(f"Building Local Inventory ({len(posts)} products)")

    for index, post in enumerate(posts, start=1):

        try:

            print(f"[{index}/{len(posts)}] {post['title']}")

            product = extract_product(post["url"])

            item = ET.SubElement(channel, "item")

            product_id = (
                product.get("mpn")
                or product.get("sku")
                or product["url"].split("/")[-1].replace(".html", "")
            )

            add(item, "id", product_id)

            add(item, "store_code", STORE_CODE)

            add(item, "availability", "in stock")

            price = product.get("price", "").strip()

            if price:
                add(item, "price", f"{price} EGP")

            add(item, "quantity", "50")

        except Exception as e:

            print()
            print("=" * 60)
            print("LOCAL INVENTORY ERROR")
            print(post["url"])
            print(e)
            print("=" * 60)

    tree = ET.ElementTree(rss)

    tree.write(
        OUTPUT_XML,
        encoding="utf-8",
        xml_declaration=True
    )

    print()
    print("=" * 60)
    print("Local Inventory Generated Successfully")
    print(OUTPUT_XML)
    print("=" * 60)


if __name__ == "__main__":
    build_local_inventory()