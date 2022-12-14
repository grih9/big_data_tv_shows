SHOWS_FILE = "datasets/tvshows.csv"
EPISODES_FILE = "datasets/episodes.csv"

DRIVER_PATH = 'driver/chromedriver'
#SELENOID_URL = 'http://127.0.0.1:4444/wd/hub' #SELECT FOR DEBUG WITHOUT CONTAINER
SELENOID_URL = 'http://172.17.0.3:4444/wd/hub'
SELENOID_CAPABILITIES = {
    "browserName": "chrome",
    "browserVersion": "100.0",
    "selenoid:options": {
        "enableVideo": False,
        "enableVNC": True,
        "sessionTimeout": "1m"
    }
}

BASE_URL = "https://myshows.me/view"

SHOW_DATA = {"show_id": 0, "title": "", "original_title": "", "status": "", "auditory": 0, "rating_myshows": 0.0,
             "rating_count": 0, "rating_kinopoisk": 0.0, "kinopoisk_count": 0, "rating_imdb": 0.0, "imdb_count": 0,
             "country": [], "genre": [], "channel": "", "total_length": 0, "episode_length": 0, "dates": "",
             "actors": [], "seasons": 0, "episodes_in_season": []}
NUMBER_OF_SHOWS = 90000
NUMBER_OF_EPISODES = 185000000

