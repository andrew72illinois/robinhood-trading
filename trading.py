from robin_stocks import *
import robin_stocks.robinhood as rr
import robin_stocks.robinhood.stocks as rrs
import robin_stocks.robinhood.markets as rrm
import os 
import time
import pandas as pd
import numpy as np
import matplotlib as mp
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

class Trading_Algorithm:
    # Constructor
    def __init__(self):
        self.robin_user = os.environ.get("robinhood_username")
        self.robin_pass = os.environ.get("robinhood_password")
        self.robin_code = os.environ.get("robinhood_code") # 2fa code changes daily
        # Log into robinhood using robin_stocks.robinhood API
        self.login = rr.login(username=self.robin_user, password=self.robin_pass, mfa_code=self.robin_code) 

    # Destructor
    def __del__(self):
        # Logs out of robinhood using robin_stocks.robinhood API
        rr.logout()

    # Creates DataFrame of Portfolio
    def build_portfolio(self):
        my_stocks = rr.build_holdings()
        # Create DataFrame
        self.df = pd.DataFrame(my_stocks) # Creates a DataFrame of stock holdings
        self.df = self.df.T # Reorganizes 
        self.df['ticker'] = self.df.index # "Ticker" replaces index label 
        self.df = self.df.reset_index(drop=True) # Removes indexes - indexes = tickers
        cols = self.df.columns.drop(['id', 'type', 'name', 'pe_ratio', 'ticker']) # Classifies the columns 
        self.df[cols] = self.df[cols].apply(pd.to_numeric, errors='coerce') # Edits columns to be of type float64 
        print(self.df) # Show DataFrame

    # Prints Portfolio as Dataframe
    def print_portfolio(self):
        print(self.df)

    # Creates a List of Stocks from Portfolio
    def create_stock_list_based_on_df(self):
        # Make a list of stocks
        self.stock_list = self.df['ticker'].to_list()
        print(self.stock_list)

    # Creates a Graph of Price Vs. Time of a Particular Stock
    def create_stock_graph(self, stock_name):
        starting_time = datetime.now() # current time
        time_axis_x = [] # x axis 
        price_axis_y = [] # y axis
        plt.figure(figsize=(10, 6)) # Create the figure
        plt.title(stock_name + ' Stock Price Over 5 Minutes', fontsize=16)
        plt.xlabel('Time', fontsize=12)
        plt.ylabel('Price', fontsize=12)
        plt.xticks(rotation=45)
        plt.grid(True)
        # Get the Latest Price of the Stock every Minute for 5 Minutes
        for i in range(6):
            time_axis_x.append(starting_time + timedelta(minutes=i)) 
            price_axis_y.append(float(rrs.get_latest_price(stock_name)[0]))
            plt.plot(time_axis_x, price_axis_y, label=stock_name + ' Stock Price', color='blue')
            plt.savefig('results/stock_prices.png')
            time.sleep(60)
        plt.close()

    # Returns a list of the top up movers of the day 
    def find_top_movers(self, direction='None'):
        top_movers_list = rrm.get_top_movers()
        return_list = []
        for stock in top_movers_list:
            return_list.append(stock.get('symbol'))
        return return_list

    # Returns a list of the top s&p500 up movers of the day 
    def find_top_movers_sp500(self):
        return rrm.get_top_movers_sp500(direction='up')

    

# Create the Trading_Algorithm Object 
algorithm = Trading_Algorithm()
algorithm.build_portfolio()
algorithm.create_stock_list_based_on_df()
algorithm.create_stock_graph('NVDA')
# print(algorithm.find_top_movers())
# print(algorithm.find_top_movers_sp500)


# Make a list of the prices of the stocks
# while(True):
#     latest_price = rrs.get_latest_price(stock_list)
#     print(latest_price)
#     time.sleep(5)




