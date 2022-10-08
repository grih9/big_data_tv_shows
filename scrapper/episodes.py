import csv

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from datetime import datetime

from selenium.webdriver.common.by import By

from constants import DRIVER_PATH, BASE_URL

# 49833  42140
#START_ID = 98573


def scrap_episodes(file, start_id=0, end_id=18500000):
    service = Service(DRIVER_PATH)
    driver = webdriver.Chrome(service=service)
    episode_data = {"episode_id": 0, "show": "", "episode_title": "", "season": 0, "episode": 0, "auditory": 0,
                    "auditory_rate": 0.0, "rating_myshows": 0.0, "rating_count": 0, "episode_length": 0, "date": "",
                    "number_of_comments": 0}

    print(f"Сборка эпизодов со {start_id=} по {end_id=}")
    time_start = datetime.now()
    try:
        write_file = open(file, "x")
        csv_writer = csv.writer(write_file)
        if file == "episodes.csv":
            csv_writer.writerow(list(episode_data.keys()))
        write_file.close()
    except Exception as e:
        print("Файл уже создан")

    with open(file, "a", encoding="utf-8", newline='') as write_file:
        csv_writer = csv.writer(write_file)
        for id in range(start_id, end_id):
            counter = 0
            is_true = False
            while not is_true and counter < 3:
                try:
                    driver.get(BASE_URL + f"/episode/{id}/")
                    elements = driver.find_elements(By.XPATH,
                                                    './/div[@class="title title__primary title__left title__space-m"]//h1[@class="title__main"]')
                    if len(elements) > 0:
                        print(f"Нет данных по {id=}")
                        counter = 10
                        continue
                    table = driver.find_elements(By.XPATH,
                                                 './/div[@class="episode-details__section border"]//table//tr[@class="info-row"]')
                    episode_data["auditory"] = 0
                    episode_data["auditory_rate"] = 0.0
                    episode_data["date"] = None
                    episode_data["episode_length"] = None
                    for elem in table:
                        elem_name = elem.text.split(":")[0]
                        elem_data = elem.text.split(":")[1]
                        if elem_name == "Всего просмотров":
                            auditory = elem_data.lstrip().split(" ")
                            auditory_rate = auditory[-1].replace("%", "")
                            episode_data["auditory"] = int("".join(auditory[:-1]))
                            episode_data["auditory_rate"] = float(auditory_rate)
                            if episode_data["auditory"] <= 3:
                                print(f"Мало данных для {id=}, {episode_data['auditory']=}")
                                episode_data["auditory"] = None
                                episode_data["auditory_rate"] = None
                                break
                        elif elem_name == "Даты выхода":
                            episode_data["date"] = elem_data.lstrip(" ").split(" ")[0]
                        elif elem_name == "Длительность":
                            episode_data["episode_length"] = elem_data.lstrip(" ")

                    if episode_data["auditory"] is None:
                        counter = 10
                        continue
                    if not episode_data["episode_length"]:
                        print(f"Нет длительности эпизода для {id=}")
                    if not episode_data["date"]:
                        print(f"Нет дат для {id=}")

                    episode_data["episode_id"] = id
                    title = driver.find_elements(By.XPATH, './/div//h1[@class="title__main"]')[0].text.split("—")
                    episode_data["episode_title"] = title[1]
                    if "special" in title[0]:
                        episode_data["episode"] = title[0].split(" ")[1]
                        episode_data["season"] = int(title[0].split(" ")[0].replace("s", ""))
                    else:
                        episode_data["episode"] = int(title[0].split("e")[1])
                        episode_data["season"] = int(title[0].split("e")[0].replace("s", ""))


                    show = driver.find_elements(By.XPATH, './/div[@class="breadcrumbs__item"][3]/a')
                    episode_data["show"] = show[0].text

                    try:
                        rating_myshows = driver.find_elements(By.XPATH, './/div[@class="ShowRating-value"]//div')
                        episode_data["rating_myshows"] = float(rating_myshows[0].text)
                        episode_data["rating_count"] = int(rating_myshows[1].text.replace("( ", "").replace(" )", "").replace(" ", ""))
                    except Exception:
                        episode_data["rating_count"] = 0
                        episode_data["rating_myshows"] = 0
                        print(f"Нет оценок для {id=}")

                    try:
                        comments_number = driver.find_elements(By.XPATH, './/div//h3//span')
                        episode_data["number_of_comments"] = int(comments_number[0].text)
                    except Exception:
                        episode_data["rating_count"] = 0
                        print(f"Нет комментариев для {id=}")
                    is_true = True
                except Exception:
                    counter += 1
                    print(f"Повторная попытка для {id=}")
            if is_true:
                csv_writer.writerow(list(episode_data.values()))

    print(f"Сбор эпизодов окончен со {start_id=} по {end_id}")
    time_end = datetime.now()
    print(f"Затрачено времени: {time_end - time_start}")
