# Stock-Market-Scrapers
These are my Python Web Scrapers for Stocks that I want to share with you

## MarketWatchScraper
This is a basic Web Scraping program from the webpage https://www.marketwatch.com/
you can investigate shares, indices, funds, cryptoturrencies and much more
the data will be stored in a dataframe

## ExtendedStockScraper
is a little bit more complex and not finished yet.
It has the purpose to crawl all the stocks I'm personally interested in, import various data,
calculate the worth of my portfolio, export complex Dataframes and visualise developments.
### This project currently includes:
- an import function to get the data of my portfolio
- code for creating DataFrames with Pandas
- the actual code for scraping Data from 'https://www.finanzen.net/' (a german page that provides realtime stock quotes)
- some calculations to find out my current depot value
- an export function to save the DataFrames in an Excel file

I also wrote code to append the data on an existing file to create some built-in graphs, 
but openpyxl always deletes my Excel commands :( 
