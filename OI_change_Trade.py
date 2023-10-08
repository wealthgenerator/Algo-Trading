from kite_trade import *
import numpy as np
import time 
import math 
import json
from datetime import datetime, timedelta
import pandas as pd
"""
1> Check the Future OI change in the first 15 mins (9:15-9:30). It alerts when the OI change is 3%. it indicates operators are interested.  
2> make a position when the price change after at 9:30 is less than 2%
3> If the price change is positive, go long, and if the price change is negative go short.
4> put stop loss at the previous day's low.
"""

"""
{'date': datetime.datetime(2023, 6, 9, 15, 2, tzinfo=tzoffset(None, 19800)), 'open': 2488.15, 'high': 2488.35, 'low': 2486.05, 'close': 2486.5, 'volume': 51500, 'oi': 36365750}, {'date': datetime.datetime(2023, 6, 9, 15, 3, tzinfo=tzoffset(None, 19800)), 'open': 2486.5, 'high': 2487.5, 'low': 2486, 'close': 2486, 'volume': 22000, 'oi': 36392500}
"""
"""
Somehow all open ietrest change comming out to be negetive. 
"""

enctoken = get_enctoken()
kite = KiteApp(enctoken=enctoken)

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
                         product=kite.PRODUCT_CNC,
                         order_type=kite.ORDER_TYPE_MARKET) #this limiting order will trigger when price reaches 90.9 and limit price is 91.0
    return order_id
    
print(LTP("NSE:RELIANCE"))


# List of stock traded in future in NSE
#https://www.nseindia.com/products-services/equity-derivatives-list-underlyings-information
df = pd.read_csv('OI_Search_Algo/ind_niftymidcap50list.csv')
df = pd.read_csv('OI_Search_Algo/Future_Stocks.csv')

# intialising veriables
Total_PL = 0.0
No_of_trade = 0.0
while True:
    #TIME = (datetime.today().strftime("%Y-%m-%d"))+" 6:00:01"
    for i in range(len(df["Symbol"])): # scanning over all the stock traded in NSE
        stock = df["Symbol"][i]
        #print(i, stock)
        instrument = "NFO:%s23JUNFUT"%stock
        response = kite.ltp(instrument)[instrument] #this work even after market close. 
        instrument_token = response['instrument_token']
        #previous_day_low_High(-1)
        #to_date=(datetime.today()+timedelta(days=0, hours=3, minutes=30)).strftime("%Y-%m-%d %H:%M:%S");print(to_date)
        to_date = (datetime.today().strftime("%Y-%m-%d"))+" 9:30:01"#;  print(to_date)
        
        from_date = ((datetime.today()-timedelta(days=1)).strftime("%Y-%m-%d"))+" 15:29:00"#;  print(from_date)
        data=(kite.historical_data(instrument_token, from_date, to_date, "minute", False, True))
        l = 0
        #print(data)
        #print(data[0]["date"],data[1]["date"],data[2]["date"],data[-1]["date"])
        #print(to_date, data[len(data)-1]["oi"], data[len(data)-1]["open"], data[len(data)-1]["high"], data[len(data)-1]["low"], data[len(data)-1]["close"])
        change_OI = (data[-1]["oi"]-data[l]["oi"])*100/data[l]["oi"]
        change_price = (data[-1]["close"]-data[l]["close"])*100/data[l]["close"]
        invested_amount=50000
        
        #check price change positive or negetive based on that decide whther to short the stock or long the stock.
        # also put a condition close & high or open and low are small?
        # try to get carried over open interest.
        HIGH,LOW = previous_day_low_High(-1)
        if (change_OI>3 and 0.0<abs(change_price)<2.0):
            print(i, stock)
            no_of_share = int(invested_amount/data[l]["close"])
            #Define_stoplose = previous days low
            #HIGH,LOW = previous_day_low_High(-1)
            print(HIGH,LOW)
            data[1]["high"]
            #trailing stoplose= tral for one percent move. 
            # exit on the same day when you are selling
            if 0.0<change_price<2.0:    # buy condition
                if (abs(data[1]["low"]-data[1]["open"])< 0.5*LTP(instrument)/100): # low and open is less that 0.5% for the first 15 mins candle 
                    #Plase lone order CNS
                    print("BUY % s %s at "%(no_of_share,stock),data[-1]["date"]," @",data[-1]["close"])
                    #order_id = my_job_Market("NSE:%s"%stock,"LONG",no_of_share)
                    PL =  0*no_of_share*(LTP(instrument)-data[-1]["close"])
            if -2.0<change_price<0.0:# Sell condition
                #Plase short order NORMAL
                if (abs(data[1]["high"]-data[1]["open"])< 0.5*LTP(instrument)/100): # low and open is less that 0.5% for the first 15 mins candle
                    print("SELL %s %s at "%(no_of_share,stock),data[-1]["date"]," @",data[-1]["close"])
                    #order_id = my_job_Market("NSE:%s"%stock,"SHORT",no_of_share)
                    PL =  0*no_of_share*(LTP(instrument)-data[-1]["close"])
            Total_PL = Total_PL + PL
            No_of_trade = No_of_trade +1
            
            #print(data[0]["date"], data[0]["close"] )
            #print(data[len(data)-1]["date"],  data[len(data)-1]["close"])   
            print(data[0]["date"],data[1]["date"],data[-1]["date"])
            print("change in OI=",change_OI, "%   and change in Price=",change_price,"%  PL=", PL) 
    time.sleep(10)
    TIME = (datetime.today().strftime("%h:%m:%s"))
    if (TIME>"6:01:00"):
        break

print("No_of_trade=",No_of_trade,"Total_PL=",Total_PL )  
