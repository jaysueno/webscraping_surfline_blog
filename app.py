# Import libraries/dependencies
import pandas as pd 
import os
import requests
from splinter import Browser
from bs4 import BeautifulSoup as bs 
import datetime as dt
import time
import pymongo

### Initialize PyMongo to work with MongoDB local server
conn = 'mongodb://localhost:27017'
client = pymongo.MongoClient(conn)

# Define database and collection
db = client.surfline_db
collection = db.news

# Define the Surfline blog page URL
url = 'https://www.surfline.com/surf-news'

# Retrive the page with the request module
response = requests.get(url)

# Convert the response to text to obtain the html
html = response.text

### We will use a Chrome browser to view and download the HTML contents of the website using the Splinter library
# Establish Chrome driver executable path. Make sure to dfine actual location on your drive.
executable_path = {'executable_path': 'C:/Users/jaysu/chromedriver'}

# Open a splinter browser
browser = Browser('chrome', **executable_path, headless=False)

# Visit the defined URL on your splinter browser
browser.visit(url)
# Give it time to load
time.sleep(5)

### We will use the BeautifulSoup Library to scrape and parse the HTML
# Create a BeautifulSoup object with the splinter broswer.html method to parse the html with 'html.parser' or 'lmxl' formats
soup = bs(browser.html, 'html.parser')

### Create a list of weblinks of each news article that we will iterate through
# Find all the image cards that hold the links to the stories with the BSoup object
news_links = soup.find_all('div', class_='quiver-feed-card__image')

# Print the number of articles
print(f'Number of stories {len(news_links)}')

### We now begin the scraping of the webpage with a for loop and uploading the data to a MongoDB database
# Begin for loop through the news_links list, create empty lists to populate scrape, and insert_one() to the collection at each iteration
for item in news_links:
    p_text = [] # the articles text contents
    tags_text = [] # the tags of the article
    date2 = []
    url = item.find('a')['href']
    browser.visit(url)
    time.sleep(1)
    soup1 = bs(browser.html, 'html.parser')
    title = soup1.find('h1').text # title of article
    p_copy = soup1.find_all('p')
    
    for copy in p_copy:
        p_text.append(copy.text)
   
    try:
        tags = soup1.find('ul', class_='sl-article-tags')
        for tag in tags.find_all('li'):
            tags_text.append(tag.text)
    except:
        print("No tags")

    try:
        element = soup1.find('div', class_='sl-editorial-author__details__date')
        date_update = element.text.split('.', maxsplit=1)
        date2 = date_update[0]
    except:
        print('No date')

    post = {
        'title': title,
        'p_text': p_text,
        'tags_text': tags_text,
        'date': date2
    }

    print(f'Scraped news article: {date2} {title}')
    print('--------------------------------')

    # Upload the scraped data into the MongoDB database
    collection.insert_one(post)


