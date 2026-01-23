from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time


options = Options()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)
url = "https://www.99acres.com/search/property/rent/bhiwadi?city=289&bedroom_num=1%2C2%2C3&preference=R&area_unit=1&budget_min=0&res_com=R&isPreLeased=N"
driver.get(url)
time.sleep(5)

last_height = driver.execute_script("return document.body.scrollHeight")

for _ in range(5):  # scroll 5 times only
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(4)  # wait for new listings
    
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height


html = driver.page_source
from bs4 import BeautifulSoup

soup = BeautifulSoup(html, "html.parser")

from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd





price_blocks = soup.find_all("div", class_="tupleNew__priceWrap")
cards = []

for pb in price_blocks:
    card = pb.find_parent("div", class_="tupleNew__outerTupleWrap")
    if card:
        cards.append(card)

print("Final cards found:", len(cards))


import re

data = []

import re

data = []

for card in cards:
    text = card.get_text(" ", strip=True)

    # -------- PRICE --------
    price = None
    price_div = card.find("div", class_="tupleNew__priceWrap")
    if price_div:
        span = price_div.find("span")
        if span:
            price = span.text.strip()

    # -------- AREA (sqft) --------
    area_sqft = None
    area_match = re.search(r"([\d,]+)\s*sqft", text)
    if area_match:
        area_sqft = area_match.group(1).replace(",", "")

    # -------- BHK --------
    bhk = None
    bhk_match = re.search(r"(\d+)\s*BHK", text)
    if bhk_match:
        bhk = bhk_match.group(1) + " BHK"

    # -------- ADDRESS (FIXED) --------
    address = None
    addr_div = card.select_one("div.tupleNew__locationName")
    if addr_div:
        address = addr_div.get_text(strip=True)

    # -------- FURNISHED (FIXED) --------
    furnished = "Unfurnished"
    content_tags = card.find("div", class_="tupleNew__contentTags")
    if content_tags:
        furn_span = content_tags.find("span", class_="tupleNew__furnished")
        if furn_span:
            furnished = furn_span.text.strip()

    data.append({
        "price": price,
        "area_sqft": area_sqft,
        "bhk": bhk,
        "furnished": furnished,
        "address": address
    })

df = pd.DataFrame(data)
print(df.head())
print("Total listings:", len(df))


print(df["furnished"].value_counts())
print(df["address"].head())
df.to_csv("99acres_listings_bhiwadi.csv", index=False)
