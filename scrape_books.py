import requests
from bs4 import BeautifulSoup
import pandas as pd
from pathlib import Path

BASE_URL = "https://books.toscrape.com/catalogue/page-{}.html"

rating_map = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}

books = []

for page in range(1, 51):
    url = BASE_URL.format(page)
    response = requests.get(url, timeout=10)

    if response.status_code != 200:
        print(f"Page {page} unavailable. Status code: {response.status_code}")
        continue

    soup = BeautifulSoup(response.text, "html.parser")
    articles = soup.find_all("article", class_="product_pod")

    for article in articles:
        title = article.h3.a["title"]
        price = article.find("p", class_="price_color").text
        availability = article.find("p", class_="instock availability").text.strip()
        rating_class = article.find("p", class_="star-rating")["class"]
        rating_text = rating_class[1]
        rating = rating_map.get(rating_text)

        books.append({
            "title": title,
            "price_raw": price,
            "availability": availability,
            "rating_text": rating_text,
            "rating": rating
        })

Path("data").mkdir(exist_ok=True)

df = pd.DataFrame(books)

output_path = Path("C:/Users/matma/OneDrive/Documents/Portefolio/Projet Python_Scrap/books_raw.csv")
df.to_csv("C:/Users/matma/OneDrive/Documents/Portefolio/Projet Python_Scrap/books_raw.csv", index=False, encoding="utf-8-sig")

print(f"Scraping completed: {len(df)} books collected.")
print(f"File created here: {output_path.resolve()}")
