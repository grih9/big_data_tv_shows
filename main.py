from constants import NUMBER_OF_EPISODES
from scrapper.episodes import scrap_episodes
from scrapper.shows import scrap_shows
from multiprocessing import Process


if __name__ == '__main__':
    #scrap_shows(0)

    p1 = Process(target=scrap_episodes, args=("episodes.csv", 42721, int(1 * NUMBER_OF_EPISODES / 24) - 1,))
    p2 = Process(target=scrap_episodes, args=("episodes2.csv", int(1 * NUMBER_OF_EPISODES / 24) - 1, int(2 * NUMBER_OF_EPISODES / 24) - 1,))
    p3 = Process(target=scrap_episodes, args=("episodes3.csv", int(2 * NUMBER_OF_EPISODES / 24) - 1, int(3 * NUMBER_OF_EPISODES / 24) - 1,))
    #p3 = Process(target=scrap_episodes, args=("episodes3.csv", 6228627, int(3 * NUMBER_OF_EPISODES / 6) - 1,))
    p4 = Process(target=scrap_episodes, args=("episodes4.csv", int(3 * NUMBER_OF_EPISODES / 24) - 1, int(4 * NUMBER_OF_EPISODES / 24),))
    #p4 = Process(target=scrap_episodes, args=("episodes4.csv", 12335049, int(3 * NUMBER_OF_EPISODES / 3),))

    p1.start()
    p2.start()
    p3.start()
    p4.start()
    p1.join()
    p2.join()
    p4.join()
