import math
import os

from bokeh.client import pull_session
from bokeh.events import PanEnd
from bokeh.embed import components, server_session
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Slider, CustomJS, Select, NumericInput, TextAreaInput
from bokeh.plotting import figure
from bokeh.resources import INLINE
from flask import Flask, render_template, jsonify, request

from connection_data import MONGO_HOST, MONGO_PORT, MONGO_USERNAME, MONGO_PASSWORD, MONGO_DB
from constants import SHOWS_FILE, EPISODES_FILE
from wrappers.MongoConnector import MongoConnector

app = Flask(__name__)

mongo = MongoConnector(MONGO_HOST, MONGO_PORT, MONGO_USERNAME, MONGO_PASSWORD, MONGO_DB)
DATA = mongo.get_shows_by_auditory(auditory=10)

dataset_shows = SHOWS_FILE
dataset_episodes = EPISODES_FILE
n_proceses = 1


@app.route('/dashboard/votes/imdb')
def graphs_imdb():
    source_imdb = ColumnDataSource()

    genre_list = ['All', 'Comedy', 'Sci-Fi', 'Action', 'Drama', 'War', 'Crime', 'Romance', 'Thriller', 'Music',
                  'Adventure', 'History', 'Fantasy', 'Documentary', 'Horror', 'Mystery', 'Family', 'Animation',
                  'Biography', 'Sport', 'Western', 'Short', 'Musical']
    controls = {
        "reviews": Slider(title="Минимальное число зрителей", value=10, start=10, end=100000, step=50, width=470),
        "info": TextAreaInput(title="Информация", value="Информация об оценках зрителей.\n\n"
                                                        "По горизонтали оценки выбранного источника (IMDB/Кинопоиск),\n"
                                                        "по вертикали оценки пользователей MyShows.\n"
                                                        "Выбор источника осуществляется с помощью выпадающего меню в правом верхнем углу.\n"
                                                        "С помошью ползунка определяется минимальное число зрителей, которые смотрят сериал "
                                                        "(по данным MyShows), для которых будет отмечена информация на графике",
                              width=470, rows=10, disabled=True)
    }

    controls_array = controls.values()

    callback = CustomJS(args=dict(source=source_imdb, controls=controls), code="""
            if (!window.full_data_save) {
                window.full_data_save = JSON.parse(JSON.stringify(source.data));
            }
            var full_data = window.full_data_save;
            var full_data_length = full_data.x.length;
            var new_data = { x: [], y: [], color: [], title_gr: [], genre: [], auditory: [] }
            for (var i = 0; i < full_data_length; i++) {
                if (full_data.auditory[i] === null)
                    continue;
                if (
                    full_data.auditory[i] > controls.reviews.value
                ) {
                    Object.keys(new_data).forEach(key => new_data[key].push(full_data[key][i]));
                }
            }
            source.data = new_data;
            source.change.emit();
        """)

    fig_imdb = figure(height=800, width=1080, tooltips=[("Title", "@title_gr"), ("Rating_myshows", "@y"),
                                                       ("Rating_imdb", "@x"), ("auditory", "@auditory")],
                      x_range=(1, 10), y_range=(2, 5))
    fig_imdb.circle(x="x", y="y", source=source_imdb, size=8, color="color", line_color=None)
    fig_imdb.xaxis.axis_label = "IMDB Rating"
    fig_imdb.yaxis.axis_label = "MyShows Rating"

    shows = DATA

    source_imdb.data = dict(
        x=[elem["rating_imdb"] for elem in shows],
        y=[elem["rating_myshows"] for elem in shows],
        auditory=[elem["auditory"] for elem in shows],
        color=["#FF9900" for _ in shows],
        title_gr=[elem["title"] for elem in shows],
        genre=[elem['genre'][0] if len(elem['genre']) > 0 else None for elem in shows]
    )

    #output_file("graph.html")
    #show(fig_imdb)

    for single_control in controls_array:
        single_control.js_on_change('value', callback)

    inputs_column = column(*controls_array, width=480, height=500)
    layout_row = row([inputs_column, fig_imdb])

    script, div = components(layout_row)
    return render_template(
        'dashboard_auditory.html',
        plot_script=script,
        plot_div=div,
        js_resources=INLINE.render_js(),
        css_resources=INLINE.render_css(),
        title_gr="IMDB vs MyShows",
        graph_data="IMDB"
    ).encode(encoding='UTF-8')
    # output_file("graph2.html")
    # show(fig_kinopoisk)


@app.route('/dashboard/votes/kinopoisk')
def graphs_kinopoisk():
    source_kinopoisk = ColumnDataSource()

    genre_list = ['All', 'Comedy', 'Sci-Fi', 'Action', 'Drama', 'War', 'Crime', 'Romance', 'Thriller', 'Music',
                  'Adventure', 'History', 'Fantasy', 'Documentary', 'Horror', 'Mystery', 'Family', 'Animation',
                  'Biography', 'Sport', 'Western', 'Short', 'Musical']
    controls = {
        "reviews": Slider(title="Минимальное число зрителей", value=10, start=10, end=100000, step=50, width=480),
        "info": TextAreaInput(title="Информация", value="Информация об оценках зрителей.\n\n"
                                                        "По горизонтали оценки выбранного источника (IMDB/Кинопоиск),\n"
                                                        "по вертикали оценки пользователей MyShows.\n"
                                                        "Выбор источника осуществляется с помощью выпадающего меню в правом верхнем углу.\n"
                                                        "С помошью ползунка определяется минимальное число зрителей, которые смотрят сериал "
                                                        "(по данным MyShows), для которых будет отмечена информация на графике",
                              width=470, rows=10, disabled=True)
    }

    controls_array = controls.values()

    callback = CustomJS(args=dict(source=source_kinopoisk, controls=controls), code="""
            if (!window.full_data_save1) {
                window.full_data_save1 = JSON.parse(JSON.stringify(source.data));
            }
            var full_data = window.full_data_save1;
            var full_data_length = full_data.x.length;
            var new_data = { x: [], y: [], color: [], title_gr: [], genre: [], auditory: [] }
            for (var i = 0; i < full_data_length; i++) {
                if (full_data.auditory[i] === null || full_data.y[i] === null)
                    continue;
                if (
                    full_data.auditory[i] > controls.reviews.value
                ) {
                    Object.keys(new_data).forEach(key => new_data[key].push(full_data[key][i]));
                }
            }
            source.data = new_data;
            source.change.emit();
        """)

    fig_kinopoisk = figure(height=800, width=1080, tooltips=[("Title", "@title_gr"), ("Rating_myshows", "@y"),
                                                             ("Rating_kinopoisk", "@x"), ("auditory", "@auditory")],
                           x_range=(1, 10), y_range=(2, 5))
    fig_kinopoisk.circle(x="x", y="y", source=source_kinopoisk, size=8, color="color", line_color=None)
    fig_kinopoisk.xaxis.axis_label = "Kinopoisk Rating"
    fig_kinopoisk.yaxis.axis_label = "MyShows Rating"

    shows = DATA

    source_kinopoisk.data = dict(
        x=[elem["rating_kinopoisk"] for elem in shows],
        y=[elem["rating_myshows"] for elem in shows],
        auditory=[elem["auditory"] for elem in shows],
        color=["#FF9900" for _ in shows],
        title_gr=[elem["title"] for elem in shows],
        genre=[elem['genre'][0] if len(elem['genre']) > 0 else None for elem in shows]
    )

    #output_file("graph.html")
    #show(fig_imdb)

    for single_control in controls_array:
        single_control.js_on_change('value', callback)
    inputs_column = column(*controls_array, width=480, height=500)
    layout_row = row([inputs_column, fig_kinopoisk])

    script, div = components(layout_row)
    return render_template(
        'dashboard_auditory.html',
        plot_script=script,
        plot_div=div,
        js_resources=INLINE.render_js(),
        css_resources=INLINE.render_css(),
        title_gr="Кинопоиск vs myshows",
        graph_data="Кинопоиск"
    ).encode(encoding='UTF-8')


@app.route('/dashboard/channels')
def graphs_channels():
    source = ColumnDataSource()
    source2 = ColumnDataSource()

    country_list = ["Все", 'Россия', 'США', 'Великобритания', 'Германия', 'Япония', 'Китай', 'Южная Корея', 'Бразилия',
                    'Испания', 'Украина', 'Канада', 'Беларусь', "Австралия", "Франция", "Таиланд", "Турция", "Италия", "СССР"]
    country_list.sort()
    controls = {
        "reviews": NumericInput(title="Милимальное число зрителей", value=10, placeholder="Введите значение", low=10, high=100000, mode="int"),
        "min_year": Slider(title="Начальная дата", start=1970, end=2023, value=1970, step=1),
        "max_year": Slider(title="Конечная дата", start=1970, end=2023, value=2023, step=1),
        "country": Select(title="Страна", value="Все", options=country_list),
        "info": TextAreaInput(title="Информация", value="Информация о каналах, на которых транслировались шоу или сериалы.\n\n"
                                                        "По горизонтали отображаются каналы/студии,\n"
                                                        "по вертикали число сериалов/шоу данного канала.\n"
                                                        "С помошью полей управления можно производить фильтрацию данных.\n",
                              width=470, rows=10, disabled=True)
    }

    controls_array = controls.values()

    shows = DATA
    # x_values = [",".join(elem["country"]) for elem in shows]
    # x_list = list(set([",".join(elem["country"]) for elem in shows]))
    # y_values = [x_values.count(elem) for elem in x_list]
    # sorted_x = sorted(x_list, key=lambda x: y_values[x_list.index(x)])

    x_values = [elem["channel"] for elem in shows]
    x_list = list(set(x_values))
    x_list2 = list(set(x_values))
    y_values = [x_values.count(elem) for elem in x_list]
    y_values2 = [sum([show["auditory"] if show["channel"] == elem else 0 for show in shows]) for elem in x_list2]
    sorted_x = list(sorted(x_list, key=lambda x: y_values[x_list.index(x)]))[::-1]
    sorted_x2 = list(sorted(x_list, key=lambda x: y_values2[x_list2.index(x)]))[::-1]
    if len(x_list) > 30:
        val = y_values[x_list.index(sorted_x[30])]
        val2 = y_values2[x_list.index(sorted_x2[30])]
        x_values = []
        x_values2 = []
        for elem in shows:
            x_v = elem["channel"]
            #if y_values[x_list.index(x_v)] > val:
            if y_values[x_list.index(x_v)] > val:
                x_values.append(x_v)
            if y_values2[x_list.index(x_v)] > val2:
                x_values2.append(x_v)
        x_list = list(set(x_values))
        x_list2 = list(set(x_values2))
        y_values = [x_values.count(elem) for elem in x_list]
        y_values2 = [sum([show["auditory"] if show["channel"] == elem else 0 for show in shows]) for elem in x_list2]
        sorted_x = list(sorted(x_list, key=lambda x: y_values[x_list.index(x)]))[::-1]
        sorted_x2 = list(sorted(x_list2, key=lambda x: y_values2[x_list2.index(x)]))[::-1]

    fig = figure(height=500, width=1080, tooltips=[("Канал", "@channel"), ("Число сериалов", "@serials")],
                 x_range=sorted_x)
    fig.vbar(x="x", top="top", source=source, width=0.9)
    fig.xaxis.axis_label = "Каналы"
    fig.yaxis.axis_label = "Число сериалов"
    fig.xaxis.major_label_orientation = math.pi / 3

    fig2 = figure(height=500, width=1080, tooltips=[("Канал", "@channel"), ("Число зрителей", "@auditory")],
                  x_range=sorted_x2)
    fig2.vbar(x="x", top="top", source=source2, width=0.9)
    fig2.xaxis.axis_label = "Каналы"
    fig2.yaxis.axis_label = "Число зрителей"
    fig2.xaxis.major_label_orientation = math.pi / 3

    fig.x_range.factors = sorted_x
    fig2.x_range.factors = sorted_x2
    callback = CustomJS(args=dict(source=source, figure=fig, controls=controls), code="""
            var xml = new XMLHttpRequest();
            xml.open("POST", "http://127.0.0.1:5000/api/channels/1", true);
            xml.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
            xml.onload = function() {
                reload = "not";
                $("#loading").hide();
                $("#content").show();
                var dataReply = JSON.parse(this.responseText)
                console.log(dataReply);
                source.data = dataReply;
                figure.x_range.factors = dataReply.sorted_x;
                figure.change.emit();
                source.change.emit();
            }
            
            var dataval = {Minv: controls.min_year.value, 
            Maxv: controls.max_year.value,
            Reviewsv: controls.reviews.value,
            Countryv: controls.country.value};
            
            var dataSend = JSON.stringify(dataval);
            
            xml.send(dataSend);
            reload = "reload";
            loading();
        """)

    callback2 = CustomJS(args=dict(source=source, figure=fig, controls=controls), code="""
                var xml = new XMLHttpRequest();
                xml.open("POST", "http://127.0.0.1:5000/api/channels/2", true);
                xml.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
                xml.onload = function() {
                    reload = "not";
                    $("#loading").hide();
                    $("#content").show();
                    var dataReply = JSON.parse(this.responseText)
                    console.log(dataReply);
                    source.data = dataReply;
                    figure.x_range.factors = dataReply.sorted_x;
                    figure.change.emit();
                    source.change.emit();
                }

                var dataval = {Minv: controls.min_year.value, 
                Maxv: controls.max_year.value,
                Reviewsv: controls.reviews.value,
                Countryv: controls.country.value};

                var dataSend = JSON.stringify(dataval);

                xml.send(dataSend);
                reload = "reload";
                loading();
            """)

    source.data = dict(
        x=x_list,
        top=y_values,
        channel=x_list,
        serials=y_values,
        sorted_x=sorted_x
    )

    source2.data = dict(
        x=x_list2,
        top=y_values2,
        channel=x_list2,
        auditory=y_values2,
        sorted_x=sorted_x2
    )

    for single_control in controls_array:
        #single_control.js_on_change('value', callback)
        single_control.js_on_change('value', callback2)


    inputs_column = column(*controls_array, width=480, height=500)
    data_column = column([fig, fig2])
    layout_row = row([inputs_column, data_column])

    script, div = components(layout_row)
    return render_template(
        'dashboard_channels.html',
        plot_script=script,
        plot_div=div,
        js_resources=INLINE.render_js(),
        css_resources=INLINE.render_css(),
        title_gr="Аналитика каналов"
    ).encode(encoding='UTF-8')


@app.route('/dashboard/years')
def graphs_years():
    source = ColumnDataSource()
    source2 = ColumnDataSource()

    country_list = ["Все", 'Россия', 'США', 'Великобритания', 'Германия', 'Япония', 'Китай', 'Южная Корея', 'Бразилия',
                    'Испания', 'Украина', 'Канада', 'Беларусь', "Австралия", "Франция", "Таиланд", "Турция", "Италия",
                    "СССР"]
    country_list.sort()
    controls = {
        "reviews": NumericInput(title="Милимальное число зрителей", value=10, placeholder="Введите значение", low=10,
                                high=100000, mode="int"),
        "min_year": Slider(title="Начальная дата", start=1970, end=2023, value=1970, step=1),
        "max_year": Slider(title="Конечная дата", start=1970, end=2023, value=2023, step=1),
        "country": Select(title="Страна", value="Все", options=country_list),
        "info": TextAreaInput(title="Информация",
                              value="Информация о каналах, на которых транслировались шоу или сериалы.\n\n"
                                    "По горизонтали отображаются каналы/студии,\n"
                                    "по вертикали число сериалов/шоу данного канала.\n"
                                    "С помошью полей управления можно производить фильтрацию данных.\n",
                              width=470, rows=10, disabled=True)
    }

    controls_array = controls.values()

    shows = DATA
    # x_values = [",".join(elem["country"]) for elem in shows]
    # x_list = list(set([",".join(elem["country"]) for elem in shows]))
    # y_values = [x_values.count(elem) for elem in x_list]
    # sorted_x = sorted(x_list, key=lambda x: y_values[x_list.index(x)])

    x_values = [elem["channel"] for elem in shows]
    x_list = list(set(x_values))
    x_list2 = list(set(x_values))
    y_values = [x_values.count(elem) for elem in x_list]
    y_values2 = [sum([show["auditory"] if show["channel"] == elem else 0 for show in shows]) for elem in x_list2]
    sorted_x = list(sorted(x_list, key=lambda x: y_values[x_list.index(x)]))[::-1]
    sorted_x2 = list(sorted(x_list, key=lambda x: y_values2[x_list2.index(x)]))[::-1]
    if len(x_list) > 30:
        val = y_values[x_list.index(sorted_x[30])]
        val2 = y_values2[x_list.index(sorted_x2[30])]
        x_values = []
        x_values2 = []
        for elem in shows:
            x_v = elem["channel"]
            # if y_values[x_list.index(x_v)] > val:
            if y_values[x_list.index(x_v)] > val:
                x_values.append(x_v)
            if y_values2[x_list.index(x_v)] > val2:
                x_values2.append(x_v)
        x_list = list(set(x_values))
        x_list2 = list(set(x_values2))
        y_values = [x_values.count(elem) for elem in x_list]
        y_values2 = [sum([show["auditory"] if show["channel"] == elem else 0 for show in shows]) for elem in x_list2]
        sorted_x = list(sorted(x_list, key=lambda x: y_values[x_list.index(x)]))[::-1]
        sorted_x2 = list(sorted(x_list2, key=lambda x: y_values2[x_list2.index(x)]))[::-1]

    fig = figure(height=600, width=1080, tooltips=[("Канал", "@channel"), ("Число сериалов", "@serials")],
                 x_range=sorted_x)
    fig.vbar(x="x", top="top", source=source, width=0.9)
    fig.xaxis.axis_label = "Каналы"
    fig.yaxis.axis_label = "Число сериалов"
    fig.xaxis.major_label_orientation = math.pi / 3

    fig2 = figure(height=600, width=1080, tooltips=[("Канал", "@channel"), ("Число зрителей", "@auditory")],
                  x_range=sorted_x2)
    fig2.vbar(x="x", top="top", source=source2, width=0.9)
    fig2.xaxis.axis_label = "Каналы"
    fig2.yaxis.axis_label = "Число зрителей"
    fig2.xaxis.major_label_orientation = math.pi / 3

    fig.x_range.factors = sorted_x
    fig2.x_range.factors = sorted_x2
    callback = CustomJS(args=dict(source=source, figure=fig, controls=controls), code="""
            var xml = new XMLHttpRequest();
            xml.open("POST", "http://127.0.0.1:5000/api/channels/1", true);
            xml.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
            xml.onload = function() {
                reload = "not";
                $("#loading").hide();
                $("#content").show();
                var dataReply = JSON.parse(this.responseText)
                console.log(dataReply);
                source.data = dataReply;
                figure.x_range.factors = dataReply.sorted_x;
                figure.change.emit();
                source.change.emit();
            }

            var dataval = {Minv: controls.min_year.value, 
            Maxv: controls.max_year.value,
            Reviewsv: controls.reviews.value,
            Countryv: controls.country.value};

            var dataSend = JSON.stringify(dataval);

            xml.send(dataSend);
            reload = "reload";
            loading();
        """)

    callback2 = CustomJS(args=dict(source=source2, figure=fig2, controls=controls), code="""
                var xml = new XMLHttpRequest();
                xml.open("POST", "http://127.0.0.1:5000/api/channels/2", true);
                xml.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
                xml.onload = function() {
                    reload = "not";
                    $("#loading").hide();
                    $("#content").show();
                    var dataReply = JSON.parse(this.responseText)
                    console.log(dataReply);
                    source.data = dataReply;
                    figure.x_range.factors = dataReply.sorted_x;
                    figure.change.emit();
                    source.change.emit();
                }

                var dataval = {Minv: controls.min_year.value, 
                Maxv: controls.max_year.value,
                Reviewsv: controls.reviews.value,
                Countryv: controls.country.value};

                var dataSend = JSON.stringify(dataval);

                xml.send(dataSend);
                reload = "reload";
                loading();
            """)

    source.data = dict(
        x=x_list,
        top=y_values,
        channel=x_list,
        serials=y_values,
        sorted_x=sorted_x
    )

    source2.data = dict(
        x=x_list2,
        top=y_values2,
        channel=x_list2,
        auditory=y_values2,
        sorted_x=sorted_x2
    )

    for single_control in controls_array:
        #single_control.js_on_change('value', callback)
        single_control.js_on_change('value', callback2)

    inputs_column = column(*controls_array, width=480, height=500)
    data_column = column([fig, fig2])
    layout_row = row([inputs_column, data_column])

    script, div = components(layout_row)
    return render_template(
        'dashboard_years.html',
        plot_script=script,
        plot_div=div,
        js_resources=INLINE.render_js(),
        css_resources=INLINE.render_css(),
        title_gr="Аналитика каналов"
    ).encode(encoding='UTF-8')



@app.route('/dashboard')
def dashboard():
    return render_template(
        'dashboard_main.html',
        plot_script="",
        plot_div="",
        js_resources=INLINE.render_js(),
        css_resources=INLINE.render_css(),
        title_gr="Dashboard",
    ).encode(encoding='UTF-8')



@app.route('/dataset')
def dataset():
    dataset_sh_str = f"{dataset_shows}"
    if dataset_shows == SHOWS_FILE:
        dataset_sh_str = "default"

    dataset_ep_str = f"{dataset_episodes}"
    if dataset_episodes == EPISODES_FILE:
        dataset_ep_str = "default"
    return render_template(
        'dataset.html',
        title="Управление датасетами",
        dataset_shows=dataset_sh_str,
        dataset_episodes=dataset_ep_str
    ).encode(encoding='UTF-8')


@app.route('/')
def home():
    return render_template(
        'home.html',
        title="Главная страница"
    ).encode(encoding='UTF-8')
    # output_file("graph2.html")
    # show(fig_kinopoisk)


@app.route('/api/channels/1', methods=['POST'])
def api_channels_1():
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

@app.route('/api/channels/2', methods=['POST'])
def api_channels_2():
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
    y_values2 = [sum([show["auditory"] if show["channel"] == elem else 0 for show in shows]) for elem in x_list]
    sorted_x2 = list(sorted(x_list, key=lambda x: y_values2[x_list.index(x)]))[::-1]
    if len(x_list) > 30:
        val2 = y_values2[x_list.index(sorted_x2[30])]
        x_values2 = []
        for elem in shows:
            x_v = elem["channel"]
            if y_values2[x_list.index(x_v)] > val2:
                x_values2.append(x_v)
        x_list2 = list(set(x_values2))
        y_values2 = [sum([show["auditory"] if show["channel"] == elem else 0 for show in shows]) for elem in x_list2]
        sorted_x2 = list(sorted(x_list2, key=lambda x: y_values2[x_list2.index(x)]))[::-1]

    source = dict(
        x=x_list2,
        top=y_values2,
        channel=x_list2,
        auditory=y_values2,
        sorted_x=sorted_x2
        )
    return jsonify(source)


@app.route('/api/dataset/shows', methods=['POST'])
def api_dataset_shows():
    file_name = request.get_data().decode("UTF-8").split('filename="')[1].split('"')[0]
    print(file_name)
    global dataset_shows, dataset_episodes
    files = os.listdir(path="./datasets/custom")
    print(files)
    if file_name != "" and file_name in files:
        file_name = f"datasets/custom/{file_name}"

        dataset_shows = file_name

    dataset_sh_str = f"{dataset_shows}"
    if dataset_shows == SHOWS_FILE:
        dataset_sh_str = "default"

    dataset_ep_str = f"{dataset_episodes}"
    if dataset_episodes == EPISODES_FILE:
        dataset_ep_str = "default"
    return render_template(
        'dataset.html',
        title="Управление датасетами",
        dataset_shows=dataset_sh_str,
        dataset_episodes=dataset_ep_str
    ).encode(encoding='UTF-8')


@app.route('/api/dataset/episodes', methods=['POST'])
def api_dataset_episodes():
    file_name = request.get_data().decode("UTF-8").split('filename="')[1].split('"')[0]
    print(file_name)
    global dataset_episodes, dataset_shows
    files = os.listdir(path="./datasets/custom")
    print(files)
    if file_name != "" and file_name in files:
        file_name = f"datasets/custom/{file_name}"

        dataset_episodes = file_name

    dataset_sh_str = f"{dataset_shows}"
    if dataset_shows == SHOWS_FILE:
        dataset_sh_str = "default"

    dataset_ep_str = f"{dataset_episodes}"
    if dataset_episodes == EPISODES_FILE:
        dataset_ep_str = "default"
    return render_template(
        'dataset.html',
        title="Управление датасетами",
        dataset_shows=dataset_sh_str,
        dataset_episodes=dataset_ep_str
    ).encode(encoding='UTF-8')


if __name__ == "__main__":
    app.run(debug=True)