import plotly
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots
from plotly.graph_objs import *
import pandas as pd
import numpy as np
import json
from utils.db_manage import QuRetType, std_db_acc_obj
from utils.fetchData import fetchTechnicals, fetchOwnership


db_acc_obj = std_db_acc_obj() 

def makeOwnershipGraph(items, tick):

    def TuplesToDF(items):
        df = pd.DataFrame(list(items))
        return df 

    def renameCols(df):
        '''
        By index
        '''
        df.rename(columns={ df.columns[0]: "No",
         df.columns[1]: "Ticker",
         df.columns[2]: "MarketCap",
         df.columns[3]: "SharesOutstanding",
         df.columns[4]: "SharesFloat",
         df.columns[5]: "InsiderOwnership",
         df.columns[6]: "InsiderTransactions", 
         df.columns[7]: "InstitutionalOwnership",         
         df.columns[8]: "InstitutionalTransactions",
         df.columns[9]: "FloatShort",
         df.columns[10]: "ShortRatio",
         df.columns[11]: "AverageVolume",
         df.columns[12]: "Price",
         df.columns[13]: "Change",
         df.columns[14]: "Volume",
         df.columns[15]: "Date"}, inplace = True)

        return df

    df = TuplesToDF(items)
    df = renameCols(df)

    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Scatter(x=df['Date'], y=df['Price'],
                    mode='lines+markers',
                    name='Price'),secondary_y=True,)

    fig.add_trace(go.Scatter(x=df.Date, y=df['InstitutionalTransactions'], \
        name='InstitutionalTransactions', mode='lines+markers',marker_size=4,
    line=dict(color='firebrick')),secondary_y=False,)

    fig.update_yaxes(title_text="<b> Price</b>", secondary_y=True)
    fig.update_yaxes(title_text="<b> InstitutionalTransactions</b>", secondary_y=False)
    fig.update_yaxes(showline=False, showgrid=False, secondary_y=False)


    fig.update_traces(line_width=1.5)
    fig.update_layout(
    title=f'Ownership ({tick})',
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
   
    lineJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return lineJSON


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
        xaxis_title="SignalDate",
        yaxis_title="Avg. Return",
        font=dict(size=10),
        #width=1400,
        #height=390,
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(
        autoexpand=False,
        l=100,
        r=20,
        t=110,
        ))


    fig.update_yaxes(showline=False, linewidth=1,gridwidth=0.2, linecolor='grey', gridcolor='rgba(192,192,192,0.5)',zeroline=True,zerolinewidth=1,zerolinecolor='black')


    lineJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return lineJSON



def makeLinesSignal(tick):

    qu = f"SELECT * FROM signals.Signals_details WHERE Symbol='{tick}' \
    ORDER BY Date"
    df = db_acc_obj.exc_query(db_name='signals', query=qu, \
    retres=QuRetType.ALLASPD)

    print(df)

    fig = make_subplots(rows=3, cols=1,
                        shared_xaxes=True,
                        vertical_spacing=0.12,
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
    name='MA crossing',mode='markers', marker_symbol='triangle-up', marker_size=10, marker_color='blue'),
                row=1, col=1)
    
    fig.add_trace(go.Scatter(x=df.Date[df.doubleSignal==1], y=df.short_mavg[df.doubleSignal==1], 
    name='Double Signal',mode='markers', marker_symbol='triangle-up', marker_size=15, marker_color='green'),
                row=1, col=1)

    fig.add_trace(go.Scatter(x=df.Date, y=df['Aroon_Up'], name='Aroon Up', mode='lines',
        line=dict(color='green')),
                row=3, col=1)

    fig.add_trace(go.Scatter(x=df.Date, y=df['Aroon_Down'], name='Aroon Down', mode='lines',\
        line=dict(color='red')),
                row=3, col=1)


    fig.update_traces(line_width=1.5)
    fig.update_layout(
    title=f'Trend Reversal Detection ({tick})',
    #width=1400,
    height=600,
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
                        vertical_spacing=0.12,
                        row_width=[0.3, 0.8, 0.2],
                        specs=[[{"rowspan":2}],
                        [None],
                        [{}]])

    fig.add_trace(go.Scatter(x=df['Date'], y=df['Close'], name='Close', mode='lines',
    line=dict(color='royalblue')),row=1, col=1)

    fig.add_trace(go.Scatter(x=df['Date'], y=df['Volume'], name='Volume', mode='lines',
    line=dict(color='black')), row=3, col=1)
    fig.update_yaxes(showline=False,linewidth=1,gridwidth=0.2, linecolor='grey', gridcolor='rgba(192,192,192,0.5)')

    fig.update_layout(
        plot_bgcolor='white',
        #width=1400,
        height=650,
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

    lineJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return lineJSON

