from flask import Flask
import logging

app = Flask(__name__)

logging.basicConfig(filename='logs/poulailler-console.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

from app import routes
