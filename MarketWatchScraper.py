import requests
from bs4 import BeautifulSoup
import lxml
import pandas as pd
from urllib.parse import urljoin
from datetime import datetime
date = 'Date: ' + datetime.now().strftime('%d.%m.%Y, Time: %H:%M:%S')
print(date)

# First we need to create a Dictionary with Stocknames and their url Symbols
stocks = ({
    'Apple Inc.':'aapl',
    'Bitcoin USD':'btcusd',
    'Dow Jones U.S. Total Stock Market Index':'dwcf',
    'MSCI Inc.':'msci'
})

# Crawler function for stocks
def stockCrawler(x):
    shortname = x
    baseurl = 'https://www.marketwatch.com/investing/stock/'
    url = urljoin(baseurl,x)
    r = requests.get(url)
    page = BeautifulSoup(r.text,'lxml')
    intraday = page.find('div',{'class':'intraday__data'})
    price = intraday.find('bg-quote',{'class':'value'}).text
    currency = intraday.find('sup', {'class': 'character'}).text
    str_price = str(currency)+str(price)
    afterchange_poi = intraday.find('bg-quote',{'class':'intraday__change'}).text.strip().split('\n')[0]
    afterchange_per = intraday.find('bg-quote',{'class':'intraday__change'}).text.strip().split('\n')[1]
    closingprice = page.find('div', {'class': 'intraday__close'}).find_all('tr', {'class': 'table__row'})[1].text.strip().split('\n')[0]
    keydata = page.find('div',{'class':'element element--list'}).find_all('span', {'class':'primary'})
    dayrange = keydata[1].text
    wr52 = keydata[2].text
    performance = page.find('div',{'class':'element element--table performance'}).find('tbody')
    onemonth = performance.find_all('li',{'class':'content__item value ignore-color'})[1].text

    row = [shortname,str_price,afterchange_poi,afterchange_per,closingprice,dayrange,wr52,onemonth]
    return row

# Creating a Dataframe to save the Stockdata
headers = ['shortname','price','CHG','CHG(%)','last close','dayrange','52 weekrange','1M performance']
stockdata = pd.DataFrame(columns = headers)

# If you want to get the prices for all the stocks in the dictionary
for s in stocks:
    stockdata.loc[len(stockdata)] = stockCrawler(stocks[s])
print(stockdata)

# Deleting a range of rows in the Df
stockdata = stockdata.drop([0,len(stockdata)-1])
# How to clear all the rows in the Df
stockdata = stockdata[0:0]
#stockdata.drop(stockdata.index,inplace=True)

# If you just want to inspect a single stock
stockdata = pd.DataFrame(columns = headers)
stockdata.loc[len(stockdata)]= stockCrawler(stocks['Apple Inc.'])
print(stockdata)