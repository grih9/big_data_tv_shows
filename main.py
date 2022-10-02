import csv

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from datetime import datetime

from selenium.webdriver.common.by import By

START_ID = 1

DRIVER_PATH = './driver/chromedriver'
service = Service(DRIVER_PATH)
driver = webdriver.Chrome(service=service)

BASE_URL = "https://myshows.me/view"
show_data = {"show_id": 0, "title": "", "original_title": "", "status": "", "auditory": 0, "rating_myshows": 0.0,
             "rating_count": 0, "rating_kinopoisk": 0.0, "kinopoisk_count": 0, "rating_imdb": 0.0, "imdb_count": 0,
             "country": [], "genre": [], "channel": "", "total_length": 0, "episode_length": 0, "dates": "",
             "actors": [], "seasons": 0, "episodes_in_season": []}
print("Сборка сериалов")
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
    for id in range(START_ID, 200000):
        driver.get(BASE_URL + f"/{id}/")
        elements = driver.find_elements(By.XPATH,
                                        './/div[@class="title title__primary title__left title__space-m"]//h1[@class="title__main"]')
        if len(elements) > 0:
            print(f"Нет данных по {id=}")
            continue
        table = driver.find_elements(By.XPATH,
                                     './/div[@class="ShowDetails__section"]//table//tr[@class="info-row"]')
        auditory = table[4].text.split(": ")[1].split(" из ")
        show_data["auditory"] = int(auditory[0].replace(" ", ""))
        assert table[4].text.split(":")[0] == "Смотрящих", f"{id=}"
        if show_data["auditory"] < 10:
            print(f"Мало данных для {id=}, {show_data['auditory']=}")
            continue

        show_data["country"] = table[1].text.split(": ")[1].split(",")
        assert table[1].text.split(": ")[0] == "Страна", f"{id=}"
        show_data["genre"] = table[2].text.split(": ")[1].split(",")
        assert table[2].text.split(": ")[0] == "Жанры", f"{id=}"
        show_data["dates"] = table[0].text.split(": ")[1]
        assert table[0].text.split(": ")[0] == "Даты выхода", f"{id=}"
        try:
            show_data["channel"] = table[3].text.split(": ")[1]
            assert table[3].text.split(": ")[0] == "Канал", f"{id=}"
        except Exception as e:
            print(f"Нет канала для {id=}")
            show_data["channel"] = None
            assert table[3].text == "Канал:", f"{id=}"
        show_data["total_length"] = table[5].text.split(": ")[1]
        assert table[5].text.split(": ")[0] == "Общая длительность", f"{id=}"
        show_data["episode_length"] = table[6].text.split(": ")[1]
        assert table[6].text.split(": ")[0] == "Длительность серии", f"{id=}"

        if len(table) >= 8 and table[7].text.split(": ")[0] == "Рейтинг IMDB":
            rating_imdb = table[7].text.split(": ")[1]
            show_data["rating_imdb"] = float(rating_imdb.split(" из ")[0])
            show_data["imdb_count"] = int("".join(rating_imdb.split(" из ")[1].split(" ")[1:]))
        elif len(table) >= 8 and table[7].text.split(": ")[0] == "Рейтинг Кинопоиска":
            rating_kinopoisk = table[7].text.split(": ")[1]
            show_data["rating_kinopoisk"] = float(rating_kinopoisk.split(" из ")[0])
            show_data["kinopoisk_count"] = int("".join(rating_kinopoisk.split(" из ")[1].split(" ")[1:]))

        if len(table) >= 9 and table[8].text.split(": ")[0] == "Рейтинг IMDB":
            rating_imdb = table[8].text.split(": ")[1]
            show_data["rating_imdb"] = float(rating_imdb.split(" из ")[0])
            show_data["imdb_count"] = int("".join(rating_imdb.split(" из ")[1].split(" ")[1:]))
        elif len(table) >= 9 and table[8].text.split(": ")[0] == "Рейтинг Кинопоиска":
            rating_kinopoisk = table[8].text.split(": ")[1]
            show_data["rating_kinopoisk"] = float(rating_kinopoisk.split(" из ")[0])
            show_data["kinopoisk_count"] = int("".join(rating_kinopoisk.split(" из ")[1].split(" ")[1:]))

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

        rating_count = driver.find_elements(By.XPATH, './/div[@class="ShowRating-value"]//div//span[@class="Counter"]')[0]
        show_data["rating_count"] = int(rating_count.text.replace("( ", "").replace(" )", "").replace(" ", ""))

        show_all = driver.find_elements(By.XPATH, './/div[@class="show-characters__show-all"]//span')
        if len(show_all) != 0:
            show_all[0].click()

        actors_list = driver.find_elements(By.XPATH, './/div[@class="show-characters__list"]//a')
        if len(actors_list) > 0:
            for actor in actors_list:
                actor_data = actor.text.split("\n")
                if len(actor_data) == 2:
                    show_data["actors"].append(actor_data[0])
                elif len(actor_data) == 3:
                    show_data["actors"].append(actor_data[1])
                else:
                    print(f"ОШИБКА АКТЕР, {id=}")
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

print("Сбор сериалов окончен")
time_end = datetime.now()
print(f"Затрачено времени: {time_end-time_start}")
# time_start = datetime.now()
# for episode in range(1, 10000000):
#     driver.get(BASE_URL + f"/episode/{episode}/")
#     print(f"Opened {episode=}")
# time_end = datetime.now()
# print(time_end-time_start)
