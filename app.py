import math
import os
from multiprocessing import Process

from bokeh.client import pull_session
from bokeh.events import PanEnd
from bokeh.embed import components, server_session
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Slider, CustomJS, Select, NumericInput, TextAreaInput, Spinner
from bokeh.plotting import figure
from bokeh.resources import INLINE
from flask import Flask, render_template, jsonify, request
from API.apis import *

from connection_data import MONGO_HOST, MONGO_PORT, MONGO_USERNAME, MONGO_PASSWORD, MONGO_DB
from constants import SHOWS_FILE, EPISODES_FILE, NUMBER_OF_EPISODES, NUMBER_OF_SHOWS
from scrapper.episodes import scrap_episodes
from scrapper.shows import scrap_shows
from wrappers.MongoConnector import MongoConnector

app = Flask(__name__)

mongo = MongoConnector(MONGO_HOST, MONGO_PORT, MONGO_USERNAME, MONGO_PASSWORD, MONGO_DB)
DATA = mongo.get_shows_by_auditory(auditory=10)

dataset_shows = SHOWS_FILE
dataset_episodes = EPISODES_FILE
n_processes = 1
is_scrapping = False


@app.route('/dashboard/votes/imdb')
def graphs_imdb():
    source_imdb = ColumnDataSource()

    genre_list = ['All', 'Comedy', 'Sci-Fi', 'Action', 'Drama', 'War', 'Crime', 'Romance', 'Thriller', 'Music',
                  'Adventure', 'History', 'Fantasy', 'Documentary', 'Horror', 'Mystery', 'Family', 'Animation',
                  'Biography', 'Sport', 'Western', 'Short', 'Musical']
    controls = {
        "reviews": Slider(title="Минимальное число зрителей", value=10, start=10, end=100000, step=50, width=470),
        "info": TextAreaInput(title="Информация об оценках зрителей:", value="По горизонтали оценки выбранного источника (IMDB/Кинопоиск),\n"
                                                        "по вертикали оценки пользователей MyShows.\n"
                                                        "Выбор источника осуществляется с помощью выпадающего меню в правом верхнем углу.\n"
                                                        "С помошью ползунка определяется минимальное число зрителей, которые смотрят сериал "
                                                        "(по данным MyShows), для которых будет отмечена информация на графике",
                              width=470, rows=10, disabled=True, css_classes=["form-control"])
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
        "info": TextAreaInput(title="Информация об оценках зрителей:", value=
        "По горизонтали оценки выбранного источника (IMDB/Кинопоиск),\n"
        "по вертикали оценки пользователей MyShows.\n"
        "Выбор источника осуществляется с помощью выпадающего меню в правом верхнем углу.\n"
        "С помошью ползунка определяется минимальное число зрителей, которые смотрят сериал "
        "(по данным MyShows), для которых будет отмечена информация на графике",
                              width=470, rows=10, disabled=True, css_classes=["form-control"])
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

    fig_kinopoisk = figure(height=800, width=1080, tooltips=[("Название", "@title_gr"), ("Рейтинг myshows", "@y"),
                                                             ("Рейтинг kinopoisk", "@x"), ("Число зрителей", "@auditory")],
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
    source3 = ColumnDataSource()

    country_list = ["Все", 'Россия', 'США', 'Великобритания', 'Германия', 'Япония', 'Китай', 'Южная Корея', 'Бразилия',
                    'Испания', 'Украина', 'Канада', "Австралия", "Франция", "Таиланд", "Турция", "Италия", "СССР"]
    country_list.sort()
    controls = {
        "reviews": NumericInput(title="Милимальное число зрителей", value=10, placeholder="Введите значение", low=10,
                                high=100000, mode="int"),
        "min_year": Spinner(title="Начальная дата", low=1970, high=2023, value=1970, step=1),
        "max_year": Spinner(title="Конечная дата", low=1970, high=2023, value=2023, step=1),
        "country": Select(title="Страна", value="Все", options=country_list),
        "info": TextAreaInput(title="Информация о каналах:",
                              value="На первом графике изображено число сериалов, выпущенных каналами (первые 30 или меньше).\n"
                                    "На втором графике изображено число зрителей сериалов, вышедших на указанном канале.\n"
                                    "На втором графике изображена средняя оценка сериалов, вышедших в указанный год.\n"
                                    "На третьем графике изображено среднее отношени числа зрителей на сериал для указанного канала.\n"
                                    "С помошью полей управления можно производить фильтрацию данных.\n",
                              width=370, rows=15, disabled=True, css_classes=["form-control"])
    }

    controls_array = controls.values()

    shows = DATA

    x_values = [elem["channel"] for elem in shows]

    x_list = list(set(x_values))
    x_list2 = x_list
    x_list3 = x_list

    y_values = [x_values.count(elem) for elem in x_list]
    y_values2ch = y_values
    y_values3ch = y_values
    y_values2 = [sum([show["auditory"] if show["channel"] == elem else 0 for show in shows]) for elem in x_list2]
    y_values3 = [int(y_values2[i] / y_values2ch[i]) if y_values[i] != 0 else 0 for i in range(len(y_values))]
    y_values2av = y_values3
    y_values3aud = y_values2

    sorted_x = list(sorted(x_list, key=lambda x: y_values[x_list.index(x)]))[::-1]
    sorted_x2 = list(sorted(x_list2, key=lambda x: y_values2[x_list2.index(x)]))[::-1]
    sorted_x3 = list(sorted(x_list3, key=lambda x: y_values3[x_list2.index(x)]))[::-1]

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
        y_values2ch = [x_values2.count(elem) for elem in x_list2]
        y_values3ch = [x_values3.count(elem) for elem in x_list3]
        y_values2 = [sum([show["auditory"] if show["channel"] == elem else 0 for show in shows]) for elem in x_list2]
        y_values3 = [int(sum([show["auditory"] if show["channel"] == elem else 0 for show in shows]) / x_values3.count(elem))
                     if x_values3.count(elem) != 0 else 0
                     for elem in x_list3]
        y_values2av = [
            int(sum([show["auditory"] if show["channel"] == elem else 0 for show in shows]) / x_values2.count(elem))
            if x_values2.count(elem) != 0 else 0
            for elem in x_list2]
        y_values3aud = [sum([show["auditory"] if show["channel"] == elem else 0 for show in shows]) for elem in x_list3]

        sorted_x = list(sorted(x_list, key=lambda x: y_values[x_list.index(x)]))[::-1]
        sorted_x2 = list(sorted(x_list2, key=lambda x: y_values2[x_list2.index(x)]))[::-1]
        sorted_x3 = list(sorted(x_list3, key=lambda x: y_values3[x_list3.index(x)]))[::-1]

    fig = figure(height=300, width=1180, tooltips=[("Канал", "@channel"), ("Число сериалов", "@serials")],
                 x_range=sorted_x)
    fig.vbar(x="x", top="top", source=source, width=0.9, color="green")
    fig.xaxis.axis_label = "Каналы"
    fig.yaxis.axis_label = "Число сериалов"
    fig.xaxis.major_label_orientation = math.pi / 3

    fig2 = figure(height=300, width=1180, tooltips=[("Канал", "@channel"), ("Число зрителей", "@auditory"),
                                                    ("Число сериалов", "@serials"), ("Зрителей на сериал", "@average")],
                  x_range=sorted_x2)
    fig2.vbar(x="x", top="top", source=source2, width=0.9, color="red")
    fig2.xaxis.axis_label = "Каналы"
    fig2.yaxis.axis_label = "Число зрителей"
    fig2.xaxis.major_label_orientation = math.pi / 3
    fig2.yaxis.formatter.use_scientific = False

    fig3 = figure(height=300, width=1180, tooltips=[("Канал", "@channel"), ("Число зрителей", "@auditory"),
                                                    ("Число сериалов", "@serials"), ("Зрителей на сериал", "@average")],
                  x_range=sorted_x3)
    fig3.vbar(x="x", top="top", source=source3, width=0.9, color="brown")
    fig3.xaxis.axis_label = "Каналы"
    fig3.yaxis.axis_label = "Среднее число зрителей"
    fig3.xaxis.major_label_orientation = math.pi / 3
    fig3.yaxis.formatter.use_scientific = False

    fig.x_range.factors = sorted_x
    fig2.x_range.factors = sorted_x2
    fig3.x_range.factors = sorted_x3
    callback = CustomJS(args=dict(source=source, figure=fig, source2=source2, figure2=fig2,
                                  source3=source3, figure3=fig3, controls=controls), code="""
                var counter = 0;
                var xml = new XMLHttpRequest();
                xml.open("POST", "http://127.0.0.1:5000/api/channels/1", true);
                xml.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
                xml.onload = function() {
                    counter = counter - 1;
                    console.log(counter);
                    if (counter == 0) {
                        console.log("show");
                        reload = "not";
                        $("#loading").hide();
                        $("#content").show();
                    } else {
                        reload = "reload";
                        loading();    
                    }
                    var dataReply = JSON.parse(this.responseText)
                    console.log(dataReply);
                    source.data = dataReply;
                    figure.x_range.factors = dataReply.sorted_x;
                    figure.change.emit();
                    source.change.emit();
                }
                
                var xml2 = new XMLHttpRequest();
                xml2.open("POST", "http://127.0.0.1:5000/api/channels/2", true);
                xml2.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
                xml2.onload = function() {
                    counter = counter - 1;
                    console.log(counter);
                    if (counter == 0) {
                        console.log("show");
                        reload = "not";
                        $("#loading").hide();
                        $("#content").show();
                    } else {
                        reload = "reload";
                        loading();    
                    }
                    var dataReply2 = JSON.parse(this.responseText)
                    console.log(dataReply2);
                    source2.data = dataReply2;
                    figure2.x_range.factors = dataReply2.sorted_x;
                    figure2.change.emit();
                    source2.change.emit();
                }
                
                var xml3 = new XMLHttpRequest();
                xml3.open("POST", "http://127.0.0.1:5000/api/channels/3", true);
                xml3.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
                xml3.onload = function() {
                    counter = counter - 1;
                    console.log(counter);
                    if (counter == 0) {
                        console.log("show");
                        reload = "not";
                        $("#loading").hide();
                        $("#content").show();
                    } else {
                        reload = "reload";
                        loading();    
                    }
                    var dataReply3 = JSON.parse(this.responseText)
                    console.log(dataReply3);
                    source3.data = dataReply3;
                    figure3.x_range.factors = dataReply3.sorted_x;
                    figure3.change.emit();
                    source3.change.emit();
                }

                var dataval2 = {Minv: controls.min_year.value, 
                Maxv: controls.max_year.value,
                Reviewsv: controls.reviews.value,
                Countryv: controls.country.value};

                var dataSend2 = JSON.stringify(dataval2);
                counter = counter + 1;
                console.log(counter);
                xml2.send(dataSend2);
                reload = "reload";
                loading();    

                var dataval = {Minv: controls.min_year.value, 
                Maxv: controls.max_year.value,
                Reviewsv: controls.reviews.value,
                Countryv: controls.country.value};

                var dataSend = JSON.stringify(dataval);
                counter = counter + 1;
                console.log(counter);
                xml.send(dataSend);
                reload = "reload";
                loading();
                
                var dataval3 = {Minv: controls.min_year.value, 
                Maxv: controls.max_year.value,
                Reviewsv: controls.reviews.value,
                Countryv: controls.country.value};

                var dataSend3 = JSON.stringify(dataval3);
                counter = counter + 1;
                console.log(counter);
                xml3.send(dataSend3);
                reload = "reload";
                loading();
                controls.max_year.low = controls.min_year.value;
                controls.min_year.high = controls.max_year.value;   
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
        serials=y_values2ch,
        average=y_values2av,
        sorted_x=sorted_x2
    )

    source3.data = dict(
        x=x_list3,
        top=y_values3,
        channel=x_list3,
        auditory=y_values3aud,
        serials=y_values3ch,
        average=y_values3,
        sorted_x=sorted_x3
    )

    for single_control in controls_array:
        single_control.js_on_change('value', callback)

    inputs_column = column(*controls_array, width=380, height=500)
    data_column = column([fig, fig2, fig3])
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
    source3 = ColumnDataSource()

    country_list = ["Все", 'Россия', 'США', 'Великобритания', 'Германия', 'Япония', 'Китай', 'Южная Корея', 'Бразилия',
                    'Испания', 'Украина', 'Канада', 'Беларусь', "Австралия", "Франция", "Таиланд", "Турция", "Италия",
                    "СССР"]

    country_list.sort()
    controls = {
        "reviews": NumericInput(title="Милимальное число зрителей", value=10, placeholder="Введите значение", low=10,
                                high=100000, mode="int"),
        "min_year": Spinner(title="Начальная дата", low=1970, high=2022, value=1970, step=1),
        "max_year": Spinner(title="Конечная дата", low=1970, high=2022, value=2022, step=1),
        "country": Select(title="Страна", value="Все", options=country_list),
        "info": TextAreaInput(title="Информация о сериалах и шоу по годам:",
                              value="На первом графике изображено число сериалов, вышедших и завершившихся в указанный год.\n"
                                    "На втором графике изображена средняя оценка сериалов, вышедших в указанный год.\n"
                                    "На третьем графике изображено число зрителей сериалов, вышедших в указанный год.\n"
                                    "С помошью полей управления можно производить фильтрацию данных.\n",
                              width=320, rows=20, disabled=True, css_classes=["form-control"])
    }

    controls_array = controls.values()

    years = [year for year in range(controls["min_year"].value, controls["max_year"].value + 1)]

    data = [mongo.get_shows(condition={"auditory": {"$gte": 10}, "date_start": {"$regex": str(year)}}) for year in years]

    y_values_start = [len(show) for show in data]
    y_values_end = [len(mongo.get_shows(condition={"auditory": {"$gte": 10},
                                                   "date_end": {"$regex": str(year)}}))
                    for year in years]

    y = [sum([show["auditory"] for show in data[i]]) for i in range(len(years))]

    rating = [sum([show["rating_myshows"] for show in data[i]]) / y_values_start[i] if y_values_start[i] != 0 else None
              for i in range(len(years))]

    fig = figure(height=400, width=620, tooltips=[("Год", "@years"), ("Начато сериалов", "@start"),
                                                  ("Окончено сериалов", "@end")])
    fig.circle(x="x", y="y_start", source=source, size=4, color="green")
    fig.circle(x="x", y="y_end", source=source, size=4, color="red")
    fig.line(x="x", y="y_start", source=source, color="green")
    fig.line(x="x", y="y_end", source=source, color="red")
    fig.xaxis.axis_label = "Год"
    fig.yaxis.axis_label = "Число сериалов"

    fig2 = figure(height=400, width=620, tooltips=[("Год", "@x"), ("Число зрителей", "@auditory"),
                                                    ("Число сериалов", "@shows"), ("Зрителей на сериал", "@average")])
    fig2.circle(x="x", y="y", source=source2, size=4, color="green")
    fig2.line(x="x", y="y", source=source2, color="green")
    fig2.xaxis.axis_label = "Год"
    fig2.yaxis.axis_label = "Число зрителей"
    fig2.yaxis.formatter.use_scientific = False

    fig3 = figure(height=400, width=620, tooltips=[("Год", "@x"), ("Оценка", "@rating"),
                                                   ("Число зрителей", "@auditory"), ("Число сериалов", "@shows")])
    fig3.circle(x="x", y="y", source=source3, size=4, color="brown")
    fig3.line(x="x", y="y", source=source3, color="brown")
    fig3.xaxis.axis_label = "Год"
    fig3.yaxis.axis_label = "Оценка Myshows"

    callback = CustomJS(args=dict(source=source, figure=fig, source2=source2, figure2=fig2, source3=source3, figure3=fig3,
                                  controls=controls), code="""
                var counter = 0;
                var xml = new XMLHttpRequest();
                xml.open("POST", "http://127.0.0.1:5000/api/years/1", true);
                xml.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
                xml.onload = function() {
                    counter = counter - 1;
                    console.log(counter);
                    if (counter == 0) {
                        console.log("show");
                        reload = "not";
                        $("#loading").hide();
                        $("#content").show();
                    }
                    else {
                        reload = "reload";
                        loading();    
                    }
                    var dataReply = JSON.parse(this.responseText)
                    console.log(dataReply);
                    source.data = dataReply;
                    figure.change.emit();
                    source.change.emit();
                }

                var xml2 = new XMLHttpRequest();
                xml2.open("POST", "http://127.0.0.1:5000/api/years/2", true);
                xml2.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
                xml2.onload = function() {
                    counter = counter - 1;
                    console.log(counter);
                    if (counter == 0) {
                        console.log("show");
                        reload = "not";
                        $("#loading").hide();
                        $("#content").show();
                    }
                    else {
                        reload = "reload";
                        loading();    
                    }
                    var dataReply2 = JSON.parse(this.responseText)
                    console.log(dataReply2);
                    source2.data = dataReply2;
                    figure2.change.emit();
                    source2.change.emit();
                }
            
                var xml3 = new XMLHttpRequest();
                xml3.open("POST", "http://127.0.0.1:5000/api/years/3", true);
                xml3.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
                xml3.onload = function() {
                    counter = counter - 1;
                    console.log(counter);
                    if (counter == 0) {
                        console.log("show");
                        reload = "not";
                        $("#loading").hide();
                        $("#content").show();
                    }
                    else {
                        reload = "reload";
                        loading();    
                    }
                    var dataReply3 = JSON.parse(this.responseText)
                    console.log(dataReply3);
                    source3.data = dataReply3;
                    figure3.change.emit();
                    source3.change.emit();
                }
                
                var dataval2 = {Minv: controls.min_year.value, 
                Maxv: controls.max_year.value,
                Reviewsv: controls.reviews.value,
                Countryv: controls.country.value};

                var dataSend2 = JSON.stringify(dataval2);
                counter = counter + 1;
                console.log(counter);
                xml2.send(dataSend2);
                reload = "reload";
                loading();    
                
                var dataval = {Minv: controls.min_year.value, 
                Maxv: controls.max_year.value,
                Reviewsv: controls.reviews.value,
                Countryv: controls.country.value};

                var dataSend = JSON.stringify(dataval);
                counter = counter + 1;
                console.log(counter);
                xml.send(dataSend);
                reload = "reload";
                loading();
                
                var dataval3 = {Minv: controls.min_year.value, 
                Maxv: controls.max_year.value,
                Reviewsv: controls.reviews.value,
                Countryv: controls.country.value};

                var dataSend3 = JSON.stringify(dataval3);
                counter = counter + 1;
                console.log(counter);
                xml3.send(dataSend3);
                reload = "reload";
                loading();
                controls.max_year.low = controls.min_year.value;
                controls.min_year.high = controls.max_year.value; 
        """)

    source.data = dict(
        x=years,
        y_start=y_values_start,
        y_end=y_values_end,
        years=years,
        start=y_values_start,
        end=y_values_end
    )

    source2.data = dict(
        x=years,
        y=y,
        auditory=y,
        shows=y_values_start,
        average=[int(y[i] / y_values_start[i]) for i in range(len(y))]
    )

    source3.data = dict(
        x=years,
        y=rating,
        auditory=y,
        rating=rating,
        shows=y_values_start
    )

    for single_control in controls_array:
        single_control.js_on_change('value', callback)

    inputs_column = column(*controls_array, width=330, height=500)
    row_figs = row([fig, fig3])
    row_figs2 = row([fig2])
    data_column = column([row_figs, row_figs2])
    layout_row = row([inputs_column, data_column])

    script, div = components(layout_row)
    return render_template(
        'dashboard_years.html',
        plot_script=script,
        plot_div=div,
        js_resources=INLINE.render_js(),
        css_resources=INLINE.render_css(),
        title_gr="Аналитика по годам"
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

@app.route('/dashboard/other')
def graphs_others():
    source = ColumnDataSource()

    fig = figure(height=300, width=370, tooltips=[("Число сериалов", "@y"), ("Число сезонов", "@x")], x_range=(0.5, 10.5))
    fig.line(x="x", y="y", source=source, color="blue")
    fig.circle(x="x", y="y", source=source, size=3, color="blue")
    fig.xaxis.axis_label = "Число сезонов"
    fig.yaxis.axis_label = "Число сериалов"

    shows = DATA
    x = [elem["number_of_seasons"] for elem in shows]

    list_x = list(set(x))

    source.data = dict(
        x=list_x,
        y=[x.count(elem) for elem in list_x],
    )

    source2 = ColumnDataSource()

    fig2 = figure(height=300, width=370, x_range=[f"{i*10+1}-{(i+1) * 10}" for i in range(10)])
    fig2.vbar(x="x", top="top", source=source2, color="blue", width=0.9)
    fig2.xaxis.axis_label = "Процент оценок сериала"
    fig2.yaxis.axis_label = "Число сериалов"
    fig2.xaxis.major_label_orientation = math.pi / 3

    data = [elem["rating_percent"] for elem in shows]

    source2.data = dict(
        x=[f"{i*10+1}-{(i+1) * 10}" for i in range(10)],
        top=[sum([1 if ((i + 1) * 10) >= elem > i * 10 else 0 for elem in data]) for i in range(10)],
    )

    source3 = ColumnDataSource()

    data = [elem["status"] for elem in shows]
    x_list = list(set(data))
    y = [data.count(elem) for elem in x_list]
    fig3 = figure(height=300, width=370, x_range=x_list)
    fig3.vbar(x="x", top="top", source=source3, color="blue", width=0.9)
    fig3.xaxis.axis_label = "Статус"
    fig3.yaxis.axis_label = "Число сериалов"
    fig3.xaxis.major_label_orientation = math.pi / 3

    fig3.x_range.factors = x_list

    source3.data = dict(
        x=x_list,
        top=y,
    )

    layout_row = column([fig, fig2, fig3])

    script, div = components(layout_row)

    return render_template(
        'dashboard_others.html',
        plot_script=script,
        plot_div=div,
        js_resources=INLINE.render_js(),
        css_resources=INLINE.render_css(),
        title_gr="Другое",
    ).encode(encoding='UTF-8')


@app.route('/dataset')
def dataset():
    global dataset_episodes, dataset_shows
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


@app.route('/scrapping')
def scrapping():
    global dataset_episodes, dataset_shows, is_scrapping
    dataset_sh_str = f"{dataset_shows}"
    if dataset_shows == SHOWS_FILE:
        dataset_sh_str = "default"

    dataset_ep_str = f"{dataset_episodes}"
    if dataset_episodes == EPISODES_FILE:
        dataset_ep_str = "default"
    return render_template(
        'scrapping.html',
        title="Скраппинг",
        dataset_shows=dataset_sh_str,
        dataset_episodes=dataset_ep_str,
        n_processes=n_processes,
        is_scrapping=is_scrapping
    ).encode(encoding='UTF-8')


@app.route('/database')
def database():
    global dataset_episodes, dataset_shows
    dataset_sh_str = f"{dataset_shows}"
    if dataset_shows == SHOWS_FILE:
        dataset_sh_str = "default"

    dataset_ep_str = f"{dataset_episodes}"
    if dataset_episodes == EPISODES_FILE:
        dataset_ep_str = "default"
    return render_template(
        'database.html',
        title="Запись в БД",
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
    return main_api_channels_1(mongo)


@app.route('/api/channels/2', methods=['POST'])
def api_channels_2():
    return main_api_channels_2(mongo)


@app.route('/api/channels/3', methods=['POST'])
def api_channels_3():
    return main_api_channels_3(mongo)

@app.route('/api/years/1', methods=['POST'])
def api_years_1():
    return main_api_years_1(mongo)


@app.route('/api/years/2', methods=['POST'])
def api_years_2():
    return main_api_years_2(mongo)


@app.route('/api/years/3', methods=['POST'])
def api_years_3():
    return main_api_years_3(mongo)


@app.route('/api/dataset/shows', methods=['POST'])
def api_dataset_shows():
    global dataset_episodes, dataset_shows

    file_name = request.get_data().decode("UTF-8").split('name="shows_file_text"')[1].split('------Web')[0].strip()
    if file_name == "default":
        dataset_shows = SHOWS_FILE
    else:
        if file_name == "":
            file_name = request.get_data().decode("UTF-8").split('filename="')[1].split('"')[0]
        print(file_name)

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
    global dataset_episodes, dataset_shows

    file_name = request.get_data().decode("UTF-8").split('name="shows_episode_text"')[1].split('------Web')[0].strip()

    if file_name == "default":
        dataset_episodes = EPISODES_FILE
    else:
        if file_name == "":
            file_name = request.get_data().decode("UTF-8").split('filename="')[1].split('"')[0]
        print(file_name)

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


@app.route('/api/scrapping', methods=['POST'])
def api_scrapping():
    global dataset_episodes, dataset_shows, n_processes, is_scrapping
    if not is_scrapping:
        try:
            is_scrapping = True
            n_processes = int(request.form['select_procs'])
            if request.form['submit'] == 'shows':
                processes = [Process(target=scrap_shows, args=(dataset_shows.split(".csv")[0] + f"({i+1}).csv",
                                                               abs(int(i * NUMBER_OF_SHOWS / n_processes) - 1),
                                                               int(i + 1 * NUMBER_OF_SHOWS / n_processes) - 1,)) for i in range(n_processes)]
                for pr in processes:
                    pr.start()
                    print(f"процесс {pr} стартовал")
                for pr in processes:
                    print(f"процесс {pr} здесь")
                    pr.join()
            elif request.form['submit'] == 'episodes':
                processes = [Process(target=scrap_episodes, args=(
                    dataset_episodes.split(".csv")[0] + f"({i+1}).csv",
                    abs(int(i * NUMBER_OF_EPISODES / n_processes) - 1),
                    int(i + 1 * NUMBER_OF_EPISODES / n_processes) - 1,)) for i in range(n_processes)]

                for pr in processes:
                    pr.start()
                    print(f"процесс {pr} стартовал")
                for pr in processes:
                    print(f"процесс {pr} здесь")
                    pr.join()
        except:
            print("Окончание")
        finally:
            is_scrapping = False


    dataset_sh_str = f"{dataset_shows}"
    if dataset_shows == SHOWS_FILE:
        dataset_sh_str = "default"

    dataset_ep_str = f"{dataset_episodes}"
    if dataset_episodes == EPISODES_FILE:
        dataset_ep_str = "default"
    return render_template(
        'scrapping.html',
        title="Скраппинг",
        dataset_shows=dataset_sh_str,
        dataset_episodes=dataset_ep_str,
        n_processes=n_processes,
        is_scrapping=is_scrapping
    ).encode(encoding='UTF-8')


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
