from flask import Flask, render_template, Response, redirect, request, url_for, flash, abort
from flask_login import login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import TextField, Form
import pymysql
import os
import plotly
import plotly.graph_objs as go
import plotly.express as px
import numpy as np
import json
import pandas as pd

from SV import app, db
from SV.models import User
from SV.forms import LoginForm, RegistrationForm
from utils.db_manage import QuRetType, std_db_acc_obj


class SearchForm(Form):
    stock = TextField('Insert Stock', id='stock_autocomplete')
    nbRows = TextField('Enter n° rows', id='numberRows')
    date_input = TextField('Enter Signal Date', id='date_input')


@app.route('/_autocomplete', methods=['GET'])
def autocomplete():
    stocksList = list(pd.read_csv('utils/stocks_list.csv').iloc[:, 1])
    return Response(json.dumps(stocksList), mimetype='application/json')



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



@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

def create_lineChart(tick='PLUG'):
    """
    Lists of stock for both NASDAQ and NYSE are present in /utils
    Instead of having a big table with both NASDAQ and NYSE stocks
    We have two list of stocks. The requests to RDS are going to be sent relatively to which list 
    the code can find the tick. Spares time execution.
    
    :param 1: user input in chart page
    :returns: json to generate a plotly chart in HTML
    """

    nasdaq = list(pd.read_csv('utils/nasdaq_list.csv').iloc[:, 0])

    if tick in nasdaq:
        table_chart = 'NASDAQ_15'
    else:
        print('nyse')
        table_chart = 'NYSE_15'

    qu=f"SELECT * FROM {table_chart} WHERE Symbol='{tick}' and Date>'2018-01-01' "
    df = db_acc_obj.exc_query(db_name='marketdata', query=qu,\
        retres=QuRetType.ALLASPD)
    data = [go.Scatter(
        x=df['Date'],
        y=df['Close'])
    ]

    print(df['Date'])

    lineJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

    return lineJSON

@app.route('/rtvs')
@login_required
def rtvs():
    return render_template('rtvs.html')


def makeHistogram(items):

    df = pd.DataFrame(list(items), columns=['ValidTick',
        'SignalDate',
        'ScanDate',
        'NScanDaysInterval',
        'PriceAtSignal',
        'LastClostingPrice',
        'PriceEvolution'])

    df['PriceEvolution'] = pd.to_numeric(df['PriceEvolution'])    
    dfPivoted = pd.pivot_table(df, values='PriceEvolution',index=['SignalDate'], aggfunc=np.mean)

    fig = go.Figure([go.Bar(x=dfPivoted.index, y=dfPivoted['PriceEvolution'])])
    fig.update_layout(title='Price Evolution, per starting Signal Date',\
        xaxis_title="SignalDate",\
        yaxis_title="Avg. PriceEvolution",
        font=dict(size=10))
    lineJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return lineJSON


def fetch(**kwargs):
    """
    Function is used in table function
    :param nRows: used to specify the number of rows to display in the /table page table
    :returns: the table
    https://stackoverflow.com/questions/7219385/how-to-join-only-one-column
    1. Gets data from DB and joins to have last Close market prices 
    2. Calculates price evolution
    """


    if 'dateInput' in kwargs:
        sDate = str(kwargs['dateInput']) 
        print("SDATE:", sDate)
        qu = f"SELECT DISTINCT ValidTick, SignalDate, ScanDate, NScanDaysInterval, PriceAtSignal,\
        LastClosingPrice, PriceEvolution FROM signals.Signals_aroon_crossing_evol\
        WHERE PriceAtSignal<5 AND SignalDate<'{sDate}'\
        ORDER BY SignalDate DESC"
    else:
        qu = "SELECT DISTINCT ValidTick, SignalDate, ScanDate, NScanDaysInterval, PriceAtSignal,\
        LastClosingPrice, PriceEvolution FROM signals.Signals_aroon_crossing_evol\
        WHERE PriceAtSignal<5\
        ORDER BY SignalDate DESC"


    items = db_acc_obj.exc_query(db_name='marketdata', query=qu, \
        retres=QuRetType.ALL)
    # checking if sql query is empty before starting pandas manipulation.
    # If empty we simply return items. No Bug.
    # If we process below py calculations with an item the website is throw an error.
    if items:
        # Calculate price evolutinds and append to list of Lists 
        dfitems = pd.DataFrame(items)
        PriceEvolution = dfitems.iloc[:,6].tolist()

        # Select only rows where Price Evolution != 0
        # Calculate mean of price evolution
        pricesNoZero = [x for x in PriceEvolution if x != 0.0]

        # part below useful otherwise if rows as input user returns 0 row having positive Price Evol, it will throw error
        if len(pricesNoZero)>1:
            averageOfReturns = sum(pricesNoZero)/len(pricesNoZero)
        else:
            averageOfReturns = 0

        return round(averageOfReturns,2), items
    else:
        return items

@app.route('/table')
@login_required
def table():

# https://stackoverflow.com/questions/57502469/plotly-how-to-plot-grouped-results-on-multiple-lines
# https://plotly.com/python/figure-labels/   
# https://code.tutsplus.com/tutorials/charting-using-plotly-in-python--cms-30286 
    form = SearchForm(request.form)
    average, items = fetch()
    lineJSON = makeHistogram(items)
    
    return render_template('table.html', average=average, form=form,items=items, plot=lineJSON)


@app.route('/table', methods=['POST'])
@login_required
def table_form():
    form = SearchForm(request.form)
    dateInput = form.date_input.data
    try:
        average, items = fetch(dateInput=dateInput)
        lineJSON = makeHistogram(items)
        return render_template('table.html', items=items, average=average, form=form, plot=lineJSON)
    except ValueError:
        average = 0
        return render_template('table.html', average=average, form=form)


def tuplesToCSV(Tuples):
    """
    To be used by Flask's Reponse class, to return a csv type
    Transform tuples int a csv style sheet
    :param 1: tuples
    :returns: a long string that mimics a CSV
    """
    reReconstructedCSV = ""

    for line in Tuples:
        c1 = line[0]
        c2 = line[1].strftime("%Y-%m-%d")
        c3 = line[2].strftime("%Y-%m-%d")
        c4 = str(line[3])
        c5 = str(line[4])
        c6 = str(line[5])
        c7 = str(line[6])

        reReconstructedLine  = c1 + ',' + c2 + ','\
             + c3 + ',' + c4 + ',' + c5 + ',' + c6 + ',' + c7 + '\n'
        reReconstructedCSV = reReconstructedCSV + reReconstructedLine

    return reReconstructedCSV

@app.route("/getCSV")
@login_required
def getCSV():
    average, fetchedData = fetch()
    reReconstructedCSV = tuplesToCSV(Tuples=fetchedData)
    print(reReconstructedCSV)
    return Response(
        reReconstructedCSV,
        mimetype="text/csv",
        headers={"Content-disposition":
                 "attachment; filename=signals.csv"})


@app.route('/investInfra')
@login_required
def investInfra():
    return render_template('investInfra.html')


@app.route('/charts',methods=['GET', 'POST'])
@login_required
def charts():
    form = SearchForm(request.form)
    line = create_lineChart()
    return render_template('charts.html', form=form, plot=line, tick='PLUG')
    #return render_template('charts.html')


@app.route('/submit', methods=['POST'])
@login_required
def getUserInput():
    """
    User input for charts table
    """
    # text = request.form['stock_input']
    form = SearchForm(request.form)
    text = form.stock.data
    processed_text = ""
    processed_text = text.upper()
    stocksList = list(pd.read_csv('utils/stocks_list.csv').iloc[:, 1])

    if not processed_text or processed_text not in stocksList:
        print(type(processed_text))
        print(processed_text)
        empty = True
        return render_template('charts.html', form=form, empty=empty)
    else:
        line = create_lineChart(tick=processed_text)
        empty = False
        return render_template('charts.html', form=form, plot=line,tick=processed_text)
        
@app.route('/infraHealth')
@login_required
def infraHealth():
    return render_template('infraHealth.html', health=True)






#https://stackoverflow.com/questions/55768789/how-to-read-in-user-input-on-a-webpage-in-flask
if __name__ == '__main__':
    db_acc_obj = std_db_acc_obj() 
    app.run(host='0.0.0.0', debug=True)
