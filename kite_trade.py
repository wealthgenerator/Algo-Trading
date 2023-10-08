import os
try:
    import requests
except ImportError:
    os.system('python -m pip install requests')
try:
    import dateutil
except ImportError:
    os.system('python -m pip install python-dateutil')

#import requests
import dateutil.parser


def get_enctoken1(userid, password, twofa):
    session = requests.Session()
    response = session.post('https://kite.zerodha.com/api/login', data={
        "user_id": userid,
        "password": password
    })
    response = session.post('https://kite.zerodha.com/api/twofa', data={
        "request_id": response.json()['data']['request_id'],
        "twofa_value": twofa,
        "user_id": response.json()['data']['user_id']
    })
    enctoken = response.cookies.get('enctoken')
    if enctoken:
        return enctoken
    else:
        raise Exception("Enter valid details !!!!")
def get_enctoken():
    with open("log_in_details.txt") as f1:
        f1_file = f1.readlines(); f1.close()
    
    user_id =  f1_file[0][:6]      # Login Id
    password = f1_file[1]      # Login password
    print([user_id,password])
    first = input("Is it your first session?[yes/no]")
    if first=="yes":
    	#####+++++++++++++LOGIN Method1:++++++++++++++++
    	twofa = input("Type you 6 degit google authetication:")         # Login Pin or TOTP
    	enctoken = get_enctoken1(user_id, password, twofa)
    	f = open("enctoken.txt", "w")
    	f.write(enctoken)
    	f.close()
    else:
    	#####+++++++++++++LOGIN Method2:++++++++++++++++
    	#login into the browser, righ_click at blank space->inspect->network->orders->headers-> copy the enctoken="" it is one of the option of cookie.
    	#enctoken = "7gKcXd+ZihFJUruQ/NEMqhL9WzTIq6zIh8AlNkzdqv53j5F14G7BjawHiFuHKFyJM19WVKxvjDmmytOD/m2jYVvJRp0r3ojfxBTq1f+tuORVgSnfSIM3Hw=="
    	with open("enctoken.txt") as f:
    	    enctoken = f.read()
    	#print(enctoken)
    return enctoken
        
class KiteApp:
    # Products
    PRODUCT_MIS = "MIS"
    PRODUCT_CNC = "CNC"
    PRODUCT_NRML = "NRML"
    PRODUCT_CO = "CO"

    # Order types
    ORDER_TYPE_MARKET = "MARKET"
    ORDER_TYPE_LIMIT = "LIMIT"
    ORDER_TYPE_SLM = "SL-M"
    ORDER_TYPE_SL = "SL"

    # Varities
    VARIETY_REGULAR = "regular"
    VARIETY_CO = "co"
    VARIETY_AMO = "amo"

    # Transaction type
    TRANSACTION_TYPE_BUY = "BUY"
    TRANSACTION_TYPE_SELL = "SELL"

    # Validity
    VALIDITY_DAY = "DAY"
    VALIDITY_IOC = "IOC"

    # Exchanges
    EXCHANGE_NSE = "NSE"
    EXCHANGE_BSE = "BSE"
    EXCHANGE_NFO = "NFO"
    EXCHANGE_CDS = "CDS"
    EXCHANGE_BFO = "BFO"
    EXCHANGE_MCX = "MCX"

    def __init__(self, enctoken):
        self.headers = {"Authorization": f"enctoken {enctoken}"}
        self.session = requests.session()
        self.root_url = "https://api.kite.trade"
        # self.root_url = "https://kite.zerodha.com/oms"
        self.session.get(self.root_url, headers=self.headers)

    def instruments(self, exchange=None):
        data = self.session.get(f"{self.root_url}/instruments",headers=self.headers).text.split("\n")
        Exchange = []
        for i in data[1:-1]:
            row = i.split(",")
            if exchange is None or exchange == row[11]:
                Exchange.append({'instrument_token': int(row[0]), 'exchange_token': row[1], 'tradingsymbol': row[2],
                                 'name': row[3][1:-1], 'last_price': float(row[4]),
                                 'expiry': dateutil.parser.parse(row[5]).date() if row[5] != "" else None,
                                 'strike': float(row[6]), 'tick_size': float(row[7]), 'lot_size': int(row[8]),
                                 'instrument_type': row[9], 'segment': row[10],
                                 'exchange': row[11]})
        return Exchange

    def quote(self, instruments):
        data = self.session.get(f"{self.root_url}/quote", params={"i": instruments}, headers=self.headers).json()["data"]
        return data

    def ltp(self, instruments):
        data = self.session.get(f"{self.root_url}/quote/ltp", params={"i": instruments}, headers=self.headers).json()["data"]
        return data

    def historical_data(self, instrument_token, from_date, to_date, interval, continuous=False, oi=False):
        params = {"from": from_date,
                  "to": to_date,
                  "interval": interval,
                  "continuous": 1 if continuous else 0,
                  "oi": 1 if oi else 0}
        lst = self.session.get(
            f"{self.root_url}/instruments/historical/{instrument_token}/{interval}", params=params,
            headers=self.headers).json()["data"]["candles"]
        records = []
        for i in lst:
            record = {"date": dateutil.parser.parse(i[0]), "open": i[1], "high": i[2], "low": i[3],
                      "close": i[4], "volume": i[5],}
            if len(i) == 7:
                record["oi"] = i[6]
            records.append(record)
        return records

    def margins(self):
        margins = self.session.get(f"{self.root_url}/user/margins", headers=self.headers).json()["data"]
        return margins

    def orders(self):
        orders = self.session.get(f"{self.root_url}/orders", headers=self.headers).json()["data"]
        return orders

    def positions(self):
        positions = self.session.get(f"{self.root_url}/portfolio/positions", headers=self.headers).json()["data"]
        return positions

    def place_order(self, variety, exchange, tradingsymbol, transaction_type, quantity, product, order_type, price=None,
                    validity=None, disclosed_quantity=None, trigger_price=None, squareoff=None, stoploss=None,
                    trailing_stoploss=None, tag=None):
        params = locals()
        #print(params)
        #print(variety,f"{self.root_url}/orders/{variety}")
        del params["self"]
        for k in list(params.keys()):
            if params[k] is None:
                del params[k]
        #print(params)
        #order_id = self.session.post(f"{self.root_url}/orders/{variety}", data=params, headers=self.headers).json()["data"]["order_id"]
        try:
        	order = self.session.post(f"{self.root_url}/orders/{variety}", data=params, headers=self.headers).json()["data"]
        	#print("order:::",order)
        except Exception as e:
        	print("Error:",e)
        return order["order_id"]

    def place_order2(self, exchange, tradingsymbol, transaction_type, quantity, product, order_type, price=None,
                    validity=None, disclosed_quantity=None, trigger_price=None, squareoff=None, stoploss=None,
                    trailing_stoploss=None, tag=None):
        params = locals()
        #print(params)
        #print(variety,f"{self.root_url}/orders/{variety}")
        del params["self"]
        for k in list(params.keys()):
            if params[k] is None:
                del params[k]
        print(params)
        #order_id = self.session.post(f"{self.root_url}/orders/{variety}", data=params, headers=self.headers).json()["data"]["order_id"]
        try:
        	order = self.session.post(f"{self.root_url}/orders", data=params, headers=self.headers).json()["data"]
        	print("order:::",order)
        except Exception as e:
        	print("Error:",e)
        
        
        return order
    '''
	#def place_order3(symbol): # produced by chatgpt
    def place_order3(symbol):
        try:
	    payload = {
	        "tradingsymbol": "BANKNIFTY21JUN35000CE",  # Replace with the desired option tradingsymbol
	        "exchange": "NFO",
	        "transaction_type": order_type,
	        "order_type": "LIMIT",  # Replace with the desired order type (e.g., LIMIT, MARKET)
	        "quantity": quantity,
	        "price": 100,  # Replace with the desired limit price if using a limit order
	        "product": "NRML"  # Replace with the desired product type (e.g., NRML, MIS)
	         }
		    
	    response = requests.post(
		        f"{base_url}/v1/orders",
		        headers=headers,
		        params=payload
		        )
		    
	    if response.status_code == 200:
	        print("Order placed successfully!")
	    else:
	        print("Order placement failed. Response:", response.json())

            except Exception as e:
	        print("An error occurred:", str(e))
    '''		

    def modify_order(self, variety, order_id, parent_order_id=None, quantity=None, price=None, order_type=None,
                     trigger_price=None, validity=None, disclosed_quantity=None):
        params = locals()
        del params["self"]
        for k in list(params.keys()):
            if params[k] is None:
                del params[k]

        order_id = self.session.put(f"{self.root_url}/orders/{variety}/{order_id}",data=params, headers=self.headers).json()["data"]["order_id"]
        #order = self.session.put(f"{self.root_url}/orders/{variety}/{order_id}",data=params, headers=self.headers).json()["data"]
       
        return order_id

    def cancel_order(self, variety, order_id, parent_order_id=None):
        order_id = self.session.delete(f"{self.root_url}/orders/{variety}/{order_id}",
                                       data={"parent_order_id": parent_order_id} if parent_order_id else {},
                                       headers=self.headers).json()["data"]["order_id"]
        return order_id
    
    def get_order_status(self, order_id):
        print(order_id)
        print( f"{self.root_url}/orders/{order_id}")
        try:
            response = self.session.get(
            f"{self.root_url}/orders/{order_id}",
            headers=self.headers)

            if response.status_code == 200:
                order_info = response.json()
                print("Order ID:", order_info["order_id"])
                print("Status:", order_info["status"])
                print("Status Message:", order_info["status_message"])
            else:
                print("Failed to retrieve order status. Response:", response.json())

        except Exception as e:
            print("An error occurred in get_order_status:", str(e))
