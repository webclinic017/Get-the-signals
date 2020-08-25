import os
from flask import Flask, render_template, url_for, redirect
from flask import Flask, request, render_template, abort, Response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sqlite3

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

    return render_template('graph.html')


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
