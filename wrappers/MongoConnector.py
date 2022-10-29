from pymongo import MongoClient

from connection_data import MONGO_SHOWS_COLLECTION


class MongoConnector:
    def __init__(self, host, port, username, password, database_name):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self._client = MongoClient(host=self.host, port=self.port, username=self.username, password=self.password)
        self._db = self._client[database_name]

    def get_client(self):
        return self._client

    def get_collection(self, collection_name):
        return self._db.get_collection(collection_name)

    def insert_tv_show(self, show_id, title, original_title, status, auditory, rating_myshows, rating_count,
                       rating_kinopoisk, kinopoisk_count, rating_imdb, imdb_count, country, genre, channel,
                       total_length, episode_length, dates, actors, seasons, episodes_in_season):
        collection = self.get_collection(MONGO_SHOWS_COLLECTION)
        #collection = self.get_collection("test")
        data = list(collection.find({"show_id": int(show_id)}))
        if len(data) > 0:
            assert len(data) == 1
            print(f"[ОШИБКА] id {show_id} уже есть в базе")
            return
        episodes = []
        actors = actors.replace("[", "").replace("]", "").replace(" '", "").replace("'", "").split(",")
        episodes_in_season = episodes_in_season.replace("[", "").replace("]", "").replace(" '", "").replace("'", "").split(",")
        genre = genre.replace("[", "").replace("]", "").replace(" '", "").replace("'", "").split(",")
        country = country.replace("[", "").replace("]", "").replace(" '", "").replace("'", "").split(",")
        rating_kinopoisk = None if rating_kinopoisk == "" else float(rating_kinopoisk)
        kinopoisk_count = None if kinopoisk_count == "" else int(kinopoisk_count)
        rating_imdb = None if rating_imdb == "" else float(rating_imdb)
        imdb_count = None if imdb_count == "" else int(imdb_count)
        for season in range(int(seasons)):
            season_data = {"season": season + 1, "number_of_episodes": int(episodes_in_season[season]),
                           "episodes": [None for _ in range(int(episodes_in_season[season]))]}
            episodes.append(season_data)
        collection.insert_one({"show_id": int(show_id), "title": title, "original_title": original_title,
                               "status": status, "auditory": int(auditory), "rating_myshows": float(rating_myshows),
                               "rating_count": int(rating_count),
                               "rating_percent": round((float(rating_count) / int(auditory)) * 100, 2),
                               "rating_kinopoisk": rating_kinopoisk, "kinopoisk_count": kinopoisk_count,
                               "rating_imdb": rating_imdb, "imdb_count": imdb_count,
                               "country": country[0].split("/"), "genre": genre, "channel": channel,
                               "total_length": total_length, "episode_length": episode_length,
                               "date_start": dates.split(" — ")[0], "date_end": dates.split(" — ")[1],
                               "actors": actors, "number_of_seasons": int(seasons), "episodes": episodes})

    def get_shows(self, condition, sort=None):
        collection = self.get_collection(MONGO_SHOWS_COLLECTION)
        if sort is not None:
            data = list(collection.find(condition).sort(*sort))
        else:
            data = list(collection.find(condition))
        return data

    def update_episodes(self, episode_id, show_title, episode_title, season, episode, auditory, auditory_rate,
                        rating_myshows, rating_count, episode_length, date, number_of_comments, show_id=0):

        collection = self.get_collection(MONGO_SHOWS_COLLECTION)
        #collection = self.get_collection("test")
        if show_id == 0:
            #print("[ПРЕДУПРЕЖДЕНИЕ], не передан show_id для ", episode_id)
            data = list(collection.find({"title": show_title, "auditory": {"$gte": int(auditory)}}))
            if len(data) > 1:
                print("[ОШИБКА] Больше одного шоу подходит под параметры. ", len(data), show_title, auditory)
                return
            elif len(data) == 0:
                print(f"[ОШИБКА] Ни одного шоу не подходит под параметры. {show_title}, {auditory}")
                return
        else:
            data = list(collection.find({"show_id": int(show_id)}))
            if len(data) == 0:
                print("[ОШИБКА] Ниодного шоу не подходит под параметры. ", show_id)
                return

        episodes_data = data[0]["episodes"]
        if "special" in episode:
            print("[ПРЕДУПРЕЖДЕНИЕ] Special (skip): ", episode, show_title)
            return
        season = int(season)
        episode = int(episode)
        try:
            #if episodes_data[season - 1]["episodes"][episode - 1] is not None:
            tmp = episodes_data[season - 1]["episodes"][episode - 1]
                #print(f"[ПРЕДУПРЕЖДЕНИЕ] id {episode_id} уже есть в базе")
                #return
        except:
            print(f"[ОШИБКА] {episode_id}. {len(episodes_data)} сезона "
                  f"{len(episodes_data[season-1]['episodes']) if season-1 < len(episodes_data) else None} эпизод, "
                  f"требуется {season} сезон, {episode} эпизод")
            return
        date = None if date == "" else date
        episode_title = episode_title.lstrip(" ")
        episode_date = {"episode_id": int(episode_id), "title": episode_title, "show": show_title,
                        "season": season, "episode": episode, "release_date": date, "auditory": int(auditory),
                        "auditory_rate": float(auditory_rate), "rating_myshows": float(rating_myshows),
                        "rating_count": int(rating_count),
                        "rating_percent": round((float(rating_count) / int(auditory)) * 100, 2) if int(auditory) != 0 else None,
                        "episode_length": episode_length,
                        "number_of_comments": int(number_of_comments)}

        episodes_data[season - 1]["episodes"][episode - 1] = episode_date

        if show_id == 0:
            ret = collection.update_one({"title": show_title},
                                        {"$set": {f"episodes": episodes_data}})
            if ret.modified_count != 1:
                print(f"[ОШИБКА] элемент не обновился для {episode_id}, {show_title}, {show_id}, {ret.modified_count}")
        else:
            ret = collection.update_one({"show_id": int(show_id)},
                                        {"$set": {f"episodes": episodes_data}})
            if ret.modified_count != 1:
                print(f"[ОШИБКА] элемент не обновился для {episode_id}, {show_title}, {show_id}, {ret.modified_count}")
