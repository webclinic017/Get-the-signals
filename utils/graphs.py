import plotly
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots
from plotly.graph_objs import *
import pandas as pd
import numpy as np
import json
from utils.db_manage import QuRetType, std_db_acc_obj
db_acc_obj = std_db_acc_obj() 


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



def makeLinesSignal():

    qu = f"SELECT * FROM signals.Signals_details WHERE Symbol='AAPL'"
    df = db_acc_obj.exc_query(db_name='signals', query=qu, \
    retres=QuRetType.ALLASPD)

    print(df)

    fig = make_subplots(rows=3, cols=1,
                        shared_xaxes=True,
                        vertical_spacing=0.02,
                        specs=[[{"rowspan":2}],
                        [None],
                        [{}]])

    fig.add_trace(go.Scatter(x=df.Date, y=df['Close'], name='Close', mode='lines'),
                row=1, col=1)

    fig.add_trace(go.Scatter(x=df.Date, y=df['long_mavg'], name='long_mvg',mode='lines',
        line=dict(color='yellow')),
                row=1, col=1)

    fig.add_trace(go.Scatter(x=df.Date, y=df['short_mavg'], name='short_mvg',mode='lines',
        line=dict(color='firebrick')),
                row=1, col=1)

    fig.add_trace(go.Scatter(x=df.Date[df.positions==1], y=df.short_mavg[df.positions==1], 
    name='signal',mode='markers', marker_symbol='triangle-up', marker_color='green'),
                row=1, col=1)

    fig.add_trace(go.Scatter(x=df.Date, y=df['Aroon_Up'], name='Aroon Up', mode='lines',
        line=dict(color='green')),
                row=3, col=1)

    fig.add_trace(go.Scatter(x=df.Date, y=df['Aroon_Down'], name='Aroon Down', mode='lines',\
        line=dict(color='red')),
                row=3, col=1)


    layout = Layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    fig.update_traces(line_width=1)
    fig.update_layout(
    title='Trend Reversal Detection (AAPL)',
    width=1400,
    height=900)
    

    lineJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return lineJSON




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

