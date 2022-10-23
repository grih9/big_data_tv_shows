import csv

from connection_data import MONGO_HOST, MONGO_PORT, MONGO_DB
from wrappers.MongoConnector import MongoConnector


def write_tv_shows_data(file):
    mongo = MongoConnector(MONGO_HOST, MONGO_PORT, MONGO_DB)

    with open(file, 'r', newline='', encoding="utf-8") as shows_file:
        reader = csv.reader(shows_file)
        headers = next(reader)
        for row in reader:
            print("Считывание ", row[0])
            mongo.insert_tv_show(*row)