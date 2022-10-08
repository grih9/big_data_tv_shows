import csv

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from datetime import datetime

from selenium.webdriver.common.by import By

from constants import DRIVER_PATH, BASE_URL

# 49833  42140
START_ID = 98573

def scrap_shows(start_id=START_ID):
    service = Service(DRIVER_PATH)
    driver = webdriver.Chrome(service=service)
    show_data = {"show_id": 0, "title": "", "original_title": "", "status": "", "auditory": 0, "rating_myshows": 0.0,
                 "rating_count": 0, "rating_kinopoisk": 0.0, "kinopoisk_count": 0, "rating_imdb": 0.0, "imdb_count": 0,
                 "country": [], "genre": [], "channel": "", "total_length": 0, "episode_length": 0, "dates": "",
                 "actors": [], "seasons": 0, "episodes_in_season": []}
    print(f"Сборка сериалов со {start_id=}")
    time_start = datetime.now()
    try:
        file = open("tvshows.csv", "x")
        csv_writer = csv.writer(file)
        csv_writer.writerow(list(show_data.keys()))
        file.close()
    except Exception as e:
        print("Файл уже создан")

    with open("tvshows.csv", "a", encoding="utf-8", newline='') as write_file:
        csv_writer = csv.writer(write_file)
        for id in range(start_id, 200000):
            driver.get(BASE_URL + f"/{id}/")
            elements = driver.find_elements(By.XPATH,
                                            './/div[@class="title title__primary title__left title__space-m"]//h1[@class="title__main"]')
            if len(elements) > 0:
                print(f"Нет данных по {id=}")
                continue
            table = driver.find_elements(By.XPATH,
                                         './/div[@class="ShowDetails__section"]//table//tr[@class="info-row"]')
            show_data["auditory"] = 0
            show_data["genre"] = None
            show_data["country"] = None
            show_data["dates"] = None
            show_data["channel"] = None
            show_data["total_length"] = None
            show_data["episode_length"] = None
            show_data["rating_imdb"] = None
            show_data["rating_kinopoisk"] = None
            show_data["imdb_count"] = None
            show_data["kinopoisk_count"] = None
            for elem in table:
                elem_name = elem.text.split(":")[0]
                elem_data = elem.text.split(":")[1]
                if elem_name == "Смотрящих":
                    auditory = elem_data.split(" из ")
                    show_data["auditory"] = int(auditory[0].replace(" ", ""))
                    if show_data["auditory"] <= 3:
                        print(f"Мало данных для {id=}, {show_data['auditory']=}")
                        show_data["auditory"] = None
                        break
                elif elem_name == "Жанры":
                    show_data["genre"] = elem_data.lstrip(" ").split(",")

                elif elem_name == "Страна":
                    show_data["country"] = elem_data.lstrip(" ").split(",")

                elif elem_name == "Даты выхода":
                    show_data["dates"] = elem_data.lstrip(" ")
                elif elem_name == "Канал":
                    try:
                        show_data["channel"] = elem_data.lstrip(" ")
                    except Exception as e:
                        show_data["channel"] = None
                elif elem_name == "Общая длительность":
                    show_data["total_length"] = elem_data.lstrip(" ")
                elif elem_name == "Длительность серии":
                    show_data["episode_length"] = elem_data.lstrip(" ")
                elif elem_name == "Рейтинг IMDB":
                    rating_imdb = elem_data.lstrip(" ")
                    show_data["rating_imdb"] = float(rating_imdb.split(" из ")[0])
                    show_data["imdb_count"] = int("".join(rating_imdb.split(" из ")[1].split(" ")[1:]))
                elif elem_name == "Рейтинг Кинопоиска":
                    rating_kinopoisk = elem_data.lstrip(" ")
                    show_data["rating_kinopoisk"] = float(rating_kinopoisk.split(" из ")[0])
                    show_data["kinopoisk_count"] = int("".join(rating_kinopoisk.split(" из ")[1].split(" ")[1:]))
            if show_data["auditory"] is None:
                continue
            if not show_data["channel"]:
                print(f"Нет канала для {id=}")
            if not show_data["rating_imdb"]:
                print(f"Нет оценки IMDB для {id=}")
            if not show_data["rating_kinopoisk"]:
                print(f"Нет оценки Кинопоиска для {id=}")
            if not show_data["episode_length"]:
                print(f"Нет длительности эпизода для {id=}")
            if not show_data["total_length"]:
                print(f"Нет общей длительности для {id=}")
            if not show_data["genre"]:
                print(f"Нет жанров для {id=}")
            if not show_data["country"]:
                print(f"Нет стран для {id=}")
            if not show_data["dates"]:
                print(f"Нет дат для {id=}")

            show_data["show_id"] = id
            title = driver.find_elements(By.XPATH,
                                         './/div[@itemprop="name"]//h1[@class="title__main"]')[0]
            show_data["title"] = title.text

            original_title = driver.find_elements(By.XPATH, './/div[@class="ShowDetails-original"]')
            if len(original_title) == 0:
                show_data["original_title"] = ""
            else:
                show_data["original_title"] = original_title[0].text

            status = driver.find_elements(By.XPATH, './/div[@itemprop="name"]//h1[@class="title__main"]//div')[0]
            show_data["status"] = status.accessible_name

            rating_myshows = driver.find_elements(By.XPATH, './/div[@class="ShowRating-value"]//div')[0]
            show_data["rating_myshows"] = float(rating_myshows.text)

            try:
                rating_count = driver.find_elements(By.XPATH, './/div[@class="ShowRating-value"]//div//span[@class="Counter"]')[0]
                show_data["rating_count"] = int(rating_count.text.replace("( ", "").replace(" )", "").replace(" ", ""))
            except Exception:
                show_data["rating_count"] = 0
                print(f"Нет оценок для {id=}")

            show_all = driver.find_elements(By.XPATH, './/div[@class="show-characters__show-all"]//span')
            if len(show_all) != 0:
                show_all[0].click()

            actors_list = driver.find_elements(By.XPATH, './/div[@class="show-characters__list"]//a')
            show_data["actors"] = []
            if len(actors_list) > 0:
                for actor in actors_list:
                    actor_data = actor.text.split("\n")
                    if len(actor_data) == 2:
                        show_data["actors"].append(actor_data[0])
                    elif len(actor_data) == 3:
                        show_data["actors"].append(actor_data[1])
                    else:
                        print(f"ОШИБКА АКТЕР, {id=}")
                        show_data["actors"] = None
            else:
                show_data["actors"] = None
                print(f"Нет актеров для {id=}")

            seasons = driver.find_elements(By.XPATH, './/div[@id="episodes"]//h3[@class="title__main"]')
            show_data["seasons"] = len(seasons)
            show_data["episodes_in_season"] = []
            for season in seasons[::-1]:
                season_data = season.accessible_name.split(" сезон ")
                show_data["episodes_in_season"].append(season_data[1])

            csv_writer.writerow(list(show_data.values()))

    print(f"Сбор сериалов окончен со {start_id=}")
    time_end = datetime.now()
    print(f"Затрачено времени: {time_end - time_start}")
