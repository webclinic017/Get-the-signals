from flask import Flask, render_template, Response, redirect, request, url_for, flash, abort
from flask_login import login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import TextField, Form
import pymysql
import os
import plotly
import plotly.graph_objs as go
import json
import pandas as pd

from SV import app, db
from SV.models import User
from SV.forms import LoginForm, RegistrationForm
from utils.db_manage import QuRetType, std_db_acc_obj


class SearchForm(Form):
    stock = TextField('Insert Stock', id='stock_autocomplete')


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

def fetch(nRows=200):
    """
    Function is used in table function

    :param nRows: used to specify the number of rows to display in the /table page table
    :returns: the table
    https://stackoverflow.com/questions/7219385/how-to-join-only-one-column

    1. Gets data from DB and joins to have last Close market prices 
    2. Calculates price evolution
    """
    qu = "select distinct ValidTick, SignalDate, ScanDate, NScanDaysInterval, PriceAtSignal, `Close` from\
            (\
            SELECT Signals_aroon_crossing.*, US_TODAY.Close FROM Signals_aroon_crossing\
            LEFT JOIN US_TODAY\
            ON Signals_aroon_crossing.ValidTick = US_TODAY.Symbol\
            ORDER BY SignalDate DESC)t"
    items = db_acc_obj.exc_query(db_name='marketdata', query=qu, \
        retres=QuRetType.MANY, nRows=nRows)

    # checking if sql query is empty before starting pandas manipulation.
    # If empty we simply return items. No Bug.
    # If we process below py calculations with an item the website is throw an error.
    if items:
        # Transform tuple of tuples in list of lists for mutability
        listofTuples = list(items)
        listofLists = []
        for tup in listofTuples:
            l = list(tup)
            listofLists.append(l)

    
        dfitems = pd.DataFrame(items)
        PriceEvolution = (( (dfitems.iloc[:,5] - dfitems.iloc[:,4]) / dfitems.iloc[:,4] ) * 100).tolist()
        
        count=0
        for line in listofLists:
            line.append(round(PriceEvolution[count],2))
            count +=1
        # re-cast to tuple of tuples for easier integration in HTML


        tupleOfTuples = tuple(tuple(x) for x in listofLists)

        return tupleOfTuples
    else:
        return items


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
@login_required
def table_form():
    nRows = request.form['text']
    nRows = int(nRows)
    items = fetch(nRows)
    return render_template('table.html', items=items)


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

        reReconstructedLine  = c1 + ',' + c2 + ','\
             + c3 + ',' + c4 + ',' + c5 + ',' + c6 + '\n'
        reReconstructedCSV = reReconstructedCSV + reReconstructedLine

    return reReconstructedCSV

@app.route("/getCSV")
@login_required
def getCSV():
    fetchedData = fetch()
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
    # text = request.form['stock_input']
    form = SearchForm(request.form)
    text = form.stock.data
    processed_text = text.upper()
    print(processed_text)

    line = create_lineChart(tick=processed_text)
    return render_template('charts.html', form=form, plot=line,tick=processed_text)


@app.route('/infraHealth')
@login_required
def infraHealth():
    return render_template('infraHealth.html', health=True)






#https://stackoverflow.com/questions/55768789/how-to-read-in-user-input-on-a-webpage-in-flask
if __name__ == '__main__':
    db_acc_obj = std_db_acc_obj() 
    app.run(host='0.0.0.0', debug=True)


