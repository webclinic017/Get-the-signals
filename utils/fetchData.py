import pandas as pd
from datetime import datetime, timedelta 

from utils.db_manage import QuRetType, std_db_acc_obj
db_acc_obj = std_db_acc_obj() 
strToday = str(datetime.today().strftime('%Y-%m-%d'))



class sp500evol:
    """
    This class serves to calculate & provide the evolution of the sp500 for a given timeframe

    :param spSTART: oldest date (STRING, format: '%Y-%m-%d')
    :param spEND: most recent date (STRING, format: '%Y-%m-%d')

    """

    
    def __init__(self, spSTART, spEND):
        self.spSTART = spSTART
        self.spEND = spEND
        self.quSP500Data = f"SELECT Date, Close FROM marketdata.sp500 \
        WHERE Date >='{self.spSTART}' \
        AND Date <='{self.spEND}'"
        self.sp500Data = db_acc_obj.exc_query(db_name='marketdata', query=self.quSP500Data, \
        retres=QuRetType.ALLASPD)
        
    
    def fetchSPEvol(self):
        sp500START_FLOAT = self.sp500Data.Close.head(1)[0]
        sp500END_FLOAT = float(self.sp500Data.Close.tail(1))
        return round(((sp500END_FLOAT-sp500START_FLOAT)/sp500START_FLOAT)*100,3)
   


def fetchSignals(**kwargs):
    """
    Function is used in table function
    :param nRows: used to specify the number of rows to display in the /table page table
    :returns: the table
    https://stackoverflow.com/questions/7219385/how-to-join-only-one-column
    1. Gets data from DB and joins to have last Close market prices 
    2. Calculates price evolution
    """

    qu = "SELECT * FROM\
        (SELECT Signals_aroon_crossing_evol.*, sectors.Company, sectors.Sector, sectors.Industry  \
        FROM signals.Signals_aroon_crossing_evol\
        LEFT JOIN marketdata.sectors \
        ON sectors.Ticker = Signals_aroon_crossing_evol.ValidTick\
        )t\
    WHERE SignalDate>'2020-12-15' \
    ORDER BY SignalDate DESC;"

    
    items = db_acc_obj.exc_query(db_name='signals', query=qu, \
        retres=QuRetType.ALL)

    # checking if sql query is empty before starting pandas manipulation.
    # If empty we simply return items. No Bug.
    # If we process below py calculations with an item the website is throw an error.
    if items and 'ALL' in kwargs:
        # Calculate price evolutions and append to list of Lists 
        dfitems = pd.DataFrame(items)

        colNames = {0:"ValidTick",
                    1:"SignalDate",
                    2:"ScanDate",
                    3:"NSanDaysInterval",
                    4:"PriceAtSignal",
                    5:"LastClosingPrice",
                    6:"PriceEvolution",
                    7:"Company",
                    8:"Sector",
                    9:"Industry"}

        dfitems = dfitems.rename(columns=colNames)


        PriceEvolution = dfitems['PriceEvolution'].tolist()

        # Calculate nbSignals
        nSignalsDF = dfitems[['ValidTick','SignalDate']]
        # or, in terms of index, same as: nSignalsDF = dfitems.iloc[:, 0:2]
        nSignalsDF = nSignalsDF.drop_duplicates()
        nSignals = len(nSignalsDF)

        # Getting first date and last date corresponding to filter (in /table page)
        spSTART = list(dfitems.iloc[-1])[1].strftime("%Y-%m-%d")
        spEND = list(dfitems.iloc[0])[1].strftime("%Y-%m-%d")


        # Select only rows where Price Evolution != 0
        # Calculate mean of price evolution
        pricesNoZero = [x for x in PriceEvolution if x != 0.0]

        # part below useful otherwise if rows as input user returns 0 row having positive Price Evol, it will throw error
        if len(pricesNoZero)>1:
            averageOfReturns = sum(pricesNoZero)/len(pricesNoZero)
        else:
            averageOfReturns = 0
        return round(averageOfReturns,2), items, spSTART, spEND, nSignals, dfitems


        # qu20 = "select * from marketdata"
        # After 20 days
        #" test = db_acc_obj.exc_query(db_name='marketdata', query=qu, \
        # retres=QuRetType.ALLASPD)

        D20 = []


    else:
        return items


def fetchTechnicals(tick='PLUG'):

    quLastDate = "SELECT * FROM Technicals ORDER BY `Date` DESC LIMIT 1"
    qu = "SELECT * FROM Technicals WHERE Date='2021-01-08' LIMIT 100"
    quTick = f"select * from marketdata.Technicals where Ticker='{tick}'\
    ORDER BY Date DESC"

    items = db_acc_obj.exc_query(db_name='marketdata', query=quTick, \
    retres=QuRetType.ALL)

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




