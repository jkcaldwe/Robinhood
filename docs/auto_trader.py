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
def populateQuoteData(position_symbols, sold_symbols, control_symbols, position_quotes):  
    # create arrays for each position symbol to store values
    # position symbols and sold symbols should never have the same symbols
    for symbol in position_symbols:
        if symbol in position_quotes:
            position_quotes[symbol].append(getQuoteBySymbol(symbol));
        else:
            position_quotes[symbol].append(getCloseBySymbol(symbol));
            position_quotes[symbol].append(getOpenBySymbol(symbol));
            position_quotes[symbol].append(getQuoteBySymbol(symbol));
    for symbol in sold_symbols:
        if symbol in position_quotes:
            position_quotes[symbol].append(getQuoteBySymbol(symbol));
        else:
            position_quotes[symbol].append(getCloseBySymbol(symbol));
            position_quotes[symbol].append(getOpenBySymbol(symbol));
            position_quotes[symbol].append(getQuoteBySymbol(symbol));
    # control symbols could have the same symbol as either position or sold and we dont want to append current quote twice
    for symbol in control_symbols:
        if symbol not in position_quotes:
            position_quotes[symbol].append(getCloseBySymbol(symbol));
            position_quotes[symbol].append(getOpenBySymbol(symbol));
            position_quotes[symbol].append(getQuoteBySymbol(symbol));
        else:
            if symbol not in position_symbols and symbol not in sold_symbols:
                position_quotes[symbol].append(getQuoteBySymbol(symbol));

    # logging.info (position_quotes);
    return position_quotes;
#----------------------------------------------------------------------------------------------------------------------------
def getQuoteBySymbol(symbol):
    #returns the current quote of a given symbol
    return (si.get_live_price(symbol));
#----------------------------------------------------------------------------------------------------------------------------
def getQuantityBySymbol(my_trader, symbol):
    #returns the current quantity in my portfolio
    return (si.get_live_price(symbol));
#----------------------------------------------------------------------------------------------------------------------------
def getOpenBySymbol(symbol):
    #Returns the current days open
    return (si.get_quote_table(symbol, True)['Open']);
#----------------------------------------------------------------------------------------------------------------------------
def getCloseBySymbol(symbol):
    #Returns the previous days close
    return (si.get_quote_table(symbol, True)['Previous Close']);
#----------------------------------------------------------------------------------------------------------------------------
def calcWeightedAverage(quoteList, window):
    #take the last items in the quote list as defined the window value
    #eg. if window value is 5, adjList will be the last 5 values in the quote list
    adjList = quoteList[-window:];
    # logging.info(adjList);
    #calculate weight multiplier for linear weighted average
    weightMultiplier = 0;
    for i in range (window + 1):
        weightMultiplier += i;
    weightMultiplier = (100 / weightMultiplier) / 100;
    # logging.info(weightMultiplier);
    #use weight multiplier and adjList to calculate weighted average
    weightedAve = 0;
    for i in range(len(adjList)):
        # logging.info(adjList[i]);
        weightedAve += ((i+1)*weightMultiplier*adjList[i]);
    
    return (weightedAve);
#----------------------------------------------------------------------------------------------------------------------------
def analyzeData(position_symbols, sold_symbols, control_symbols, averageList, quoteList, my_trader):
    #Develop a score for the control symbols
    control_multiplier = 0;
    for symbol in control_symbols:
        if symbol == "SPY":
            #Temporary lists of data
            tempAverage = averageList[symbol];
            tempQuote = quoteList[symbol];
            #compare latest average to previous close
            PercentfromPrevClose = (tempAverage[len(tempAverage) - 1] - tempQuote[0])/tempQuote[0];
            #weighted averages for last hour, 30% last 10 mins, 30% last 30 mins, 40% last hour.  Based on averages being calculated every 10 minutes
            lastTen = (tempAverage[len(tempAverage) - 1] - tempAverage[len(tempAverage) - 2])/tempAverage[len(tempAverage) - 2];
            lastThirty = (tempAverage[len(tempAverage) - 1] - tempAverage[len(tempAverage) - 4])/tempAverage[len(tempAverage) - 4];
            lastHour = (tempAverage[len(tempAverage) - 1] - tempAverage[len(tempAverage) - 7])/tempAverage[len(tempAverage) - 7];
            weightedHour = (lastTen*0.3) + (lastThirty*0.3) + (lastHour*0.4);
            #calculate the control multiplier - using 150 as a base, adjust to modify control for other stocks - 1% increase will result in 1.5 multiplier
            control_multiplier = ((weightedHour*0.4) + (PercentfromPrevClose*0.6)) * 150;
    logging.info(control_multiplier);

    #for each stock in sold stocks, determine if we should but back
    for symbol in position_symbols:
        #Temporary lists of data
        tempAverage = averageList[symbol];
        tempQuote = quoteList[symbol];
    
    return (weightedAve);
#----------------------------------------------------------------------------------------------------------------------------
def sellPosition(my_trader, symbol, quantity):
    #find stock instrument for buy order
    stock_instrument = my_trader.instruments(symbol)[0];
    current_price = getQuoteBySymbol(symbol);
    #minimum amount I'm willing to take.  Set at 2% lower than current to make sure it sells.
    limit_price = round(current_price - (current_price * 0.02), 2);
    logging.info(limit_price);
    sell_order = my_trader.place_limit_sell_order(stock_instrument["url"], symbol, "GFD", limit_price, quantity);
    logging.info (sell_order);
#----------------------------------------------------------------------------------------------------------------------------
def buyPosition(my_trader, symbol, quantity):
    #find stock instrument for buy order
    stock_instrument = my_trader.instruments(symbol)[0];
    #get current price to calculate approximate cost for built in protection and limit price
    current_price = getQuoteBySymbol(symbol);
    approx_tot_price = current_price * quantity;
    #place a limit buy order.  Make the limit 1% above current price.  Should execute immediately.  Rounded to 2 decimal places or it wont work.
    limit_price = round(current_price * 1.01, 2);
    logging.info(limit_price);
    if (symbol == 'SPY' and approx_tot_price < 10000 ):
        # GFD is good for day
        buy_order = my_trader.place_limit_buy_order(stock_instrument["url"], symbol, "GFD", limit_price, quantity);
    elif (symbol != 'SPY' and approx_tot_price < 2000):
        buy_order = my_trader.place_limit_buy_order(stock_instrument["url"], symbol, "GFD", limit_price, quantity);
    logging.info (buy_order);
    # return ("buy position");
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
    

