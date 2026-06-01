import requests
from bs4 import BeautifulSoup
import pandas as pd
from pathlib import Path
from urllib.parse import urljoin
import re
import time

BASE_URL = "https://books.toscrape.com/catalogue/page-{}.html"

rating_map = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}

books = []

session = requests.Session()

headers = {
    "User-Agent": "Mozilla/5.0"
}

for page in range(1, 51):
    url = BASE_URL.format(page)
    print(f"Scraping page {page}/50 : {url}")

    try:
        response = session.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Erreur page {page} : {e}")
        continue

    soup = BeautifulSoup(response.text, "html.parser")
    articles = soup.find_all("article", class_="product_pod")

    for i, article in enumerate(articles, start=1):
        title = article.h3.a["title"]
        price = article.find("p", class_="price_color").text
        availability = article.find("p", class_="instock availability").text.strip()

        rating_class = article.find("p", class_="star-rating")["class"]
        rating_text = rating_class[1]
        rating = rating_map.get(rating_text)

        detail_href = article.h3.a["href"]
        detail_url = urljoin(url, detail_href)

        print(f"  Livre {i}/{len(articles)} : {title[:50]}")

        try:
            detail_response = session.get(detail_url, headers=headers, timeout=15)
            detail_response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"  Erreur page détail : {detail_url}")
            print(f"  {e}")

            books.append({
                "title": title,
                "price_raw": price,
                "availability": availability,
                "stock_available": None,
                "rating_text": rating_text,
                "rating": rating,
                "detail_url": detail_url
            })

            continue

        detail_soup = BeautifulSoup(detail_response.text, "html.parser")
        detail_availability = detail_soup.find("p", class_="instock availability").text.strip()

        stock_match = re.search(r"\((\d+) available\)", detail_availability)

        if stock_match:
            stock_available = int(stock_match.group(1))
        else:
            stock_available = None

        books.append({
            "title": title,
            "price_raw": price,
            "availability": detail_availability,
            "stock_available": stock_available,
            "rating_text": rating_text,
            "rating": rating,
            "detail_url": detail_url
        })

        time.sleep(0.1)

Path("data").mkdir(exist_ok=True)

df = pd.DataFrame(books)

output_path = Path("C:/Users/matma/OneDrive/Documents/Portefolio/Projet Python_Scrap/books_raw.csv")
output_path.parent.mkdir(parents=True, exist_ok=True)

df.to_csv(output_path, index=False, encoding="utf-8-sig")

print(f"Scraping completed: {len(df)} books collected.")
print(f"File created here: {output_path.resolve()}")