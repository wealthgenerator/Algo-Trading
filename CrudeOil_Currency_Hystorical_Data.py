from kite_trade import *
import time  
import numpy as np
from datetime import datetime, timedelta
from pytz import timezone 
import pandas as pd
import matplotlib.pyplot as plt

month_list = ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC']

enctoken = get_enctoken()
kite = KiteApp(enctoken=enctoken)
print("Session started---------------------")

stock="CRUDEOILM";  Month = "NOV"; exc = "MCX"; dir_ = "CRUDE_DATA/%s"%Month; year=23; interval = "10minute"
stock="JPYINR";  Month = "OCT";  exc = "CDS"; dir_ = "CURRENCY_DATA/%s"%Month; year=23; interval = "5minute"
index = month_list.index(Month); N_Month = month_list[index+1 if (index+1)<=11 else (index+1)-12];  N_N_Month = month_list[index+2 if (index+2)<=11 else (index+2)-12 ]
today = (datetime.now(timezone("Asia/Kolkata")).strftime("%Y-%m-%d")).split('-'); print(today)
now_month = month_list[int(today[1])-1] ; print(now_month)
# contracts are launched six month prior its expairy but it is actively traded for three month. for expample 20-october expiary contract launched on 20-april 
# -but in MCX it is actively traded from 20 th july

if now_month != Month: max_ = 50 + int(today[2])-20 # as contcat endaround 20 the month and next month expairy start from 20 th month. 
else:    max_ = 50+10+int(today[2])

   
data_list = [Month, N_Month, N_N_Month]; days = [max_,max_-30, max_-60 if (max_-60)>0 else 0] #as minimum value of max_=50, no of days for the next to next month trading day cant be less than zero
year_list = [year, year if (index+1)<=11 else year+1, year if (index+2)<=11 else year+1 ]

print(data_list)
for i, Month in enumerate(data_list):
    print(Month,days[i])
    if i==0: file_name = "%s%s%s-%sFUT"%(stock,year_list[i],Month,Month)
    else: file_name = "%s%s%s-%sFUT"%(stock,year_list[i],Month,data_list[0])
    if days[i]>0: #if no of days is greater than 0 for given month then only ask for hostorical data 
        instrument = "%s:%s%s%sFUT"%(exc,stock,year_list[i],Month)
        response = kite.ltp(instrument)[instrument] #this work even after market close. 
        instrument_token = response['instrument_token']
        to_date = (datetime.now(timezone("Asia/Kolkata")).strftime("%Y-%m-%d"))+" 9:00:01"#;  print(to_date)
        from_date = ((datetime.now(timezone("Asia/Kolkata"))-timedelta(days=days[i])).strftime("%Y-%m-%d"))+" 23:00:00"#;  print(from_date)
        data=(kite.historical_data(instrument_token, from_date, to_date, interval, False, True))
        df = pd.DataFrame(data);  df.to_csv("%s/%s_%s.csv"%(dir_,file_name,interval),index=False)


file_name = "%s%s%s-%sFUT_%s"%(stock,year_list[0],data_list[0],data_list[0],interval); data_current = pd.read_csv("%s/%s.csv"%(dir_,file_name), index_col=False)
file_name = "%s%s%s-%sFUT_%s"%(stock,year_list[1],data_list[1],data_list[0],interval); data_N = pd.read_csv("%s/%s.csv"%(dir_,file_name))
#file_name = "%s%s%s-%sFUT_%s"%(stock,year_list[2],data_list[2],data_list[0],interval); data_N_N = pd.read_csv("%s/%s.csv"%(dir_,file_name))

#plt.plot(data_OCT["date"],data_OCT["close"]);plt.plot(data_NOV["date"],data_NOV["close"])

#data_OCT["close"].plot(); data_NOV["close"].plot();data_DEC["close"].plot()
#plt.savefig("CRUDE_DATA/CRUDEOILM.png")
N_len = len(data_N["date"]); print(N_len); print(len(data_current["close"][-N_len:]))#;print(len(data_current["close"]))
#print(len(data_current["close"][-N_len-1:-1]-data_N["close"]))

premium = {
    "current_date" : [],
    "current_close" : [],
    "N_date" : [],
    "N_close" : [],
    "Premium" : []
    }
#print(data_current["close"].values[-N_len-1:])
#print(data_N["close"].values)
premium["current_date"] = data_current["date"].values[-N_len:]; premium["current_close"] = data_current["close"].values[-N_len:]
premium["N_date"] = data_N["date"]; premium["N_close"] = data_N["close"];
P = data_current["close"].values[-N_len:]-data_N["close"].values; premium["Premium"] = P
df3 = pd.DataFrame(premium)
df3.to_csv("%s/%s_%s%s_%s.csv"%(dir_,stock,data_list[0],year,interval))

plt.plot(data_N["date"],P)# .value givea numy array. otheriwse you will have index value storred. 
plt.savefig("%s/%s_premium_%s_%s.png"%(dir_,stock,data_list[0],interval))

#print(data[-1])

