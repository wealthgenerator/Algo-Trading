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
'''
from kite_trade import *
import time  
import numpy as np

enctoken = get_enctoken()
kite = KiteApp(enctoken=enctoken)
'''



