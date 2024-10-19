import time
from selenium import webdriver
from bs4 import BeautifulSoup

PATH = "C:\Program Files (x86)\chromedriver.exe"
url = "https://charlotte.craigslist.org/search/cta#search=1~gallery~0~0"

driver = webdriver.Chrome()

driver.get(url)
time.sleep(5)
html = driver.page_source
soup = BeautifulSoup(html, "html.parser")
postings = soup.find_all("li",class_="cl-search-result cl-search-view-mode-gallery")

for posting in postings:
    title = posting.find("a", class_="cl-app-anchor")  # Using the text-only posting title
    title_text = title.get_text(strip=True) if title else "No title"
    price = posting.find("span", class_="priceinfo").get_text(strip=True) if posting.find("span", class_="priceinfo") else "No price"
    link = posting.find("a")["href"] if posting.find("a") else "No link"
    miles = posting.find("div", class_="meta").get_text(strip=True) if posting.find("div", class_="meta") else "No meta info"
    milage = ""
    if(posting.find("div", class_="meta")):
        split_text = miles.split("·")
        if(split_text[1]==None):
            milage = "No Miles"
        else:
            milage = split_text[1]
       

    # Print the extracted details
    print(f"Title: {title_text}")
    print(f"Price: {price}")
    print(f"Link: {link}")
    print(f"Miles: {milage}")
    print("---")

driver.quit()
