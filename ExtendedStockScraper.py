import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import openpyxl
import re
import time
from datetime import datetime
date = 'Date: ' + datetime.now().strftime('%d.%m.%Y, Time: %H:%M:%S')
print(date)
#import lxml

# At first I'm loading an Excel file with all the sources (information and links) about the stocks I want to investigate
# This file also contains the data of my portfolio
path_sources = 'C:\\Users\\andre\\Documents\\Python\Web_Scraper\Stock-Market-Srapers\Stocks_Sources.xlsx'
sources = pd.read_excel(path_sources,sheet_name='Sources')

# Preparation of the first DataFrame for general informations about the stock market
stMaHeaders = ['name','type','price','CHG','CHG(%)','factor']
dfStMarket = pd.DataFrame(columns = stMaHeaders)

# This is a function that extracts data from my excel file and scrapes data from a finance webpage
def stockMarketScraper(x):
    time.sleep(.1)
    r = requests.get(x[1]['link'])
    soup = BeautifulSoup(r.text, 'html.parser')
    name = x[1]['shortname']
    category = x[1]['category']
    price, plusminus, percent = np.zeros(3)
    try:
        values = [e.text.strip() for e in soup.find('div', {'class': 'snapshot__values'}) if len(e) >= 3]
    except:
        pass
    if len(values) >= 3:
        c_val = [re.sub("[^ \w\%.,+-]", "", e) for e in values]
        price = c_val[0]
        if len(price) > 1 and price[-1].isalpha():
            price = f'{price[:-3]} {price[-3:]}'
        plusminus = c_val[-2]
        if not plusminus[-1].isdigit():
            plusminus = re.sub(r"(\w{3}$)", r" \1", plusminus)
        percent = c_val[-1]
    factor = float(re.sub('[.%a-zA-Z+-]', '', price).replace(',', '.'))
    if price == 0:
        price = 'NaN'
    datarow = [name,category,price,plusminus,percent,factor]
    return datarow

# I'm selecting and saving the stockmarket data I want to scrape:
for row in sources.iterrows():
    if row[1]['category'] == 'Index' or row[1]['category'] == 'currency':
        dfStMarket.loc[len(dfStMarket)] = stockMarketScraper(row)

# changing the start of the df index to 1
dfStMarket.index = dfStMarket.index + 1
# to check the result
#print(dfStMarket)


# Preparation of the dataframe Portfolio
poHeaders = ['name','category','current price','52W High','52W Low']
dfPrices = pd.DataFrame(columns = poHeaders)


# Filtering of the sources-df (for stocks I'm invested in) and resetting the index
sources_f = sources[sources['numbers'] > 0].reset_index()
sources_f.index = sources_f.index +1


# Scraper function for my portfolio
def portfolioStockScraper(x):
    name = x['shortname']
    category = x['category']
    longHigh,longLow,price = np.zeros(3)

    # Portfolio Scraper
    time.sleep(.1)
    r = requests.get(x['link'])
    soup = BeautifulSoup(r.text, 'html.parser')
    if category == 'stocks':
        try:
            values = [e.text.strip() for e in soup.find('div', {'class': 'snapshot__values'}) if len(e) >= 3]
        except:
            try:
                values = [e.text.strip() for e in soup.find('div', {'class': 'table-responsive quotebox'}) if
                          len(e) >= 3]
            except:
                pass
        if (len(values) < 3 and len(values) >= 1) or len(re.sub("[.%a-zA-Z+-]", "", values[0])) <= 1:
            try:
                values = [e.text.strip() for e in soup.find('div', {'class': 'snapshot__values-second'}) if len(e) >= 3]
                c_val = [re.sub("[^ \w\%.,+-]", "", e) for e in values]
                price, plusminus, percent = c_val[:3]
            except:
                pass
        if price == 0 and (len(values) >= 1 and len(values[0]) < 3) and len(values[0]) > 3:
            valj = ''.join(values)
            c_val = re.sub("[^ \w\%.,+-]", " ", valj).split(' ')
            if len(c_val) >= 3:
                price, plusminus, percent = c_val[:3]
        if price == 0 and len(values) >= 3:
            c_val = [re.sub("[^ \w\%.,+-]", "", e) for e in values]
            price, plusminus, percent = c_val[:3]

        table = soup.find_all('table', {'class': 'table table--content-right table--headline-first-col'})
        for t in table:
            if 'EUR' in t.find_all('td')[1].text:
                longHigh = t.find_all('td')[13].text.split(' ')[0]
                longLow = t.find_all('td')[15].text.split(' ')[0]

    elif category == 'funds':
        price = soup.find('div', {'class':'table-responsive quotebox'}).find('td').text.replace(' ','')
        tablef = soup.find_all('div', {'id': 'SnapshotQuoteData'})[0].find_all('td')
        longHigh = tablef[-2].text.split(' ')[0]
        longLow = tablef[-1].text.split(' ')[0]

    elif category == 'currency':
        price = dfStMarket.loc[x['index']]['price']
        tables = soup.find('table', {'class': 'table table--headline-first-col table--content-right'})
        if tables != None:
            tables = tables.find_all('tr')[-2:]
            longHigh = tables[-1].find_all('td')[-1].text.split(' ')[0]
            longLow = tables[-2].find_all('td')[-1].text.split(' ')[0]

    def dollar (conv = 1):
        conv = float(dfStMarket[dfStMarket['name'] == 'Dollar']['factor'])
        return conv

    if 'usd' in str(price).lower():
        price = float(re.sub('[ .%a-zA-Z+-]', '', str(price)).replace(',', '.'))/ dollar()
    else:
        price = float(re.sub('[ .%a-zA-Z+-]', '', str(price)).replace(',', '.'))

    datarow = [name,category,price,longHigh,longLow]
    return datarow

# Saving the scraped data into the dataframe Prices
for row in sources_f.iterrows():
    dfPrices.loc[len(dfPrices)] = portfolioStockScraper(row[1])
dfPrices.index = dfPrices.index + 1


# Concatenation of the data to a complete DataFrame about my portfolio
columns = [
    dfPrices['name'].astype(str),
    dfPrices['category'].astype(str),
    sources_f['numbers'].astype(float),
    sources_f['buyingcourse'].astype(float),
    dfPrices['current price'].astype(float),
    sources_f['asset base'].astype(float),
    dfPrices['52W High'].astype(str),
    dfPrices['52W Low'].astype(str)
]
dfPf = pd.concat(columns, axis = 1)


# Based on the data I can calculate my current asset as well as earnings and losses for every stock
dfPf['current asset'] = dfPf['numbers'] * dfPf['current price']
dfPf['win/loss(EUR)'] = dfPf['current asset'] - dfPf['asset base']
dfPf['win/loss(%)'] = (dfPf['current asset'] - dfPf['asset base']) / dfPf['asset base'] * 100

# values in total
asset_base = round(sum(dfPf['asset base']),2)
depot_value = round(sum(dfPf['current asset']),2)
win_loss = round(sum(dfPf['win/loss(EUR)']),2)
win_lossP = round(((depot_value - asset_base) / asset_base*100),2)

total = [asset_base,depot_value,win_loss,win_lossP]
total = [format(round(t,2),'.2f') for t in total]

# Calculation of customized Portfolio categories
asiaflist = ['MSCI Asia','MSCI China','MSCI India']

currencies = sum(dfPf[dfPf['category'] == 'currency']['current asset'])
stocks = sum(dfPf[dfPf['category'] == 'stocks']['current asset'])
dfFunds = dfPf[dfPf['category'] == 'funds']
asiafunds = sum(dfFunds[dfFunds['name'].isin(asiaflist)]['current asset'])
worldfunds = sum(dfFunds[~dfFunds['name'].isin(asiaflist)]['current asset'])

dfCat = pd.DataFrame({
    'name':['Currencies','Stocks','Asiafunds','Worldfunds'],
    'value':[currencies,stocks,asiafunds,worldfunds]},
     index=range(4))

dfCat['value'] = dfCat['value'].astype(float).round(decimals=2)

dfCat['parts'] = dfCat['value']/np.sum(dfCat['value'])*100
dfCat['parts'] = dfCat['value'].astype(float).round(decimals=2)


# print(dfPf.columns)
# I'm not satisfied with the order of the columns yet
newOrder = ['name','category','numbers','buyingcourse','current price','asset base','current asset','win/loss(EUR)',\
'win/loss(%)', '52W High', '52W Low']
dfPf = dfPf.reindex(columns = newOrder)


# Reformatting with replace, regex, etc. and saving the strings in dfPfStr
dfPfStr = dfPf

dfPfStr['numbers'] = dfPfStr['numbers'].astype(str)
numberlist = [round(float(n),10) for n in dfPf['numbers']]
numberlist = [(str(int(n)) if str(n)[-2:] == '.0' else str(n).replace('.',',')) for n in numberlist]
dfPfStr['numbers'] = numberlist

dfPfStr['buyingcourse'] = dfPfStr['buyingcourse'].round(decimals=2).astype(str)
dfPfStr['buyingcourse'] = [re.sub(r"(\d+)(\d{3})\.(\d{2})$", r"\1.\2,\3",str('{:.2f}'.format(float(i)))) \
    if len('{:.2f}'.format(float(i))) > 6 else str('{:.2f}'.format(float(i))).replace('.',',') for i in dfPfStr['buyingcourse']]

dfPfStr['current price'] = dfPfStr['current price'].round(decimals=2).astype(str)
dfPfStr['current price'] = [re.sub(r"(\d+)(\d{3})\.(\d{2})$", r"\1.\2,\3",str('{:.2f}'.format(float(i)))) \
    if len('{:.2f}'.format(float(i))) > 6 else str('{:.2f}'.format(float(i))).replace('.',',') for i in dfPfStr['current price']]

dfPfStr['asset base'] = dfPfStr['asset base'].round(decimals=2).astype(str)
dfPfStr['asset base'] = [re.sub(r"(\d+)(\d{3})\.(\d{2})$", r"\1.\2,\3",str('{:.2f}'.format(float(i)))) \
    if len('{:.2f}'.format(float(i))) > 6 else str('{:.2f}'.format(float(i))).replace('.',',') for i in dfPfStr['asset base']]

dfPfStr['current asset'] = dfPfStr['current asset'].round(decimals=2).astype(str)
dfPfStr['current asset'] = [re.sub(r"(\d+)(\d{3})\.(\d{2})$", r"\1.\2,\3",str('{:.2f}'.format(float(i)))) \
    if len('{:.2f}'.format(float(i))) > 6 else str('{:.2f}'.format(float(i))).replace('.',',') for i in dfPfStr['current asset']]

dfPfStr['win/loss(EUR)'] = dfPfStr['win/loss(EUR)'].round(decimals=2).astype(str)
dfPfStr['win/loss(EUR)'] = [re.sub(r"(\w+)(\d{3})\.(\d{2})$", r"\1.\2,\3",str('{:.2f}'.format(float(i)))) \
    if len('{:.2f}'.format(float(i))) > 6 else str('{:.2f}'.format(float(i))).replace('.',',') for i in dfPfStr['win/loss(EUR)']]

dfPfStr['win/loss(%)'] = dfPfStr['win/loss(%)'].round(decimals=2).astype(str)
dfPfStr['win/loss(%)'] = [str('{:.2f}'.format(float(i))).replace('.',',') for i in dfPfStr['win/loss(%)']]

totStr = [re.sub(r"(\w+)(\d{3})\.(\d{2})$", r"\1.\2,\3",str('{:.2f}'.format(float(i)))) \
    if len('{:.2f}'.format(float(i))) > 6 else str('{:.2f}'.format(float(i))).replace('.',',') for i in total]


# Finally I'm appending the calculations in a row to the Dataframe
dfPfStr.loc[len(dfPfStr.index)+1] = ['total','all','','','',totStr[0],totStr[1],totStr[2],totStr[3],'','']
#print(dfPfStr)


# You can also export the DataFrames to Excel
path = "C:\\Users\\andre\\OneDrive\Desktop\Stock_Scraper.xlsx"
with pd.ExcelWriter(path, engine='openpyxl') as writer:
    dfStMarket.to_excel(writer,sheet_name='Market')
    dfPf.to_excel(writer,sheet_name='Portfolio')
    dfPfStr.to_excel(writer,sheet_name='Full Portfolio')
    dfCat.to_excel(writer,sheet_name='Categories')
