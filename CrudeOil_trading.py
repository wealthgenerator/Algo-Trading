'''
ABOUT: 

Add stopelose
Add a criteria on the interday change after first 20 min calender. also avoid creading position in intraday when previous candel is very large put the criteria on it. 

'''

from kite_trade import *
from kite_trade2 import *
import time
import numpy as np
from datetime import datetime, timedelta
from pytz import timezone 
import pandas as pd
import matplotlib.pyplot as plt
import os.path as path

dic = {
    "current_date" : [],
    "current_close" : [],
    "premium" : [],
    "SMA20"   : [],
    "SMA10"   : [],
    "status"  : [],
    "lot_size": [],
    "algo"    : []   
    }

def save_into_the_file(df,name,current_date,current_close,SMA10,SMA20,status,lot_size,algo,premium):
    #df = pd.read_csv(name)# csv file
    dic["current_date"] = current_date.values[-1]
    dic["current_close"] =  current_close.values[-1]
    dic["premium"] =  premium.values[-1]#; print(premium.values[-1])
    dic["SMA10"] = SMA10.values[-1]; dic["SMA20"] = SMA20.values[-1]; dic["status"] = status; dic["lot_size"] = lot_size; dic["algo"] = algo
    df.loc[len(df)] = dic
    df.to_csv(name,index=False)
    
month_list = ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC']



kite_api="yes"
stock="CRUDEOILM";  Month = "NOV"; inter = 10; lot_size = 2; exc = "MCX"; year=23;  interval = "%sminute"%inter;days = 10
print("this is for inter:",inter)
if kite_api=="no":
    enctoken = get_enctoken()
    kite = KiteApp(enctoken=enctoken)
else:
    kite = get_kite_api()
    
print("Session started---------------------")

file_name = "%s_%s.csv"%(stock,Month)
if path.exists(file_name)==False:
    dfm = pd.DataFrame(dic)
    dfm.to_csv(file_name,index=False)
    l=0
else: 
    dfm = pd.read_csv(file_name)
    #print(dfm["status"].values)
    if len(dfm["status"].values) ==0: l = 0
    elif dfm["status"].values[-1] != "exit": l = 0
    else: 
        l=1; algo =  dfm["algo"].values[-1]
        open_premium = dfm["current_close"].values[-1]
    
    
index = month_list.index(Month); N_Month = month_list[index+1 if (index+1)<=11 else (index+1)-12]
today = (datetime.now(timezone("Asia/Kolkata")).strftime("%Y-%m-%d")).split('-')#; print("today",today)
now_month = month_list[int(today[1])-1] ; print("current month:",now_month)
# contracts are launched six month prior its expairy but it is actively traded for three month. for expample 20-october expiary contract launched on 20-april 
# -but in MCX it is actively traded from 20 th july

if now_month != Month: max_ = 50 + int(today[2])-20 # as contcat endaround 20 the month and next month expairy start from 20 th month. 
else:    max_ = 50+10+int(today[2])

   
data_list = [Month, N_Month]
year_list = [year, year if (index+1)<=11 else year+1]

instrument = "%s:%s%s%sFUT"%(exc,stock,year_list[0],data_list[0]); response = kite.ltp(instrument)[instrument]; instrument_token = response['instrument_token']
N_instrument = "%s:%s%s%sFUT"%(exc,stock,year_list[1],data_list[1]); N_response = kite.ltp(N_instrument)[N_instrument]; N_instrument_token = N_response['instrument_token']
instrument1 = "%s%s%sFUT"%(stock,year_list[0],data_list[0])

# job will wait if you submitted before 9:18AM.
on_hr = 9; on_mn = 18
def intial_wait():  
    now_time = datetime.now(timezone("Asia/Kolkata")).strftime("%H:%M").split(":"); hr = float(now_time[0]); mn = float(now_time[1])
    if (hr*60 + mn < on_hr*60 + on_mn): 
        wait =(on_hr-hr)*3600 + (on_mn-mn)*60 if mn<on_mn else (on_hr-hr-1)*3600 + (60+on_mn-mn)*60
    else: wait=0.0
    return hr,mn,wait

while True:
    hr,mn,wait =  intial_wait()
    if (hr*60 + mn < on_hr*60 + on_mn): print("Now time is %i:%i and job will wait for %s hours"%(hr,mn,wait/3600) );time.sleep(wait)
    to_date = datetime.now(timezone("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S"); minute= int(to_date.split(":")[1]); second= int(to_date.split(":")[2]);
    wait = 60*((int(minute/inter)+1)*inter - minute-1) + 60-second; time.sleep(wait);to_date = datetime.now(timezone("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S")
    start = time.time()
    from_date = ((datetime.now(timezone("Asia/Kolkata"))-timedelta(days=days)).strftime("%Y-%m-%d"))+" 9:00:00"#;  print(from_date)
    #N_from_date = ((datetime.now(timezone("Asia/Kolkata"))-timedelta(days=days[1])).strftime("%Y-%m-%d"))+" 9:00:00"#;  print(from_date)
    #print(from_date)
    data = (kite.historical_data(instrument_token, from_date, to_date, interval, False, True))[-100:]; df = pd.DataFrame(data)
    N_data =(kite.historical_data(N_instrument_token, from_date, to_date, interval, False, True))[-100:]; N_df = pd.DataFrame(N_data)

    #df = pd.DataFrame(data);  df.to_csv("%s/%s_%s.csv"%(dir_,file_name,interval),index=False)
    #data_current = pd.read_csv("%s"%(file_name), index_col=False)
    #print(df.head(3)); print(N_df.head(3)); print(df.tail(3)); print(N_df.tail(3))
    
    date = N_df["date"]
    premium = df["close"] - N_df["close"]
    #print( df["close"]);print(N_df["close"]); print("premium",premium)
    current_close = df["close"]; N_close = N_df["close"]
    
    N=len(premium)
    SMA50 = current_close.rolling(50).mean()
    SMA20 = premium.rolling(20).mean()
    SMA10 = premium.rolling(10).mean()

    
    #save_into_the_file(dfm,file_name,date,current_close,SMA10,SMA20,"BUY",lot_size,algo,premium)
    open_premium = 0.0; close_premium = 0.0
    total_profit = 0.0; total_number_trade = 0; above = 1
    print("At %s with current_close[i]=%s and  premium[i]=%s, SMA20=%s, SMA10=%s"%(date.values[-1], current_close.values[-1], premium.values[-1],SMA20.values[-1], SMA10.values[-1]))
    algo = 10
    if algo != 50:
        # SELL the the contract when premium is above 140 and SMA10 is lower than SMA20 of 15 minute cancle close
        # And buy the contract when MA20[i]<SMA10[i] and premium[i]<90
        if SMA20.values[-1]>SMA10.values[-1] and premium.values[-1]>140 :
            if l==0: # l=0 means there is no exting postion already
                open_premium = current_close.values[-1] 
                print("SOLD contract on %s with current_close[i]=%s and  premium[i]=%s"%( date.values[-1], current_close.values[-1], premium.values[-1]))
                order_id = my_job_Market(instrument1,exc,"SHOT",lot_size,kite) 
                l=1; algo=2
                save_into_the_file(dfm,file_name,date,current_close,SMA10,SMA20,"SHOT",lot_size,algo,premium)
                #total_number_trade =  total_number_trade + 1
               
        if (SMA20.values[-1]<SMA10.values[-1] and premium.values[-1]<90) and (algo == 2):
            if l==1:
                close_premium = current_close.values[-1] 
                order_id = my_job_Market(instrument1,exc,"BUY",lot_size,kite)    
                save_into_the_file(dfm,file_name,date,current_close,SMA10,SMA20,"EXIT",lot_size,algo,premium)
                profit = open_premium - close_premium
                total_profit = total_profit + profit
                print("closing on date: %s with current_close[i]=%s, profit=%s, total profit=%s for the month %s"%(date[-1], current_close[-1],profit, total_profit, Month))
            l=0

    #if algo !=3:  
        # BUY the the contract when premium is below 50 and SMA10> SMA20 of 15 minute cancle close
        # And Sell the contract when MA20[i]>SMA10[i] and premium[i]>90
        if SMA20.values[-1]<SMA10.values[-1] and premium.values[-1]<50 :
            if l==0: # l=0 means there is no exting postion already
                open_premium = current_close.values[-1] 
                order_id = my_job_Market(instrument1,exc,"BUY",lot_size,kite) 
                l=1; algo=3
                save_into_the_file(dfm,file_name,date,current_close,SMA10,SMA20,"BUY",lot_size,algo,premium)
                print("Bought contract on %s with current_close[i]=%s and  premium[i]=%s"%( date.values[-1], current_close.values[-1], premium.values[-1]))
                #total_number_trade =  total_number_trade + 1
                
        if (SMA20.values[-1]>SMA10.values[-1] and premium.values[-1]>90) and algo==3:
            if l==1:
                close_premium = current_close.values[-1] 
                order_id = my_job_Market(instrument1,exc,"SHOT",lot_size,kite)     
                save_into_the_file(dfm,file_name,date,current_close,SMA10,SMA20,"EXIT",lot_size,algo,premium)
                profit = -open_premium + close_premium
                total_profit = total_profit + profit
                print("closing on date: %s with current_close[i]=%s, profit=%s, total profit=%s for the month %s"%(date.values[-1], current_close.values[-1],profit, total_profit, Month))
            l=0
        
    end = time.time(); print("excution time:",end-start)
    #print(date.values[-1],to_date,current_close.values[-1], SMA50.values[-1])
    
