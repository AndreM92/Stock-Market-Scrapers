import requests
from bs4 import BeautifulSoup
import lxml 
# if the package lxml shows problems with Python 3.11 use: html.parser instead
import numpy as np
import pandas as pd
import openpyxl
import re
import time
from datetime import datetime
date = 'Date: ' + datetime.now().strftime('%d.%m.%Y, Time: %H:%M:%S')
print(date)

# At first I'm loading an Excel file with all the sources (information and links) about the stocks I want to investigate
# This file also contains the data of my portfolio
path_sources = 'C:\\Users\\andre\\Documents\\Python\Web_Scraper\Stocks_Sources.xlsx'
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
print(dfStMarket)


# Preparation of the dataframe Portfolio
poHeaders = ['name','type','numbers','buying course','current price','asset base','current asset','win/loss(EUR)','win/loss(%)','52W High','52W Low']
dfPortfolio = pd.DataFrame(columns = poHeaders)

# Filtering of the sources-df (for stocks I'm invested in) and resetting the index
sources_f = sources[sources['numbers'] > 0].reset_index()
sources_f.index = sources_f.index +1


# Scraper function for my portfolio
def portfolioStockScraper(x):
    name = x[1]['shortname']
    category = x[1]['category']
    number = x[1]['numbers']
    b_course = round(x[1]['buyingcourse'],2)
    abase = round(x[1]['asset base'],2)
    longHigh = 'NaN'
    longLow = 'NaN'
    price = 0
    digits = 0
    usd = float(dfStMarket[dfStMarket['name'] == 'Dollar']['factor'])

    # Portfolio Scraper
    time.sleep(.1)
    r = requests.get(x[1]['link'])
    soup = BeautifulSoup(r.text, 'html.parser')
    if row[1]['category'] == 'stocks':
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

    elif row[1]['category'] == 'funds':
        price = soup.find('div', {'class':'table-responsive quotebox'}).find('td').text.replace(' ','')
        tablef = soup.find_all('div', {'id': 'SnapshotQuoteData'})[0].find_all('td')
        longHigh = tablef[-2].text.split(' ')[0]
        longLow = tablef[-1].text.split(' ')[0]

    elif row[1]['category'] == 'currency':
        price = dfStMarket.loc[x[1]['index']]['price']
        tables = soup.find('table', {'class': 'table table--headline-first-col table--content-right'})
        if tables != None:
            tables = tables.find_all('tr')[-2:]
            longHigh = tables[-1].find_all('td')[-1].text.split(' ')[0]
            longLow = tables[-2].find_all('td')[-1].text.split(' ')[0]

    if 'usd' in str(price).lower() and usd != 0:
        digits = float(re.sub('[ .%a-zA-Z+-]', '', str(price)).replace(',', '.'))
        price = round(digits / usd,2)
    else:
        price = float(re.sub('[ .%a-zA-Z+-]', '', str(price)).replace(',', '.'))

    # Based on the data I can calculate my current asset, earnings and losses for every stock
    cur_asset = round(number * price,2)
    winloss = round(cur_asset - abase,2)
    winlossP = round((cur_asset-abase)/abase*100,2)

    # Formatting (personal preference)
    price = str(format(price,'.2f')).replace('.',',')
    b_course = str(format(b_course,'.2f')).replace('.',',')
    if str(number)[-2:] == '.0':
        number = int(number)
    number = str(number).replace('.',',')

    datarow = [name,category,number,b_course,price,abase,cur_asset,winloss,winlossP,longHigh,longLow]
    return datarow

# Saving the scraped data into the dataframe Portfolio
for row in sources_f.iterrows():
    dfPortfolio.loc[len(dfPortfolio)] = portfolioStockScraper(row)
dfPortfolio.index = dfPortfolio.index + 1


# values in total
asset_base = round(sum(dfPortfolio['asset base']),2)
depot_value = round(sum(dfPortfolio['current asset']),2)
win_loss = round(sum(dfPortfolio['win/loss(EUR)']),2)
win_lossP = round(((depot_value-asset_base)/asset_base*100),2)

# Append the calculations in a row to the Dataframe
dfPortfolio.loc[len(dfPortfolio.index)+1] = ['total','all','','','',asset_base,depot_value,win_loss,win_lossP,'','']
print(dfPortfolio)


# Calculation of customized Portfolio categories
asiaflist = ['MSCI Asia','MSCI China','MSCI India']
currencies = sum(dfPortfolio[dfPortfolio['type'] == 'currency']['current asset'])
stocks = sum(dfPortfolio[dfPortfolio['type'] == 'stocks']['current asset'])
dfFunds = dfPortfolio[dfPortfolio['type'] == 'funds']
asiafunds = sum(dfFunds[dfFunds['name'].isin(asiaflist)]['current asset'])
worldfunds = sum(dfFunds[~dfFunds['name'].isin(asiaflist)]['current asset'])

categories = [currencies, stocks, asiafunds, worldfunds]

dfCategories = pd.DataFrame(categories, index = ['Currencies', 'Stocks', 'Asia Funds', 'World Funds'], columns = ['value'])
print(dfCategories)


# Lastly I'm exporting the dataframes to an Excel file
path = "C:\\Users\\andre\\OneDrive\Desktop\Stock_Scraper.xlsx"
with pd.ExcelWriter(path, engine='openpyxl') as writer:
    dfStMarket.to_excel(writer,sheet_name='Market')
    dfPortfolio.to_excel(writer,sheet_name='Portfolio')
    dfCategories.to_excel(writer,sheet_name='Categories')
