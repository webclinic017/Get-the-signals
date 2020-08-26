# Authentication


from sqlite_utils import from_csv_to_sqlite3
from bokeh.util.string import encode_utf8
from bokeh.resources import INLINE
from bokeh.models import DataRange1d
from bokeh.embed import components
from bokeh.models import ColumnDataSource, CustomJS, Slider
from bokeh.layouts import column
from bokeh.plotting import figure, output_file, show
import numpy as np
import sqlite3
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, url_for, redirect, request, Response, abort
import os
from flask_migrate import Migrate
from flask_login import LoginManager


login_manager = LoginManager()


#####################################

app = Flask(__name__)

app.config['SECRET_KEY'] = "mysecretkey"
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)
Migrate(app, db)


login_manager.init__app(app)
login_manager.login_view = 'login'


@app.route('/')
def index():
    return render_template('home.html')


@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/graph')
def graph():
    x = [x*0.005 for x in range(0, 200)]
    y = x

    source = ColumnDataSource(data=dict(x=x, y=y))

    plot = figure(plot_width=400, plot_height=400)
    plot.line('x', 'y', source=source, line_width=3, line_alpha=0.6)

    callback = CustomJS(args=dict(source=source), code="""
            var data = source.data;
            var f = cb_obj.value
            var x = data['x']
            var y = data['y']
            for (var i = 0; i < x.length; i++) {
                y[i] = Math.pow(x[i], f)
            }
            source.change.emit();
        """)

    slider = Slider(start=0.1, end=4, value=1, step=.1, title="power")
    slider.js_on_change('value', callback)

    layout = column(slider, plot)
    script, (plot_div, slider_div) = components((plot, column(slider)))
    kwargs = {'script': script, 'plot_div': plot_div, 'slider_div': slider_div}
    kwargs['title'] = 'bokeh-with-flask'

    return render_template('graph.html', **kwargs)


@app.route('/multiple')
def multiple():
    title = 'multiple'
    from bokeh.plotting import figure

    # First Plot
    p = figure(plot_width=400, plot_height=400)
    p.circle([1, 2, 3, 4, 5], [6, 7, 2, 4, 5],
             size=20, color="navy", alpha=0.5)

    # Second Plot
    p2 = figure(plot_width=400, plot_height=400)
    p2.square([5, 8, 3, 4, 5], [20, 7, 2, 1, 25],
              size=20, color="red", alpha=0.5)

    script, div = components(p)
    script2, div2 = components(p2)

    return render_template('multiple.html', title=title, script=script,
                           div=div, script2=script2, div2=div2)


@app.route('/table')
def table():
    def fetch():
        conn = sqlite3.connect("US_STOCKS.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT TICKER, SECTOR, PRICE, INDUSTRY, VOLUME FROM OVERVIEW")
        items = cursor.fetchmany(50)
        return items
        # simply to have a proposer display without commas and parantheses specific to tuple format
        # items = [item[0] for item in items]

    try:
        items = fetch()
    except sqlite3.OperationalError:
        from_csv_to_sqlite3()
        items = fetch()

    return render_template('table.html', items=items)


if __name__ == '__main__':
    app.run(debug=True)
