# Shopee Top 100 Sales per Category Scraper

This code scrapes the top 100 sales per category in [Shopee](https://shopee.ph/ "Shopee Philippines"). The scraped data is stored on csv files named after the categories.

Dependencies:
* pandas
* requests
* beautifulsoup4
* selenium (NOTE: install chrome web driver to be able to run selenium, specificy the path in the ``` .env ``` file if needed by your OS)
* dotenv

Notes:
* If the scraper stops because of a timeout, uncomment everything in ``` main.py ``` and run it again.