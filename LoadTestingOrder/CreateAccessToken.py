import sys
sys.path.append("./")

import requests
import json
import pandas as pd

#from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
#from fyers_logger import FyersLogger

#To date time
from datetime import datetime
import pytz

tz = pytz.timezone('Asia/Kolkata')

#For UAT
login_url = "https://api.fyers.in/vagator/dev/login"
verify_url = "https://api.fyers.in/vagator/dev/verify_pin"
refresh_token_url = "https://api.fyers.in/vagator/dev/refresh_token"

#For Production
#login_url = "https://api.fyers.in/vagator/v1/login"
#verify_url = "https://api.fyers.in/vagator/v1/verify_pin"
#refresh_token_url = "https://api.fyers.in/vagator/v1/refresh_token"

client_pass_file = "LoadTestingOrder/info.csv"
client_pass_acc_file = "LoadTestingOrder/output.csv"

SUCCESS = 1
ERROR = -1
CLIENT_ID = "client_id"
PASSWORD = "password"
ACCESS_TOKEN = "access_token"
REFRESH_TOKEN = "refresh_token"
FY_ID = "fy_id"
APP_ID = "app_id"
REQUEST_KEY = "request_key"
IDENTITY_TYPE = "identity_type"
REQUEST_IDENTIFIER = "identifier"
BIOMETRIC_ENABLE = "biometric_enable"
DATA = "data"
PIN = "pin"

#To write logs
log_path = str(Path.home()) + '/logs'
date = datetime.now(). strftime("%d-%b-%Y")
filename = f"{log_path}/CreateAccessToken_{date}.log"
log_file = open(filename, "a")

#Function to read input.csv file to fetch client details and make it python tuples
def get_client_details_df():
    try:
        df = pd.read_csv(client_pass_file)
        data = tuple(df.itertuples(index=False, name=None))
        return [SUCCESS, data, ""]
    except Exception as e:
        print(e)
        return [ERROR, -99, e]

#Function to call login and authentication of vagator
def login(clients_data):
    try:
        df_headers = [CLIENT_ID, PASSWORD, ACCESS_TOKEN, REFRESH_TOKEN]
        df = pd.DataFrame(columns=df_headers)
        for data in clients_data:
            client_id = data[0]
            password = data[1]
            client_pin = data[2]

            # Get request key after login
            access_token_payload = {
                FY_ID: client_id,
                PASSWORD: password,
                APP_ID: "2"
            }

            headers_text = {
                'content-type': 'text/plain'
            }
            
            response = requests.request(
                "POST", login_url, headers=headers_text,
                data=json.dumps(access_token_payload)
            )
            
            dateNow=datetime.now(tz).strftime("%d-%b-%Y %H:%M:%S %f")
            text = (f"{dateNow} - Login response - {response.text}\n")
            log_file.write(text)

            #import pdb; pdb.set_trace()
            response_data = json.loads(response.text)
            request_key = response_data[REQUEST_KEY]

            # Get access token and refresh token after entering pin value
            access_token_payload = {
                REQUEST_KEY: request_key,
                IDENTITY_TYPE: PIN,
                REQUEST_IDENTIFIER: str(client_pin),
                BIOMETRIC_ENABLE: 'N'            
            }
            headers_json = {
                'Content-Type': 'application/json'
            }
            access_response = requests.request(
                "POST", verify_url, headers=headers_json, 
                data=json.dumps(access_token_payload)
            )        
            access_token_data = json.loads(access_response.text)
            access_token = access_token_data[DATA][ACCESS_TOKEN]
            refresh_token = access_token_data[DATA][REFRESH_TOKEN]
            
            row = [client_id, password, access_token, refresh_token]
            temp_df = pd.DataFrame([row], columns=df_headers)
            df = pd.concat([df,temp_df], ignore_index=True)

            # # Get access token which has validity for 30 days
            # refresh_token_payload = {
            #     REFRESH_TOKEN: refresh_token,
            #     IDENTITY_TYPE: PIN,
            #     REQUEST_IDENTIFIER: str(client_pin)
            # }
            # refresh_response = requests.request(
            #     "POST", refresh_token_url, headers=headers_json, 
            #     data=json.dumps(refresh_token_payload)
            # )
            # print(refresh_response.text)

        #To python dataframe to CSV with indexing false
        df.to_csv(client_pass_acc_file, encoding='utf-8', index=False)
        
    except Exception as e:
        print(e)

def main():
    #import pdb; pdb.set_trace()
    clients_data = get_client_details_df()
    if clients_data[0] == ERROR:
        sys.exit()
    
    login(clients_data=clients_data[1])

if __name__ == '__main__':
    main()