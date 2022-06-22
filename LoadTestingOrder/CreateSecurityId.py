import sys
sys.path.append("./")

#import requests
#import json
import pandas as pd

from fy_config.fy_connections import connectRedis
from fy_config.fy_common_internal_functions import INTERNAL_checkSymbolNameOrToken, INTERNAL_getSymExAndSegment

symbol_file = "LoadTestingOrder/BulkScrips.csv"
symbol_security_file = "LoadTestingOrder/BulkScripsToken.csv"

SUCCESS = 1
ERROR = -1
SECURITY_ID = "security_id"
EXCHANGE = "exchange"
SYMBOL = "symbol"
INSTRUMENT = "instrument"

#Function to read input.csv file to fetch client details and make it python tuples
def get_symbol_details():
    try:
        df = pd.read_csv(symbol_file)
        data = tuple(df.itertuples(index=False, name=None))
        return [SUCCESS, data, ""]
    except Exception as e:
        print(e)
        return [ERROR, -99, e]

#Function to call login and authentication of vagator
#Function to get tokens from redis local memory
def getToken(symbol_data):
    try:
        
        localMemory = connectRedis(callingFuncName='')

        df_headers = [SECURITY_ID, EXCHANGE, SYMBOL, INSTRUMENT]
        df = pd.DataFrame(columns=df_headers)
        
        for data in symbol_data:
            try:
                exchange_string = data[0]
                symbol_name = data[1]
                instrument_name = data[2]

                symbol = exchange_string + ":" + symbol_name + "-" + instrument_name
                #import pdb; pdb.set_trace()
                # Converting symbol name to token
                checkSymbolList = INTERNAL_checkSymbolNameOrToken(symbol,localMemory=localMemory,callingFuncName='')

                # Splitting the token to get the exchange, segment and scripCode
                symbolList = INTERNAL_getSymExAndSegment(checkSymbolList[1][0],callingFuncName='')
                
                row = [symbolList[1][2], exchange_string, symbol_name, instrument_name]
                temp_df = pd.DataFrame([row], columns=df_headers)
                df = pd.concat([df,temp_df], ignore_index=True)
            
            except Exception as e:
               print(e)
               continue
               
        #To python dataframe to CSV with indexing false
        df.to_csv(symbol_security_file, encoding='utf-8', index=False)

    except Exception as e:
        print(e)

def main():
    #import pdb; pdb.set_trace()
    symbol_data = get_symbol_details()
    if symbol_data[0] == ERROR:
        sys.exit()
    
    getToken(symbol_data=symbol_data[1])

if __name__ == '__main__':
    main()