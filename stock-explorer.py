import streamlit as st
import pandas as pd
import datetime
import numpy as np 
import pandas_datareader.data as web
from pandas import Series, DataFrame
import matplotlib.pyplot as plt
from matplotlib import style
import matplotlib as mpl
import altair as alt
#import yfinance as yf
#yf.pdr_override()
###https://github.com/ranaroussi/yfinance

from pytickersymbols import PyTickerSymbols

stock_data = PyTickerSymbols()
countries = stock_data.get_all_countries()
indices = stock_data.get_all_indices()
industries = stock_data.get_all_industries()

max_width = 100
padding_top = 1
padding_right = 5
padding_left = 5
padding_bottom = 20
color ='Black'
backgr = 'white'

st.markdown(
        f"""
<style>
    .reportview-container .main .block-container{{
        max-width: {max_width}vw;
        padding-top: {padding_top}rem;
        padding-right: {padding_right}rem;
        padding-left: {padding_left}rem;
        padding-bottom: {padding_bottom}rem;
    }}
    .reportview-container .main {{
        color: {color};
        background-color: {backgr};
    }}
</style>
""",
        unsafe_allow_html=True,
    )

peers_to_pick = ['Endeavour Silver','Silver Index','Gold Index','Barrick Gold','Gold Index', 'Silver Index', 'Apple Inc', 'Tesla','WTI Oil','Fortuna Silver','First Majestic','Pan American Silver','Fresnillo Silver','Wheaton Precious Metals','Hecla Mining','Hochschild Mining','Newmont Gold','Gea Group','Krones','ZS','OKTA','Crowdstrike','TMICY','PLTR','RDS-A','BPAQF','COP']
stockdict = {'Endeavour Silver': 'EXK','Fortuna Silver':'FSM','First Majestic':'AG','Silver Index':'SI=F','Gold Index':'GC=F','Barrick Gold':'GOLD','Pan American Silver':'PAAS','Fresnillo Silver':'FRES.L','Wheaton Precious Metals':'WPM','Hecla Mining':'HL','Newmont Gold':'NEM','Tesla Inc':'TSLA','Apple Inc':'AAPL','WTI Oil':'CL=F','Hochschild Mining':'HCHDF','GEA Group':'G1A.DE','Krones':'KRN.DE','Crowdstrike':'CRWD'}
selected_default = ['Endeavour Silver','Silver Index','Gold Index']
selected_deffund = ['Endeavour Silver','Barrick Gold','Fortuna Silver','First Majestic']
list_of_markets = ['DAX','MDAX','SDAX','TECDAX','DOW JONES','FTSE 100','NASDAQ 100','S&P 500']
#mainstock = st.sidebar.selectbox('Aktien auswählen',stocks_to_pick)


st.title('Aktien-Analyse und Trading-Signale')
#st.write('Bitte Tickersymbol links in Seitennmenü auswählen')

st.sidebar.write("hello schmiedevs")
pairs = st.sidebar.checkbox('Basisanalyse')
fundamentals = st.sidebar.checkbox('Vergleich Fundamentaldaten')
commodities = st.sidebar.checkbox('Commodity Pairs')

st.sidebar.write('Beobachtungszeitraum wählen')
start = st.sidebar.date_input('Start Datum',datetime.date(2018, 1, 1))
end = st.sidebar.date_input('End Datum',datetime.date.today())


st.sidebar.write('''todos

    -Währung umstellen
    -Automatically compare all pairs and see if they mostly correlated in the past yet there is a current spread
    -Second screen for permanent pairs "asset class screen"
    ''')




#@st.cache 
def get_data(ticker_symbol):
    df = web.DataReader(ticker_symbol, 'yahoo', start, end)
    return df


def stock_financials(stock):
    df_ticker = web.get_quote_yahoo(mainstock)
    try:
        volat_df = web.DataReader(mainstock,'yahoo',start=start,end=end)['Adj Close']
        analysis = volat_df.std()
        longName = df_ticker['longName']
        fiftyrange = df_ticker['fiftyTwoWeekRange']
        sharesout = df_ticker['sharesOutstanding']
        sharesout2 = f"{sharesout.values[0]:,}"
        bookval = df_ticker['bookValue']
        marketcap = df_ticker['marketCap']
        marketcap2 = f"{marketcap.values[0]:,}"
        
        pricetobook = df_ticker['priceToBook']
        lastPrice = df_ticker['price']
        st.subheader('Fundamentaldaten für {}'.format(longName.to_string(index=False)))
        st.write('Marktkapitalisierung: {} $'.format(marketcap2.format(marketcap2).replace(',','.')))
        st.write('Buchwert: {} $'.format(bookval.to_string(index=False)))
        st.write('Preis zu Buchwert Ratio: {} '.format(pricetobook.to_string(index=False)))
        st.write('Ausstehende Aktien: {} Stück'.format(sharesout2.format(sharesout2).replace(',','.')))
        st.write('52 Wochen Spanne: {} $'.format(fiftyrange.to_string(index=False)))
        st.write('Letzter Kurs: {} $'.format(lastPrice.to_string(index=False)))
        st.write('Volatilität - Std.Abw.: {} $'.format(analysis.round(3)) )
    except:
        st.write("Kopfdaten für Ticker {} leider nicht vollständig verfügbar".format(stock))
        analysis = volat_df.std()
        fiftyrange = df_ticker['fiftyTwoWeekRange']
        lastPrice = df_ticker['price']
        st.write('52 Wochen Spanne: {} $'.format(fiftyrange.to_string(index=False)))
        st.write('Letzter Kurs: {} $'.format(lastPrice.to_string(index=False)))
        st.write('Volatilität - Std.Abw.: {} $'.format(analysis.round(3)) )


def plot_datatails(stock):
    st.subheader('Auszug Rohdaten für Tickersymbol {}'.format(stock))
    st.write(df.tail())

def create_linecharts(stock):
    st.subheader('Kursverlauf {} bis {}'.format(start,end))
    df['mAvg'] = df['Adj Close'].rolling(window=100).mean()
    df2 = df[['Adj Close','mAvg']]
    chart1 = st.line_chart(df2)


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


def returns_chart(stock):
    st.subheader('Rendite je Handelstag')
    rets = df['Adj Close'] / df['Adj Close'].shift(1) - 1
    st.bar_chart(rets)


def normalize_data(df):
    min = df.min()
    max = df.max()
    x = df 
    y = (x - min) / (max - min)
    return y



def create_normalized_linecharts(mainstock,comparestock):
    if comparestock != mainstock :
        st.subheader('Normalisierter Kursverlauf')
        close_px = web.DataReader([mainstock,comparestock],'yahoo',start=start,end=end)['Adj Close']
        norm_px = normalize_data(close_px)
        norm_px.columns = [mainstock,comparestock]
        st.line_chart(norm_px)
    else:
        st.write("Bitte Vergleichswert auswählen")


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



def peer_review_menu():
    st.title('Peer-Group Analyse')
    st.write('Aktien zum Direktvergleich auswählen')
    
    

def peer_review(stocklist):
    peerdata = web.DataReader(stocklist,'yahoo',start=start,end=end)['Adj Close']
    peer_norm = normalize_data(peerdata)
    peer_norm.columns = stocklist
    st.line_chart(peer_norm)
    

    retscomp = peerdata.pct_change()
    corr = retscomp.corr()
    st.subheader('Auszug Korrelationsdaten')
    st.write(corr.head())
    
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    ax = fig.add_subplot(1,1,1)
    plt.figure(figsize=(20,10))

    ax.scatter(
        peer_norm[stocklist[0]],
        peer_norm[stocklist[1]],
    )

    ax.set_xlabel(stocklist[0])
    ax.set_ylabel(stocklist[1])
    st.subheader('Korrelationsmatrix Scatterplot')
    st.pyplot(fig)

def get_stocks(stock_index):
    stock_tickers = []
    stock_data = PyTickerSymbols()
    list_stocks = stock_data.get_stocks_by_index(stock_index)
    #st.write(list(german_stocks))
    for i in list_stocks:
        tickersymbol = i['symbols'][0]['yahoo']
        stock_tickers.append(tickersymbol)
    df = web.get_quote_yahoo(stock_tickers)
    df.set_index('shortName',inplace=True, drop=True)
    st.write(df[['marketCap','bookValue','price','priceToBook','fiftyDayAverage','fiftyTwoWeekRange','bidSize','askSize']])
    st.write(stock_tickers)

if pairs:
    defaultval = 'EXK'
    mainstock = st.text_area("Bitte Ticker Symbol eingeben (z.b. EXK)",defaultval)
    submit1 = st.button('Abfragen')    
    df = get_data(mainstock)

    stock_financials(mainstock)
    plot_datatails(mainstock)
    create_linecharts(mainstock)
    volume_charts(mainstock)
    returns_chart(mainstock)
    st.title('Referenzwert und Normalisierung')
    #dictval = stockdict.index(mainstock)
    #st.write(dictval)
    #if dictval in peers_to_pick:
    #   peers_to_pick.pop(mainstock)
    comparestock_raw = st.selectbox('Vergleichswert auswählen',peers_to_pick)
    comparestock = stockdict.get(comparestock_raw)
        
    create_normalized_linecharts(mainstock,comparestock)
    kaufsignal(mainstock,comparestock)
    create_ratiochart(mainstock,comparestock)

    stocklist_raw = st.multiselect('Aktien auswählen',peers_to_pick,selected_default)

    stocklist = []
    for item in stocklist_raw:
        stocklist.append(stockdict.get(item))
        
    peer_review_menu()
    peer_review(stocklist)

elif commodities:
    st.title('Gold-Silber Ratio')
    create_ratiochart('SI=F','GC=F')
    st.title('Gold-Öl Ratio')
    create_ratiochart('CL=F','GC=F')

    
    
elif fundamentals:

    st.subheader('Fundamentalanalayse')
    stocklist_fund = st.multiselect('Aktien auswählen',peers_to_pick,selected_deffund)

    stocklist = []
    for item in stocklist_fund:
        stocklist.append(stockdict.get(item))
        
    df = web.get_quote_yahoo(stocklist)
    df.set_index('shortName',inplace=True, drop=True)
    st.write(df[['marketCap','bookValue','price','priceToBook','fiftyDayAverage','fiftyTwoWeekRange','bidSize','askSize']])

    
    more_data = st.button('Aktienindizes durchsuchen')
    st.write('Abfragedauer ca 1 Minute. Nach Ladevorgang: Klick auf Spalten um Werte zu sortieren')
    if more_data:
        get_all_tickers = st.selectbox('Aktien Index auswählen',list_of_markets)
        get_stocks(get_all_tickers)
    


else:
    st.write('Bitte im Menü links einen Analaysescreen auswählen')




