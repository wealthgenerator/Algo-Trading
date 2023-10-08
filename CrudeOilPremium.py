from kite_trade import *
import time  
import numpy as np
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt

enctoken = get_enctoken()
kite = KiteApp(enctoken=enctoken)
print("Session started---------------------")

stock="CRUDEOILM"; Month = "OCT" ; file_name = "%s23%sFUT"%(stock,Month)
instrument = "MCX:%s23%sFUT"%(stock,Month)
response = kite.ltp(instrument)[instrument] #this work even after market close. 
instrument_token = response['instrument_token']
to_date = (datetime.today().strftime("%Y-%m-%d"))+" 9:30:01"#;  print(to_date)
from_date = ((datetime.today()-timedelta(days=40)).strftime("%Y-%m-%d"))+" 15:29:00"#;  print(from_date)
data=(kite.historical_data(instrument_token, from_date, to_date, "minute", False, True))
df = pd.DataFrame(data);  df.to_csv("CRUDE_DATA/%s.csv"%file_name,index=False)


data_OCT = pd.read_csv("CRUDE_DATA/CRUDEOILM23%sFUT.csv"%"OCT", index_col=False)
data_NOV = pd.read_csv("CRUDE_DATA/CRUDEOILM23%sFUT.csv"%"NOV")
data_DEC = pd.read_csv("CRUDE_DATA/CRUDEOILM23%sFUT.csv"%"DEC")

#plt.plot(data_OCT["date"],data_OCT["close"]);plt.plot(data_NOV["date"],data_NOV["close"])

#data_OCT["close"].plot(); data_NOV["close"].plot();data_DEC["close"].plot()
#plt.savefig("CRUDE_DATA/CRUDEOILM.png")
NOV_len = len(data_NOV["date"]); print(NOV_len); print(len(data_OCT["close"][-NOV_len-1:-1]));print(len(data_NOV["close"]))
print(len(data_OCT["close"][-NOV_len-1:-1]-data_NOV["close"]))
print(data_OCT["close"][1:3])
plt.plot(data_NOV["date"],data_OCT["close"].values[-NOV_len-1:-1]-data_NOV["close"].values)# .value givea numy array. otheriwse you will have index value storred. 
plt.savefig("CRUDE_DATA/CRUDEOILM_premium.png")

#print(data[-1])

