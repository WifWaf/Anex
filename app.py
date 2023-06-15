from flask import Flask
from flask_cors import CORS
from flask import Response
from waitress import serve
import logging


# create the app
app = Flask(__name__)

# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///alch_test.db"
# initialize the app with the extension
CORS(app)

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')


@app.before_request
def basic_authentication():
    if request.method.lower() == 'options':
        return Response()


from views import *


if __name__ == '__main__':
    serve(app, host="localhost", port=5001)  # serve app on localhost only
    # context = ('cert.pem', 'key.pem')
    # app.run(debug=True, port=5001)  # or any other vacant port
    # app.run(host='192.168.1.213', port=4002, debug=False, ssl_context=context, threaded=True)
