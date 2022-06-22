from bdb import set_trace
import sys
sys.path.append("./")

import requests
import json
import pandas as pd
import threading

import request as req
import fyers_funct as fy_fun

from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from fyers_logger import FyersLogger

#To get times in micro secs
from datetime import datetime    
import pytz

#To write logs
log_path = str(Path.home()) + '/logs'
date = datetime. now(). strftime("%d-%b-%Y")
filename = f"{log_path}/BulkOrderTest_{date}.log"
log_file = open(filename, "a")

#logger = FyersLogger(
#    "LoadTestOrder", "DEBUG", logger_handler=TimedRotatingFileHandler(log_path + '/' + filename, when='midnight')
#)

client_pass_acc_file = "LoadTestingOrder/output.csv"
security_file = "LoadTestingOrder/BulkScrips.csv"

SUCCESS = 1
ERROR = -1
order_count = 1

tz = pytz.timezone('Asia/Kolkata')

def get_client_details_df():
    try:
        df = pd.read_csv(client_pass_acc_file)
        data = tuple(df.itertuples(index=False, name=None))

        return [SUCCESS, data, ""]
    except Exception as e:
        print(e)
        return [ERROR, -99, e]

def PlaceOrderRecursively(client_data, security_data, thread_count, lock):
    try:
        
        for data in client_data:
            access_token = data[2]
            cli_id = data[0]
            body = {
                'headers': {
                    'cookie': '',
                    'authorization': access_token,
                    'user_ip': ''
                }
            }

            symbol = security_data[0] + ":" + security_data[1] + "-" + security_data[2]

            body["body"] = {
                "noConfirm": True,
                "productType": "INTRADAY",
                "side": 1,
                "symbol": symbol, #"NSE:UNIONBANK-EQ",
                "qty": 1,
                "disclosedQty": 0,
                "type": 2,
                "limitPrice": 0,
                "validity": "DAY",
                "filledQty": 0,
                "stopPrice": 0,
                "offlineOrder": False
            }

            #Placing order to Voyager

            reqObj = req.Request(body)
            resp=200
            global order_count

            count=int(sys.argv[1])
            for i in range(count):
                dateNow=datetime.now(tz).strftime("%d-%b-%Y %H:%M:%S %f")
                #logger.debug(dateNow, extra={"text" : "Before Order Post","count":order_count})
                text = (f"{dateNow} - Before Order Post {cli_id}, symbol : {symbol}, thread_count : {thread_count}, count : {order_count}\n")
                
                lock.acquire()
                log_file.write(text)
                lock.release()
                
                result = fy_fun.fyOrdersPOST(reqObj, resp)
                
                dateNow1=datetime.now(tz).strftime("%d-%b-%Y %H:%M:%S %f")
                text1 = (f"{dateNow1} - After Order Post {cli_id}, symbol : {symbol}, thread_count : {thread_count}, count : {order_count}\n")#,resp : {result}\n") 
               
                lock.acquire()
                log_file.write(text1)
                order_count = order_count+1
                lock.release()

                i=i+1

    except Exception as e:
        print(e)
        return [ERROR, -99, e]


def main():
    
    clients_data = get_client_details_df()
    
    if clients_data[0] == ERROR:
        sys.exit()
    else:
        
        security_df = pd.read_csv(security_file)
        security_data = tuple(security_df.itertuples(index=False, name=None))
        
        lock = threading.Lock()

        thread_count = 1

        for security_data1 in security_data:
            t1 = threading.Thread(target=PlaceOrderRecursively, args=(clients_data[1], security_data1, thread_count, lock))
            t1.start()
            t1.join()
            thread_count =  thread_count + 1

if __name__ == '__main__':
    main()