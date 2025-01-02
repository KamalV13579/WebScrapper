import time
from selenium import webdriver
from bs4 import BeautifulSoup
from openai import OpenAI
from dotenv import load_dotenv
import os

PATH = "C:\Program Files (x86)\chromedriver-latest.exe"

def getPurpose():
    while True:
        purpose = input("Are you buying or selling a car?").strip().lower()
        if (purpose == "buying" or purpose == "selling"):
            return purpose
        print("Please enter 'buying' or 'selling'.")

def getPreferences():
    preferences = {}
    preferences['make'] = input("Enter car make (or press Enter to skip): ").strip()
    preferences['model'] = input("Enter car model (or press Enter to skip): ").strip()
    preferences['year'] = input("Enter minimum car year (or press Enter to skip): ").strip()
    preferences['miles'] = input("Enter maximum mileage (or press Enter to skip): ").strip()
    preferences['price'] = input("Enter maximum price (or press Enter to skip): ").strip()
    return preferences

def getCarInfo():
    carInfo = {}
    carInfo['make'] = input("Enter car make: ").strip()
    carInfo['model'] = input("Enter car model: ").strip()
    carInfo['year'] = input("Enter car year: ").strip()
    carInfo['miles'] = input("Enter car mileage: ").strip()
    carInfo['price'] = "N/A"
    return carInfo

def scraper(driver, info):
    url = "https://charlotte.craigslist.org/search/cta"
    search = ""

    if info['make']:
        search += f"&auto_make_model={info['make']}"
        if(info['model']):
            search += f"%20{info['model']}"
    elif info['model']:
        search += f"&auto_make_model={info['model']}"
    if info['year']:
        search += f"&min_auto_year={info['year']}"
    if info['miles']:
        search += f"&max_auto_miles={info['miles']}"
    if info['price'] and info['price'] != "N/A":
        search += f"&max_price={info['price']}"

    full_url = url + "?" + search

    driver.get(full_url)
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    postings = soup.find_all("div",class_="cl-search-result cl-search-view-mode-gallery")

    listings = []
    for posting in postings:
        title_element = posting.find('a', class_='cl-app-anchor text-only posting-title')
        title = title_element.text.strip() if title_element else "N/A"
        price_element = posting.find("span" , class_="priceinfo")
        price = price_element.text.strip() if price_element else "N/A"
        link = title_element['href'] if title_element else "#"
        listings.append({"title": title, "price": price, "link": link})

    return listings

def suggestPrice(listings):
    prices = []
    for listing in listings:
        if listing['price'] != "N/A":
            prices.append(int(listing['price'].replace("$", "").replace(",", "")))

    if prices:
        avg_price = sum(prices) / len(prices)
        return f"Based on similar cars, we suggest listing your car at around ${avg_price:.2f}."
    else:
        return "No similar cars found. Try broadening your search."
    
def suggestBuy(listings):
  load_dotenv()
  useCase = input("Do you have a specific use for the car you are buying? (Enter to skip):").strip()
  API_KEY = os.getenv("OPENAI_API_KEY")

  client = OpenAI(api_key= API_KEY)
  messages = [{"role": "system", "content": "You are an expert car analyst."}]

  if useCase:
    messages.append(
        {
            "role": "user",
            "content": (
                f"I am looking for a car for the following use case: {useCase}. "
                "Here are car listings scraped from Craigslist. Analyze and determine "
                "which car is the best value based on make, model, price, mpg, maintenance, "
                "value held, and any other relevant details:\n"
                + "\n".join(
                    [
                        f"- {listing['title']} | Price: {listing['price']} | Link: {listing['link']}"
                        for listing in listings
                    ]
                )
                + "Output the best car to buy based on its value and give a very brief justification."
            ),
        }
    )
  else:
    messages.append(
        {
            "role": "user",
            "content": (
                "Here are car listings scraped from Craigslist. Analyze and determine "
                "which car is the best value based on make, model, price, mpg, maintenance, "
                "value held, and any other relevant details:\n"
                + "\n".join(
                    [
                        f"- {listing['title']} | Price: {listing['price']} | Link: {listing['link']}"
                        for listing in listings
                    ]
                )
                + "Output the best car to buy based on its value and give a very brief justification."
            ),
        }
    )
  completion = client.chat.completions.create(
  model="gpt-4o-mini",
  store=True,
  messages = messages
)
  print(completion.choices[0].message)


def main():
    driver = webdriver.Chrome()
    purpose = getPurpose()
    if(purpose == "buying"):
        info = getPreferences()
        listings = scraper(driver, info)
        suggestBuy(listings)
        
    else:
        info = getCarInfo()
        listings = scraper(driver, info)
        result = suggestPrice(listings)
        print(result)

    
    driver.quit()

main()
    



