#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 13 08:38:38 2023
@author: bag
"""

from kite_trade import *
import numpy as np
import time 
import math 
import json
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
""" ALGORITHM
1> moving average crossing and RSI algorith for crude OIL
2>
3>
"""

"""
{'date': datetime.datetime(2023, 6, 9, 15, 2, tzinfo=tzoffset(None, 19800)), 'open': 2488.15, 'high': 2488.35, 'low': 2486.05, 'close': 2486.5, 'volume': 51500, 'oi': 36365750}, {'date': datetime.datetime(2023, 6, 9, 15, 3, tzinfo=tzoffset(None, 19800)), 'open': 2486.5, 'high': 2487.5, 'low': 2486, 'close': 2486, 'volume': 22000, 'oi': 36392500}
"""
"""
Somehow all open ietrest change comming out to be negetive. 
"""
enctoken = get_enctoken()
kite = KiteApp(enctoken=enctoken)
print("Session started---------------------")



def LTP(instrument):
	return kite.ltp(instrument)[instrument]['last_price']

def previous_day_low_High(l):
    to_date = (datetime.today().strftime("%Y-%m-%d"))+" 9:10:01"#;  print(to_date)
    
    from_date = ((datetime.today()-timedelta(days=7)).strftime("%Y-%m-%d"))+" 9:00:00"#;  print(from_date)
    data=(kite.historical_data(instrument_token, from_date, to_date, "day", False, True))
    #print(data)
    return data[l]["low"], data[l]["high"]

def my_job_Market(contract,direction,quantity):
    # Code to execute
    order_id = kite.place_order(variety=kite.VARIETY_REGULAR,
                         exchange=kite.EXCHANGE_NFO,
                         tradingsymbol=contract,
                         transaction_type=kite.TRANSACTION_TYPE_BUY if direction=='LONG' else kite.TRANSACTION_TYPE_SELL,
                         quantity=quantity,#
                         product=kite.PRODUCT_NRML,
                         order_type=kite.ORDER_TYPE_MARKET) #this limiting order will trigger when price reaches 90.9 and limit price is 91.0
    return order_id
def RSI(series,period=14):
    #https://zerodha.com/varsity/chapter/indicators-part-1/
    delta = series.diff().dropna() #Calculate differences between two successive points.
    u = delta * 0
    d = u.copy()
    #print(len(u))
    u[delta > 0] = delta[delta > 0]
    d[delta < 0] = -delta[delta < 0]
    u[u.index[period-1]] = np.mean( u[:period] ) #first value is sum of avg gains
    u = u.drop(u.index[:(period-1)])
    d[d.index[period-1]] = np.mean( d[:period] ) #first value is sum of avg losses
    d = d.drop(d.index[:(period-1)])
    # DataFrame.ewm calculate exponantial moving average with exponant=1/(1+com)
    #https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.ewm.html
    rs = pd.DataFrame.ewm(u, com=period-1, adjust=False).mean() / \
         pd.DataFrame.ewm(d, com=period-1, adjust=False).mean()
    return 100 - 100 / (1 + rs)
    #return df


def calculate_super_trend(dataframe, period=10, multiplier=3):
    """
    Calculates the SuperTrend indicator based on the given dataframe.
    
    Args:
        dataframe (pandas.DataFrame): Input data containing 'high', 'low', and 'close' columns.
        period (int): Number of periods for calculation. Default is 10.
        multiplier (int): Multiplier for calculating the Average True Range (ATR). Default is 3.
    
    Returns:
        pandas.DataFrame: Dataframe with SuperTrend values appended as a new column.
    
    Theory:
        The ATR calculation involves determining the average true range of price fluctuations over a specified period. The true range is the maximum value among the following three calculations:

            1>The difference between the current period's high and low.
            2>The absolute value of the difference between the current period's high and the previous period's close.
            3>The absolute value of the difference between the current period's low and the previous period's close.
    """
    df = dataframe.copy()
    atr_multiplier = multiplier
    atr_period = period
    close_column = 'close'
    
    # Calculate True Range (TR)
    df['tr1'] = abs(df['high'] - df['low'])
    df['tr2'] = abs(df['high'] - df[close_column].shift())
    df['tr3'] = abs(df['low'] - df[close_column].shift())
    df['tr'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)
    
    # Calculate Average True Range (ATR)
    df['atr'] = df['tr'].rolling(window=atr_period).mean()
    plt.plot(df['atr'],label="atr"); plt.legend(); plt.show()
    # Calculate SuperTrend Upper Band (STUB)
    df['stub'] = df[close_column] + (atr_multiplier * df['atr'])
    
    # Calculate SuperTrend Lower Band (STLB)
    df['stlb'] = df[close_column] - (atr_multiplier * df['atr'])
    plt.plot(df['stub'],label="stub"); plt.plot(df['stlb'],label="stlb");plt.plot(df[close_column],label="close_column"); plt.legend(); plt.show()
    # Calculate SuperTrend
    df['supertrend'] = None
    df.loc[df[close_column] > df['stlb'], 'supertrend'] = 1 # supertrend put to 1 for rows whose close is greter than stlb 
    df.loc[df[close_column] < df['stub'], 'supertrend'] = -1
    
    # Forward fill the SuperTrend values to make them continuous
    df['supertrend'] = df['supertrend'].ffill() # if there is data missing fill it with ***
    
    return df



instrument = "MCX:%s23JULFUT"%"CRUDEOILM"
print(LTP(instrument))

import pandas as pd
response = kite.ltp(instrument)[instrument] #this work even after market close. 
instrument_token = response['instrument_token']
#previous_day_low_High(-1)
#to_date=(datetime.today()+timedelta(days=0, hours=3, minutes=30)).strftime("%Y-%m-%d %H:%M:%S");print(to_date)
while True:
    to_date =(datetime.today()+timedelta(days=0, hours=3, minutes=30)).strftime("%Y-%m-%d %H:%M:%S")#;  print(to_date)
    from_date = ((datetime.today()-timedelta(days=14)).strftime("%Y-%m-%d"))+" 9:29:00"#;  print(from_date)
    data=(kite.historical_data(instrument_token, from_date, to_date, "15minute", False, True))
    df = pd.DataFrame(); df = df.append(pd.DataFrame(data))
    series = df["close"][1:20]
    #print(series)
    #print(series.diff())
    #print(series.diff().dropna())
    
    df["RSI"] = RSI(df["close"],period=14)
    df["supertrend"] = calculate_super_trend(df, period=10, multiplier=3)['supertrend']
    plt.plot(df['supertrend'], label='supertrend'); plt.legend()
    plt.show()
    #print(rsi)
    #print(to_date,df["date"][len(df["date"])-1], rsi[len(df["date"])-1])
    #print(to_date,df["date"][0],rsi)
    df["MA20"] = pd.DataFrame.ewm(df["close"], span=20, adjust=False).mean()
    df["MA10"] = pd.DataFrame.ewm(df["close"], span=10, adjust=False).mean()
    print("time->",to_date,"MA20 ",df["MA20"][len(df["MA20"])-1],"MA10 ",df["MA10"][len(df["MA10"])-1],"RSI ",df["RSI"][len(df["date"])-1], "LTP", LTP(instrument))
    if (df["MA20"][len(df["MA20"])-1]< df["MA10"][len(df["MA10"])-1] and  df["RSI"][len(df["date"])-1]<50):
        job_id = my_job_Market(instrument,"SHORT",2)
        break
    time.sleep(400)
    
'''
df["MA20"] = MA20; df["MA10"] = MA10;
plt.plot(df['MA20'], label='MA20')
plt.plot(df['MA10'], label='MA10')
plt.plot(df['close'], label='close')
plt.legend()
plt.show()
'''
'''
def strategy(records):
#https://www.profitaddaweb.com/2017/07/implementation-of-simple-moving-average.html
 total_closing_price = 0
 record_count = 0
 order_placed = False
 last_order_placed = None
 last_order_price = 0
 profit = 0

 for record in records:
  record_count += 1
  total_closing_price += record["close"]
  
  #Moving avearge is calculated for every 5 ticks(records)
  if record_count >= 5:
   moving_average = total_closing_price/5

   # If moving average is greater than last tick, place a buy order
   if record["close"] &amp;gt; moving_average:
    if last_order_placed == "SELL" or last_order_placed is None:
     
     # If last order was sell, exit the stock first
     if last_order_placed == "SELL":
      print ("Exit SELL")

      # Calculate profit
      profit += last_order_price - record["close"]
      last_order_price = record["close"]

     # Fresh BUY order
     print ("place new BUY order")
     last_order_placed = "BUY"

  # If moving average is lesser than last tick, and there is a position, place a sell order
   elif record["close"] &amp;lt; moving_average:
    if last_order_placed == "BUY":
     
     # As last order was a buy, first let's exit the position
     print ("Exit BUY")
     
     # Calculate profit
     profit += record["close"] - last_order_price
     last_order_price = record["close"]
     
     # Fresh SELL order
     print ("place new SELL order")
     last_order_placed = "SELL"
     

   
   total_closing_price -= records[record_count-5]["close"]
 print ("Gross Profit ", profit)
 # PLace the last order 
 place_order(last_order_placed)

# Place an order based upon transaction type(BUY/SELL)
def place_order(transaction_type):
 kite.order_place(tradingsymbol="RELIANCE", exchange="NSE", quantity=1, transaction_type=transaction_type, order_type="MARKET", product="CNC")


def start():
 records = get_historical_data()
 strategy(records)

start()
'''
