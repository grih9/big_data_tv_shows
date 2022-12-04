import os

from flask import render_template, jsonify, request


def main_api_channels_1(mongo):
    data_get = request.get_json(force=True)

    print(data_get)
    if data_get["Countryv"] == "Все":
        shows = mongo.get_shows(condition={"auditory": {"$gte": data_get["Reviewsv"]}})
                                           #"date_start": {"$gte": data_get["Minv"], "$lte": data_get["Maxv"]}})
    else:
        shows = mongo.get_shows(condition={"auditory": {"$gte": data_get["Reviewsv"]}, "country": data_get["Countryv"]})

    x_values = [elem["channel"] for elem in shows]
    x_list = list(set(x_values))
    y_values = [x_values.count(elem) for elem in x_list]
    sorted_x = list(sorted(x_list, key=lambda x: y_values[x_list.index(x)]))[::-1]
    if len(x_list) > 30:
        val = y_values[x_list.index(sorted_x[30])]
        x_values = []
        for elem in shows:
            x_v = elem["channel"]
            if y_values[x_list.index(x_v)] > val:
                x_values.append(x_v)
        x_list = list(set(x_values))
        y_values = [x_values.count(elem) for elem in x_list]
        sorted_x = list(sorted(x_list, key=lambda x: y_values[x_list.index(x)]))[::-1]

    source = dict(
        x=x_list,
        top=y_values,
        channel=x_list,
        serials=y_values,
        sorted_x=sorted_x
        )
    return jsonify(source)


def main_api_channels_2(mongo):
    data_get = request.get_json(force=True)

    print(data_get)
    if data_get["Countryv"] == "Все":
        shows = mongo.get_shows(condition={"auditory": {"$gte": data_get["Reviewsv"]}})
                                           #"date_start": {"$gte": data_get["Minv"], "$lte": data_get["Maxv"]}})
    else:
        shows = mongo.get_shows(condition={"auditory": {"$gte": data_get["Reviewsv"]}, "country": data_get["Countryv"]})

    x_values = [elem["channel"] for elem in shows]
    x_list = list(set(x_values))
    x_list2 = list(set(x_values))
    y_values = [x_values.count(elem) for elem in x_list]
    y_values2ch = [x_values.count(elem) for elem in x_list2]
    y_values2 = [sum([show["auditory"] if show["channel"] == elem else 0 for show in shows]) for elem in x_list2]
    sorted_x2 = list(sorted(x_list2, key=lambda x: y_values2[x_list2.index(x)]))[::-1]
    y_values2av = [int(y_values2[i] / y_values2ch[i]) if y_values[i] != 0 else 0 for i in range(len(y_values))]
    if len(x_list2) > 30:
        val2 = y_values2[x_list2.index(sorted_x2[30])]
        x_values2 = []
        for elem in shows:
            x_v = elem["channel"]
            if y_values2[x_list2.index(x_v)] > val2:
                x_values2.append(x_v)
        x_list2 = list(set(x_values2))
        y_values = [x_values.count(elem) for elem in x_list2]
        y_values2 = [sum([show["auditory"] if show["channel"] == elem else 0 for show in shows]) for elem in x_list2]
        sorted_x2 = list(sorted(x_list2, key=lambda x: y_values2[x_list2.index(x)]))[::-1]
        y_values2ch = [x_values2.count(elem) for elem in x_list2]
        y_values2av = [
            int(sum([show["auditory"] if show["channel"] == elem else 0 for show in shows]) / x_values2.count(elem))
            if x_values2.count(elem) != 0 else 0
            for elem in x_list2]

    source = dict(
        x=x_list2,
        top=y_values2,
        channel=x_list2,
        auditory=y_values2,
        serials=y_values2ch,
        average=y_values2av,
        sorted_x=sorted_x2
    )

    return jsonify(source)


def main_api_channels_3(mongo):
    data_get = request.get_json(force=True)

    print(data_get)
    if data_get["Countryv"] == "Все":
        shows = mongo.get_shows(condition={"auditory": {"$gte": data_get["Reviewsv"]}})
                                           #"date_start": {"$gte": data_get["Minv"], "$lte": data_get["Maxv"]}})
    else:
        shows = mongo.get_shows(condition={"auditory": {"$gte": data_get["Reviewsv"]}, "country": data_get["Countryv"]})

    x_values = [elem["channel"] for elem in shows]

    x_list = list(set(x_values))
    x_list2 = list(set(x_values))
    x_list3 = list(set(x_values))

    y_values = [x_values.count(elem) for elem in x_list]
    y_values2 = [sum([show["auditory"] if show["channel"] == elem else 0 for show in shows]) for elem in x_list2]
    y_values3 = [int(y_values2[i] / y_values[i]) if y_values[i] != 0 else 0 for i in range(len(y_values))]
    y_values3ch = [x_values.count(elem) for elem in x_list3]
    y_values3aud = [sum([show["auditory"] if show["channel"] == elem else 0 for show in shows]) for elem in x_list3]

    sorted_x = list(sorted(x_list, key=lambda x: y_values[x_list.index(x)]))[::-1]
    sorted_x2 = list(sorted(x_list2, key=lambda x: y_values2[x_list2.index(x)]))[::-1]
    sorted_x3 = list(sorted(x_list3, key=lambda x: y_values3[x_list3.index(x)]))[::-1]

    if len(x_list) > 30:
        val = y_values[x_list.index(sorted_x[30])]
        val2 = y_values2[x_list2.index(sorted_x2[30])]
        val3 = y_values3[x_list3.index(sorted_x3[30])]
        x_values = []
        x_values2 = []
        x_values3 = []
        for elem in shows:
            x_v = elem["channel"]
            if y_values[x_list.index(x_v)] > val:
                x_values.append(x_v)
            if y_values2[x_list2.index(x_v)] > val2:
                x_values2.append(x_v)
            if y_values3[x_list3.index(x_v)] > val3:
                x_values3.append(x_v)
        x_list = list(set(x_values))
        x_list2 = list(set(x_values2))
        x_list3 = list(set(x_values3))
        y_values = [x_values.count(elem) for elem in x_list]
        y_values2 = [sum([show["auditory"] if show["channel"] == elem else 0 for show in shows]) for elem in x_list2]
        y_values3 = [int(sum([show["auditory"] if show["channel"] == elem else 0 for show in shows]) / x_values3.count(elem))
                     if x_values3.count(elem) != 0 else 0
                     for elem in x_list3]
        sorted_x3 = list(sorted(x_list3, key=lambda x: y_values3[x_list3.index(x)]))[::-1]
        y_values3ch = [x_values3.count(elem) for elem in x_list3]
        y_values3aud = [sum([show["auditory"] if show["channel"] == elem else 0 for show in shows]) for elem in x_list3]

    source = dict(
        x=x_list3,
        top=y_values3,
        channel=x_list3,
        auditory=y_values3aud,
        serials=y_values3ch,
        average=y_values3,
        sorted_x=sorted_x3
    )
    return jsonify(source)


def main_api_years_1(mongo):
    data_get = request.get_json(force=True)

    print(data_get)

    years = [year for year in range(data_get["Minv"], data_get["Maxv"] + 1)]

    if data_get["Countryv"] == "Все":
        y_values_start = [len(mongo.get_shows(condition={"auditory": {"$gte": data_get["Reviewsv"]},
                                                         "date_start": {"$regex": str(year)}}))
                          for year in years]
        y_values_end = [len(mongo.get_shows(condition={"auditory": {"$gte": data_get["Reviewsv"]},
                                                       "date_end": {"$regex": str(year)}}))
                        for year in years]
    else:
        y_values_start = [len(mongo.get_shows(condition={"auditory": {"$gte": data_get["Reviewsv"]},
                                                         "date_start": {"$regex": str(year)},
                                                         "country": data_get["Countryv"]}))
                          for year in years]
        y_values_end = [len(mongo.get_shows(condition={"auditory": {"$gte": data_get["Reviewsv"]},
                                                       "date_end": {"$regex": str(year)},
                                                       "country": data_get["Countryv"]}))
                        for year in years]
    source = dict(
        x=years,
        y_start=y_values_start,
        y_end=y_values_end,
        years=years,
        start=y_values_start,
        end=y_values_end
    )
    return jsonify(source)


def main_api_years_2(mongo):
    data_get = request.get_json(force=True)

    print(data_get)

    years = [year for year in range(data_get["Minv"], data_get["Maxv"] + 1)]

    if data_get["Countryv"] == "Все":
        data = [mongo.get_shows(condition={"auditory": {"$gte": data_get["Reviewsv"]},
                                                         "date_start": {"$regex": str(years[i])}})
                for i in range(len(years))]
    else:
        data = [mongo.get_shows(condition={"auditory": {"$gte": data_get["Reviewsv"]},
                                           "date_start": {"$regex": str(years[i])},
                                           "country": data_get["Countryv"]})
                for i in range(len(years))]

    print(000)
    y_values_start = [len(show) for show in data]
    print(123)
    y = [sum([show["auditory"] for show in data[i]]) for i in range(len(years))]
    print(456)
    source = dict(
        x=years,
        y=y,
        auditory=y,
        shows=y_values_start,
        average=[int(y[i] / y_values_start[i]) if y_values_start[i] != 0 else 0 for i in range(len(y))]
    )

    return jsonify(source)


def main_api_years_3(mongo):
    data_get = request.get_json(force=True)

    print(data_get)

    years = [year for year in range(data_get["Minv"], data_get["Maxv"] + 1)]

    if data_get["Countryv"] == "Все":
        data = [mongo.get_shows(condition={"auditory": {"$gte": data_get["Reviewsv"]},
                                           "date_start": {"$regex": str(years[i])}})
                for i in range(len(years))]
    else:
        data = [mongo.get_shows(condition={"auditory": {"$gte": data_get["Reviewsv"]},
                                           "date_start": {"$regex": str(years[i])},
                                           "country": data_get["Countryv"]})
                for i in range(len(years))]

    y_values_start = [len(show) for show in data]
    print(123)
    y = [sum([show["auditory"] for show in data[i]]) for i in range(len(years))]
    print(456)
    rating = [sum([show["rating_myshows"] for show in data[i]]) / y_values_start[i] if y_values_start[i] != 0 else None
              for i in range(len(years))]
    print(789)
    source = dict(
        x=years,
        y=rating,
        auditory=y,
        rating=rating,
        shows=y_values_start
    )

    return jsonify(source)
