import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup

from config import USER_AGENT, REQUEST_TIMEOUT

HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/",
    "Cache-Control": "no-cache",
}

session = requests.Session()

retry = Retry(
    total=8,
    connect=8,
    read=8,
    backoff_factor=3,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=frozenset(["GET"]),
    respect_retry_after_header=True,
)

adapter = HTTPAdapter(max_retries=retry)

session.mount("https://", adapter)
session.mount("http://", adapter)


def clean(value):
    if not value:
        return ""
    return " ".join(str(value).split())


def meta_content(soup, attr, value):

    tag = soup.find("meta", attrs={attr: value})

    if tag:
        return clean(tag.get("content", ""))

    return ""


def extract_product(url):

    time.sleep(1.2)

    last_error = None

    for attempt in range(3):

        try:

            response = session.get(
                url,
                headers=HEADERS,
                timeout=REQUEST_TIMEOUT
            )

            response.raise_for_status()

            break

        except requests.exceptions.HTTPError as e:

            last_error = e

            if e.response is not None and e.response.status_code == 429:

                wait = 15 * (attempt + 1)

                print(f"429 received, waiting {wait} seconds...")

                time.sleep(wait)

                continue

            raise

    else:

        raise last_error

    soup = BeautifulSoup(response.text, "lxml")

    product = {}

    # -----------------------------
    # URL
    # -----------------------------

    product["url"] = url

    # -----------------------------
    # TITLE
    # -----------------------------

    h1 = soup.find("h1")

    product["title"] = clean(
        h1.get_text()
        if h1 else ""
    )

    # -----------------------------
    # DESCRIPTION
    # -----------------------------

    product["description"] = (
        meta_content(
            soup,
            "itemprop",
            "description"
        )
        or
        meta_content(
            soup,
            "name",
            "description"
        )
    )

    # -----------------------------
    # IMAGE
    # -----------------------------

    product["image"] = meta_content(
        soup,
        "itemprop",
        "image"
    )

    if not product["image"]:

        img = soup.find("img")

        if img:

            product["image"] = (
                img.get("src")
                or img.get("data-src")
                or ""
            )

    # -----------------------------
    # BRAND
    # -----------------------------

    brand_meta = soup.select_one(
        '[itemprop="brand"] meta[itemprop="name"]'
    )

    if brand_meta:

        product["brand"] = clean(
            brand_meta.get("content", "")
        )

    else:

        product["brand"] = "SCARTECH"

    # -----------------------------
    # SKU
    # -----------------------------

    product["sku"] = meta_content(
        soup,
        "itemprop",
        "sku"
    )

    # -----------------------------
    # MPN
    # -----------------------------

    product["mpn"] = meta_content(
        soup,
        "itemprop",
        "mpn"
    )

    # -----------------------------
    # PRICE
    # -----------------------------

    price_tag = soup.select_one(
        "div.field.hide span.price"
    )

    if price_tag:

        product["price"] = clean(
            price_tag.get_text()
        )

    else:

        product["price"] = ""

    product["currency"] = "EGP"

    # -----------------------------
    # STOCK
    # -----------------------------

    status = soup.select_one(
        "div.field.hide span.status"
    )

    if status:

        if clean(status.get_text()).lower() == "on":

            product["availability"] = "in_stock"

        else:

            product["availability"] = "out_of_stock"

    else:

        product["availability"] = "in_stock"

    # -----------------------------
    # CONDITION
    # -----------------------------

    product["condition"] = "new"

    return product


if __name__ == "__main__":

    url = "https://www.scartech-eg.com/2026/08/epson-ex5260-projector-lamp.html"

    product = extract_product(url)

    print()

    for key, value in product.items():

        print(f"{key:15}: {value}")