#https://github.com/TradeViaPython/Kite_Zerodha
#bwIHfrIBHA7Jpc9iDJax6xt1cr3X7%2F5kl7LhtAptbgQWTFZGyMPrzSd7EP7Qn6%2BchnBFFFCBoI0NadgEvDyR9KwbaUK9PaeCxfl3mnQ1B1IZSV51H80oLQ%3D%3D

from kite_trade import *
import time  
import numpy as np

enctoken = get_enctoken()
kite = KiteApp(enctoken=enctoken)
print("Session started---------------------")

last_traded_price_lis= np.loadtxt("last_traded_list.txt")
# What are the instrument you will trade Today

instrument_list = ["EUR","USD", "GBP"]
contract_list = {"EUR":"EURINR23JUNFUT","USD":"USDINR23JUNFUT","GBP":"GBPINR23JUNFUT"}
SL_data = {"EUR":{"Trigger":90.9,"SL":91.00}, "USD":{"Trigger":83.5,"SL":83.505}, "GBP":{"Trigger":104.5,"SL":104.51} }

Last_traded = {"EUR":{"Last_trade":last_traded_price_lis[0],"Profit_booking_step":0.2,"LONG_order_id":"230531202969507", "SHORT_order_id":"230531202969507"}, 
                     "USD":{"Last_trade":last_traded_price_lis[1],"Profit_booking_step":0.2,"LONG_order_id":"230531202969507", "SHORT_order_id":"230531202969507"}, 
                     "GBP":{"Last_trade":last_traded_price_lis[2],"Profit_booking_step":0.2,"LONG_order_id":"230531202969507","SHORT_order_id":"230531202969507"}}

def LTP(instrument):
	return kite.ltp(instrument)[instrument]['last_price']

def my_job(contract,direction,quantity,price):
    # Code to execute
    order_id = kite.place_order(variety=kite.VARIETY_REGULAR,
                         exchange=kite.EXCHANGE_CDS,
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
                         order_type=kite.ORDER_TYPE_MARKET)
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
    
        if(order["order_id"]== Last_traded[ins]["LONG_order_id"] and order["status"]=="COMPLETE"):
            #Placing new BUY order 
            print("Profit booked for: ",order["tradingsymbol"], order["status"])
            Last_traded[ins]["Last_trade"] = Last_traded[ins]["Last_trade"] - Last_traded[ins]["Profit_booking_step"]
            price = Last_traded[ins]["Last_trade"] - Last_traded[ins]["Profit_booking_step"]; price = round(price,2)
            order_id = my_job(contract_list[ins],"LONG",10,price); Last_traded[ins]["LONG_order_id"]=order_id
            print("%s New %s LONG order placed @"%(Samai(time.localtime()),ins),price,"with last traded price", round(Last_traded[ins]["Last_trade"],2))
            #modify the Sell order price
            #if(order["order_id"]== Last_traded["EUR"]["add_order_id"] and order["status"][:3]=="AMO"):
            price = Last_traded[ins]["Last_trade"] + Last_traded[ins]["Profit_booking_step"]
            order_id = modify_my_job(Last_traded[ins]["SHORT_order_id"], None, 10, price); Last_traded[ins]["SHORT_order_id"]=order_id
            print("%s %s SHORT order is modified to ->"%(Samai(time.localtime()),ins),price, "with last traded price", round(Last_traded[ins]["Last_trade"],2))    
            #ADDING NEW POSITION CASE--------------------------------------------
        if(order["order_id"]== Last_traded[ins]["SHORT_order_id"] and order["status"]=="COMPLETE"):
            print("Trend againtst in your favour,SHORTing Position for: ",order["tradingsymbol"], order["status"])
            #Placing new BUY order
            Last_traded[ins]["Last_trade"] = Last_traded[ins]["Last_trade"] + Last_traded[ins]["Profit_booking_step"]
            price = Last_traded[ins]["Last_trade"] + Last_traded[ins]["Profit_booking_step"]; price = round(price,2)
            order_id = my_job(contract_list[ins],"SHOT",10,price); Last_traded[ins]["SHORT_order_id"]=order_id
            print("%sNew %s SHORT order placed @"%(Samai(time.localtime()),ins),price,"with last traded price", round(Last_traded[ins]["Last_trade"],2))
                    
            #modify the BUY order price
            price = Last_traded[ins]["Last_trade"] - Last_traded[ins]["Profit_booking_step"]
            order_id = modify_my_job(Last_traded[ins]["LONG_order_id"], None, 10, price); Last_traded[ins]["LONG_order_id"]=order_id
            print(" %s %s LONG order is modified to ->"%(Samai(time.localtime()),ins),price, "with last traded price", round(Last_traded[ins]["Last_trade"],2))

def First_order(ins,Last_traded):
    price = Last_traded[ins]["Last_trade"] - Last_traded[ins]["Profit_booking_step"]
    order_id = my_job(contract_list[ins],"LONG",10,price); Last_traded[ins]["LONG_order_id"]=order_id; print("%s %s LONG order placed @"%(Samai(time.localtime()),ins),price)
    #print("EUR exit_order_id",Last_traded[ins]["exit_order_id"])
    price = Last_traded[ins]["Last_trade"] + Last_traded[ins]["Profit_booking_step"]; price = round(price,2)
    order_id = my_job(contract_list[ins],"SHOT",10,price); Last_traded[ins]["SHORT_order_id"]=order_id; print("%s %s SHORT order placed @"%(Samai(time.localtime()),ins),price)
    #print("EUR add_order_id",Last_traded["EUR"]["add_order_id"]) 

def First_order2(ins,Last_traded):
    diff = LTP("CDS:%s"%ins)-Last_traded[ins]["Last_trade"]
    factor = int(diff/Last_traded[ins]["Profit_booking_step"])
    if diff>0.0: 
        print("%s opend positive, Last traded price was %s and LTP %s"%(ins[:3],Last_traded[ins]["Last_trade"],LTP("CDS:%s"%ins)))
        
    else:
        print("%s opend positive, Last traded price was %s and LTP %s"%(ins[:3],Last_traded[ins]["Last_trade"],LTP("CDS:%s"%ins)))
        
    if(factor<=1.0):
        
        price = Last_traded[ins]["Last_trade"] - Last_traded[ins]["Profit_booking_step"]
        order_id = my_job(contract_list[ins],"LONG",10,price); Last_traded[ins]["%s_order_id"%("LONG")]=order_id; print("%s %s %s order placed @"%(Samai(time.localtime()),ins,"LONG"),price)
        #print("EUR exit_order_id",Last_traded[ins]["exit_order_id"])
        price = Last_traded[ins]["Last_trade"] + Last_traded[ins]["Profit_booking_step"]; price = round(price,2)
        order_id = my_job(contract_list[ins],"SHOT",10,price); Last_traded[ins]["SHORT_order_id"]=order_id; print("%s %s SHORT order placed @"%(Samai(time.localtime()),ins),price)
        #print("EUR add_order_id",Last_traded["EUR"]["add_order_id"]) 
    else: 
        
            price2 = Last_traded[ins]["Last_trade"] + factor*np.sign(diff)*Last_traded[ins]["Profit_booking_step"]
            direction2 = "LONG" if diff<0.0 else "SHORT"; order_id = my_job_market(contract_list[ins],direction2,10*factor)
            Last_traded[ins]["Last_trade"]=round(price2,2); Last_traded[ins]["%s_order_id"%direction2]=order_id
            print("%s %s %s order placed @"%(Samai(time.localtime()),ins,direction2),LTP("CDS:%s"%ins))
            
            price = Last_traded[ins]["Last_trade"] - np.sign(diff)*Last_traded[ins]["Profit_booking_step"]; price = round(price,2)
            direction2 = "SHORT" if diff<0.0 else "LONG"; order_id = my_job(contract_list[ins],direction2,10,price); Last_traded[ins]["%s_order_id"%direction2]=order_id
            print("%s %s %s order placed @"%(Samai(time.localtime()),ins,direction2),price)
        #print("EUR add_order_id",Last_traded["EUR"]["add_order_id"]) 
        

def Samai(result):
    return "%s:%s:%s"%(result.tm_hour,result.tm_min,result.tm_sec)

print("Trading started at-->",Samai(time.localtime()))

#+++++++++Placing stoplose in all CURRENCY
for i in range(len(kite.positions()['net'])):
    #print(kite.positions()['net']) # there are two list a)"net": all the orders in postions b)"day": of you buy a stock today that listed here. it is also listed in "net"
    position = kite.positions()['net'][i]
    #print(position)
    if (position["tradingsymbol"][3:6]=="INR" and position["tradingsymbol"][-3:]=="FUT"):
        ins = position["tradingsymbol"][:3]
        print("Putting Stoplose on : ",position["tradingsymbol"], position["quantity"]) 
        order_id = my_job_SL_Tigger(position["tradingsymbol"],"LONG",abs(position["quantity"]),SL_data[ins]["SL"],SL_data[ins]["Trigger"])
        print("%s Putting Stoplose on : "%(Samai(time.localtime())),position["tradingsymbol"],"for", position["quantity"],"@",SL_data[ins]["SL"], "with Trigger@",SL_data[ins]["Trigger"]) 
    
    '''
        print("Putting Stoplose on : ",position["tradingsymbol"], position["quantity"]) 
        order_id = my_job_SL_Tigger(position["tradingsymbol"],"LONG",abs(position["quantity"]),SL_data["EUR"]["SL"],SL_data["EUR"]["Trigger"])
        print("%s Putting Stoplose on : "%(Samai(time.localtime())),position["tradingsymbol"],"for", position["quantity"],"@",SL_data["EUR"]["SL"], "with Trigger@",SL_data["EUR"]["Trigger"]) 
    
    if (position["tradingsymbol"]=="USDINR23JUNFUT"):   
        print("Putting Stoplose on : ",position["tradingsymbol"], position["quantity"]) 
        order_id = my_job_SL_Tigger(position["tradingsymbol"],"LONG",abs(position["quantity"]),SL_data["USD"]["SL"],SL_data["USD"]["Trigger"])
        print("%s Putting Stoplose on : "%(Samai(time.localtime())),position["tradingsymbol"],"for", position["quantity"],"@",SL_data["USD"]["SL"], "with Trigger@",SL_data["USD"]["Trigger"]) 
    '''
#++++++++++++Profit Booking  and Trading in instrument_list    
result = time.localtime()
if (result.tm_hour>=0 and result.tm_min>=0 ):
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
                
                

