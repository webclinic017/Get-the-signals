import os
from flask import Flask, render_template, url_for, redirect
from flask import Flask, request, render_template, abort, Response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sqlite3
import numpy as np

from bokeh.plotting import figure, output_file, show
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, CustomJS, Slider
from bokeh.embed import components


from sqlite_utils import from_csv_to_sqlite3

app = Flask(__name__)

app.config['SECRET_KEY'] = "mysecretkey"


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


@app.route('/bar')
def bar():
    bar_labels = labels
    bar_values = values
    return render_template('bar_chart.html', title='Bitcoin Monthly Price in USD', max=17000, labels=bar_labels, values=bar_values)


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
