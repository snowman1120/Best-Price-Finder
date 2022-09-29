"""
This module handles operations regarding web scraping.
"""
import datetime
from product import Product
from similarity_checker import is_similar
import requests
from datetime import date
from bs4 import BeautifulSoup
import pymongo
import os
import dotenv
from bson.objectid import ObjectId
from get_proxy import get_proxy
import logging
logging.basicConfig(filename='amazon-scraper.log', level=logging.DEBUG, format="%(name)s:%(levelname)s:%(asctime)s:%(message)s")


def scrape_data(key:str, count:int,sample_item:Product, page:int=1) :
    """
    Extracts the urls, product titles and prices from Amazon website for given search term for given count.<br>
     Returns list containing dictionaries of format : {'url':<str>, 'title' : <str> , 'price' : <float>}
    :param key: The search term used to search on Amazon website.
    :param count: The number of results required.
    :param page: Page number of search results.
    :return: List of dictionaries containing url, title and price of the products.
    """

    ####### get mongodb details ########

    # load the environment variables
<<<<<<< HEAD
    try:
        dotenv.load_dotenv()
        user = os.getenv('USER')
        passwd = os.getenv('PASSWD')

        # connect to the mongodb database
        client = pymongo.MongoClient(
            f"mongodb+srv://{user}:{passwd}@cluster0.x6statp.mongodb.net/?retryWrites=true&w=majority")

        db_name = "Data_amazon"
        db = client[db_name]

        table_name = sample_item.url
        if len(table_name) >= 255:
            table_name = key
        table = db[table_name]
    except Exception as e:
        logging.exception(e)
        return
=======
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
>>>>>>> 85367af577aa29a8d9b9b8c3d326608e1cbe234b

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

    proxies = get_proxy()

    key = key.replace(' ', '+')

    counter = 0
    titles = []             # stores titles of products to avoid duplicates
    finished = False

    try :
        while True:
            data = []  # to store the results of this page
            url = f"https://www.amazon.in/s?k={key}&page={page}&crid=308S42405947R&qid=1664363653&sprefix=%2Caps%2C179&ref=sr_pg_{page}"

            products_page = None
            for proxy in proxies:
                try :
                    products_page = requests.get(url, headers=HEADERS, proxies=proxy)
                    break
                except :
                    continue

            if products_page == None:
                logging.exception("Proxy not available currently. Please try again after some time.")
                return

            soup = BeautifulSoup(products_page.content, "html.parser")

            search_class1 = "a-section a-spacing-small a-spacing-top-small"
            search_class2 = "a-section a-spacing-small puis-padding-left-small puis-padding-right-small"
            search_class3 = "a-section a-spacing-small puis-padding-left-micro puis-padding-right-micro"

            final_tags = []
            tags = soup.find_all('div', attrs={'class': search_class1})
            final_tags += tags
            tags = soup.find_all('div', attrs={'class': search_class2})
            final_tags += tags
            tags = soup.find_all('div', attrs={'class': search_class3})
            final_tags += tags

            for tag in final_tags[1:]:
                try :
                   title = tag.find('h2').span.string
                   url = tag.find('h2').a.get('href')
                   url = f"https://www.amazon.com{url}"
                except Exception as e:
                    logging.exception(e)
                    continue

                # don't insert duplicate entries....
                if title not in titles:
                    try :
                        new_item = Product(url)
                        new_item.title = title
                        data.append(new_item)
                        titles.append(title)
                        counter += 1
                    except Exception as e:
                        logging.exception(e)
                        continue

            logging.info(f"{len(data)} no. of items added..")

            # check if we have extracted the given number of records
            if counter+len(data) >= count:
                logging.info(f"Required results obtained : {count}")
                data = data[0:count-counter]
                for item in data:
                    new_product = is_similar(sample_item, item)
                    if new_product != False:
                        logging.info("Adding %s to database..." %new_product.title)
                        table.insert_one({
                            'url':new_product.url,
                            'title' : new_product.title,
                            'price' : new_product.price
                        })
                        logging.info("Product inserted successfully.")
                client.close()
                logging.info("\nScraping process complete.")
                return data

            # check if this is the last page of the search results
            if soup.find('div', attrs={'class': 'a-section a-text-center s-pagination-container'}) == None :
                logging.info("This is the last page...")
                logging.info(f"{len(data)} no. of items extracted...")
                finished = True
            else :
                logging.info("Going to next page....")
                page = page + 1

            for item in data:
                try :
                    new_product = is_similar(sample_item, item)
                except Exception as e:
                    logging.exception(e)
                    continue
                if new_product != False:
                    table.insert_one({
                        'url': new_product.url,
                        'title': new_product.title,
                        'price': new_product.price})
            if finished :
                break

        client.close()
        logging.info("\nScraping process complete.")
        return data

    except Exception as e:
        logging.exception(e)

def update_db(db_name, table_name):
    logging.info(f"\nStarting update for {db_name}.{table_name}...")
    # load the environment variables
    dotenv.load_dotenv()
    user = os.getenv('USER')
    passwd = os.getenv('PASSWD')

    # connect to the mongodb database
    client = pymongo.MongoClient(
        f"mongodb+srv://{user}:{passwd}@cluster0.x6statp.mongodb.net/?retryWrites=true&w=majority")

    db = client[db_name]
    table = db[table_name]

    cursor = table.find({})
    for document in cursor:
        try :
            new_product = Product(document['url'])
            new_product.get_title()
            new_product.get_price()
            table.update_one(
                { 'url' : new_product.url},
                { '$set' : {'title' : new_product.title, 'price' : new_product.price}}
            )

        except (requests.exceptions.MissingSchema , requests.exceptions.ConnectionError) :
            table.delete_one({'_id' : ObjectId(document['_id'])})
            logging.info("Document deleted...")
            continue
        except Exception as e:
            logging.exception(e)

    logging.info("\nUpdate complete.")



"""url5 = "https://www.amazon.com/16-Core-32-Thread-Unlocked-Processor-Motherboard/dp/B09M3R1Z72"
url = "https://www.amazon.com/SanDisk-2TB-Extreme-Portable-SDSSDE81-2T00-G25/dp/B08GV4YYV7?th=1"
url3 = 'https://www.amazon.com/AT-DL72219-2-Handset-Cordless-Unsurpassed/dp/B088B1Y75K/ref=sr_1_46?keywords=phone&qid' \
       '=1664287424&qu=eyJxc2MiOiI5LjIwIiwicXNhIjoiOC43MCIsInFzcCI6IjcuOTEifQ%3D%3D&sr=8-46&th=1 '
sample = Product(url5)
sample.get_title()
sample.get_description()

scrape_data("ryzen motherboard", 100, sample)
"""
#update_db('Data_amazon', 'https://www.amazon.com/SanDisk-2TB-Extreme-Portable-SDSSDE81-2T00-G25/dp/B08GV4YYV7?th=1')
