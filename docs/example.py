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

def main():
	# structure to keep each stock data in
	stock_data = namedtuple("stock_data", "field1 field2 field3");

	#log in and return trade handle
	my_trader = login();

	# print(my_trader.positions());
	position_symbols = getCurrentPositions(my_trader);
	print(position_symbols);

	#Create data array for each symbol in my positions and initialize with current quote
	position_quotes_init = defaultdict(list);
	position_quotes = populateQuoteData(position_symbols, position_quotes_init);

	#Call function to add quote data to position quotes
	run = True;
	# while (run):
	# 	position_quotes = populateQuoteData(position_symbols, position_quotes);
	# 	time.sleep(30);

	#Get stock information
	    #Note: Sometimes more than one instrument may be returned for a given stock symbol
	# stock_instrument = my_trader.instruments("KNDI")[0]
	# print(stock_instrument)

	# #Get a stock's quote
	# print(my_trader.print_quote("KNDI"));

	#Prompt for a symbol
	#my_trader.print_quote()

	# #Print multiple symbols
	# my_trader.print_quotes(stocks=["BBRY", "FB", "MSFT"])

	# #View all data for a given stock ie. Ask price and size, bid price and size, previous close, adjusted previous close, etc.
	#quote_info = my_trader.quote_data("KNDI");
	# access specific object of the returned quote data
	# print(quote_info['ask_price']);
	# quote_info = my_trader.quote_data("RARX");
	# print(quote_info['ask_price']);



	# #Place a buy order (uses market bid price)
	# buy_order = my_trader.place_buy_order(stock_instrument, 1)

	# #Place a sell order
	# sell_order = my_trader.place_sell_order(stock_instrument, 1)
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
	
	print (position_quotes);
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
	print ("exiting");
	exit();
#----------------------------------------------------------------------------------------------------------------------------
# Call the main function.  Did this way so I could define functions of main later in code.
main();