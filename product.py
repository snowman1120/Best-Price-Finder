import requests
from datetime import date
from bs4 import BeautifulSoup
from get_proxy import get_proxy
import logging
logging.basicConfig(filename='amazon-scraper.log', level=logging.DEBUG, format="%(name)s:%(levelname)s:%(asctime)s:%(message)s")



class Product :
    """
    attributes: url, title, price, description, image_url
    """
    # create a user agent
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip',
        'DNT': '1',  # Do Not Track Request Header
        'Connection': 'close'
    }
    proxy_ips = get_proxy()

    def __init__(self, url):
        self.url = url
        self.title = None
        self.price = None
        self.description = None

        product_page = None
        for proxy in Product.proxy_ips:
            try :
                product_page = requests.get(self.url, headers=Product.HEADERS, proxies=proxy)
                break
            except :
                continue
        if product_page == None:
            raise Exception("Proxy ip unavailable. Please try again after some time.")

        soup = BeautifulSoup(product_page.content, "html.parser")

        self.soup = soup

    def get_title(self):
        product_page = requests.get(self.url, headers=Product.HEADERS, proxies=Product.proxy_ips[1])
        soup = BeautifulSoup(product_page.content, "html.parser")
        title = None

        #title = self.soup.find('div', attrs={'id' : 'title_feature_div'}).div.h1.span.string
        try :
            title = soup.find('div', attrs={'id': 'title_feature_div'}).div.h1.span.string
            title = title.strip()
            self.title = title
        except Exception as e:
            raise Exception(soup.prettify())

        if title == None:
            #raise Exception("Could not extract the title for %s" %self.url)
            #raise Exception(str(self.soup))
            raise Exception("Titles not found...")

    def get_price(self):
        product_page = requests.get(self.url, headers=Product.HEADERS, proxies=Product.proxy_ips[0])
        soup = BeautifulSoup(product_page.content, "html.parser")

        #price_tag = self.soup.find('div', attrs={'id' : 'apex_desktop'})
        price_tag = soup.find('div', attrs={'id' : 'apex_desktop'})
        price_tag = price_tag.find('span', attrs={'class':'a-offscreen'})
        if price_tag == None:
            price = "NA"
        else :
            price = float(price_tag.string.replace('$', ''))
        self.price = price

    def get_description(self):
        """product_page = requests.get(self.url, headers=HEADERS)
        soup = BeautifulSoup(product_page.content, "html.parser")"""

        description = "NA"
        # two formats of product description exist, hence try finding both
        try :
            description = self.soup.find('div', attrs={'id':'productDescription'}).p.span.string
        except :
            desc_tags = self.soup.find_all('div' , attrs={'class':'celwidget aplus-module 3p-module-b aplus-standard'})
            description = ''
            for tag in desc_tags:
                # there are two possible types

                # find texts in <p> tags
                p_tags = tag.find_all('p', attrs= {'class' : 'a-spacing-base'})
                for p_tag in p_tags:
                    if p_tag.string != None:
                        description += p_tag.string

                # find texts in <ul> <li> tags
                list_tags = tag.find_all('span', attrs={'class':'a-list-item'})
                for list_tag in list_tags:
                    if list_tag.string != None:
                        description += list_tag.string


        self.description = description

    def get_info(self):
        """
        Gives information about the products in the JSON format
        :return: returns dictionary containing 'title', 'price', 'url' and 'description' as keys
        """
        return {
            'url' : self.url,
            'title' : self.title,
            'price' : self.price,
            'description' : self.description
        }


url = "https://www.amazon.com/SanDisk-2TB-Extreme-Portable-SDSSDE81-2T00-G25/dp/B08GV4YYV7?th=1"
url2 = "https://www.amazon.com/Joylifeboard-iPhone-Protective-Military-Rubber/dp/B0BBPWD4NH/ref=sr_1_54_sspa?keywords" \
       "=phone&qid=1664287424&qu=eyJxc2MiOiI5LjIwIiwicXNhIjoiOC43MCIsInFzcCI6IjcuOTEifQ%3D%3D&sr=8-54-spons&spLa" \
       "=ZW5jcnlwdGVkUXVhbGlmaWVyPUEzMlI4T0NWWFZZSkZHJmVuY3J5cHRlZElkPUEwNjIzODc3MllJNVFWMldIVzE5TiZlbmNyeX" \
       "B0ZWRBZElkPUEwMTE3MTI1NVdJUlVIUlkyTFRMJndpZGdldE5hbWU9c3BfYnRmJmFjdGlvbj1jbGlja1JlZGlyZWN0JmRvT" \
       "m90TG9nQ2xpY2s9dHJ1ZQ&th=1 "
url3 = 'https://www.amazon.com/AT-DL72219-2-Handset-Cordless-Unsurpassed/dp/B088B1Y75K/ref=sr_1_46?keywords=phone&qid' \
       '=1664287424&qu=eyJxc2MiOiI5LjIwIiwicXNhIjoiOC43MCIsInFzcCI6IjcuOTEifQ%3D%3D&sr=8-46&th=1 '
url4 = "https://www.amazon.com/AT-CL82307-Expandable-Cordless-Answering/dp/B0735Q3Z6T/ref=sr_1_36?keywords=phone&qid" \
       "=1664287424&qu=eyJxc2MiOiI5LjIwIiwicXNhIjoiOC43MCIsInFzcCI6IjcuOTEifQ%3D%3D&sr=8-36&th=1 "
new_product = Product(url)
new_product.get_title()
new_product.get_price()
new_product.get_description()
print(new_product.get_info())
#pr = Product("https://www.sfsfd.org")"""