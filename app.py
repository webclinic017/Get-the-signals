from SV import app, db
from flask import render_template, redirect, request, url_for, flash, abort
from flask_login import login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import TextField, Form
import pymysql
import os
import plotly
import plotly.graph_objs as go
import json
import pandas as pd


from SV.models import User
from SV.forms import LoginForm, RegistrationForm
from utils.db_manage import QuRetType, std_db_acc_obj

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/welcome')
@login_required
def welcome_user():
    return render_template('welcome_user.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You logged out!')
    return redirect(url_for('home'))


@app.route('/login', methods=['GET', 'POST'])
def login():

    form = LoginForm()
    if form.validate_on_submit():
        # Grab the user from our User Models table
        user = User.query.filter_by(email=form.email.data).first()

        # Check that the user was supplied and the password is right
        # The verify_password method comes from the User object
        # https://stackoverflow.com/questions/2209755/python-operation-vs-is-not

        if user.check_password(form.password.data) and user is not None:
            # Log in the user

            login_user(user)
            flash('Logged in successfully.')

            # If a user was trying to visit a page that requires a login
            # flask saves that URL as 'next'.
            next = request.args.get('next')

            # So let's now check if that next exists, otherwise we'll go to
            # the welcome page.
            if next == None or not next[0] == '/':
                next = url_for('welcome_user')

            return redirect(next)
    return render_template('login.html', form=form)



class SearchForm(Form):
    autocomp = TextField('Insert ticker', id='tick_autocomplete')
    # https://www.youtube.com/watch?v=32Vmb1sYbuw&ab_channel=Cairocoders
    pass

def fetch(nRows=50):
    """
    Function is used in table function

    :param nRows: used to specify the number of rows to display in the /table page table
    :returns: the table
    """
    qu = "SELECT ticker, sector, price, industry, change_, volume FROM usStocksOverview"
    items = db_acc_obj.exc_query(db_name='flaskfinance', query=qu, \
        retres=QuRetType.MANY, nRows=nRows)

    print(items)
    return items


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


@app.route('/chart')
@login_required
def chart():
    return render_template('chart.html')

def create_lineChart(tick='PLUG'):
    """
    Lists of stock for both NASDAQ and NYSE are present in /utils
    Instead of having a big table with both NASDAQ and NYSE stocks
    We have two list of stocks. The requests to RDS are going to be sent relatively to which list 
    the code can find the tick. Spares time execution.
    
    :param 1: user input in chart page
    :returns: json to generate plotly in HTML
    """

    nasdaq = list(pd.read_csv('utils/nasdaq_list.csv').iloc[:, 0])

    if tick in nasdaq:
        table_chart = 'NASDAQ_15'
    else:
        print('nyse')
        table_chart = 'NYSE_15'

    qu=f"SELECT * FROM {table_chart} WHERE Symbol='{tick}'"
    df = db_acc_obj.exc_query(db_name='marketdata', query=qu,\
        retres=QuRetType.ALLASPD)
    print(df)
    data = [go.Scatter(
        x=df['Date'],
        y=df['Close'])
    ]

    lineJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

    return lineJSON



@app.route('/rtvs')
@login_required
def rtvs():

    return render_template('rtvs.html')

@app.route('/table')
@login_required
def table():
    items = fetch()
    return render_template('table.html', items=items)


@app.route('/table', methods=['POST'])
def table_form():
    nRows = request.form['text']
    nRows = int(nRows)
    items = fetch(nRows)
    print(nRows)
    return render_template('table.html', items=items)


@app.route('/charts')
@login_required
def charts():

    line = create_lineChart()
    return render_template('charts.html', plot=line, tick='PLUG')

@app.route('/charts', methods=['POST'])
def my_form_post():
    text = request.form['text']
    processed_text = text.upper()
    line = create_lineChart(tick=processed_text)
    print(processed_text)
    return render_template('charts.html', plot=line,tick=processed_text)

#https://stackoverflow.com/questions/55768789/how-to-read-in-user-input-on-a-webpage-in-flask
if __name__ == '__main__':
    db_acc_obj = std_db_acc_obj() 
    app.run(host='0.0.0.0', debug=True)


