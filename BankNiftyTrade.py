#https://github.com/TradeViaPython/Kite_Zerodha
#https://kite.trade/forum/discussion/5574/change-in-format-of-weekly-options-instruments

'''
NSE has introduced NIFTY weekly options with which all the weekly instruments format has changed.
Now the tradingsymbol BANKNIFTY14FEB1927500CE has become BANKNIFTY1921425000CE.
The format is BANKNIFTY<YY><M><DD>strike<PE/CE>
The month format is 1 for JAN, 2 for FEB, 3, 4, 5, 6, 7, 8, 9, O(capital o) for October, N for November, D for December. 
if your price is too high order might not be placed.
'''

from kite_trade import *
import numpy as np
import time 
import math 
import json
from datetime import datetime, timedelta

from matplotlib import *
import matplotlib.pyplot as plt

enctoken = get_enctoken()
kite = KiteApp(enctoken=enctoken)
print("Session started---------------------")


contract_list = {"EUR":"EURINR23JUNFUT","USD":"USDINR23JUNFUT"}
SL_data = {"EUR":{"Trigger":90.9,"SL":91.00}, "USD":{"Trigger":83.5,"SL":83.505}, "GBP":{"Trigger":103,"SL":103.1} }

Last_traded = {"EUR":{"Last_trade":88.44,"Profit_booking_step":0.2,"exit_order_id":"230531202969507","add_order_id":"230531202969507"}, 
                     "USD":{"Last_trade":82.5,"Profit_booking_step":0.2,"exit_order_id":"230531202969507","add_order_id":"230531202969507"}, 
                     "GBP":{"Last_trade":102.74,"Profit_booking_step":0.2,"exit_order_id":"230531202969507","add_order_id":"230531202969507"}}
instrument_list = ["EUR","USD"]

def LTP(instrument):
	return kite.ltp(instrument)[instrument]['last_price']

def my_job(contract,direction,quantity,price):
    # Code to execute
    order_id = kite.place_order(variety=kite.VARIETY_REGULAR,
                         exchange=kite.EXCHANGE_NFO,
                         tradingsymbol=contract,
                         transaction_type=kite.TRANSACTION_TYPE_BUY if direction=='LONG' else kite.TRANSACTION_TYPE_SELL,
                         quantity=quantity,#
                         product=kite.PRODUCT_NRML,
                         order_type=kite.ORDER_TYPE_LIMIT, #this limiting order will trigger when price reaches 90.9 and limit price is 91.0
                         price=price)
    return order_id
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
def my_job_SL_Tigger(contract,direction,quantity,price,trigger):
    # Code to execute
    order_id = kite.place_order(variety=kite.VARIETY_REGULAR,
                         exchange=kite.EXCHANGE_CDS,
                         tradingsymbol=contract,
                         transaction_type=kite.TRANSACTION_TYPE_BUY if direction=='LONG' else kite.TRANSACTION_TYPE_SELL,
                         quantity=quantity,#
                         product=kite.PRODUCT_NRML,
                         order_type=kite.ORDER_TYPE_SL, #this limiting order will trigger when price reaches 90.9 and limit price is 91.0
                         price=price,
                         trigger_price=trigger)
    #print("Executing code...")
    return order_id
def modify_my_job(order_id, parent_order_id, quantity, price):
    order_id = kite.modify_order(variety=kite.VARIETY_REGULAR,
                                 order_id=order_id, 
                                 parent_order_id=parent_order_id,
                                 quantity=quantity,
                                 price=price,
                                 order_type=kite.ORDER_TYPE_LIMIT)

    return order_id

def cancel_order(order):
	if (order["status"]=="OPEN"):
		print("canceling",order["tradingsymbol"])
		kite.cancel_order(variety=kite.VARIETY_REGULAR, order_id=order["order_id"])

def updating_position(order,ins,Last_traded):
    
        if(order["order_id"]== Last_traded[ins]["exit_order_id"] and order["status"]=="COMPLETE"):
            #Placing new BUY order 
            print("Profit booked for: ",order["tradingsymbol"], order["status"])
            Last_traded[ins]["Last_trade"] = Last_traded[ins]["Last_trade"] - Last_traded[ins]["Profit_booking_step"]
            price = Last_traded[ins]["Last_trade"] - Last_traded[ins]["Profit_booking_step"]; price = round(price,2)
            order_id = my_job(contract_list[ins],"LONG",10,price); Last_traded[ins]["exit_order_id"]=order_id
            print("%s New %s exit order placed @"%(Samai(time.localtime()),ins),price,"with last traded price", round(Last_traded[ins]["Last_trade"],2))
            #modify the Sell order price
            #if(order["order_id"]== Last_traded["EUR"]["add_order_id"] and order["status"][:3]=="AMO"):
            price = Last_traded[ins]["Last_trade"] + Last_traded[ins]["Profit_booking_step"]
            order_id = modify_my_job(Last_traded[ins]["add_order_id"], None, 10, price); Last_traded[ins]["add_order_id"]=order_id
            print("%s %s add order is modified to ->"%(Samai(time.localtime()),ins),price, "with last traded price", round(Last_traded[ins]["Last_trade"],2))    
            #ADDING NEW POSITION CASE--------------------------------------------
        if(order["order_id"]== Last_traded[ins]["add_order_id"] and order["status"]=="COMPLETE"):
            print("Famr gainst our favour,Adding Position for: ",order["tradingsymbol"], order["status"])
            #Placing new BUY order
            Last_traded[ins]["Last_trade"] = Last_traded[ins]["Last_trade"] + Last_traded[ins]["Profit_booking_step"]
            price = Last_traded[ins]["Last_trade"] + Last_traded[ins]["Profit_booking_step"]; price = round(price,2)
            order_id = my_job(contract_list[ins],"SHOT",10,price); Last_traded[ins]["add_order_id"]=order_id
            print("%s New %s add order placed @"%(Samai(time.localtime()),ins),price,"with last traded price", round(Last_traded[ins]["Last_trade"],2))
                    
            #modify the BUY order price
            price = Last_traded[ins]["Last_trade"] - Last_traded[ins]["Profit_booking_step"]
            order_id = modify_my_job(Last_traded[ins]["exit_order_id"], None, 10, price); Last_traded[ins]["exit_order_id"]=order_id
            print(" %s %s exit order is modified to ->"%(Samai(time.localtime()),ins),price, "with last traded price", round(Last_traded[ins]["Last_trade"],2))

def First_order(ins,Last_traded):
    price = Last_traded[ins]["Last_trade"] - Last_traded[ins]["Profit_booking_step"]
    order_id = my_job(contract_list[ins],"LONG",10,price); Last_traded[ins]["exit_order_id"]=order_id; print("%s %s Exit order placed @"%(Samai(time.localtime()),ins),round(price,2))
    #print("EUR exit_order_id",Last_traded[ins]["exit_order_id"])
    price = Last_traded[ins]["Last_trade"] + Last_traded[ins]["Profit_booking_step"]; price = round(price,2)
    order_id = my_job(contract_list[ins],"SHOT",10,price); Last_traded[ins]["add_order_id"]=order_id; print("%s %s add order placed @"%(Samai(time.localtime()),ins),round(price,2))
    #print("EUR add_order_id",Last_traded["EUR"]["add_order_id"]) 

def Samai(result):
    return "%s:%s:%s"%(result.tm_hour,result.tm_min,result.tm_sec)

def Hystorical_OI_data(instrument, from_date, to_date, interval):
    data=(kite.historical_data(instrument_token, from_date, to_date, interval, False, True))
    print("function call",data[0]["date"],data[-1]["date"])
    OI_list = [data[i]["oi"] for i in range(len(data))]
    #print(OI_list)
    return OI_list
import pandas as pd
def Hystorical_TOI_data(strike, from_date, to_date, interval):
    array = [0,100,200,300,400,500]
    for inc in array:
        instrument = "NFO:BANKNIFTY23615%sCE"%(strike+inc); print(instrument);response = kite.ltp(instrument)[instrument]; instrument_token = response['instrument_token']
        data=(kite.historical_data(instrument_token, from_date, to_date, interval, False, True))
        file_name = "historical_data_BANKNIFTY23615%sCE.csv"%(strike+inc)
        #https://medium.com/@ganeshnagarvani/collecting-data-through-kites-historical-api-for-algorithmic-trading-9bf8ce425f45
        df = pd.DataFrame(); df = df.append(pd.DataFrame(data)); df.to_csv(file_name,index=False)
        #with open(file_name, "w") as f:
        #    json.dump(data, f, default=json_serial)
    	#print("function call",data[0]["date"],data[-1]["date"])
        OI_list = np.array([data[i]["oi"] for i in range(len(data))])
        if inc==0: 
            OI_CE_list = OI_list*0
        OI_CE_list = OI_CE_list + OI_list
        instrument = "NFO:BANKNIFTY23615%sPE"%(strike-inc); response = kite.ltp(instrument)[instrument]; instrument_token = response['instrument_token']
        data=(kite.historical_data(instrument_token, from_date, to_date, interval, False, True))
        file_name = "historical_data_BANKNIFTY23615%sPE.csv"%(strike-inc)
        df = pd.DataFrame(); df = df.append(pd.DataFrame(data)); df.to_csv(file_name,index=False)
        OI_list = np.array([data[i]["oi"] for i in range(len(data))])
        if inc==0: 
            OI_PE_list = OI_list*0
        OI_PE_list = OI_PE_list + OI_list
    #print(OI_list)
    return OI_CE_list, OI_PE_list
    
# Method to get nearest strikes
def round_nearest(x,num=50): return int(math.ceil(float(x)/num)*num)
def nearest_strike_bnf(x): return round_nearest(x,100)
def nearest_strike_nf(x): return round_nearest(x,50)


#+++++++++Placing stoplose in CURRENCY

print("Trading started at-->",Samai(time.localtime()))
#order_id = my_job("BANKNIFTY23JUN35000PE","SHOT",25,10)
#order_id = my_job("BANKNIFTY2360144500CE","SHOT",25,5) 


stradle_strike = nearest_strike_bnf(round(LTP("NSE:NIFTY BANK"),2))
lot_size=25; no_lot = 1; prifit_per_lot = 100
#print(LTP("NSE:RELIANCE"))
#print(LTP("NFO:BANKNIFTY23608%sCE"%stradle_strike))
#print(LTP("CDS:USDINR23JUNFUT"))

print("Stradel_Sell_algorith @ %s"%stradle_strike)

CE_strike = "BANKNIFTY23615%sCE"%stradle_strike
PE_strike = "BANKNIFTY23615%sPE"%stradle_strike
instrument = "NFO:%s"%CE_strike
#print(kite.ltp(instrument))

response = kite.ltp(instrument)[instrument] #this work even after market close. 
instrument_token = response['instrument_token']#; print(instrument_token)
#from_date = datetime.date(2023, 6, 1) #YYYY,MM,DD
#to_date = datetime.date(2022, 6, 6)
#historical_data = kite.historical_data(instrument_token, from_date, to_date, "day")
print("Time &   Oi of ",instrument)
from_date="2023-05-29 09:15:00"
to_date = "2023-06-08 15:25:00"
OI_list = Hystorical_OI_data(instrument, from_date, to_date, "minute")
plt.plot(range(len(OI_list)),OI_list); plt.show()
OI_CE_list, OI_PE_list = Hystorical_TOI_data(stradle_strike, from_date, to_date, "minute")
plt.plot(range(len(OI_CE_list)),OI_CE_list,label="TOI_CE");plt.plot(range(len(OI_PE_list)),OI_PE_list,label="TOI_PE"); plt.legend(); plt.show()
while True:
    #to_date=datetime.today().strftime("%Y-%m-%d %H:%M:%S") + " 03:30:00"; print(to_date)
    to_date=(datetime.today()+timedelta(days=0, hours=3, minutes=30)).strftime("%Y-%m-%d %H:%M:%S");print(to_date)
    from_date = ((datetime.today()-timedelta(days=7)).strftime("%Y-%m-%d"))+" 09:15:00";  print(from_date)
    data=(kite.historical_data(instrument_token, from_date, to_date, "minute", False, True))
    print(to_date, data[len(data)-1]["oi"], data[len(data)-1]["open"], data[len(data)-1]["high"], data[len(data)-1]["low"], data[len(data)-1]["close"])
    #Hystorical_OI_data(instrument, from_date, to_date, "minute")

    time.sleep(62)
    
    #print(data[len(data)-1],data[len(data)-2])
#print('Open_interest',response["NFO:%s"%CE_strike]["oi"])

'''
while True:
    result = time.localtime()
    if (result.tm_hour>=9 and result.tm_min>0 ):
        #print(time.localtime())
        #order_id = my_job_Market(CE_strike,"SHORT",lot_size*no_lot)
        #order_id = my_job_Market(PE_strike,"SHORT",lot_size*no_lot)
        CE_strike_price_int = LTP("NFO:%s"%CE_strike)
        PE_strike_price_int = LTP("NFO:%s"%PE_strike)
        total_premium_int = CE_strike_price_int + PE_strike_price_int
        print("%s Creating stardel :"%Samai(time.localtime())," at strike price: ",stradle_strike, " with total premium(%s(PE)+%s(CE))=%s"%(PE_strike_price_int,CE_strike_price_int,total_premium_int)) 
    
    
        
        while True:
            CE_strike_price = LTP("NFO:%s"%CE_strike)
            PE_strike_price = LTP("NFO:%s"%PE_strike)

            total_premium = CE_strike_price + PE_strike_price
            change_in_premium = total_premium - total_premium_int
            print("%s NIFTY BANK:"%Samai(time.localtime()),round(LTP("NSE:NIFTY BANK"),2),"change_in_premium ",round(change_in_premium,2))
            if change_in_premium> prifit_per_lot:
                #order_id = my_job_Market(CE_strike,"LONG",lot_size*no_lot)
                #order_id = my_job_Market(PE_strike,"LONG",lot_size*no_lot)
                print("%s closing the stardel with profit:"%Samai(time.localtime()),change_in_premium*no_lot*lot_size )
                break
            
            if(abs(LTP("NSE:NIFTY BANK") - stradle_strike)>1200 ):
                #order_id = my_job_Market(CE_strike,"LONG",lot_size*no_lot)
                #order_id = my_job_Market(PE_strike,"LONG",lot_size*no_lot)
                print("%s closing the stardel with lose:"%Samai(time.localtime()),change_in_premium*no_lot*lot_size )
                break
            time.sleep(10)
        break
    time.sleep(10)
'''
'''
    for ins in instrument_list:   
       First_order(ins,Last_traded)
    while True:       
        for i in range(len(kite.orders())):
            order = kite.orders()[i]#; print(order)
            #PROFIT BOOKING CASE---------------------------------------------------
            for ins in instrument_list: 
                updating_position(order,ins,Last_traded)
        result = time.localtime()
        #if(order["status"]=="AMO"):print("Cheking market at : ",result.tm_hour,":",result.tm_min,":",result.tm_sec)
        # closing the open position 5 min before Currency market closing time @ 5PM 
        if (result.tm_hour>=13 and result.tm_min>25 ):
            for i in range(len(kite.orders())):
                
                order = kite.orders()[i]#; print(order)
                if(order["tradingsymbol"][:3]=="EUR" or order["tradingsymbol"][:3]=="USD" or order["tradingsymbol"][:3]=="GBP"):
                    cancel_order(order)
            break
            
        time.sleep(10)
                
                
#kite.get_order_status(order_id)
   
    #price = Last_traded["EUR"]["Last_trade"] + Last_traded["EUR"]["Profit_booking_step"]; print("EUR SELL@",price)
    #order_id = my_job(contract_list["EUR"],"SHORT",10,price)
    

        price = Last_traded_price["USD"]["Last_trade"] - Last_traded_price["USD"]["Profit_booking_step"]; print("USD buy@",price)
        my_job(contract_list["USD"],"LONG",10,price)
        
        price = Last_traded_price["USD"]["Last_trade"] + Last_traded_price["USD"]["Profit_booking_step"]; print("USD SELL@",price)
        my_job(contract_list["USD"],"SHORT",10,price)
        time.sleep(60)  # Wait for 60 seconds before checking the schedule again
    
	instrument = "NSE:NIFTY BANK";print(LTP(instrument))
	if( position["tradingsymbol"][:4]=="BANK" and LTP(instrument)> 44300 ):
		#kite.place_order3(position["tradingsymbol"])
		kite.place_order2(exchange=kite.EXCHANGE_NFO,
                         tradingsymbol=position["tradingsymbol"],
                         transaction_type=kite.TRANSACTION_TYPE_SELL,
                         quantity=abs(position["quantity"]),#
                         product=kite.PRODUCT_NRML,
                         order_type=kite.ORDER_TYPE_MARKET, #this limiting order will trigger when price reaches 90.9 and limit price is 91.0
                         price=44900,
                         trigger_price=44800)
                
	

#Stradel Adjustment
instrument = "NSE:RELIANCE"

print(LTP(instrument))
#Autosquareoff the position when banknifty goes to 1200 point in either directions.
instrument = "NSE:NIFTY BANK";print(LTP(instrument))
#if( LTP(instrument)> 44300 or LTP(instrument)< 42500):
if( LTP(instrument)> 44300 ):
   kite.place_order(variety=kite.VARIETY_REGULAR,
                         exchange=kite.EXCHANGE_NFO,
                         tradingsymbol="BANKNIFTY2360143700CE",
                         transaction_type=kite.TRANSACTION_TYPE_BUY,
                         quantity=1,#
                         product=kite.PRODUCT_NRML,
                         order_type=kite.ORDER_TYPE_SL, #this limiting order will trigger when price reaches 90.9 and limit price is 91.0
                         price=44900,
                         disclosed_quantity=None,
                         trigger_price=44800,
                         squareoff=None,
                         stoploss=None,
                         trailing_stoploss=None,
                         tag="TradeViaPython")
	#kite.cancel_order(variety=kite.VARIETY_REGULAR, order_id=order["order_id"])	

'''	


