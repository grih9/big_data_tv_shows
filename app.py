from bokeh.embed import components
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure, output_file, show
from bokeh.resources import INLINE

from connection_data import MONGO_HOST, MONGO_PORT, MONGO_USERNAME, MONGO_PASSWORD, MONGO_DB
from wrappers.MongoConnector import MongoConnector
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    source_imdb = ColumnDataSource()
    source_kinopoisk = ColumnDataSource()

    fig_imdb = figure(height=900, width=1080, tooltips=[("Title", "@title"), ("Rating_myshows", "@y"),
                                                               ("Rating_imdb", "@x")], x_range=(1, 10), y_range=(2, 5))
    fig_imdb.circle(x="x", y="y", source=source_imdb, size=6, color="color", line_color=None)
    fig_imdb.xaxis.axis_label = "IMDB Rating"
    fig_imdb.yaxis.axis_label = "MyShows Rating"

    fig_kinopoisk = figure(height=900, width=1080, tooltips=[("Title", "@title"), ("Rating_myshows", "@y"),
                                                             ("Rating_kinopoisk", "@x")], x_range=(1, 10), y_range=(2, 5))
    fig_kinopoisk.circle(x="x", y="y", source=source_kinopoisk, size=6, color="color", line_color=None)
    fig_kinopoisk.xaxis.axis_label = "Kinopoisk Rating"
    fig_kinopoisk.yaxis.axis_label = "MyShows Rating"

    mongo = MongoConnector(MONGO_HOST, MONGO_PORT, MONGO_USERNAME, MONGO_PASSWORD, MONGO_DB)
    shows = mongo.get_shows_by_auditory(auditory=900)

    source_imdb.data = dict(
        x=[elem["rating_imdb"] for elem in shows],
        y=[elem["rating_myshows"] for elem in shows],
        color=["#FF9900" for _ in shows],
        title=[elem["title"] for elem in shows],
        genre=[elem['genre'][0] if len(elem['genre']) > 0 else None for elem in shows]
    )

    source_kinopoisk.data = dict(
        x=[elem["rating_kinopoisk"] for elem in shows],
        y=[elem["rating_myshows"] for elem in shows],
        color=["#FF9900" for _ in shows],
        title=[elem["title"] for elem in shows],
        genre=[elem['genre'][0] if len(elem['genre']) > 0 else None for elem in shows]
    )

    #output_file("graph.html")
    #show(fig_imdb)
    script1, div1 = components(fig_imdb)
    script2, div2 = components(fig_kinopoisk)
    return render_template(
        'index.html',
        plot_script1=script1,
        plot_script2=script2,
        plot_div1=div1,
        plot_div2=div2,
        js_resources=INLINE.render_js(),
        css_resources=INLINE.render_css(),
        title="IMDB vs MyShows"
    ).encode(encoding='UTF-8')
    # output_file("graph2.html")
    # show(fig_kinopoisk)

if __name__ == "__main__":
    app.run(debug=True)