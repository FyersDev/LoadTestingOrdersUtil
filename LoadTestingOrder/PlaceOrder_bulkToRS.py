from bdb import set_trace
import sys
sys.path.append("./")

#import requests
#import json
import pandas as pd

import request as req
import fyers_funct as fy_fun

from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from fyers_logger import FyersLogger

#To get times in micro secs
from datetime import datetime    
import pytz

from fy_trading_internal_functions import INTERNAL_createAndSendOmsRequest

#To write logs
log_path = str(Path.home()) + '/logs'
date = datetime.now(). strftime("%d-%b-%Y")
filename = f"{log_path}/BulkOrderTestRS_{date}.log"
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
            OMSid=data[0]
            body = {
                'headers': {
                    'cookie': '',
                    'authorization': access_token,
                    'user_ip': ''
                }
            }

            urlForRequest = 'http://internal-Fyers-Internal-Loadbalancer-2106555724.ap-south-1.elb.amazonaws.com/RupeeSeedWS/orderEntry/index'
            #urlForRequest = 'http://tradeonline-uat.fyers.in:8080/RupeeSeedWS/orderEntry/index'

            aesKey = '+YFIvHxjE0HGy4uC2UNCGPQD3bVgCzS/mTiUwGtzUaE='
            OMStoken = 'f35ce0ffd67c35a79c7b'
           
            body["body"] = {
                'token_id': OMStoken,
                'client_id': OMSid,
                'source': 'W',
                'client_type': 'C',
                'exch_client_id': OMSid,
                'user_id': '3678924',
                'user_type': 'C',
                'securityid': '10753',
                'inst_type': 'EQ',
                'exchange': 'NSE',
                'buysell': 'B',
                'quantitytype': 'LMT',
                'quantity': '1',
                'price': '1',
                'productlist': 'I',
                'OrderType': 'DAY',
                'offline_flag': 'false',
                'row_1': '',
                'row_2': '',
                'triggerprice': '0',
                'disclosequantity': '0',
                'marketProflag': 'N',
                'marketProVal': '0',
                'ParticipantType': 'B',
                'settlor': '',
                'Gtcflag': 'N',
                'EncashFlag': 'N',
                'pan_id': 'AQCPG3783E'
            }

            count=int(sys.argv[1])
            for i in range(count):
                dateNow=datetime.now(tz).strftime("%d-%b-%Y %H:%M:%S %f")
                text = (f"{dateNow} - Before Order Post {OMSid}, count : {order_count}\n")
                log_file.write(text)
                #import pdb; pdb.set_trace()
                sendReqFuncRet = INTERNAL_createAndSendOmsRequest(OMSid, OMStoken, aesKey,body, urlForRequest, callingFuncName=PlaceOrderRecursively,userIp=1234)
                        
                # if sendReqFuncRet[0] == ERROR_C_1:
                #     return sendReqFuncRet
                # omsResponse = sendReqFuncRet[1]

                # # Decrypt the response received from the OMS
                # readOmsResponseFuncRet = INTERNAL_decryptOmsResponse(omsResponse, aesKey,callingFuncName=callingFuncName)
                # if readOmsResponseFuncRet[0] == ERROR_C_1:
                #     return readOmsResponseFuncRet
                # userInfoList = readOmsResponseFuncRet[1]

                # # Check for user invalidation. If yes, re-send the request
                # readOmsResponseFuncRet2 = INTERNAL_readOmsDecryptedResponse(userInfoList,tokenHash, paramsPayload,
                # urlForRequest,fyId=OMSid, localMemory=localMemory,callingFuncName=callingFuncName,orderPlacement=True, userIp=userIp)
                # return readOmsResponseFuncRet2

                dateNow1=datetime.now(tz).strftime("%d-%b-%Y %H:%M:%S %f")
                text1 = (f"{dateNow1} - After Order Post : {sendReqFuncRet}.\n") 
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