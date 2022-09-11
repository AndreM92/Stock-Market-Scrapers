import requests
from bs4 import BeautifulSoup
import lxml
import numpy as np
import pandas as pd
import openpyxl
import re
import time
from datetime import datetime
date = 'Date: ' + datetime.now().strftime('%d.%m.%Y, Time: %H:%M:%S')
shortdate = datetime.now().strftime('%d.%m.%Y %H:%M')
print(date)

# At first I'm loading an Excel file with all the sources (information and links) about the stocks I want to investigate
# and the data of my portfolio
path_sources = 'C:\\Users\\andre\\Documents\\Python\Web_Scraper\Stocks_Sources.xlsx'
sources = pd.read_excel(path_sources,sheet_name='Sources')
# I want my Index to start at 1
sources.index = sources.index + 1
#print(sources)

# creating lists for the variables I'm looking for
names = []
types = []
prices = []
plusminus = []
percent = []
factor = []

# preparing the data for the Dataframe "marketdata"
for row in sources.iterrows():
    time.sleep(.25)
    r = requests.get(row[1]['link'])
    soup = BeautifulSoup(r.text, 'lxml')
    # Scraping the current price and the intraday volatility with a for-loop for indices and currencies
    if row[1]['category'] == 'Index' or row[1]['category'] == 'currency':
        names.append(row[1]['name'])
        types.append(row[1]['category'])
        price = soup.find('div',{'class':'col-xs-5'}).text.strip()
        prices.append(price)
        plusminus.append(soup.find('div',{'class':'col-xs-4'}).text.strip())
        percent.append(soup.find('div',{'class':'col-xs-3'}).text.strip())
        factor.append(re.sub('[USDEURCHFPKT.]','',price).replace(',','.'))

# I'm creating the first Dataframe marketdata for an overview
marketdata = pd.DataFrame({'name':names,
                           'type':types,
                           'price':prices,
                           'CHG':plusminus,
                           'CHG%':percent,
                           'factor':factor})
marketdata.index = marketdata.index + 1
print(marketdata)

names = []
types = []
prices = []
numbers = []
b_course = []
abase = []
factor = []

# filtering the Df and resetting the index
sources_f = sources[sources['number'] > 0].reset_index()
sources_f.index = sources_f.index +1

# preparing the data for the Dataframe "portfolio"
for row in sources_f.iterrows():
    names.append(row[1]['name'])
    types.append(row[1]['category'])
    numbers.append(row[1]['number'])
    b_course.append(row[1]['buyingcourse'])
    abase.append(row[1]['asset base'])
    if row[1]['category'] == 'currency':
        price = marketdata.loc[row[1]['index']]['price']
    # Scraping the current price and the intraday volatility with a for-loop for shares and funds
    else:
        time.sleep(.25)
        r = requests.get(row[1]['link'])
        soup = BeautifulSoup(r.text, 'lxml')
        if row[1]['category'] == 'shares':
            price = soup.find('span', {'class': 'snapshot__value-current realtime-push'}).text.replace(' ','')
        elif row[1]['category'] == 'funds':
            price = soup.find('div', {'class':'table-responsive quotebox'}).find('td').text.replace(' ','')
    if 'USD' in price:
        price = float(re.sub('[USDEURCHF.]','',price).replace(',','.')) /float(marketdata.loc[4]['factor'])
    else:
        price = float(re.sub('[USDEURCHFPKT.]','',price).replace(',','.'))
    price = str(round(price,4)) + 'EUR'
    prices.append(price)
    factor.append(float(re.sub('[USDEURCHFPKT]','',price)))

# Based on the data I can calculate earnings, losses and my depot value
cur_asset = [round(a*b,3) for a,b in zip(numbers,factor)]
win_loss = [round(a-b,3) for a,b in zip(cur_asset,abase)]
percent = [round((a-b)/b,3) for a,b in zip(cur_asset,abase)]
asset_base = round(sum(abase),3)
depot_value = round(sum(cur_asset),3)
balance = depot_value-asset_base
balance_p = (depot_value-asset_base)/asset_base

# Now I can create the second Dataframe "portfolio"
portfolio = pd.DataFrame({'name':names,
                           'type':types,
                           'numbers':numbers,
                           'buying course':b_course,
                           'asset base':abase,
                            shortdate:prices,
                           'current asset':cur_asset,
                           'win/loss':win_loss,
                           'win/loss%':percent},
                           index = [i for i in range(1,len(names)+1)])

# Append the calculations to the Dataframe
portfolio.loc[len(portfolio.index)+1] = ['total', 'all', '', '', asset_base, '', depot_value, balance, balance_p]
print(portfolio)


# Exporting and appending the Dataframes to an Excel file
path = "C:\\Users\\andre\\OneDrive\Desktop\Stock_Scraper.xlsx"
with pd.ExcelWriter(path, engine='openpyxl') as writer:
    marketdata.to_excel(writer,sheet_name='Market')
    portfolio.to_excel(writer,sheet_name='Portfolio')

print('depot value: ' + str(depot_value))