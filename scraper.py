"""
This module handles operations regarding web scraping.
"""
import datetime

import requests
from datetime import date
from bs4 import BeautifulSoup
import pymongo
import os
import dotenv
import logging
logging.basicConfig(filename='amazon-scraper.log', level=logging.DEBUG, format="%(name)s:%(levelname)s:%(asctime)s:%(message)s")


def scrape_data(key:str, count:int, page:int=1) -> list:
    """
    Extracts the product titles and prices from Amazon website for given search term for given count.<br>
     Returns list containing dictionaries of format : {'title' : <str> , 'price' : <float>}
    :param key: The search term used to search on Amazon website.
    :param count: The number of results required.
    :param page: Page number of search results.
    :return: List of dictionaries containing title and price.
    """

    ####### get mongodb details ########

    current_date = str(date.today())
    current_time = datetime.datetime.now()
    current_time = str(current_time.strftime("%H:%M:%S"))

    # load the environment variables
    dotenv.load_dotenv()
    user = os.getenv('USER')
    passwd = os.getenv('PASSWD')

    # connect to the mongodb database
    client = pymongo.MongoClient(
        f"mongodb+srv://{user}:{passwd}@cluster0.x6statp.mongodb.net/?retryWrites=true&w=majority&ssl_cert_reqs=ssl.CERT_NONE")

    db_name = key.replace(' ', '_')     # remove the whitespaces
    db_name = f"{db_name}_{current_date}"

    db = client[db_name]

    table = db[current_time]

    #################################

    # create a user agent
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip',
        'DNT': '1',  # Do Not Track Request Header
        'Connection': 'close'
    }

    key = key.replace(' ', '+')

    data = []               # to store the results
    titles = []             # stores titles of products to avoid duplicates

    while True:
        url = f"https://www.amazon.com/s?k={key}&page={page}"

        products_page = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(products_page.content, "html.parser")

        tags = soup.find_all('div', attrs={'class' : 's-result-item s-asin sg-col-0-of-12 sg-col-16-of-20 sg-col '
                                                     's-widget-spacing-small sg-col-12-of-16'})
        search_class = "a-section a-spacing-small a-spacing-top-small"

        if len(tags) == 0:          # if the items are listed in grid-format
            tags = soup.find_all('div',
                        attrs={'class' : 'a-section a-spacing-small puis-padding-left-small puis-padding-right-small'})
            search_class = "a-section a-spacing-small puis-padding-left-small puis-padding-right-small"

        for tag in tags:
            temp = tag.find_next('div', attrs={'class':{search_class}})

            # some results may be due to ads or any other types of promotions, so don't include them
            try :
                title = temp.div.h2.a.span.string
                price = temp.find_next('div',
                            attrs={'class':'a-section a-spacing-none a-spacing-top-small s-price-instructions-style'}).\
                    div.a.span.span.string
            except Exception as e:
                logging.exception(e)
                continue

            if price == 'Limited time deal' :
                price_tag = temp.find_next('div', attrs={'class' : 'a-row a-size-base a-color-base'}).a.span.span.string
                price = price_tag

            try :
                price = float(price.replace('$', '').replace(',', ''))
            except :
                price = "NA"

            # don't insert duplicate entries....
            if title not in titles:
                new_item = {'title' : title, 'price' : price}
                data.append(new_item)
                titles.append(title)

        logging.info(f"{len(data)} no. of items added..")

        # check if we have extracted the given number of records
        if len(data) >= count:
            logging.info(f"Required results obtained : {count}")
            data = data[0:count]
            for item in data:
                table.insert_one(item)
            client.close()
            return data

        # check if this is the last page of the search results
        if soup.find('div', attrs={'class': 'a-section a-text-center s-pagination-container'}) == None :
            logging.info("This is the last page...")
            logging.info(f"{len(data)} no. of items extracted...")
            break
        else :
            logging.info("going to next page....")
            page = page + 1

    for item in data:
        table.insert_one(item)
    client.close()
    return data
