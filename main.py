from analyze_dataset.scv_analyzer import write_tv_shows_data
from constants import SHOWS_FILE

if __name__ == '__main__':
    write_tv_shows_data(SHOWS_FILE)
    #scrap_shows(0)
    # ssh = paramiko.SSHClient()
    # ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # ssh.connect(hostname=SSH_HOST, username=SSH_USERNAME, pkey="./key.pem")
    # print("Connected")
    # server = SSHTunnelForwarder(
    #     (SSH_HOST, 22),
    #     ssh_username=SSH_USERNAME,
    #     ssh_pkey="./key.pem",
    #     remote_bind_address=(LOCAL_HOST, LOCAL_PORT),
    #     local_bind_address=(LOCAL_HOST, LOCAL_PORT),
    # )
    #
    # server.start()
    #
    # headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0'}
    # r = requests.get('http://127.0.0.1:5000', headers=headers).content
    # print(r)
    # server.stop()
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
