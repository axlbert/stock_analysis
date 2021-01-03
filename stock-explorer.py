import streamlit as st
import pandas as pd
import datetime
import numpy as np 
import pandas_datareader.data as web
from pandas import Series, DataFrame
import matplotlib.pyplot as plt
from matplotlib import style
import matplotlib as mpl

stocks_to_pick = ['EXK','GOLD','GC=F', 'SI=F', 'AAPL', 'TSLA','CL=F']
compares_to_pick = ['EXK','GOLD','GC=F', 'SI=F', 'AAPL', 'TSLA','CL=F']


mainstock = st.sidebar.selectbox(
    'Aktien auswählen',
     stocks_to_pick)

st.title('Aktien-Analyse und Trading-Signale')
st.write('Bitte Tickersymbol links in Seitennmenü auswählen')

start = st.sidebar.date_input('Start Datum',datetime.date(2018, 1, 1))
end = st.sidebar.date_input('End Datum',datetime.date(2020, 12, 31))


st.sidebar.write('''todos
- fundamentaldaten einblenden
- ticker-suche im Dax und S&P500
- Peer Group Korrelationen
- Volatilität untersuchen
- Mapping Tickersymbol und Text
''')

selected_default = ['EXK','SI=F']
#stocklist = st.sidebar.multiselect('Aktien auswählen',stocks_to_pick,selected_default)

def get_data(ticker_symbol):
    df = web.DataReader(ticker_symbol, 'yahoo', start, end)
    return df

#@st.cache
df = get_data(mainstock)

def plot_datatails(stock):
    st.subheader('Auszug Rohdaten für Tickersymbol {}'.format(stock))
    st.write(df.tail())
plot_datatails(mainstock)

def create_linecharts(stock):
    st.subheader('Kursverlauf {} bis {}'.format(start,end))
    df['mAvg'] = df['Adj Close'].rolling(window=100).mean()
    df2 = df[['Adj Close','mAvg']]
    chart1 = st.line_chart(df2)
create_linecharts(mainstock)

def volume_charts(stock):
    st.subheader('Handelsvolumen für {}'.format(stock))
    closing = web.DataReader(mainstock,'yahoo',start=start,end=end)[['Adj Close','Volume']]
    fig, axs = plt.subplots()
    ax2=axs.twinx()
    axs.plot(closing['Volume'])
    axs.set_ylabel("Handelsvolumen",color="red",fontsize=10)
    #axs.set_ylim(1000000,10000000)
    ax2.plot(closing['Adj Close'],color="blue")
    ax2.set_ylabel("Schlusskurs",color="blue",fontsize=10)
    st.pyplot(fig)
volume_charts(mainstock)

def returns_chart(stock):
    st.subheader('Rendite je Handelstag')
    rets = df['Adj Close'] / df['Adj Close'].shift(1) - 1
    st.line_chart(rets)
returns_chart(mainstock)

def normalize_data(df):
    min = df.min()
    max = df.max()
    x = df 
    y = (x - min) / (max - min)
    return y


st.title('Vergleichswert und Normalisierung')

comparestock = st.selectbox(
    'Vergleichswert auswählen',
     compares_to_pick)

def create_normalized_linecharts(mainstock,comparestock):
    if comparestock != mainstock :
        st.subheader('Normalisierter Kursverlauf')
        close_px = web.DataReader([mainstock,comparestock],'yahoo',start=start,end=end)['Adj Close']
        norm_px = normalize_data(close_px)
        norm_px.columns = [mainstock,comparestock]
        st.line_chart(norm_px)
    else:
        st.write("Bitte Vergleichswert auswählen")
create_normalized_linecharts(mainstock,comparestock)

def kaufsignal(mainstock,comparestock):
    if comparestock != mainstock :
        first = web.DataReader(mainstock,'yahoo',start=start,end=end)['Adj Close']
        second = web.DataReader(comparestock,'yahoo',start=start,end=end)['Adj Close']
        mavg_first = first.rolling(200,center=True,min_periods=1).mean()
        mavg_second = second.rolling(200,center=True,min_periods=1).mean()
        first_r = round(first[-1],2)
        mavg_first_r = round(mavg_first[-1],2)
        second_r = round(second[-1],2)
        mavg_second_r = round(mavg_second[-1],2)
        st.write('{} steht aktuell bei {} $. Der rollierende Mittelwert liegt bei {} $'.format(mainstock,first_r,mavg_first_r))
        st.write('{} steht aktuell bei {} $. Der rollierende Mittelwert liegt bei {} $'.format(comparestock,second_r,mavg_second_r))
    else:
        st.write("Bitte Vergleichswert auswählen")
kaufsignal(mainstock,comparestock)

def create_ratiochart(mainstock,comparestock):
    first = web.DataReader(comparestock,'yahoo',start=start,end=end)['Adj Close']
    second = web.DataReader(mainstock,'yahoo',start=start,end=end)['Adj Close']
    ratio = first/second
    #ratio_norm = normalize_data(ratio)
    mavg = ratio.rolling(200,min_periods=1).mean()
    st.subheader('Kursverhältnis zwischen {} und {}'.format(mainstock,comparestock))
    fulldf = [ratio, mavg]
    result = pd.concat(fulldf, axis=1)
    result.columns = ['Ratio','MAVG']
    #chart1 = st.line_chart(result)
    st.line_chart(result)
    if mavg[-1] > ratio[-1]:
        st.write('**Verkaufs**empfehlung für {} .'.format(mainstock))
    else:
        st.write('**Kauf**empfehlung für {} .'.format(mainstock))

    #st.write(result.tail())
    st.write('MAVG liegt bei {} , aktuelle Ratio liegt bei {}'.format(round(mavg[-1],2),round(ratio[-1],2)))
    #st.bar_chart(mavg)
create_ratiochart(mainstock,comparestock)
