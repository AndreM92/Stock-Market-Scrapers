import sys
from qtpy import QtWidgets

import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from datetime import datetime
date = 'Date: ' + datetime.now().strftime('%d.%m.%Y, Time: %H:%M:%S')

# Import the class MainWindow from mainwindow.py
from Qt_Creator.mainwindow import Ui_MainWindow

# Import the DataFrames from StockScraper.py
from StockScraper import dfStMarket, dfPfStr, dfCat

total = dfPfStr.loc[len(dfPfStr.index)]
currencies, stocks, asiafunds, worldfunds = [re.sub(r"(\w+)(\d{3})\.(\d{2})$", r"\1.\2,\3",str('{:.2f}'.format(float(i)))) \
    if len('{:.2f}'.format(float(i))) > 6 else str('{:.2f}'.format(float(i))).replace('.',',') for i in dfCat['value']]


app = QtWidgets.QApplication(sys.argv)

# Class MainWindow inherits all characteristics of QtWidgets and QMainWindow
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent = None):
        super().__init__(parent)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setWindowTitle('Stock Market Update')
        self.ui.dateTime.setText(date)

        self.fillMarketTable()
        self.fillPortfolioTable()
        self.ui.portValue.setText(total['current asset'] + ' EUR')
        self.ui.assetBase.setText(total['asset base'] + ' EUR')
        self.ui.winLoss.setText(total['win/loss(EUR)'] + ' EUR')
        self.ui.winLossP.setText(total['win/loss(%)'] + ' %')
        if '-' in str(total['win/loss(EUR)']):
            self.ui.winLoss.setStyleSheet('QLineEdit{color:red}')
            self.ui.winLossP.setStyleSheet('QLineEdit{color:red}')

        self.ui.currencies.setText(currencies + ' EUR')
        self.ui.stocks.setText(stocks + ' EUR')
        self.ui.asiafunds.setText(asiafunds + ' EUR')
        self.ui.worldfunds.setText(worldfunds + ' EUR')

        # Create Canvas figure
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        # Add Canvas into layout
        self.ui.gLayout.addWidget(self.canvas)
        self.createPieChart()


    def fillMarketTable(self):
        for r in dfStMarket.iterrows():
            row = self.ui.tableWidgetMarket.rowCount()
            self.ui.tableWidgetMarket.insertRow(row)
            col = 0
            for e in r[1]:
                self.ui.tableWidgetMarket.setItem(row, col, QtWidgets.QTableWidgetItem(str(e)))
                col = col + 1

    def fillPortfolioTable(self):
        for r in dfPfStr[:-1].iterrows():
            row = self.ui.tabWidP.rowCount()
            self.ui.tabWidP.insertRow(row)
            col = 0
            for e in r[1]:
                self.ui.tabWidP.setItem(row, col, QtWidgets.QTableWidgetItem(str(e)[:12]))
                col = col + 1

    def createPieChart(self):
        # I want to visualise the stock distribution of my portfolio
        labels = [n for n in dfCat['name']]
        # category values and percentages are already calculated and imported
#        totalCat = np.sum(dfCat['value'])
        percentages = [p for p in dfCat['parts']]

        plt.pie(percentages,labels=labels,autopct='%1.2f%%',startangle=90)
        self.canvas.draw()


window = MainWindow()
window.show()
sys.exit(app.exec_())
