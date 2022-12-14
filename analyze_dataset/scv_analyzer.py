import csv

from connection_data import MONGO_HOST, MONGO_PORT, MONGO_DB, MONGO_PASSWORD, MONGO_USERNAME
from wrappers.MongoConnector import MongoConnector


def write_tv_shows_data(file):
    mongo = MongoConnector(MONGO_HOST, MONGO_PORT, MONGO_USERNAME, MONGO_PASSWORD, MONGO_DB)

    with open(file, 'r', newline='', encoding="utf-8") as shows_file:
        reader = csv.reader(shows_file)
        headers = next(reader)
        for row in reader:
            if int(row[0]) % 100 == 0:
                print("Считывание ", row[0])
            mongo.insert_tv_show(*row)


def write_episodes_from_file(file):
    mongo = MongoConnector(MONGO_HOST, MONGO_PORT, MONGO_USERNAME, MONGO_PASSWORD, MONGO_DB)

    with open(file, 'r', newline='', encoding="utf-8") as shows_file:
        reader = csv.reader(shows_file)
        if "episodes.csv" in file:
            headers = next(reader)
            print(f"Файл {file}, пропуск элементов")
            for i in range(19500):
                next(reader)
        if "episodes2.csv" in file:
            print(f"Файл {file}, пропуск элементов")
            # for i in range(15000):
            #     next(reader)
        if "episodes3.csv" in file:
            print(f"Файл {file}, пропуск элементов")
            for i in range(29500):
                next(reader)
        print(f"Файл {file}, пропуск элементов")
        if "episodes5.csv" in file:
            print(f"Файл {file}, пропуск элементов")
            for i in range(64000):
                next(reader)
        if "episodes6.csv" in file:
            print(f"Файл {file}, пропуск элементов")
            for i in range(70000):
                next(reader)
        if "episodes7.csv" in file:
            print(f"Файл {file}, пропуск элементов")
            for i in range(75000):
                next(reader)
        for row in reader:
            if int(row[0]) % 10 == 0:
                print("Считывание ", row[0])
            mongo.update_episodes(*row)
        print("Конец считывания файла ", file)
