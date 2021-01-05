import pandas as pd
import os
import numpy as np
from datetime import datetime, timedelta 

from utils.db_manage import QuRetType, std_db_acc_obj
db_acc_obj = std_db_acc_obj() 
strToday = str(datetime.today().strftime('%Y-%m-%d'))
strToday = '2021-01-01'

def fetchSignals(**kwargs):
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
        qu = f"SELECT DISTINCT ValidTick, SignalDate, ScanDate, NScanDaysInterval, PriceAtSignal,\
        LastClosingPrice, PriceEvolution FROM signals.Signals_aroon_crossing_evol\
        WHERE PriceAtSignal<15 AND SignalDate<='{sDate}'\
        ORDER BY SignalDate DESC"
    else:
        qu = "SELECT DISTINCT ValidTick, SignalDate, ScanDate, NScanDaysInterval, PriceAtSignal,\
        LastClosingPrice, PriceEvolution FROM signals.Signals_aroon_crossing_evol\
        WHERE PriceAtSignal<15\
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
        
        # Getting first date and last date corresponding to filter (/table)
        firstD = list(dfitems.iloc[0])[1].strftime("%Y-%m-%d")
        lastD = list(dfitems.iloc[-1])[1].strftime("%Y-%m-%d")


        # Select only rows where Price Evolution != 0
        # Calculate mean of price evolution
        pricesNoZero = [x for x in PriceEvolution if x != 0.0]

        # part below useful otherwise if rows as input user returns 0 row having positive Price Evol, it will throw error
        if len(pricesNoZero)>1:
            averageOfReturns = sum(pricesNoZero)/len(pricesNoZero)
        else:
            averageOfReturns = 0

        return round(averageOfReturns,2), items, firstD, lastD
    else:
        return items


def fetchTechnicals():

    qu = f"SELECT * FROM Technicals WHERE Date='{strToday}' LIMIT 100"

    items = db_acc_obj.exc_query(db_name='marketdata', query=qu, \
    retres=QuRetType.ALL)

    return items, strToday