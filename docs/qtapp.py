import sys
from PyQt5.QtWidgets import QMainWindow, QPushButton, QApplication
from PyQt5 import QtCore
import logging
import auto_trader

#configure logging to print debug messages on the screen
logging.basicConfig(level=logging.DEBUG)

class TraderGui(QMainWindow):
    
    running = False;

    def __init__(self):
        super().__init__()
        self.initUI()
        tradeLogic = auto_trader.TraderApp().main();
        
        
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
    
app = QApplication(sys.argv)
autoTrader = TraderGui()
sys.exit(app.exec_())
