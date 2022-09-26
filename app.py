import logging
from flask import Flask, render_template, request, jsonify
import threading
import dotenv, os
import pymongo
from scraper import scrape_data
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
                count = int(req_data['count'])
                duration = int(req_data['duration'])
            except :
                key = request.form['key']
                count = int(request.form['count'])
                duration = int(request.form['duration'])

                # load the environment variables
            dotenv.load_dotenv()
            user = os.getenv('USER')
            passwd = os.getenv('PASSWD')

            # connect to the mongodb database
            client = pymongo.MongoClient(
                f"mongodb+srv://{user}:{passwd}@cluster0.x6statp.mongodb.net/?retryWrites=true&w=majority&ssl_cert_reqs=ssl.CERT_NONE")

            db_name = "Job_info"
            duration = f"{str(duration)}_hrs"
            db = client[db_name]
            table = db[duration]

            table.insert_one({'key': key, 'count':count})

            client.close()


            return jsonify(message="Job created successfully.")
        except Exception as e:
            return jsonify(message=str(e))


@app.route('/trigger', methods=['POST'])
def trigger_function():
    if request.method == 'POST':
        data = request.get_json()
        duration = int(data['duration'])
        duration = f"{str(duration)}_hrs"
        searches = get_job_info("Job_info", duration)

        if len(searches) == 0:
            return jsonify(message="No job to run")

        # start the process of saving the data in background
        new_thread = threading.Thread(target=save_data, args=[searches])
        new_thread.start()

        return jsonify(message="Saving begun...")



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
        results.append({'key':document['key'], 'count':document['count']})


    return results


def save_data(searches):
    for search in searches:
        key = search['key']
        count = search['count']

        # start the process of saving the data in background
        new_thread = threading.Thread(target=scrape_data, args=(key, count))
        new_thread.start()
        new_thread.join()



if __name__ == '__main__' :
    app.run()