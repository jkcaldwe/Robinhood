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
#support google finance for historical data
import csv,datetime,requests,time
import numpy as np

# class TraderApp(QObject):
    # Global position quotes to be used by timer
position_quotes = [];
#----------------------------------------------------------------------------------------------------------------------------
def main():
    logging.basicConfig(level=logging.DEBUG)
    # structure to keep each stock data in
    # stock_data = namedtuple("stock_data", "field1 field2 field3");

    #log in and return trade handle
    my_trader = login();

    # print(my_trader.positions());
    position_symbols = getCurrentPositions(my_trader);
    logging.info(position_symbols);

    #Create data array for each symbol in my positions and initialize with current quote
    position_quotes_init = defaultdict(list);
    position_quotes = populateQuoteData(position_symbols, position_quotes_init);


#----------------------------------------------------------------------------------------------------------------------------
def getCurrentPositions(my_trader):
    #get current bought in postiions
    #Gets the total number of open positions also past positions since many are 0.  This filters based only on positions where there are a quantity of stocks
    current_positions = defaultdict(list);
    for i in range (len(my_trader.positions()['results'])):
        if (float(my_trader.positions()['results'][i]['quantity']) != 0):
            #Index one of the open positions and get the instrument URL then find the symbol for the position
            response = urlopen(my_trader.positions()['results'][i]['instrument']);
            json_data = json.loads(response.read());
            current_positions[json_data['symbol']].append(float(my_trader.positions()['results'][i]['quantity']));
    # print ("symbol: " + json_data['symbol'] + " quantity: " + my_trader.positions()['results'][i]['quantity']);

    return current_positions;
#----------------------------------------------------------------------------------------------------------------------------
def populateQuoteData(position_symbols, position_quotes):
    # create arrays for each position symbol to store values
    for symbol in position_symbols:
        if symbol in position_quotes:
            position_quotes[symbol].append(getQuoteBySymbol(symbol));
        else:
            position_quotes[symbol].append(getOpenBySymbol(symbol));
            position_quotes[symbol].append(getQuoteBySymbol(symbol));
    # logging.info (position_quotes);
    return position_quotes;
#----------------------------------------------------------------------------------------------------------------------------
def getQuoteBySymbol(symbol):
    return (si.get_live_price(symbol));
#----------------------------------------------------------------------------------------------------------------------------
def getQuantityBySymbol(my_trader, symbol):
    return (si.get_live_price(symbol));
#----------------------------------------------------------------------------------------------------------------------------
def getOpenBySymbol(symbol):
    return (si.get_quote_table(symbol, True)['Open']);
#----------------------------------------------------------------------------------------------------------------------------
def calcWeightedAverage(quoteList, window):
    #take the last items in the quote list as defined the window value
    #eg. if window value is 5, adjList will be the last 5 values in the quote list
    adjList = quoteList[-window:];
    logging.info(adjList);
    #calculate weight multiplier for linear weighted average
    weightMultiplier = 0;
    for i in range (window + 1):
        weightMultiplier += i;
    weightMultiplier = (100 / weightMultiplier) / 100;
    logging.info(weightMultiplier);
    #use weight multiplier and adjList to calculate weighted average
    weightedAve = 0;
    for i in range(len(adjList)):
        logging.info(adjList[i]);
        weightedAve += ((i+1)*weightMultiplier*adjList[i]);
    
    return (weightedAve);
#----------------------------------------------------------------------------------------------------------------------------
def sellPosition(my_trader, symbol):
    sell_order = my_trader.place_sell_order(symbol, 1);
    return (si.get_quote_table(symbol, True)['Open']);
#----------------------------------------------------------------------------------------------------------------------------
def buyPosition(my_trader, symbol, quantity):
    approx_price = getQuoteBySymbol(symbol) * quantity;
    if (symbol == 'SPY' and approx_price < 10000 ):
        buy_order = my_trader.place_buy_order(symbol, quantity);
    elif (symbol != 'SPY' and approx_price < 2000):
        buy_order = my_trader.place_buy_order(symbol, quantity);
    logging.info (buy_order);
    return ("buy position");
#----------------------------------------------------------------------------------------------------------------------------
def login():
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
def exitApp():
    logging.info ("exiting");
    exit();
#----------------------------------------------------------------------------------------------------------------------------

#configure logging to print debug messages on the screen
#Start the widget and runs main code.  Eventually hook data into widget through slots
#if __name__ == '__main__':   
# app = QApplication(sys.argv)
# traderApp = TraderApp()
# sys.exit(app.exec_())
    

