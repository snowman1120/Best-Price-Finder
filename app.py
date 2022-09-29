import logging
from flask import Flask, render_template, request, jsonify
import threading
import dotenv, os
import pymongo
import ssl
from scraper import scrape_data, update_db
from product import Product
logging.basicConfig(filename='amazon-scraper.log', level=logging.DEBUG, format="%(name)s:%(levelname)s:%(asctime)s:%(message)s")


app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/results', methods=['POST'])
def show_results():
    if request.method == 'POST':
        try :
            try :
                req_data = request.get_json()
                key = req_data['key']
                sample_url = req_data['sample_url']
                duration = int(req_data['duration'])
            except :
                key = request.form['key']
                sample_url = request.form['sample_url']
                duration = int(request.form['duration'])

                # load the environment variables
            dotenv.load_dotenv()
            user = os.getenv('USER')
            passwd = os.getenv('PASSWD')

            # connect to the mongodb database
            client = pymongo.MongoClient(
<<<<<<< HEAD
                f"mongodb+srv://{user}:{passwd}@cluster0.x6statp.mongodb.net/?retryWrites=true&w=majority",
                                        tls=True, tlsAllowInvalidCertificates=True)
=======
                f"mongodb+srv://{user}:{passwd}@cluster0.x6statp.mongodb.net/?retryWrites=true&w=majority&ssl_cert_reqs=ssl.CERT_NONE")
>>>>>>> 85367af577aa29a8d9b9b8c3d326608e1cbe234b

            db_name = "Job_info"
            duration = f"{str(duration)}_hrs"
            db = client[db_name]
            table = db[duration]

            table.insert_one({'url' : sample_url})
            logging.info(f"Inserted url {sample_url} in Job_info database...")
            client.close()

            sample_item = Product(sample_url)
            sample_item.get_title()
            sample_item.get_description()

            logging.info(f"\nStarting process for scraping data for url:{sample_item.url} and key:{key}..." )

            # scraping for 1000 records
            new_thread = threading.Thread(target=scrape_data, args=(key, 1000, sample_item))
            new_thread.start()
            new_thread.join()

            return jsonify(message="Job created successfully.")
        except Exception as e:
            return str(e)


@app.route('/trigger', methods=['POST'])
def trigger_function():
    if request.method == 'POST':
        data = request.get_json()
        duration = int(data['duration'])
        duration = f"{duration}_hrs"
        searches = get_job_info("Job_info", duration)

        if len(searches) == 0:
            return jsonify(message="No job to run")

        # start the process of saving the data in background
        new_thread = threading.Thread(target=update_data, args=[searches])
        new_thread.start()
        new_thread.join()

        return jsonify(message="Update begun...")



def get_job_info(db_name,table_name):
    # load the environment variables
    dotenv.load_dotenv()
    user = os.getenv('USER')
    passwd = os.getenv('PASSWD')

    # connect to the mongodb database
    client = pymongo.MongoClient(
        f"mongodb+srv://{user}:{passwd}@cluster0.x6statp.mongodb.net/?retryWrites=true&w=majority&ssl_cert_reqs=ssl.CERT_NONE")

    db = client[db_name]
    table = db[table_name]
    cursor = table.find({})
    results = []
    for document in cursor:
        results.append({'url' : document['url']})

    return results


def update_data(searches):
    for search in searches:
        new_thread = threading.Thread(target=update_db, args = ("Data_amazon", search['url']))
        new_thread.start()
        new_thread.join()



if __name__ == '__main__' :
    app.run()