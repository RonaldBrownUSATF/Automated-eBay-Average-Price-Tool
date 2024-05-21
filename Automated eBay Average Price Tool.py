# Automated eBay Average Price Tool

from bs4 import BeautifulSoup
import requests 
import numpy as np
import csv
from datetime import datetime
import schedule
import time
import pytz
import subprocess

LINK = "https://www.ebay.com/sch/i.html?_from=R40&_trksid=p4432023.m570.l1313&_nkw=16lb+shotput&_sacat=0"
# Edit LINK for the web address and search applicable to desired item to track
# Web address hardcoded into script for scheduled use

# Can be changed to ask users to input web address
# LINK = input("Please enter the web address of the eBay listing you've search: ")
# Web address based on user input, best used with scheduler and prompts turned off
# To use: comment out lines 1 - 118, use lines 120 - 167

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
    print("The average price of a",item, "on eBay is $", round(get_average(prices_without_outliers), 2))
    print("The lowest price is $",round(min(prices_without_outliers), 2))
    print("The highest price is $",round(max(prices_without_outliers), 2))
    save_to_file(prices)

# Creating a script to run Python file based on user input
def run_script():
    subprocess.run(['python', 'Automated eBay Average Price Tool.py'])

# Function to schedule the job
def schedule_job(run_time):
    cst_timezone = pytz.timezone('US/Central')
    cst_now = datetime.now(cst_timezone)
    schedule.every().day.at(run_time).do(run_script).tag('daily_job')
    print(f'Scheduled daily job at {cst_now.strftime("%Y-%m-%d")} {run_time} CST')

# Prompting user to schedule the script
while True:
    choice = input("Would you like to schedule this script to run? (yes/no): ").lower()
    if choice == 'yes':
        break
    elif choice == 'no':
        print("Script not scheduled to run.")
        exit()
    else:
        print("Invalid choice. Please enter 'yes' or 'no'.")

# Prompting user to select time
def select_time():
    while True:
        run_time = input("Enter the time to run the script in 'HH:MM' format (e.g., 15:00 for 3 PM): ")
        try:
            datetime.strptime(run_time, '%H:%M')
            return run_time
        except ValueError:
            print("Invalid time format. Please enter time in 'HH:MM' format.")

selected_time = select_time()
schedule_job(selected_time)

# Continuous loop to run the scheduler
while True:
    schedule.run_pending()
    time.sleep(60)  # Check every minute

"""LINK = input("Please enter the web address of the eBay listing you've search: ")

def get_prices_by_link(link):
    r = requests.get(link)
    page_parse = BeautifulSoup(r.text, 'html.parser')
    search_results = page_parse.find("ul",{"class":"srp-results"}).find_all("li",{"class":"s-item"})

    item_prices = []

    for result in search_results:
        price_as_text = result.find("span",{"class":"s-item__price"}).text
        if "to" in price_as_text:
            continue
        price = float(price_as_text[1:].replace(",",""))
        item_prices.append(price)
    return item_prices

response = requests.get(LINK)
html_content = response.text

soup = BeautifulSoup(html_content, "html.parser")
query_param = soup.find("input", {"id": "gh-ac"})
if query_param:
    item = query_param.get("value")
else:
    item = ""

def remove_outliers(prices, m=2):
    data = np.array(prices)
    return data[abs(data - np.mean(data)) < m * np.std(data)]

def get_average(prices):
    return np.mean(prices)

def save_to_file(prices):
    fields=[datetime.today().strftime("%B-%D-%Y"),np.around(get_average(prices),2)]
    with open('prices.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(fields)

if __name__ == "__main__":
    prices = get_prices_by_link(LINK)
    prices_without_outliers = remove_outliers(prices)

    print("The average price of a",item, "on eBay is $", round(get_average(prices_without_outliers), 2))
    print("The lowest price is $",round(min(prices_without_outliers), 2))
    print("The highest price is $",round(max(prices_without_outliers), 2))
    save_to_file(prices)"""
