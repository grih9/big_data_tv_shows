from bokeh.client import pull_session
from bokeh.embed import components, server_session
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Slider, CustomJS, Select
from bokeh.plotting import figure
from bokeh.resources import INLINE
from flask import Flask, render_template

from connection_data import MONGO_HOST, MONGO_PORT, MONGO_USERNAME, MONGO_PASSWORD, MONGO_DB
from wrappers.MongoConnector import MongoConnector

app = Flask(__name__)

mongo = MongoConnector(MONGO_HOST, MONGO_PORT, MONGO_USERNAME, MONGO_PASSWORD, MONGO_DB)
DATA = mongo.get_shows_by_auditory(auditory=10000)
print(123)

@app.route('/dashboard/votes/imdb')
def graphs_imdb():
    source_imdb = ColumnDataSource()

    genre_list = ['All', 'Comedy', 'Sci-Fi', 'Action', 'Drama', 'War', 'Crime', 'Romance', 'Thriller', 'Music',
                  'Adventure', 'History', 'Fantasy', 'Documentary', 'Horror', 'Mystery', 'Family', 'Animation',
                  'Biography', 'Sport', 'Western', 'Short', 'Musical']
    controls = {
        "reviews": Slider(title="Минимальное число зрителей", value=10, start=10, end=100000, step=50, width=470)
    }

    controls_array = controls.values()

    callback = CustomJS(args=dict(source=source_imdb, controls=controls), code="""
            console.log('Tap event occurred at x-position: ');
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
        'dashboard.html',
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
        "reviews": Slider(title="Минимальное число зрителей", value=10, start=10, end=100000, step=50, width=480)
    }

    controls_array = controls.values()

    callback = CustomJS(args=dict(source=source_kinopoisk, controls=controls), code="""
            if (!window.full_data_save1) {
                console.log("HELLO")
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
        'dashboard.html',
        plot_script=script,
        plot_div=div,
        js_resources=INLINE.render_js(),
        css_resources=INLINE.render_css(),
        title_gr="Кинопоиск vs myshows",
        graph_data="Кинопоиск"
    ).encode(encoding='UTF-8')


@app.route('/dashboard/channels2')
def graphs_channels2():
    source_imdb = ColumnDataSource()

    country_list = ['Россия', 'США', 'Великобритания', 'Германия', 'Япония', 'Китай', 'Южная Корея', 'Бразилия', 'Испания',
                    'Украина', 'Канада', 'Беларусь']
    controls = {
        "reviews": Slider(title="Минимальное число зрителей", value=10, start=100, end=100000, step=150, width=470),
        "min_year": Slider(title="Начальная дата", start=1970, end=2023, value=1970, step=1),
        "max_year": Slider(title="Конечная дата", start=1970, end=2023, value=2023, step=1),
        "genre": Select(title="Страна", value="Все", options=country_list)
    }

    controls_array = controls.values()

    callback = CustomJS(args=dict(source=source_imdb, controls=controls), code="""
            if (!window.full_data_save) {
                window.full_data_save = JSON.parse(JSON.stringify(source.data));
            }
            var full_data = window.full_data_save;
            var full_data_length = full_data.x.length;
            var new_data = { x: [], y: [], color: [], title_gr: [], country: [], auditory: [], released: [], channel: [] }
            for (var i = 0; i < full_data_length; i++) {
                if (full_data.auditory[i] === null || full_data.released[i] === null || full_data.country[i] === null ||
                 full_data.channel[i] === null)
                    continue;
                if (
                    full_data.auditory[i] > controls.reviews.value &&
                    Number(full_data.released[i].slice(-4)) >= controls.min_year.value &&
                     Number(full_data.released[i].slice(-4)) <= controls.max_year.value &&
                     (controls.country.value === 'All' || full_data.country[i].split(",").some(ele => ele.trim() === controls.country.value))
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
        'dashboard.html',
        plot_script=script,
        plot_div=None,
        js_resources=INLINE.render_js(),
        css_resources=INLINE.render_css(),
        title_gr="IMDB vs MyShows",
        graph_data="IMDB"
    ).encode(encoding='UTF-8')
@app.route('/dashboard/channels')
def graphs_channels():
    with pull_session(url="http://localhost:5006/") as session:
        # generate a script to load the customized session
        script = server_session(session_id=session.id, url='http://localhost:5006')
        # use the script in the rendered page
        return render_template("dashboard.html", script=script, plot_script="",
        plot_div="",
        js_resources=INLINE.render_js(),
        css_resources=INLINE.render_css(), title_gr="Channels",
        graph_data=None, template="Flask")


@app.route('/dashboard')
def dashboard():
    return render_template(
        'dashboard.html',
        plot_script="",
        plot_div="",
        js_resources=INLINE.render_js(),
        css_resources=INLINE.render_css(),
        title_gr="Графики",
        graph_data=None
    ).encode(encoding='UTF-8')


@app.route('/ind')
def ind():
    return render_template(
        'index.html',
    ).encode(encoding='UTF-8')

@app.route('/')
def home():
    return render_template(
        'home.html',
        title="Главная страница"
    ).encode(encoding='UTF-8')
    # output_file("graph2.html")
    # show(fig_kinopoisk)


if __name__ == "__main__":
    app.run(debug=True)