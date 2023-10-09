# Algo-Trading
Algo-Trading python code for Zerodha

# Installation 

1) Download the whole direcotry with 'kite_trade.py' file. Kite_trade.py is the main file. Inaddition I have provided several alogoithm trade Banknifty, stocks, Crudeoil, Currency pairs like USD/INR,GBP/INR, EUR/INR
2) To login to the zerodha you need only "log_in_details.txt" which contain your user_iD in the firl line ad password in the second line.
3) keep the file in same directory where your code file is stored

# Prerequisites
Python >=3.*,  Panda, numpy, matloplib

# Python Code Example
LOGIN
```
from kite_trade import *
import time  
import numpy as np

enctoken = get_enctoken()
kite = KiteApp(enctoken=enctoken)
```
Other Methods
```
# Basic calls
print(kite.margins())
print(kite.orders())
print(kite.positions())

# Get instrument or exchange
print(kite.instruments())
print(kite.instruments("NSE"))
print(kite.instruments("NFO"))

# Get Live Data
print(kite.ltp("NSE:RELIANCE"))
print(kite.ltp(["NSE:NIFTY 50", "NSE:NIFTY BANK"]))
print(kite.quote(["NSE:NIFTY BANK", "NSE:ACC", "NFO:NIFTY22SEPFUT"]))

# Get Historical Data
import datetime
instrument_token = 9604354
from_datetime = datetime.datetime.now() - datetime.timedelta(days=7)     # From last & days
to_datetime = datetime.datetime.now()
interval = "5minute"
print(kite.historical_data(instrument_token, from_datetime, to_datetime, interval, continuous=False, oi=False))


# Place Order
order = kite.place_order(variety=kite.VARIETY_REGULAR,
                         exchange=kite.EXCHANGE_NSE,
                         tradingsymbol="ACC",
                         transaction_type=kite.TRANSACTION_TYPE_BUY,
                         quantity=1,
                         product=kite.PRODUCT_MIS,
                         order_type=kite.ORDER_TYPE_MARKET,
                         price=None,
                         validity=None,
                         disclosed_quantity=None,
                         trigger_price=None,
                         squareoff=None,
                         stoploss=None,
                         trailing_stoploss=None,
                         tag="TradeViaPython")

print(order)

# Modify order
kite.modify_order(variety=kite.VARIETY_REGULAR,
                  order_id="order_id",
                  parent_order_id=None,
                  quantity=5,
                  price=200,
                  order_type=kite.ORDER_TYPE_LIMIT,
                  trigger_price=None,
                  validity=kite.VALIDITY_DAY,
                  disclosed_quantity=None)

# Cancel order
kite.cancel_order(variety=kite.VARIETY_REGULAR,
                  order_id="order_id",
                  parent_order_id=None)
                  

```
# Algorithms
Moving average
```
panda moving average
```
RSI
```
RSI
```
STOCASTIC
```
STOCASTIC
```
Money Flow Index
```
Money Flow Index
```
