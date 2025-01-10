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
import yfinance as yf

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
    def find_top_movers(self):
        top_movers_list = rrm.get_top_movers()
        return_list = []
        for stock in top_movers_list:
            return_list.append(stock.get('symbol'))
        return return_list

    # Implementation should be changed (layout of df is wrong) 
    def find_top_movers_as_data_frame(self):
        top_movers_list = rrm.get_top_movers()
        top_movers_df = pd.DataFrame(top_movers_list)
        top_movers_df = top_movers_df.T # Reorganizes 
        # self.top_movers_df['ticker'] = self.top_movers_df.index # "Ticker" replaces index label 
        # self.top_movers_df = self.top_movers_df.reset_index(drop=True) # Removes indexes - indexes = tickers
        # cols = self.top_movers_df.columns.drop(['symbol']) # Classifies the columns 
        # self.top_movers_df[cols] = self.top_movers_df[cols].apply(pd.to_numeric, errors='coerce') # Edits columns to be of type float64 
        return top_movers_df

    # Returns a list of the top s&p500 up movers of the day 
    def find_top_movers_sp500(self):
        return rrm.get_top_movers_sp500(direction='up')
        
    # Using yfinance instead robin_stocks for data
    # Implementing function to buy and sell stocks based on moving average crossover 
    def moving_average_crossover(self, stock_name, execute_real=False):
        timer = 0
        while timer < 5: # Will execute over a period of 30 mins 
            data = yf.download(stock_name, period='5d', interval='5m') # Get the data over the past 5 days and an interval of 5 minutes
            data['SMA50'] = data['Close'].rolling(window=50).mean() # Add the close price over a window of 50
            data['SMA200'] = data['Close'].rolling(window=200).mean() # Add the close price over a window of 200

            signal = self.moving_average_signal(data) # Get the signal for buying and selling 
            
            # Buy and Sell based on the signal
            if signal == 'BUY':
                self.place_buy_order(stock_name, 1, execute_real)
            elif signal == 'SELL':
                self.place_sell_order(stock_name, 1, execute_real)

            print(signal)
            time.sleep(300) # Wait 5 minutes
            timer += 1

    # Helper function to get the signal - logic section
    def moving_average_signal(self, data):
        if data['SMA50'].iloc[-2] < data['SMA200'].iloc[-2] and data['SMA50'].iloc[-1] > data['SMA200'].iloc[-1]: 
            return "BUY"  # Golden Cross (SMA50 crosses above SMA200)
        elif data['SMA50'].iloc[-2] > data['SMA200'].iloc[-2] and data['SMA50'].iloc[-1] < data['SMA200'].iloc[-1]:
            return "SELL"  # Death Cross (SMA50 crosses below SMA200)
        else:
            return "HOLD"  # No crossover

    # Function to place an order, default is to not buy for real
    def place_buy_order(self, stock, amount, real=False):
        if real:
            try: 
                response = rr.orders.order_buy_market(stock, amount)
                print(f"Bought {amount} shares of {stock}")
                return response
            except:
                print("Error in Buying")
                return None
        else:
            try:
                response = float(rrs.get_latest_price(stock)) * amount
                print(f"Theoretical: Bought {amount} shares of {stock}")
                return response
            except:
                print("Theoretical: Error in Buying")
                return None
    
    # Function to place an order, default is to not sell for real
    def place_sell_order(self, stock, amount, real=False):
        if real:
            try: 
                response = rr.orders.order_sell_market(stock, amount)
                print(f"Sold {amount} shares of {stock}")
                return response
            except:
                print("Error in Selling")
                return None
        else:
            try:
                response = float(rrs.get_latest_price(stock)) * amount
                print(f"Theoretical: Sold {amount} shares of {stock}")
                return response
            except:
                print("Theoretical: Error in Selling")
                return None
        

####################### TESTING ################################

# Create the Trading_Algorithm Object 
algorithm = Trading_Algorithm()
algorithm.moving_average_crossover('AAPL', False)




