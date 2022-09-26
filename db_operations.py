"""
This module includes operations to interact with the Mongodb database. Currently, it is not used in implementation yet.
"""

import pymongo
import os
import dotenv
import logging
logging.basicConfig(filename='amazon-scraper.log', level=logging.DEBUG, format="%(name)s:%(levelname)s:%(asctime)s:%(message)s")


def insert_data(table_name:str, data:list, db_name:str='Product_info') -> None:
    """
    Inserts the data in given database and table of Mongodb.
    :param table_name: Name of the table name
    :param data: List of dictionaries
    :param db_name: Database name. Default is 'Product_info'
    :return: None
    """

    # load the environment variables
    dotenv.load_dotenv()
    user = os.getenv('USER')
    passwd = os.getenv('PASSWD')

    # connect to the mongodb database
    client = pymongo.MongoClient(f"mongodb+srv://{user}:{passwd}@cluster0.x6statp.mongodb.net/?retryWrites=true&w=majority")

    db = client[db_name]

    table_name = table_name.replace(' ', '_')           # remove the whitespaces
    table = db[table_name]

    for document in data:
        table.insert_one(document)

    client.close()

