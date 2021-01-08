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
    fig.update_layout(title='Average return, per starting Signal Date (ex: "the stocks signaled on the 22nd December have an average return of 45% until today")',\
        xaxis_title="SignalDate",\
        yaxis_title="Avg. Return",
        font=dict(size=10),
        width=1400,
        height=390,
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(
        autoexpand=False,
        l=100,
        r=20,
        t=110,
        ))

    fig.add_shape(type='line',
                    x0=dfPivoted.index.min(),
                    y0=0,
                    x1=dfPivoted.index.max(),
                    y1=0,
                    line=dict(color='rgba(192,192,192,0.5)',),
                    xref='x',
                    yref='y'
    )

    fig.update_yaxes(showline=False, linewidth=1,gridwidth=0.2, linecolor='grey', gridcolor='rgba(192,192,192,0.5)')


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
                        row_width=[0.3, 0.8, 0.2],
                        specs=[[{"rowspan":2}],
                        [None],
                        [{}]])

    fig.add_trace(go.Scatter(x=df.Date, y=df['Close'], name='Close', mode='lines+markers',marker_size=4,
    line=dict(color='royalblue')),
                row=1, col=1)

    fig.add_trace(go.Scatter(x=df.Date, y=df['long_mavg'], name='long_mvg 50',mode='lines',
        line=dict(color='orange',dash='dash')),
                row=1, col=1)

    fig.add_trace(go.Scatter(x=df.Date, y=df['short_mavg'], name='short_mvg 10',mode='lines',
        line=dict(color='firebrick')),
                row=1, col=1)

    fig.add_trace(go.Scatter(x=df.Date[df.positions==1], y=df.short_mavg[df.positions==1], 
    name='crossing',mode='markers', marker_symbol='triangle-up', marker_size=10, marker_color='green'),
                row=1, col=1)

    fig.add_trace(go.Scatter(x=df.Date, y=df['Aroon_Up'], name='Aroon Up', mode='lines',
        line=dict(color='green')),
                row=3, col=1)

    fig.add_trace(go.Scatter(x=df.Date, y=df['Aroon_Down'], name='Aroon Down', mode='lines',\
        line=dict(color='red')),
                row=3, col=1)


    fig.update_traces(line_width=1.5)
    fig.update_layout(
    title='Trend Reversal Detection (AAPL)',
    width=1400,
    height=900,
    plot_bgcolor='rgba(0,0,0,0)',
    margin=dict(
    autoexpand=False,
    l=100,
    r=20,
    t=110,
    ),
    legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1
)
    )
    fig.update_yaxes(showline=False, linewidth=1,gridwidth=0.2, linecolor='grey', gridcolor='rgba(192,192,192,0.5)')

    fig['layout']['xaxis2']['title']='Date'
    fig['layout']['yaxis']['title']='Close'
    fig['layout']['yaxis2']['title']='Aroon'

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
        table_chart = 'NASDAQ_20'
    else:
        table_chart = 'NYSE_20'

    qu=f"SELECT * FROM {table_chart} WHERE Symbol='{tick}'"
    df = db_acc_obj.exc_query(db_name='marketdata', query=qu,\
        retres=QuRetType.ALLASPD)

    fig = go.Figure()

    fig = make_subplots(rows=3, cols=1,
                        shared_xaxes=True,
                        vertical_spacing=0.1,
                        row_width=[0.3, 0.8, 0.2],
                        specs=[[{"rowspan":2}],
                        [None],
                        [{}]])

    fig.add_trace(go.Scatter(x=df['Date'], y=df['Close'], name='Close', mode='lines',
    line=dict(color='royalblue')),row=1, col=1)

    fig.add_trace(go.Scatter(x=df['Date'], y=df['Volume'], name='Volume', mode='lines',
    line=dict(color='black')), row=3, col=1)

    fig.update_layout(
        plot_bgcolor='white',
        width=1400,
        height=800,
        margin=dict(
        autoexpand=False,
        l=100,
        r=20,
        t=110,
    )
    )

    fig['layout']['xaxis2']['title']='Date'
    fig['layout']['yaxis']['title']='Close'
    fig['layout']['yaxis2']['title']='Volume'
    fig.update_yaxes(showline=False, linewidth=1,gridwidth=0.2, linecolor='grey', gridcolor='rgba(192,192,192,0.5)')

    lineJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return lineJSON

