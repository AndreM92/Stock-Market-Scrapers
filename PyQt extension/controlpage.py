import sys
from qtpy import QtWidgets

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from datetime import datetime
date = 'Date: ' + datetime.now().strftime('%d.%m.%Y, Time: %H:%M:%S')

# import the class MainWindow from mainwindow.py
from Qt_Creator.mainwindow import Ui_MainWindow

from StockScraper import dfStMarket, dfPortfolio, categories
total = dfPortfolio[-1:]

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
        self.ui.portValue.setText(str(float(total['current asset'])).replace('.', ',') + ' EUR')
        self.ui.assetBase.setText(str(float(total['asset base'])).replace('.', ',') + ' EUR')
        self.ui.winLoss.setText(str(float(total['win/loss(EUR)'])).replace('.', ',') + ' EUR')
        self.ui.winLossP.setText(str(float(total['win/loss(%)'])).replace('.', ',') + ' %')
        if '-' in str(total['win/loss(EUR)']):
            self.ui.winLoss.setStyleSheet('QLineEdit{color:red}')
            self.ui.winLossP.setStyleSheet('QLineEdit{color:red}')

        self.ui.currencies.setText(str(round(categories[0])).replace('.', ',') + ' EUR')
        self.ui.stocks.setText(str(round(categories[1],2)).replace('.', ',') + ' EUR')
        self.ui.asiafunds.setText(str(round(categories[2])).replace('.', ',') + ' EUR')
        self.ui.worldfunds.setText(str(round(categories[3])).replace('.', ',') + ' EUR')

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
        for r in dfPortfolio[:-1].iterrows():
            row = self.ui.tabWidP.rowCount()
            self.ui.tabWidP.insertRow(row)
            col = 0
            for e in r[1]:
                self.ui.tabWidP.setItem(row, col, QtWidgets.QTableWidgetItem(str(e)[:10]))
                col = col + 1

    def createPieChart(self):
        # I want to visualise the stock distribution of my portfolio
        labels = ['Currencies', 'Stocks', 'Asiafunds', 'Worldfunds']
        # category values are already calculated ad imported
        total = sum(categories)
        percentages = [c / total for c in categories]

        plt.pie(percentages,labels=labels,autopct='%1.2f%%',startangle=90)
        self.canvas.draw()


window = MainWindow()
window.show()
sys.exit(app.exec_())