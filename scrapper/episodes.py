import csv

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from datetime import datetime

from selenium.webdriver.common.by import By

from connection_data import MONGO_HOST, MONGO_PORT, MONGO_USERNAME, MONGO_PASSWORD, MONGO_DB
from constants import DRIVER_PATH, BASE_URL, SELENOID_CAPABILITIES, SELENOID_URL
from wrappers.MongoConnector import MongoConnector


# 49833  42140
#START_ID = 98573


def get_episode_data(driver, id, auditory_min=3):
    episode_data = {"episode_id": 0, "show": "", "episode_title": "", "season": 0, "episode": 0, "auditory": 0,
                    "auditory_rate": 0.0, "rating_myshows": 0.0, "rating_count": 0, "episode_length": 0, "date": "",
                    "number_of_comments": 0}
    elements = driver.find_elements(By.XPATH,
                                    './/div[@class="title title__primary title__left title__space-m"]//h1[@class="title__main"]')
    if len(elements) > 0:
        print(f"Нет данных по {id=}")
        counter = 10
        return episode_data, False, counter
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
            if episode_data["auditory"] <= auditory_min:
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
        return episode_data, False, counter
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
        episode_data["rating_count"] = int(
            rating_myshows[1].text.replace("( ", "").replace(" )", "").replace(" ", ""))
    except Exception:
        episode_data["rating_count"] = 0
        episode_data["rating_myshows"] = 0
        print(f"Нет оценок для {id=}")

    try:
        comments_number = driver.find_elements(By.XPATH, './/div//h3//span')
        episode_data["number_of_comments"] = int(comments_number[0].text)
    except Exception:
        episode_data["number_of_comments"] = 0
        print(f"Нет комментариев для {id=}")
    return episode_data, True, 0


def scrap_episodes(file, start_id=0, end_id=18500000):
    # service = Service(DRIVER_PATH)
    # driver = webdriver.Chrome(service=service)
    driver = webdriver.Remote(
        command_executor=SELENOID_URL,
        desired_capabilities=SELENOID_CAPABILITIES)
    episode_data = {"episode_id": 0, "show": "", "episode_title": "", "season": 0, "episode": 0, "auditory": 0,
                    "auditory_rate": 0.0, "rating_myshows": 0.0, "rating_count": 0, "episode_length": 0, "date": "",
                    "number_of_comments": 0}

    print(f"Сборка эпизодов со {start_id=} по {end_id=}")
    # time_start = datetime.now()
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
                    episode_data, is_true, counter = get_episode_data(driver, id)
                except Exception:
                    counter += 1
                    print(f"Повторная попытка для {id=}")
            if is_true:
                csv_writer.writerow(list(episode_data.values()))

    # print(f"Сбор эпизодов окончен со {start_id=} по {end_id}")
    # time_end = datetime.now()
    # print(f"Затрачено времени: {time_end - time_start}")


def scrap_seasons_episodes_from_show(show_id, file_name, driver):
    try:
        file = open(file_name, "x")
        csv_writer = csv.writer(file)
        file.close()
    except Exception as e:
        print("Файл уже создан")

    with open(file_name, "a", encoding="utf-8", newline='') as write_file:
        csv_writer = csv.writer(write_file)
        driver.get(BASE_URL + f"/{show_id}/")
        seasons = driver.find_elements(By.XPATH, './/div[@id="episodes"]//h3[@class="title__main"]//a')
        seasons = [season.get_attribute("href") for season in seasons]
        for i in range(len(seasons) - 1, -1, -1):
            driver.get(seasons[i])
            episodes = driver.find_elements(By.XPATH, './/div[@class="GridItem"]/a')
            episodes = [episode.get_attribute("href") for episode in episodes]
            for k in range(len(episodes)):
                driver.get(episodes[k])
                ep_id = int(episodes[k].split("/")[-2])
                data, is_true, _ = get_episode_data(driver, ep_id, auditory_min=0)
                assert is_true
                data["season"] = len(seasons) - i if len(seasons) - i < data["season"] else data["season"]
                data["episode"] = (k + 1) if isinstance(data["episode"], int) and (k + 1) < data["episode"] else data["episode"]
                data["show_id"] = show_id
                if int(data["auditory"]) < int(data["rating_count"]):
                    print(f"[ПРЕДУПРЕЖДЕНИЕ] Число просмотров {data['auditory']} меньше числа оценок {data['rating_count']} для {ep_id}")
                csv_writer.writerow(list(data.values()))


def scrap_episodes_from_db(pr_type, auditory=1000, condition=None):
    if condition is None:
        condition = {"auditory": {"$gte": auditory}, "episodes.episodes.$": {"$ne": None}}
    mongo = MongoConnector(MONGO_HOST, MONGO_PORT, MONGO_USERNAME, MONGO_PASSWORD, MONGO_DB)
    #shows = mongo.get_shows(condition={"auditory": {"$gte": auditory}, "episodes.episodes": None}, sort=["auditory", -1])
    shows = mongo.get_shows(condition=condition, sort=["auditory", -1])
    #shows = mongo.get_shows(condition={"show_id": 74693}, sort=["auditory", -1])
    shows1 = shows[:len(shows)//3]
    shows2 = shows[len(shows)//3:2*len(shows)//3]
    shows3 = shows[2*len(shows)//3:]
    if pr_type == 1:
        # service = Service(DRIVER_PATH)
        # driver = webdriver.Chrome(service=service)
        driver = webdriver.Remote(
            command_executor=SELENOID_URL,
            desired_capabilities=SELENOID_CAPABILITIES)
        print(len(shows1))
        for show in shows1:
            show_id = show["show_id"]
            #scrap_seasons_episodes_from_show(show_id, "episodes5.csv", driver)
            scrap_seasons_episodes_from_show(show_id, "episodes8.csv", driver)
    elif pr_type == 2:
        # service = Service(DRIVER_PATH)
        # driver = webdriver.Chrome(service=service)
        driver = webdriver.Remote(
            command_executor=SELENOID_URL,
            desired_capabilities=SELENOID_CAPABILITIES)
        print(len(shows2))
        for show in shows2:
            show_id = show["show_id"]
            scrap_seasons_episodes_from_show(show_id, "episodes9.csv", driver)
            #scrap_seasons_episodes_from_show(show_id, "episodes6.csv", driver)
    elif pr_type == 3:
        # service = Service(DRIVER_PATH)
        # driver = webdriver.Chrome(service=service)
        driver = webdriver.Remote(
            command_executor=SELENOID_URL,
            desired_capabilities=SELENOID_CAPABILITIES)
        print(len(shows3))
        for show in shows3:
            show_id = show["show_id"]
            scrap_seasons_episodes_from_show(show_id, "episodes10.csv", driver)
            #scrap_seasons_episodes_from_show(show_id, "episodes7.csv", driver)

