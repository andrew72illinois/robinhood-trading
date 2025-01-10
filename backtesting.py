import trading
import pyalgotrade
import time
import pandas as pd
import numpy as np
import matplotlib as mp
import matplotlib.pyplot as plt
from robin_stocks import *
import robin_stocks.robinhood as rr
import robin_stocks.robinhood.stocks as rrs
import robin_stocks.robinhood.markets as rrm

def Fibonacci_Retracements_On_Historical_Data(ticker):
    data = rrs.get_stock_historicals(ticker, interval='10minute', span='day') # data is a list of dictionaries
    high = float(data[0]['high_price'])
    low = float(data[0]['low_price'])
    for index in data:
        if float(index['high_price']) > high:
            high = float(index['high_price'])
        if float(index['low_price']) < low:
            low = float(index['low_price'])
    diff = high - low
    levels = {
            '100%': high,
            '61.8%' : high - .618 * diff,
            '50%' : high - .5 * diff,
            '38.2%' : high - .382 * diff,
            '23.6%' : high - .236 * diff,
            '0%' : low
    }
    plt.figure(figsize=(10,6))
    count = 0
    graph = {"time" : [], "price" : []}
    
    for index in data:
        graph['price'].append(float(index['close_price']))
        graph['time'].append(count * 10)
        count+=1 
    plt.plot(graph['time'], graph['price'], label=f'{ticker} Price', color='blue')  
    for level in levels.values():
        plt.axhline(level, linestyle='--', label=f'{level:.2f}')
    plt.title(f'{ticker} Fibonacci Retracements')
    plt.xlabel('Time')
    plt.ylabel('Price')
    plt.grid(True)
    plt.savefig('results/fibonacci_retracements.png')

Fibonacci_Retracements_On_Historical_Data('NVDA')