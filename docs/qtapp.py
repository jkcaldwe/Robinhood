import sys
from PyQt5.QtWidgets import QMainWindow, QPushButton, QApplication
from PyQt5 import QtCore
import logging
import auto_trader
#Support default dict list
from collections import defaultdict
#Date
import datetime

#configure logging to print debug messages on the screen
logging.basicConfig(level=logging.DEBUG)

class TraderGui(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.initUI()

        # Define global variables for the class instance
        self.quoteTimer = QtCore.QTimer();
        self.positionTimer = QtCore.QTimer();
        self.position_quotes = [];
        self.position_symbols = [];
        # Call main trader logic
        # tradeLogic = auto_trader.TraderApp().main();
        self.main();
        
    def initUI(self):      
        # Define UI elements
        btn1 = QPushButton("Button 1", self)
        btn1.move(30, 50)

        btn2 = QPushButton("Button 2", self)
        btn2.move(150, 50)
        #Connect UI elements to slots
        btn1.clicked.connect(self.buttonClicked)            
        btn2.clicked.connect(self.buttonClicked)
        
        self.statusBar()
        #Define main window
        self.setGeometry(300, 300, 290, 150)
        self.setWindowTitle('Event sender')
        self.show()
    
    def main(self):
        
        #log in and return trade handle.  'self' defines it as a global across the class
        self.my_trader = auto_trader.login();

        # Get current open positions and quantity of the position
        self.position_symbols = auto_trader.getCurrentPositions(self.my_trader);
        logging.info(self.position_symbols);

        #Create data array for each symbol in my positions and initialize with opening and current quote
        position_quotes_init = defaultdict(list);
        self.position_quotes = auto_trader.populateQuoteData(self.position_symbols, position_quotes_init);
        logging.info(self.position_quotes);
        
        #Create a timer and append current quote data to the position quote list
        self.quoteTimer.timeout.connect(self.func_quoteTimer);
        #Timer will repeat every 2 minutes
        self.quoteTimer.start(120000);

        self.positionTimer.timeout.connect(self.func_posSymbolsTimer);
        #Trigger every 15 minutes to update current positions
        self.positionTimer.start(900000);

    def buttonClicked(self):
        sender = self.sender()
        self.statusBar().showMessage(sender.text() + ' was pressed')
        logging.info(sender.text() + ' was pressed');

    def func_quoteTimer(self):
        self.position_quotes = auto_trader.populateQuoteData(self.position_symbols, self.position_quotes);
        logging.info(self.position_quotes);    

    def func_posSymbolsTimer(self):
        self.position_symbols = auto_trader.getCurrentPositions(self.my_trader);
        logging.info(self.position_symbols);    

#Define timer as global so it will keep running while app is alive
# timer = QtCore.QTimer();
# Global to get position quotes
# position_quotes = [];
#Start application
app = QApplication(sys.argv)
autoTrader = TraderGui()
sys.exit(app.exec_())
