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




def makeHistogram(items):

    df = pd.DataFrame(list(items), columns=['ValidTick',
        'SignalDate',
        'ScanDate',
        'NScanDaysInterval',
        'PriceAtSignal',
        'LastClostingPrice',
        'PriceEvolution',
        'Company',
        'Sector',
        'Industry'])


    df['PriceEvolution'] = pd.to_numeric(df['PriceEvolution'])    
    df = df[(df['PriceEvolution']!=0)]
    dfPivoted = pd.pivot_table(df, values='PriceEvolution',index=['SignalDate'], aggfunc=np.mean)

    dfMin = df[(df['LastClostingPrice'] < 15)]
    dfMid = df[(df['LastClostingPrice'] >= 15) & (df['LastClostingPrice'] <= 60)]
    dfMax = df[(df['LastClostingPrice'] > 60)]

    dfPivotedMin = pd.pivot_table(dfMin, values='PriceEvolution',index=['SignalDate'], aggfunc=np.mean)
    dfPivotedMid = pd.pivot_table(dfMid, values='PriceEvolution',index=['SignalDate'], aggfunc=np.mean)
    dfPivotedMax = pd.pivot_table(dfMax, values='PriceEvolution',index=['SignalDate'], aggfunc=np.mean)

    meanMin = round(dfPivotedMin.PriceEvolution.mean(),2)
    meanMid = round(dfPivotedMid.PriceEvolution.mean(),2)
    meanMax = round(dfPivotedMax.PriceEvolution.mean(),2)


    #fig = go.Figure([go.Bar(x=dfPivoted.index, y=dfPivoted['PriceEvolution'])])
    fig = go.Figure(data=[
        go.Bar(name='<15$', x=dfPivoted.index, y = dfPivotedMin.PriceEvolution),
        go.Bar(name='>=15$ & <=60$', x=dfPivoted.index, y = dfPivotedMid.PriceEvolution),
        go.Bar(name='>60$', x=dfPivoted.index, y = dfPivotedMax.PriceEvolution)
    ])
    fig.update_layout(barmode='group')

    fig.update_layout(title='Average return, per starting Signal Date \
(ex: "the stocks signaled on the 22nd December have an average return of 45% until today") low price stocks.\
<br><b>Stocks caracterized by lower prices yield significantly higher returns than other price intervals.<b>',\
        xaxis_title="SignalDate",
        yaxis_title="Avg. Return (%)",
        font=dict(size=10),
        #width=1400,
        #height=390,
        plot_bgcolor='rgba(0,0,0,0)')

    
    fig.add_hline(y=dfPivotedMin["PriceEvolution"].mean(), annotation_text=f"{meanMin}%",line_dash="dot",\
        line=dict( color="blue", width=1),annotation_font_color="blue")
    fig.add_hline(y=dfPivotedMid["PriceEvolution"].mean(), annotation_text=f"{meanMid}%",line_dash="dot", \
        line=dict( color="red", width=1),annotation_font_color="red")
    fig.add_hline(y=dfPivotedMax["PriceEvolution"].mean(), annotation_text=f"{meanMax}%",line_dash="dot", \
        annotation_font_color="green", annotation_position="bottom left", line=dict( color="green", width=1))

    fig.update_yaxes(showline=False, linewidth=1,gridwidth=0.2, linecolor='grey', gridcolor='rgba(192,192,192,0.5)',zeroline=True,zerolinewidth=1,zerolinecolor='black')


    lineJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return lineJSON


def makeLinesSignal(tick):

    qu = f"SELECT * FROM signals.Signals_details WHERE Symbol='{tick}' \
    ORDER BY Date"
    df = db_acc_obj.exc_query(db_name='signals', query=qu, \
    retres=QuRetType.ALLASPD)


    fig = make_subplots(rows=5, cols=1,
                        shared_xaxes=True,
                        vertical_spacing=0.03,
                        row_width=[0.25, 0.25, 0.1, 0.25,0.25],
                        specs=[[{"rowspan":2}],
                        [None],
                        [{}],
                        [{}],
                        [{}]
                        ])
    """
    fig.add_trace(go.Scatter(x=df.Date, y=df['Close'], name='Close', mode='lines+markers',marker_size=4,
    line=dict(color='royalblue')),
                row=1, col=1)
    """
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

    fig.add_trace(go.Scatter(x=df.Date, y=df['TR'], name='TR', mode='lines',\
        line=dict(color='purple')),
                row=4, col=1)

    fig.add_trace(go.Scatter(x=df.Date, y=df['ATR'], name='ATR', mode='lines',\
        line=dict(color='blue')),
                row=4, col=1)

    fig.add_trace(go.Scatter(x=df.Date, y=df['Volume'], name='Volume', mode='lines',\
        line=dict(color='purple')),
                row=5, col=1)

    fig.update_traces(line_width=1.5)
    fig.update_layout(
    title=f'Trend Reversal Detection ({tick})',
    #width=1400,
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


    fig['layout']['xaxis4']['title']='Date'
    fig['layout']['yaxis']['title']='Price'
    fig['layout']['yaxis2']['title']='Aroon'
    fig['layout']['yaxis3']['title']='TR'
    fig['layout']['yaxis4']['title']='Volume'
    

    annotations = []

    annotations.append(dict(xref='paper', yref='paper', x=0, y=-0.09,
                              xanchor='left', yanchor='top',
                              text='Log scale is used for vol. to have better grasp incoming vol on smaller caps',
                              font=dict(family='Arial',
                                        size=12,
                                        color='rgb(150,150,150)'),
                              showarrow=False))

    fig.update_layout(annotations=annotations)
    

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

