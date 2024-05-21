# Ebay Web Scraping App

from bs4 import BeautifulSoup
import requests 
import numpy as np
import csv
from datetime import datetime
import schedule
import time
import pytz
import subprocess

# Can be changed to ask users to input web address, best used with scheduler turned off
# LINK = input("Please enter the web address of the eBay listing you've search: ")

LINK = "https://www.ebay.com/sch/i.html?_from=R40&_trksid=p4432023.m570.l1313&_nkw=16lb+shotput&_sacat=0"

def get_prices_by_link(link):
    r = requests.get(link)
# Using 'get' to request web link as the source
    page_parse = BeautifulSoup(r.text, 'html.parser')
    search_results = page_parse.find("ul",{"class":"srp-results"}).find_all("li",{"class":"s-item"})
# Requesting source material's HTLM data, to be parsed using BS4

    item_prices = []

# Parsed data is used to find and define item price, accounting for ranged pricing
    for result in search_results:
        price_as_text = result.find("span",{"class":"s-item__price"}).text
        if "to" in price_as_text:
            continue
        price = float(price_as_text[1:].replace(",",""))
        item_prices.append(price)
    return item_prices

# Making another request to the LINK to identify the itme
response = requests.get(LINK)
html_content = response.text

# Parsing the web page to find search query parameter, based on URL
# Ignores webpage search bar
soup = BeautifulSoup(html_content, "html.parser")
query_param = soup.find("input", {"id": "gh-ac"})
if query_param:
    item = query_param.get("value")
else:
    item = ""

# Removing outliers by excluding all listings 2 standard deviations above/below mean, using numpy
# Eliminates spam, scam, and fake listings
def remove_outliers(prices, m=2):
    data = np.array(prices)
    return data[abs(data - np.mean(data)) < m * np.std(data)]

def get_average(prices):
    return np.mean(prices)

# Creating an Excel doc that saves upon use
# Used to track price over time, get better understanding of trends
def save_to_file(prices):
    fields=[datetime.today().strftime("%B-%D-%Y"),np.around(get_average(prices),2)]
    with open('prices.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(fields)

if __name__ == "__main__":
    prices = get_prices_by_link(LINK)
    prices_without_outliers = remove_outliers(prices)

# Price rounded to fit normal currency usage
    print("The average price of a", item, "on eBay is $", round(get_average(prices_without_outliers), 2))

    save_to_file(prices)

# Creating a script to run Python file every day at 3pm CST
def run_script():
    subprocess.run(['python', 'eBay Price Averaging Tool.py'])

# Defining the time to run the script (3 PM CST)
def schedule_job():
    cst_timezone = pytz.timezone('US/Central')
    cst_now = datetime.now(cst_timezone)
    schedule.every().day.at('15:00').do(run_script).tag('daily_job')
    print(f'Scheduled daily job at {cst_now.strftime("%Y-%m-%d %H:%M:%S %Z")} CST')

schedule_job()

# Continuous loop to run the scheduler
while True:
    schedule.run_pending()
    time.sleep(60)  # Check every minute