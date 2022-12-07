from multiprocessing import Process

from analyze_dataset.scv_analyzer import write_tv_shows_data, write_episodes_from_file
from constants import SHOWS_FILE
from scrapper.episodes import scrap_episodes_from_db, scrap_episodes

if __name__ == '__main__':
    """
        write shows from file to db
    """
    #write_tv_shows_data(SHOWS_FILE)

    """
        write episodes to db
    """
    #for file in ["datasets/episodes.csv", "datasets/episodes2.csv", "datasets/episodes3.csv", "datasets/episodes4.csv"]:
    # for file in ["datasets/episodes5.csv", "datasets/episodes6.csv", "datasets/episodes7.csv"]:
    #     print(f"Считывание файла {file}")
    #     write_episodes_from_file(file)
    # p1 = Process(target=write_episodes_from_file, args=("datasets/episodes8.csv",))
    # p2 = Process(target=write_episodes_from_file, args=("datasets/episodes9.csv",))
    # p3 = Process(target=write_episodes_from_file, args=("datasets/episodes10.csv",))
    # p1.start()
    # p2.start()
    # p3.start()
    # p1.join()
    # p2.join()
    # p3.join()

    """
        scrap shows
    """
    # scrap_shows(0)

    """
        scrap episodes
    """

    #scrap_episodes_from_db(1000)

    # p1 = Process(target=scrap_episodes_from_db, args=(1, 899,))
    # p2 = Process(target=scrap_episodes_from_db, args=(2, 899,))
    # p3 = Process(target=scrap_episodes_from_db, args=(3, 899,))
    # p1 = Process(target=scrap_episodes_from_db, args=(1, 80, {"country": "Россия", "auditory": {"$gte": 80},
    #                                                           "episodes.episodes.$": {"$ne": None}},))
    # p2 = Process(target=scrap_episodes_from_db, args=(2, 80, {"country": "Россия", "auditory": {"$gte": 80},
    #                                                           "episodes.episodes.$": {"$ne": None}},))
    # p3 = Process(target=scrap_episodes_from_db, args=(3, 80, {"country": "Россия", "auditory": {"$gte": 80},
    #                                                           "episodes.episodes.$": {"$ne": None}},))
    p1 = Process(target=scrap_episodes_from_db, args=(1, 500, {"auditory": {"$gte": 500},
                                                               "episodes.episodes.rating_count": 0},))
    p2 = Process(target=scrap_episodes_from_db, args=(2, 500, {"auditory": {"$gte": 500},
                                                               "episodes.episodes.rating_count": 0},))
    p3 = Process(target=scrap_episodes_from_db, args=(3, 500, {"auditory": {"$gte": 500},
                                                               "episodes.episodes.rating_count": 0},))
    p1.start()
    p2.start()
    p3.start()
    p1.join()
    p2.join()
    p3.join()

    #Process(scrap_episodes("episodes5.csv", 17676067, 17676075,))
    """
            scrap episodes parallel
    """
    # p1 = Process(target=scrap_episodes, args=("episodes.csv", 42721, int(1 * NUMBER_OF_EPISODES / 24) - 1,))
    # p2 = Process(target=scrap_episodes, args=("episodes2.csv", int(1 * NUMBER_OF_EPISODES / 24) - 1, int(2 * NUMBER_OF_EPISODES / 24) - 1,))
    # p3 = Process(target=scrap_episodes, args=("episodes3.csv", int(2 * NUMBER_OF_EPISODES / 24) - 1, int(3 * NUMBER_OF_EPISODES / 24) - 1,))
    # #p3 = Process(target=scrap_episodes, args=("episodes3.csv", 6228627, int(3 * NUMBER_OF_EPISODES / 6) - 1,))
    # p4 = Process(target=scrap_episodes, args=("episodes4.csv", int(3 * NUMBER_OF_EPISODES / 24) - 1, int(4 * NUMBER_OF_EPISODES / 24),))
    # #p4 = Process(target=scrap_episodes, args=("episodes4.csv", 12335049, int(3 * NUMBER_OF_EPISODES / 3),))
    #
    # p1.start()
    # p2.start()
    # p3.start()
    # p4.start()
    # p1.join()
    # p2.join()
    # p4.join()
