from pymongo import MongoClient

from connection_data import MONGO_SHOWS_COLLECTION


class MongoConnector():
    def __init__(self, host, port, database_name):
        self.host = host
        self.port = port
        self._client = MongoClient(host=self.host, port=self.port)
        self._db = self._client[database_name]

    def get_client(self):
        return self._client

    def get_collection(self, collection_name):
        return self._db.get_collection(collection_name)

    def insert_tv_show(self, show_id, title, original_title, status, auditory, rating_myshows, rating_count,
                       rating_kinopoisk, kinopoisk_count, rating_imdb, imdb_count, country, genre, channel,
                       total_length, episode_length, dates, actors, seasons, episodes_in_season):
        collection = self.get_collection(MONGO_SHOWS_COLLECTION)

        episodes = []
        actors = actors.replace("[", "").replace("]", "").replace(" '", "").replace("'", "").split(",")
        episodes_in_season = episodes_in_season.replace("[", "").replace("]", "").replace(" '", "").replace("'", "").split(",")
        genre = genre.replace("[", "").replace("]", "").replace(" '", "").replace("'", "").split(",")
        country = country.replace("[", "").replace("]", "").replace(" '", "").replace("'", "").split(",")
        rating_kinopoisk = None if rating_kinopoisk is "" else float(rating_kinopoisk)
        kinopoisk_count = None if kinopoisk_count is "" else int(kinopoisk_count)
        rating_imdb = None if rating_imdb is "" else float(rating_imdb)
        imdb_count = None if imdb_count is "" else int(imdb_count)
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

    def update_episodes(self, show_title, episode_title, season, episode, auditory, auditory_rate, rating_myshows,
                        rating_count, episode_length, date, number_of_comments):

        collection = self.get_collection(MONGO_SHOWS_COLLECTION)
        data = collection.find({"title": show_title})
        assert len(data) == 1
        episode = {}
        actors = actors.replace("[", "").replace("]", "").replace(" '", "").replace("'", "").split(",")
        episodes_in_season = episodes_in_season.replace("[", "").replace("]", "").replace(" '", "").replace("'", "").split(",")
        genre = genre.replace("[", "").replace("]", "").replace(" '", "").replace("'", "").split(",")
        country = country.replace("[", "").replace("]", "").replace(" '", "").replace("'", "").split(",")
        rating_kinopoisk = None if rating_kinopoisk is "" else float(rating_kinopoisk)
        kinopoisk_count = None if kinopoisk_count is "" else int(kinopoisk_count)
        rating_imdb = None if rating_imdb is "" else float(rating_imdb)
        imdb_count = None if imdb_count is "" else int(imdb_count)
        for season in range(int(seasons)):
            season_data = {"season": season + 1, "number_of_episodes": int(episodes_in_season[season]),
                           "episodes": [None for _ in range(int(episodes_in_season[season]))]}
            episodes.append(season_data)
        collection.update_one({"title": show_title}, {"$set": {epi}})