from connection_data import MONGO_HOST, MONGO_PORT, MONGO_DB, MONGO_PASSWORD, MONGO_USERNAME
from wrappers.MongoConnector import MongoConnector


def update_channels(old_value, new_value):
    mongo = MongoConnector(MONGO_HOST, MONGO_PORT, MONGO_USERNAME, MONGO_PASSWORD, MONGO_DB)

    data = mongo.get_shows_by_channel(old_value)
    for show in data:
        mongo.update_show_param(show["show_id"], "channel", new_value)


if __name__ == '__main__':
    update_channels("1 + 1", "1+1")
    update_channels("CTC", "СТС")
    update_channels("STS", "СТС")
    update_channels("HTB", "НТВ")
    update_channels("NTV", "НТВ")
    update_channels("ТВЦ", "ТВ Центр")
    update_channels("Россия 1", "Россия-1")
