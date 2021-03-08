import pandas as pd
import os
import numpy as np
from datetime import datetime, timedelta 

from utils.db_manage import QuRetType, std_db_acc_obj
db_acc_obj = std_db_acc_obj() 
strToday = str(datetime.today().strftime('%Y-%m-%d'))


def fetchSignalSectorsEvol():
    qu = "SELECT Date, AVG(Close), Sector FROM\
    (\
    SELECT * FROM\
            (\
            SELECT Symbol, Date, Close, Volume\
            FROM marketdata.NASDAQ_20\
            WHERE Symbol IN\
            (SELECT DISTINCT ValidTick FROM signals.Signals_aroon_crossing)\
            AND Date>'2020-12-16'\
            )t\
        LEFT JOIN marketdata.sectors\
        ON t.Symbol = sectors.Ticker\
    )t2\
    GROUP BY Date, Sector"

    df = db_acc_obj.exc_query(db_name='signals', query=qu, \
    retres=QuRetType.ALLASPD)
    print(df)

    return df


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
        qu = f"SELECT * FROM \
            (SELECT Signals_aroon_crossing_evol.*, sectors.Company, sectors.Sector, sectors.Industry  FROM signals.Signals_aroon_crossing_evol\
            LEFT JOIN marketdata.sectors ON sectors.Ticker = Signals_aroon_crossing_evol.ValidTick\
            )t\
        WHERE SignalDate BETWEEN '2020-12-15' AND '{sDate}' \
        ORDER BY SignalDate DESC"
    else:
        qu = "SELECT * FROM\
            (SELECT Signals_aroon_crossing_evol.*, sectors.Company, sectors.Sector, sectors.Industry  FROM signals.Signals_aroon_crossing_evol\
            LEFT JOIN marketdata.sectors ON sectors.Ticker = Signals_aroon_crossing_evol.ValidTick\
            )t\
        WHERE SignalDate>'2020-12-15' ORDER BY SignalDate DESC;"

    
    items = db_acc_obj.exc_query(db_name='signals', query=qu, \
        retres=QuRetType.ALL)
    # checking if sql query is empty before starting pandas manipulation.
    # If empty we simply return items. No Bug.
    # If we process below py calculations with an item the website is throw an error.

    if items:
        # Calculate price evolutions and append to list of Lists 
        dfitems = pd.DataFrame(items)
        PriceEvolution = dfitems.iloc[:,6].tolist()

        # Calculate nbSignals
        nSignalsDF = dfitems.iloc[:, 0:2]
        nSignalsDF = nSignalsDF.drop_duplicates()
        nSignals = len(nSignalsDF)

        # Getting first date and last date corresponding to filter (/table)
        firstD = list(dfitems.iloc[0])[1].strftime("%Y-%m-%d")
        lastD = list(dfitems.iloc[-1])[1].strftime("%Y-%m-%d")
        # "lastD" == oldest

        quSP500beg = f"SELECT * FROM marketdata.sp500 WHERE Date='{lastD}'"
        quSP500end = f"SELECT * FROM marketdata.sp500 WHERE Date='{firstD}'"

        sp500beg = db_acc_obj.exc_query(db_name='marketdata', query=quSP500beg, \
        retres=QuRetType.ALLASPD)
        sp500end = db_acc_obj.exc_query(db_name='marketdata', query=quSP500end, \
        retres=QuRetType.ALLASPD)

        sp500beg = sp500beg['Close'].to_list()[0]
        sp500end = sp500end['Close'].to_list()[0]


        SP500evol = round(((sp500end-sp500beg)/sp500beg)*100,3)

        # Select only rows where Price Evolution != 0
        # Calculate mean of price evolution
        pricesNoZero = [x for x in PriceEvolution if x != 0.0]

        # part below useful otherwise if rows as input user returns 0 row having positive Price Evol, it will throw error
        if len(pricesNoZero)>1:
            averageOfReturns = sum(pricesNoZero)/len(pricesNoZero)

        else:
            averageOfReturns = 0
        return round(averageOfReturns,2), items, firstD, lastD, SP500evol, nSignals
    else:
        return items


def fetchTechnicals(tick='PLUG'):

    quLastDate = "SELECT * FROM Technicals ORDER BY `Date` DESC LIMIT 1"
    qu = "SELECT * FROM Technicals WHERE Date='2021-01-08' LIMIT 100"
    quTick = f"select * from marketdata.Technicals where Ticker='{tick}'\
    ORDER BY Date DESC"

    items = db_acc_obj.exc_query(db_name='marketdata', query=quTick, \
    retres=QuRetType.ALL)

    """
    lastDate = db_acc_obj.exc_query(db_name='marketdata', query=quLastDate, \
    retres=QuRetType.ALLASPD)
    lastDate = lastDate['Date'].to_list()[0]
    """
    return items

def fetchOwnership(tick):

    quTick = f"select * from marketdata.Ownership where Ticker='{tick}'\
    ORDER BY Date DESC"

    items = db_acc_obj.exc_query(db_name='marketdata', query=quTick, \
    retres=QuRetType.ALL)

    return items

def evolNasdaq15dols():
    qu = "select Symbol, Close from marketdata.NASDAQ_20 where Date = '2020-12-16' \
        AND Close < 15"

    qu2 = "select Symbol, Close from marketdata.NASDAQ_20 where Date = '2021-02-19' \
        AND Close < 15"

    df1 = db_acc_obj.exc_query(db_name='marketdata', query=qu, \
    retres=QuRetType.ALLASPD)

    df2 = db_acc_obj.exc_query(db_name='marketdata', query=qu2, \
    retres=QuRetType.ALLASPD)

    dfMerged = df1.merge(df2, how='left', on='Symbol')
    dfMerged['Evolution'] = (dfMerged['Close_y'] - dfMerged['Close_x'])\
        /dfMerged['Close_x']
    meanEvol = dfMerged['Evolution'].mean()





