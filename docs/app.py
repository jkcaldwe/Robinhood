import sys
from PyQt5.QtWidgets import QMainWindow, QPushButton, QApplication
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

#configure logging to print debug messages on the screen
logging.basicConfig(level=logging.DEBUG)

class Example(QMainWindow):
    
    def __init__(self):
        super().__init__()
        
        self.initUI()
        
        
    def initUI(self):      

        btn1 = QPushButton("Button 1", self)
        btn1.move(30, 50)

        btn2 = QPushButton("Button 2", self)
        btn2.move(150, 50)
      
        btn1.clicked.connect(self.buttonClicked)            
        btn2.clicked.connect(self.buttonClicked)
        
        self.statusBar()
        
        self.setGeometry(300, 300, 290, 150)
        self.setWindowTitle('Event sender')
        self.show()
        
    
    def buttonClicked(self):
        sender = self.sender()
        self.statusBar().showMessage(sender.text() + ' was pressed')
        logging.debug(sender.text() + ' was pressed');    
    


#----------------------------------------------------------------------------------------------------------------------------
def main():
    # structure to keep each stock data in
    stock_data = namedtuple("stock_data", "field1 field2 field3");

    #log in and return trade handle
    my_trader = login();

    # print(my_trader.positions());
    position_symbols = getCurrentPositions(my_trader);
    logging.info(position_symbols);

    #Create data array for each symbol in my positions and initialize with current quote
    position_quotes_init = defaultdict(list);
    position_quotes = populateQuoteData(position_symbols, position_quotes_init);

    #Call function to add quote data to position quotes
    run = True;
    # while (run):
    #   position_quotes = populateQuoteData(position_symbols, position_quotes);
    #   time.sleep(30);

#----------------------------------------------------------------------------------------------------------------------------
def getCurrentPositions(my_trader):
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
def populateQuoteData(position_symbols, position_quotes):
    # create arrays for each position symbol to store values
    for symbol in position_symbols:
        position_quotes[symbol].append(getQuoteBySymbol(symbol));

    logging.debug (position_quotes);
    return position_quotes;
#----------------------------------------------------------------------------------------------------------------------------
def getQuoteBySymbol(symbol):
    return (si.get_live_price(symbol));
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
    logging.debug ("exiting");
    exit();
#----------------------------------------------------------------------------------------------------------------------------
#Start the widget and runs main code.  Eventually hook data into widget through slots
#if __name__ == '__main__':   
app = QApplication(sys.argv)
ex = Example()
main();
sys.exit(app.exec_())
    

