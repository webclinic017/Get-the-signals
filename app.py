from flask import Flask, render_template, Response, redirect, request, url_for, flash, abort
from flask_login import login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import TextField, Form
import pymysql
import os
import numpy as np
import json
import pandas as pd
from datetime import datetime, timedelta 

from SV import app, db
from SV.models import User
from SV.forms import LoginForm, RegistrationForm
from utils.db_manage import QuRetType, std_db_acc_obj
from utils.fetchData import fetchSignals, fetchTechnicals
from utils.graphs import makeLinesSignal, makeHistogram, create_lineChart


strToday = str(datetime.today().strftime('%Y-%m-%d'))

class SearchForm(Form):
    stock = TextField('Insert Stock', id='stock_autocomplete')
    nbRows = TextField('Enter n° rows', id='numberRows')
    date_input = TextField('Enter Signal Date', id='date_input')
    reset = TextField('Reset', id='reset')
    getcsv = TextField('Download', id='getcsv')


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



@app.route('/rtvs')
@login_required
def rtvs():
    return render_template('rtvs.html')





@app.route('/table')
@login_required
def table():

# https://stackoverflow.com/questions/57502469/plotly-how-to-plot-grouped-results-on-multiple-lines
# https://plotly.com/python/figure-labels/   
# https://code.tutsplus.com/tutorials/charting-using-plotly-in-python--cms-30286 
    form = SearchForm(request.form)
    average, items, firstD, lastD = fetchSignals()
    lineJSON = makeHistogram(items)
    

    test = makeLinesSignal()

    return render_template('table.html', \
        average=average, form=form,items=items, \
            plot=lineJSON, strToday=strToday, firstD=firstD, lastD=lastD, test=test)




@app.route('/table', methods=['POST'])
@login_required
def table_form():
    form = SearchForm(request.form)
    dateInput = form.date_input.data
    reset = form.reset.data
    getcsv = form.getcsv.data

    try:
        average, items, firstD, lastD = fetchSignals(dateInput=dateInput)
        lineJSON = makeHistogram(items)
        return render_template('table.html', firstD=firstD, lastD=lastD, \
            items=items, average=average, form=form, plot=lineJSON, strToday=strToday)
    except ValueError:
        average = 0
        return render_template('table.html', average=average, form=form,strToday=strToday)


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

@app.route("/getCSV", methods=['GET'])
@login_required
def getCSV():
    average, fetchedData, firstD, lastD = fetchSignals()
    reReconstructedCSV = tuplesToCSV(Tuples=fetchedData)
    return Response(
        reReconstructedCSV,
        mimetype="text/csv",
        headers={"Content-disposition":
                 "attachment; filename=signals.csv"})


@app.route('/technicals')
@login_required
def technicals():
    items, strToday = fetchTechnicals()
    return render_template('technicals.html', items=items, strToday=strToday)
    

@app.route('/macroView')
@login_required
def macroView():
    return render_template('macroView.html')
    



@app.route('/investInfra')
@login_required
def investInfra():
    return render_template('investInfra.html')


@app.route('/charts',methods=['GET', 'POST'])
@login_required
def charts():
    form = SearchForm(request.form)
    line = create_lineChart()

    test = makeLinesSignal()


    return render_template('charts.html', form=form, plot=line, tick='PLUG', test=test)
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
