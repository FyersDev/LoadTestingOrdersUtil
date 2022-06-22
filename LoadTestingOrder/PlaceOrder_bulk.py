from bdb import set_trace
import sys
sys.path.append("./")

import requests
import json
import pandas as pd

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

SUCCESS = 1
ERROR = -1

tz = pytz.timezone('Asia/Kolkata')

def get_client_details_df():
    try:
        df = pd.read_csv(client_pass_acc_file)
        data = tuple(df.itertuples(index=False, name=None))

        return [SUCCESS, data, ""]
    except Exception as e:
        print(e)
        return [ERROR, -99, e]

def PlaceOrderRecursively(client_data):
    try:

        order_count=1

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

            body["body"] = {
                "noConfirm": True,
                "productType": "INTRADAY",
                "side": 1,
                "symbol": "NSE:UNIONBANK-EQ",
                "qty": 1,
                "disclosedQty": 0,
                "type": 1,
                "limitPrice": 35,
                "validity": "DAY",
                "filledQty": 0,
                "stopPrice": 0,
                "offlineOrder": False
            }

            #Placing order to Voyager

            reqObj = req.Request(body)
            resp=200

            count = int(sys.argv[1])
            for i in range(count):
                dateNow=datetime.now(tz).strftime("%d-%b-%Y %H:%M:%S %f")
                #logger.debug(dateNow, extra={"text" : "Before Order Post","count":order_count})
                text = (f"{dateNow} - Before Order Post {cli_id}, count : {order_count}\n")
                log_file.write(text)
                 
                result = fy_fun.fyOrdersPOST(reqObj, resp)
                #result["output_time"]=str(datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S.%f"))
                #logger.debug("After Order Post", extra=result)
                dateNow1=datetime.now(tz).strftime("%d-%b-%Y %H:%M:%S %f")
                text1 = (f"{dateNow1} - After Order Post, resp : {result}\n") 
                log_file.write(text1)

                order_count=order_count+1

                i=i+1

    except Exception as e:
        print(e)
        return [ERROR, -99, e]


def main():
    
    clients_data = get_client_details_df()
    if clients_data[0] == ERROR:
        sys.exit()

    clients_data1 = PlaceOrderRecursively(clients_data[1])

if __name__ == '__main__':
    main()
