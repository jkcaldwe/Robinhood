import sys
#Robinhood
from Robinhood import Robinhood
# Threading allows for timers to be run
import threading
import time
# need to get JSON data given a URL and process the JSON data
from urllib.request import urlopen
import json
# Add dictionary to create dynamic dictionary of lists of symbol names to store lists of values
from collections import defaultdict
# allows for structure like objects in Python
from collections import namedtuple
# import stock_info module from yahoo_fin
from yahoo_fin import stock_info as si
#To print from Qt in console
import logging
#Import QtApp
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore
from PyQt5.QtCore import QObject

class TraderApp(QObject):
    # Global position quotes to be used by timer
    position_quotes = [];
    #----------------------------------------------------------------------------------------------------------------------------
    def main(self):
        logging.basicConfig(level=logging.DEBUG)
        # structure to keep each stock data in
        # stock_data = namedtuple("stock_data", "field1 field2 field3");

        #log in and return trade handle
        my_trader = self.login();

        # print(my_trader.positions());
        position_symbols = self.getCurrentPositions(my_trader);
        logging.info(position_symbols);

        #Create data array for each symbol in my positions and initialize with current quote
        position_quotes_init = defaultdict(list);
        position_quotes = self.populateQuoteData(position_symbols, position_quotes_init);

        #Call function to add quote data to position quotes
        logging.info ("Before Timer");
        
        timer.timeout.connect(self.updateQuoteData)
        timer.start(500)
        # while (run):
        #   position_quotes = populateQuoteData(position_symbols, position_quotes);
        #   time.sleep(30);

    #----------------------------------------------------------------------------------------------------------------------------
    def getCurrentPositions(self, my_trader):
        #get current bought in postiions
        #Gets the total number of open positions also past positions since many are 0.  This filters based only on positions where there are a quantity of stocks
        symbols = [];
        for i in range (len(my_trader.positions()['results'])):
            if (float(my_trader.positions()['results'][i]['quantity']) != 0):
                #Index one of the open positions and get the instrument URL then find the symbol for the position
                response = urlopen(my_trader.positions()['results'][i]['instrument']);
                json_data = json.loads(response.read());
                symbols.append(json_data['symbol']);
        # print ("symbol: " + json_data['symbol'] + " quantity: " + my_trader.positions()['results'][i]['quantity']);

        return symbols;
    #----------------------------------------------------------------------------------------------------------------------------
    def populateQuoteData(self, position_symbols, position_quotes):
        # create arrays for each position symbol to store values
        for symbol in position_symbols:
            position_quotes[symbol].append(self.getQuoteBySymbol(symbol));

        logging.info (position_quotes);
        return position_quotes;
    #----------------------------------------------------------------------------------------------------------------------------
    def getQuoteBySymbol(self, symbol):
        return (si.get_live_price(symbol));
    #----------------------------------------------------------------------------------------------------------------------------
    def login(self):
        #Pull Robinhood login data from text file so not exposed in code
        lines = [] #Declare an empty list named "lines"
        with open ('C:\\Users\\joshua.caldwell\\Stock_App\\RH_auth.txt', 'rt') as in_file:  #Open file lorem.txt for reading of text data.
            for line in in_file:
                lines.append(line);  #add that line to our list of lines.
        username = lines[0].rstrip();
        password = lines[1].rstrip();
        qr_code = lines[2];
        # print(username + ":"+ password + ":" + qr_code);        #print the list object.

        #Setup and open my trader
        my_trader = Robinhood();
        #login to Robinhood using username and password from file
        my_trader.login(username=username, password=password, qr_code=qr_code);
        return my_trader;
    #----------------------------------------------------------------------------------------------------------------------------
    def updateQuoteData(self):
        print ('in');
        logging.info ("timer");
    #----------------------------------------------------------------------------------------------------------------------------
    def exitApp(self):
        logging.info ("exiting");
        exit();
#----------------------------------------------------------------------------------------------------------------------------

#configure logging to print debug messages on the screen
timer = QtCore.QTimer()
#Start the widget and runs main code.  Eventually hook data into widget through slots
#if __name__ == '__main__':   
# app = QApplication(sys.argv)
# traderApp = TraderApp()
# sys.exit(app.exec_())
    

