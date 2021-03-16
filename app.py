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
from utils.fetchData import fetchSignals, fetchTechnicals, fetchOwnership, evolNasdaq15dols, fetchSignalSectorsEvol
from utils.graphs import makeSignalSectorEvol, makeLinesSignal, makeHistogram, create_lineChart, makeOwnershipGraph


strToday = str(datetime.today().strftime('%Y-%m-%d'))
magickey = os.environ.get('magickey')



class SearchForm(Form):
    stock = TextField('Insert Stock', id='stock_autocomplete')
    nbRows = TextField('Enter n° rows', id='numberRows')
    date_input = TextField('Enter Signal Date', id='date_input')
    reset = TextField('Reset', id='reset')
    getcsv = TextField('Download', id='getcsv')
    mW = TextField('mW', id='mW')
    validChartSignal = TextField('validChartSignal', id='validChartSignal')


@app.route('/_autocomplete', methods=['GET'])
def autocomplete():
    stocksList = list(pd.read_csv('utils/stocks_list.csv').iloc[:, 1])
    return Response(json.dumps(stocksList), mimetype='application/json')



@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    formW = SearchForm(request.form)
    magic = formW.mW.data
    
    if form.validate_on_submit():
        if magic==magickey:
            user = User(email=form.email.data,
                        username=form.username.data,
                        password=form.password.data)

            db.session.add(user)
            db.session.commit()
            flash('Thanks for registering! Now you can login!')
            return redirect(url_for('login'))
        else:
            return render_template('register.html', form=form, formW=formW,magics=False)


    return render_template('register.html', form=form, formW=formW, magics=True)


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


# TODO (decorator?)
"""
def tablePage_basic():
    form = SearchForm(request.form)
    average, items, firstD, lastD, SP500evol = fetchSignals()
    lineJSON = makeHistogram(items)
"""




@app.route('/changeSignalChart', methods=['POST'])
@login_required
def changeSignalChart():
    form = SearchForm(request.form)
    average, items, firstD, lastD, SP500evol, nSignals = fetchSignals()
    plot = makeHistogram(items)

    validChartSignal = form.validChartSignal.data
    validChartSignal = validChartSignal.replace(" ", "")

    SignalChart = makeLinesSignal(tick=validChartSignal)

    return render_template('table.html', average=average, form=form,items=items, \
        plot=plot, strToday=strToday, SP500evol=SP500evol, firstD=firstD, lastD=lastD, SignalChart=SignalChart)




def generateDashboard():
    form = SearchForm(request.form)



@app.route('/table')
@login_required
def table():

    form = SearchForm(request.form)
    average, items, firstD, lastD, SP500evol, nSignals = fetchSignals()
    plot = makeHistogram(items)
    
    SignalChart = makeLinesSignal(tick='AAME')

    dfEvols = fetchSignalSectorsEvol()
    signalSectorEvolChart = makeSignalSectorEvol(dfEvols)


    fetchSignalSectorsEvol()

    return render_template('table.html', \
        average=average, form=form,items=items, \
        plot=plot, strToday=strToday, SP500evol=SP500evol, \
        firstD=firstD, lastD=lastD, SignalChart=SignalChart, nSignals=nSignals, \
        signalSectorEvolChart = signalSectorEvolChart)     



@app.route('/table', methods=['POST'])
@login_required
def table_form():
    form = SearchForm(request.form)
    dateInput = form.date_input.data
    reset = form.reset.data
    getcsv = form.getcsv.data

    try:
        average, items, firstD, lastD, SP500evol, nSignals = fetchSignals(dateInput=dateInput)
        plot = makeHistogram(items)

        return render_template('table.html', \
        SP500evol=SP500evol, firstD=firstD, \
        lastD=lastD, items=items, \
        average=average, form=form, \
        lot=plot, strToday=strToday, \
        nSignals=nSignals)
    except ValueError:
        average = 0
        return render_template('table.html', average=average, \
        form=form, strToday=strToday)



@app.route('/filtered_signals')
@login_required
def filtered_signals():

    form = SearchForm(request.form)
    average, items, firstD, lastD, SP500evol, nSignals = fetchSignals()
    
    SignalChart = makeLinesSignal(tick='AAME')

    return render_template('filtered_signals.html', \
        average=average, form=form,items=items, \
        strToday=strToday, SP500evol=SP500evol, \
        firstD=firstD, lastD=lastD, \
        nSignals=nSignals, SignalChart=SignalChart)     


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
    average, fetchedData, firstD, lastD, SP500evol, nSignals = fetchSignals()
    reReconstructedCSV = tuplesToCSV(Tuples=fetchedData)
    return Response(
        reReconstructedCSV,
        mimetype="text/csv",
        headers={"Content-disposition":
                 "attachment; filename=signals.csv"})


@app.route('/technicals')
@login_required
def technicals():
    form = SearchForm(request.form)
    text = form.stock.data.upper()
    items = fetchTechnicals()

    return render_template('technicals.html',items=items, form=form)
    
@app.route('/technicals', methods=['POST'])
@login_required
def submitTechnicals():
    form = SearchForm(request.form)
    text = form.stock.data.upper()
    items = fetchTechnicals(text)

    return render_template('technicals.html', 
    items=items,
    form=form, 
    stock=text)


@app.route('/ownership')
@login_required
def ownership():
    tick= 'PLUG'
    form = SearchForm(request.form)
    text = form.stock.data.upper()
    items = fetchOwnership(tick)
    plot = makeOwnershipGraph(items, tick)

    return render_template('ownership.html',
    items=items,
    form=form,
    plot=plot)
    

@app.route('/ownership', methods=['POST'])
@login_required
def submitOwnership():
    form = SearchForm(request.form)
    text = form.stock.data.upper()
    items = fetchOwnership(text)
    plot = makeOwnershipGraph(items, text)

    return render_template('ownership.html', items=items,\
    form=form, stock=text,plot=plot)


@app.route('/macroView')
@login_required
def macroView():
    return render_template('macroView.html')
    



@app.route('/investInfra')
@login_required
def investInfra():
    return render_template('investInfra.html')


@app.route('/about')
@login_required
def about():
    return render_template('about.html')



@app.route('/search')
@login_required
def search():
    form = SearchForm(request.form)
    
    return render_template('search.html', form=form)



@app.route('/charts',methods=['GET', 'POST'])
@login_required
def charts():
    form = SearchForm(request.form)
    line = create_lineChart()

    return render_template('charts.html', form=form, plot=line, tick='PLUG')


@app.route('/submit', methods=['POST'])
@login_required
def getUserInput():
    """
    User input for charts table
    """
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
        return render_template('charts.html', form=form, \
        plot=line,tick=processed_text)
        



@app.route('/infraHealth')
@login_required
def infraHealth():
    return render_template('infraHealth.html', health=True)



if __name__ == '__main__':
    db_acc_obj = std_db_acc_obj()
    app.run(host='0.0.0.0', debug=True)
