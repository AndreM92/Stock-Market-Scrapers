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
print(date)

# At first I'm loading an Excel file with all the sources (information and links) about the stocks I want to investigate
# and the data of my portfolio
path_sources = 'C:\\Users\\andre\\Documents\\Python\Web_Scraper\Stocks_Sources.xlsx'
sources = pd.read_excel(path_sources,sheet_name='Sources')

# Preparation of the first DataFrame for general informations about the stock market
stMaHeaders = ['name','type','price','CHG','CHG(%)','factor']
dfStMarket = pd.DataFrame(columns = stMaHeaders)

# This is a function that extracts data from my excel file and scrapes data from a finance webpage
def stockMarketScraper(x):
    time.sleep(.1)
    r = requests.get(x[1]['link'])
    soup = BeautifulSoup(r.text, 'lxml')
    name = x[1]['shortname']
    category = x[1]['category']
    price = soup.find('div',{'class':'col-xs-5'}).text.strip()
    plusminus = soup.find('div',{'class':'col-xs-4'}).text.strip()
    percent = soup.find('div',{'class':'col-xs-3'}).text.strip()
    factor = re.sub('[USDEURCHFPKT.]','',price).replace(',','.')
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
poHeaders = ['name','type','numbers','buying course','current price','asset base','current asset','win/loss','win/loss(%)']
dfPortfolio = pd.DataFrame(columns = poHeaders)

# Filtering of the sources-df (for stocks I'm invested in) and resetting the index
sources_f = sources[sources['numbers'] > 0].reset_index()
sources_f.index = sources_f.index +1

# Scraper function for my portfolio
def portfolioStockScraper(x):
    name = x[1]['shortname']
    category = x[1]['category']
    number = x[1]['numbers']
    b_course = x[1]['buyingcourse']
    abase = round(x[1]['asset base'],3)
    if row[1]['category'] == 'currency':
        price = dfStMarket.loc[x[1]['index']]['price']
    else:
        # portfolio Scraper
        time.sleep(.1)
        r = requests.get(x[1]['link'])
        soup = BeautifulSoup(r.text, 'lxml')
        if row[1]['category'] == 'shares':
            price = soup.find('span', {'class': 'snapshot__value-current realtime-push'}).text.replace(' ','')
        elif row[1]['category'] == 'funds':
            price = soup.find('div', {'class':'table-responsive quotebox'}).find('td').text.replace(' ','')
    if 'USD' in price:
        priceUSD = float(re.sub('[USDEURCHF.]', '',str(price)).replace(',','.'))
        price = priceUSD/float(dfStMarket.loc[4]['factor'])
    else:
        price = float(re.sub('[USDEURCHFPKT.]','',str(price)).replace(',','.'))

    # Based on the data I can calculate my current asset, earnings and losses for every stock
    cur_asset = round(number * price,2)
    winloss = round(cur_asset - abase,2)
    winlossP = round((cur_asset-abase)/abase*100,2)

    # personal preference
    if str(number)[-1] == '0':
        number = int(number)
    else:
        number = str(round(number,5)).replace('.',',')
    b_course = str(round(b_course,2)).replace('.',',')
    tidyprice = str(round(price,2)).replace('.',',') + 'EUR'

    datarow = [name,category,number,b_course,tidyprice,abase,cur_asset,winloss,winlossP]
    return datarow

# Saving scraped data into the dataframe Portfolio
for row in sources_f.iterrows():
    dfPortfolio.loc[len(dfPortfolio)] = portfolioStockScraper(row)
dfPortfolio.index = dfPortfolio.index + 1
#print(dfPortfolio)

# values in total
asset_base = round(sum(dfPortfolio['asset base']),2)
depot_value = round(sum(dfPortfolio['current asset']),2)
win_loss = round(sum(dfPortfolio['win/loss']),2)
win_lossP = round(((depot_value-asset_base)/asset_base*100),2)

# Append the calculations as a new row to the Dataframe
dfPortfolio.loc[len(dfPortfolio.index)+1] = ['total','all','','','',asset_base,depot_value,win_loss,win_lossP]
print(dfPortfolio)


# Lastly I'm exporting the dataframes to an Excel file
path = "C:\\Users\\andre\\OneDrive\Desktop\Stock_Scraper.xlsx"
with pd.ExcelWriter(path, engine='openpyxl') as writer:
    dfStMarket.to_excel(writer,sheet_name='Market')
    dfPortfolio.to_excel(writer,sheet_name='Portfolio')
