import numpy as np
import time 
import math 
import json
from datetime import datetime, timedelta

def LTP(instrument):
	return kite.ltp(instrument)[instrument]['last_price']

def my_job(contract,direction,exch,quantity,price,kite):
    # Code to execute
    order_id = kite.place_order(variety=kite.VARIETY_REGULAR,
                         exchange=exch,
                         tradingsymbol=contract,
                         transaction_type=kite.TRANSACTION_TYPE_BUY if direction=='BUY' else kite.TRANSACTION_TYPE_SELL,
                         quantity=quantity,#
                         product=kite.PRODUCT_NRML,
                         order_type=kite.ORDER_TYPE_LIMIT, #this limiting order will trigger when price reaches 90.9 and limit price is 91.0
                         price=price)
    return order_id
def my_job_Market(contract,exch,direction,quantity,kite):
    # Code to execute
    order_id = kite.place_order(variety=kite.VARIETY_REGULAR,
                         exchange=exch,
                         tradingsymbol=contract,
                         transaction_type=kite.TRANSACTION_TYPE_BUY if direction=='BUY' else kite.TRANSACTION_TYPE_SELL,
                         quantity=quantity,#
                         product=kite.PRODUCT_NRML,
                         order_type=kite.ORDER_TYPE_MARKET) #this limiting order will trigger when price reaches 90.9 and limit price is 91.0
                        
    return order_id
def my_job_SL_Tigger(contract,direction,quantity,price,trigger,kite):
    # Code to execute
    order_id = kite.place_order(variety=kite.VARIETY_REGULAR,
                         exchange=exch,
                         tradingsymbol=contract,
                         transaction_type=kite.TRANSACTION_TYPE_BUY if direction=='BUY' else kite.TRANSACTION_TYPE_SELL,
                         quantity=quantity,#
                         product=kite.PRODUCT_NRML,
                         order_type=kite.ORDER_TYPE_SL, #this limiting order will trigger when price reaches 90.9 and limit price is 91.0
                         price=price,
                         trigger_price=trigger)
    #print("Executing code...")
    return order_id
def modify_my_job(order_id, parent_order_id, quantity, price,kite):
    order_id = kite.modify_order(variety=kite.VARIETY_REGULAR,
                                 order_id=order_id, 
                                 parent_order_id=parent_order_id,
                                 quantity=quantity,
                                 price=price,
                                 order_type=kite.ORDER_TYPE_LIMIT)

    return order_id

