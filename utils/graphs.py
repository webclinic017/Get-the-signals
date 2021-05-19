import plotly
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from plotly.graph_objs import *
import pandas as pd
import numpy as np
import json
from utils.db_manage import QuRetType, std_db_acc_obj


db_acc_obj = std_db_acc_obj() 



def renameCols(df,names):
    '''
    replaces df col names with list of names (by index)

    :param 1: dataframe
    :param 2: list column names
    :returns: dataframe with new column names
    '''
    # Get a list of indices corresponding to number of cols, starting from 0
    indices = list(range(len(list(df.columns))))

    for i in indices:
        df.rename(columns={df.columns[i]: f"{names[i]}"}, inplace=True)

    return df


def TuplesToDF(items):
    '''
    Converts Tuple of Tuples to a dataframe
    '''
    df = pd.DataFrame(list(items))
    return df 




def lineNBSignals(dfitems):
    fig = go.Figure(data=go.Scatter(x=dfitems.index, y=dfitems.iloc[:, 0]))

    fig.update_traces(line_width=1.5)
    fig.update_layout(
    title=f'Evolution of the number of signals over time',
    #width=1400,
    plot_bgcolor='rgba(0,0,0,0)',
    )
    fig.update_yaxes(showline=False, linewidth=1,gridwidth=0.2, linecolor='grey', gridcolor='rgba(192,192,192,0.5)')

    lineJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return lineJSON



##### TABLE PAGE #######
def makeLinesSignal(tick):

    qu = f"SELECT t.*,t2.Gap FROM\
    (SELECT * FROM signals.Signals_details\
    WHERE Symbol='{tick}')t\
    LEFT JOIN \
    (SELECT * FROM marketdata.Technicals WHERE Ticker='{tick}')t2\
    ON t2.Date = t.Date;"

    df = db_acc_obj.exc_query(db_name='signals', query=qu, \
    retres=QuRetType.ALLASPD)

    fig = make_subplots(rows=7, cols=1,
                        shared_xaxes=True,
                        vertical_spacing=0.03,
                        row_width=[0.15, 0.15, 0.15, 0.15, 0.15,0.15,0.30],
                        specs=[[{"rowspan":2}],
                        [None],
                        [{}],
                        [{}],
                        [{}],
                        [{}],
                        [{}]
                        ])
    fig.add_trace(go.Candlestick(x=df.Date,open=df.Open,close=df.Close,low=df.Low,high=df.High),
                row=1, col=1)

    fig.update_layout(xaxis_rangeslider_visible=False)
    
    fig.add_trace(go.Scatter(x=df.Date, y=df['long_mavg'], name='long_mvg 50',mode='lines',
        line=dict(color='orange',dash='dash')),
                row=1, col=1)

    fig.add_trace(go.Scatter(x=df.Date, y=df['short_mavg'], name='short_mvg 10',mode='lines',
        line=dict(color='royalblue')),
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

    fig.add_trace(go.Scatter(x=df.Date, y=df['Volume'], name='Volume', mode='lines',\
        line=dict(color='purple')),
                row=4, col=1)

    fig.add_trace(go.Scatter(x=df.Date, y=df['diff_stock_bench'], name='diff_stock_bench', mode='lines',\
        line=dict(color='purple')),
                row=5, col=1)


    fig.add_trace(go.Scatter(x=df.Date, y=df['rolling_mean_35'], name='rolling_mean_35', mode='lines',\
        line=dict(color='red')),
                row=6, col=1)
    
    fig.add_trace(go.Scatter(x=df.Date, y=df['RSI'], name='RSI', mode='lines',\
        line=dict(color='Orange')),
                row=7, col=1)

    fig.update_yaxes(showline=False, linewidth=1,gridwidth=0.2, linecolor='grey', gridcolor='rgba(192,192,192,0.5)',zeroline=True,zerolinewidth=1,zerolinecolor='black')


    fig.update_traces(line_width=1.5)
    fig.update_layout(
    title=f'Trend Reversal Detection ({tick})',
    #width=1400,
    height=1100,
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


    fig['layout']['xaxis6']['title']='Date'
    fig['layout']['yaxis']['title']='Price'
    fig['layout']['yaxis2']['title']='Aroon'
    fig['layout']['yaxis3']['title']='Volume'
    fig['layout']['yaxis4']['title']='diff_stock_bench'
    fig['layout']['yaxis5']['title']='rolling_mean_35'
    fig['layout']['yaxis6']['title']='RSI'


    annotations = []

    annotations.append(dict(xref='paper', yref='paper', x=0, y=-0.09,
                              xanchor='left', yanchor='top',
                              #text='Log scale is used for vol. to have better grasp incoming vol on smaller caps',
                              font=dict(family='Arial',
                                        size=12,
                                        color='rgb(150,150,150)'),
                              showarrow=False))
    
    fig.update_layout(annotations=annotations)
    

    lineJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return lineJSON






def makeOwnershipGraph(items, tick):


    names = ["No","Ticker","MarketCap","SharesOutstanding","SharesFloat","InsiderOwnership",\
        "InsiderTransactions","InstitutionalOwnership","InstitutionalTransactions","FloatShort",\
            "ShortRatio","AverageVolume","Price","Change","Volume","Date"]

    df = TuplesToDF(items)
    df = renameCols(df,names)

    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Scatter(x=df['Date'], y=df['Price'],
                    mode='lines+markers',
                    name='Price'),secondary_y=True,)

    fig.add_trace(go.Scatter(x=df.Date, y=df['InstitutionalTransactions'], \
        name='InstitutionalTransactions', mode='lines+markers',marker_size=4,
    line=dict(color='firebrick')),secondary_y=False,)

    fig.add_trace(go.Scatter(x=df.Date, y=df['FloatShort'], \
    name='FloatShort', mode='lines+markers',marker_size=4,
    line=dict(color='#9467bd',dash='dash')),secondary_y=False,)

    fig.update_yaxes(title_text="<b> Price ($) </b>", secondary_y=True)
    fig.update_yaxes(title_text="<b> InstitutionalTransactions <br> & FloatShort (%)</b>", secondary_y=False)
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