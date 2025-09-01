import argparse
import re
import sqlite3
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
import pandas as pd

BASE = "https://books.toscrape.com/"


def star_to_int(star_str: str) -> int:
    mapping = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
    for name, val in mapping.items():
        if name in star_str:
            return val
    return 0


def parse_price(p: str) -> float:
    return float(re.sub(r'[^0-9\.]', '', p))


def parse_availability(txt: str) -> int:
    m = re.search(r'(\d+)', txt)
    return int(m.group(1)) if m else 0


def get_soup(url: str) -> BeautifulSoup:
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return BeautifulSoup(r.text, "html.parser")


def scrape_category(cat_url: str, cat_name: str, collected: int, limit: int = 0):
    """
    Raspagem de uma categoria inteira. Para no limite global se atingido.
    """
    books = []
    next_url = cat_url
    while next_url:
        soup = get_soup(next_url)
        for art in soup.select("article.product_pod"):
            # dados da listagem
            title = art.h3.a["title"]
            rel = art.h3.a["href"]
            product_url = urljoin(next_url, rel)
            rating = star_to_int(" ".join(art.p["class"]))
            price = parse_price(art.select_one(".price_color").text.strip())
            img_rel = art.find("img")["src"]
            image_url = urljoin(BASE, img_rel)

            # detalhe do livro
            bs = get_soup(product_url)
            desc = bs.select_one("#product_description ~ p")
            desc_txt = desc.text.strip() if desc else None
            upc_el = bs.select_one("th:-soup-contains('UPC') + td")
            upc = upc_el.text if upc_el else None
            avail_txt = bs.select_one(".availability").text.strip()
            availability = parse_availability(avail_txt)

            books.append({
                "title": title, "price": price, "rating": rating, "availability": availability,
                "category": cat_name, "image_url": image_url, "product_page_url": product_url,
                "description": desc_txt, "upc": upc
            })

            collected += 1
            if limit and collected >= limit:
                return books, collected, True  # atingiu limite global

        nxt = soup.select_one("li.next > a")
        next_url = urljoin(next_url, nxt["href"]) if nxt else None
    return books, collected, False


def persist_incremental(books, out_dir="data"):
    """
    Salva incrementalmente os livros em CSV e SQLite.
    Acrescenta novos livros ao arquivo existente.
    """
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    csv_path = Path(out_dir) / "books.csv"
    db_path = Path(out_dir) / "books.db"

    df = pd.DataFrame(books)

    # CSV: append (header só se arquivo não existir)
    header = not csv_path.exists()
    df.to_csv(csv_path, mode="a", index=False, header=header)

    # SQLite: append
    con = sqlite3.connect(db_path)
    df.to_sql("books", con, if_exists="append", index_label="id")
    con.close()

    print(f"[persist] +{len(df)} rows -> {csv_path}, {db_path}")


def scrape_all(limit: int = 0):
    soup = get_soup(BASE)
    cats = []
    for a in soup.select(".side_categories a"):
        name = a.text.strip()
        href = urljoin(BASE, a["href"])
        if "catalogue" not in href and "category" not in href:
            continue
        cats.append((name, href))

    collected = 0
    for name, href in cats:
        print(f"[cat] {name}")
        books, collected, done = scrape_category(href, name, collected, limit)
        if books:
            persist_incremental(books)
        if done:
            print(f"[done] limite de {limit} livros atingido")
            break


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="Limite TOTAL de livros (0 = completo)")
    args = ap.parse_args()
    scrape_all(limit=args.limit)


if __name__ == "__main__":
    main()
