
from cmath import exp
import jwt
import sys 
import json
import time
import redis
import traceback
import jwt.exceptions

from fy_config.fy_base_functions import get_logger, logEntryFunc2
from fy_config.fy_connections import CACHE_REDIS_TRADING

moduleName = "vagator_auth_check"
RELOGIN_REQUIRED = 1015
#Error code for Internal tech dashboard

WRONG_CHECKSUM                  = -215

#Error code for auth module

VERIFIED_OTP                    = 1001
INVALID_OTP                     = -1002
WRONG_OTP                       = -1003
VERIFIED_PIN                    = 1004
WRONG_PIN                       = -1005
INVALID_PIN                     = -1006
SOMETHING_WENT_WRONG            = -1007
VERIFIED_TOKEN                  = 1008
INVALID_TOKEN                   = -1009
INVALID_PASSWORD                = -1010
VALID_PASSWORD                  = -1011
EXPIRED_TOKEN                   = -1012
VALID_TOKEN                     = 1013
RELOGIN_REQUIRED                = 1015
WRONG_BIOMETRIC                 = -1016
VERIFIED_BIOMETRIC              = 1017
EXCEPT_SOMETHING_WENT_WRONG     = -1018
USER_EXIST                      = 1019
USER_DOES_NOT_EXIST             = -1019 #show error messaege
ACCOUNT_DELETED                 = -1020 #show error messaege
ACCOUNT_BLOCKED                 = -1021 #show error messaege
VERIFIED_YOB                    = 1022
WRONG_YOB                       = -1022
ACCOUNT_BLOCKED_FYERS           = -1023 #show error messaege
INVALID_USER                    = -1024 #show error messaege
REQUEST_SUCCESSFULL             = 1025
INCORRECT_DATE_FORMAT           = -1026
INVALID_REQUEST_KEY             = -1027
EXPIRED_REQUEST_KEY             = -1028
WRONG_REQUEST_KEY               = -1029
TIME_OUT                        = -1030 #show error messaege
RECAPTCHA_NOT_PROVIDED          = -1031
RECAPTCHA_NOT_VERIFIED          = -1032 #show error messaege
PIN_NOT_CREATED                 = -1033 #show error messaege
BIOMETRIC_NOT_ENABLED           = -1034 #show error messaege
EMPTY_LIST                      = -1035
EMPTY_DICT                      = -1036
WRONG_DATA_PROVIDED             = -1037
DUPLICATE_VALUE_TABLE           = -1038
OLD_TIMESTAMP_PROVIDED          = -1039
INVALID_USER_AGENT              = -1040
RUPEE_SEED_ERROR                = -1041
INVALID_EMAIL_ID                = -1042
OTP_SENT                        = 1043
OTP_NOT_SENT                    = -1043
INVALID_INPUT                   = -1044
LMS_ERROR                       = -1045
INVALID_TOKEN_ID                = -1046
INVALID_TOKEN_ID_APP            = -1047
WRONG_PAN                       = -1048
WRONG_PWD                       = -1049
VERIFIED_PWD                    = 1049
USED_PWD                        = -1050
OTP_LIMIT_EXCEEDED              = -1051
INVALID_PAN                     = -1052
TELIGENZ_DOWN                   = -1053
BIOMETRIC_ENABLED_C             =  1054
DATA_NOT_FOUND                  = -1055
PWD_CHANGE_FAILED               = -1056
FCM_DATA_NOT_PROVIDED           = -1057
PUSH_NOTI_DOWN                  = -1058
USER_NOT_VERIFIED_CODE          = -1059
USER_VERIFIED_CODE              = 1059

ERROR_C_INVALID_TOKEN_3             = -19
#JWT Subs
CREATE_PASSWORD                 = "create_pwd"      # create password
CREATE_PIN                      = "create_pin"      # create pin for first time user
CREATE_PIN_F                    = "create_pin_f"    # create pin after forgot password
FORGOT_PAWSSWORD                = "forgot_pwd"      # forgot password
FORGOT_UID                      = "forgot_uid"      # forgot user_id/fyers_id
GUEST_REGISTER                  = "guest_reg"       # guest registration
GUEST_LOGIN                     = "guest_login"     
TEMPORARY_PASSWORD              = "temp_pwd"        # temporary password
FORGOT_PIN                      = "forgot_pin"      # forgot pin
CHANGE_PWD                      = "change_pwd"      # change password
CHANGE_PIN                      = "change_pin"      # change pin
SET_BIO                         = "set_bio"

#Keys
DICT_DATA                       = "data"
USER_STATUS                     = "user_status"
PWD_CREATED                     = "pwd_created"
PWD_RESET_REQUIRED              = "pwd_reset_required"
PIN_CREATED                     = "pin_created"
USER_VERIFIED                   = "user_verified"
BIOMETRIC_ENABLED               = "biometric_enabled"
USER_BLOCKED                    = "user_blocked"
FAILED_ATTEMPTS                 = "failed_attempts"

# SECRET_KEY                      = "HonoluluVacation"
SECRET_KEY                      = "n&(0k+j$2av*)r7htz(4g0@g18$u^+jgtdpwm-m_e71mvdf+yi"
RECAPTCHA_SITE_KEY_V3           = "6LcOCX4bAAAAAAuyQ07mOtPj2JHu5Efa_N476jZ5"
RECAPTCHA_SECRET_KEY_V3         = "6LcOCX4bAAAAACppwXIM99Wumg4vFKJgS224y36Y"

#for localhost only
# RECAPTCHA_SITE_KEY_MO_V2           = "6LdwiQwdAAAAACpCa6GWe8gUoz-4na1Tp9c9qbZ7" #Mobile APP
RECAPTCHA_SECRET_KEY_MO_V2         = "6LdwiQwdAAAAAGeCtAmqIEznAsKnE4x0NiiyT_g8" #Mobile APP

#for dev lambda and localhost both
# RECAPTCHA_SITE_KEY_V2           = "6LettYEbAAAAADnnFS-n9rMX4MnQr5hoh5OqzlNA" # local testing only
# RECAPTCHA_SECRET_KEY_V2         = "6LettYEbAAAAAIJCcVd74JmSwMUVv5vWNiHCmy3B" # local testing only

TEST_RECAPTCHA_SECRET_KEY_V2    = "6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe"
RECAPTCHA_SECRET_KEY_V2         = "6LcrW84cAAAAAHMDoEHtjf4wchJ_snNqNDI-3YOM" # live and dev only

CACHE_K_MOB_APP_VER             = "appVer-1000" 

#Redis expiry

T_CACHE_24                      = 86400
T_CACHE_1                       = 3600
T_CACHE_OTP                     = 900
T_CACHE_OTP_RESP                = 180
T_CACHE_TOKEN                   = 300
T_CACHE_VERSION                 = 21600

T_JWT_REQ_KEY                   = 180
T_JWT_REQ_KEY_OTP               = 900


FY_INHOUSE_APP_LIST             = ["2","4"]


#limits
PWD_MAX         = 20
PWD_MIN         = 6

#JWT https://login.fyers.in
JWT_CLAIMS_V_ISSUER_API         = "api.fyers.in"
JWT_CLAIMS_V_ISSUER_DEFAULT     = "https://login.fyers.in"

JWT_CLAIMS_V_AUDIENCE_DEFAULT_1 = ["x:0"]
JWT_CLAIMS_V_REFRESH_TOKEN      = "refresh_token"
JWT_CLAIMS_V_ACCESS_TOKEN       = "access_token"


# Encryption Keys
FY_ENCRYPT_DB_AESKEY_1          = "fyAuth91537"
FY_ENCRYPT_TOKENID              = "nH0XGfTyDxSiGMGEDC874L8_3NF_VJFIbZswYVP7AGY="
FY_ENCRYPT_APP_SECRETKEY        = "UIQ4vLk6AVwo3YDL015dZGowp_uqiD1d7-KPJYw1pCI="



SENDGRID_API_KEY = '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'

# 101 : fyers app
# 102 : third party app
BOPATH                          = "https://account.fyers.in/webclient/index.cfm"
KAPSYSTEM_BASE_URL              = "http://107.20.199.106/sms/1/text/query?"
GOOGLE_RECAPTCHA_API            = "https://www.google.com/recaptcha/api/siteverify"
KAPSYSTEM_USER_NAME             = "fyers"
KAPSYSTEM_PWD                   = "FyersSms@865@1"
KAPSYSTEM_SENDER                = "FFYERS"
KAPSYSTEM_CONTENT_TEMPLATE_ID   = "1607100000000031776"
KAPSYSTEM_PRINCIPAL_ENTITY_ID   = "1601100000000010499"

# API KEYS
API_K_FYERSID                   = "fyers_id"
API_K_TOKENHASH                 = "token_id"
API_K_APPID                     = "app_id"
API_K_SECRETKEY                 = "secret_key"
API_K_CALLBACK_URL              = "cb"
API_K_DISPLAY_MSG_TYPE          = "message_type"
API_K_COOKIE                    = "cookie"
API_K_ID_1                      = "id"
API_K_TYPE_FLAG                 = "typeFlag"
API_K_DATA_1                    = "data"
API_K_STATUS                    = "s"
API_K_STATUS_1                  = "status"
API_K_MSG                       = "message"
API_K_CODE                      = "code"
API_K_TIME                      = "t"
API_K_REQUEST_KEY               = "request_key"
API_K_EMAIL_ID                  = "email_id"
API_K_MOBILE_NO                 = "mobile_no"

# API json responses values
API_V_SUCCESS                   = "ok"
API_V_ERROR                     = "error"
API_V_ERROR_CODE                = "errorcode"

# User Account Status
ACCOUNT_IS_ACTIVE                  = 0
ACCOUNT_IS_DELETED                 = 1
ACCOUNT_BLOCKED_BY_FAILED_ATTEMPTS = 2
ACCOUNT_BLOCKED_FROM_FYERS         = 3
ACCOUNT_IS_TEMPORARY_STATE         = 4

OTP_ATTEMPTS                       = 20
# Html display message type
API_V_DISPLAY_MSG_TYPE_NEUTRAL  = 1
API_V_DISPLAY_MSG_TYPE_SUCCESS  = 2  #show success messaege
API_V_DISPLAY_MSG_TYPE_WARNING  = -1
API_V_DISPLAY_MSG_TYPE_ERROR    = -2 #show error messaege

SUCCESS_C_1                     = 1
ERROR_C_1                       = -1

ERROR_C_DEMO_USER               = -357
ERROR_C_INV_SQL_INJECTION       = -999
ERROR_C_INV_STRING_FORMAT       = -307

# Preventing SQL Injections
MYSQL_INJECTION_PREVENT_1 = "insert"
MYSQL_INJECTION_PREVENT_2 = "update"
MYSQL_INJECTION_PREVENT_3 = "select"
MYSQL_INJECTION_PREVENT_4 = "drop"
MYSQL_INJECTION_PREVENT_5 = "count"

MYSQL_INJECTION_PREVENT_LIST = [MYSQL_INJECTION_PREVENT_1,MYSQL_INJECTION_PREVENT_2,MYSQL_INJECTION_PREVENT_3,MYSQL_INJECTION_PREVENT_4,MYSQL_INJECTION_PREVENT_5]

#APP IDs
# APP_ID_MOBILE                   = "3" #old
APP_ID_MOBILE                   = "4"
APP_ID_WEB                      = "2"


#Log Dict defines
API_LOG_K_OP_TYPE                   = "operation_type"
API_LOG_K_FY_ID                     = "fy_id"
API_LOG_K_APP_ID                    = "app_id"
API_LOG_K_API_TYPE                  = "api_type"
API_LOG_K_HIT_TIME                  = "api_hit_time"
API_LOG_K_DESCRIPTION               = "description"
API_LOG_K_CITY                      = "city"
API_LOG_K_STATE                     = "state"
API_LOG_K_COUNTRY                   = "country"
API_LOG_K_ZIP_CODE                  = "zip_code"
API_LOG_K_TIME_ZONE                 = "time_zone"
API_LOG_K_DEVICE_IP                 = "device_ip"
API_LOG_K_DEVICE_OS                 = "device_os"

API_LOG_K_OS_VERSION                = "os_version"

API_LOG_K_DEVICE_TYPE               = "device_type" #PC/MOBILE/BOT
API_LOG_K_DEVICE_BROWSER            = "device_browser"

API_LOG_K_BROWSER_VERSION           = "browser_version"

API_LOG_K_TRANS_TYPE                = "transaction_type"

#Rupeeseed BASE URL

# REQ_URL_OMS_MAIN_1                  =  "http://15.206.241.17:8080/RupeeSeedWS/" #UAT
REQ_URL_OMS_MAIN_1                  =  "https://tradeonline-pub.fyers.in/RupeeSeedWS/" #Live
REQ_URL_OMS_MAIN_11                  =  "https://tradeonline-auth.fyers.in/RupeeSeedWS/"

GOOGLE_OAUTH = "https://www.googleapis.com/oauth2/v3/userinfo"
#marina
PUSH_NOTI_REG = "api.fyers.in/marina/v1/PushNoti/register"

#Rupeeseed Endpoint

API_OMS_REQ_PATH_SESSION_CREATE     = "SessionCreate/"
API_OMS_REQ_PATH_CHANGE_PASSWORD    = "Changepassword/ChangePass/"

FULL_SESSION_CREATE_API             = REQ_URL_OMS_MAIN_11 + API_OMS_REQ_PATH_SESSION_CREATE
FULL_CHANGE_PASSWORD_API            = REQ_URL_OMS_MAIN_11 + API_OMS_REQ_PATH_CHANGE_PASSWORD

# API OMS KEYS - USER DETAILS
API_OMS_K_USER_DETAILS              = "USER_DETAIL"
API_OMS_K_USER_ID_2                 = "USERID" # NOT USED
API_OMS_K_USER_ENTITY_ID            = "ENTITYID"
API_OMS_K_USER_UM_TYPE              = "UM_USER_TYPE"
API_OMS_K_USER_EM_NAME              = "EM_NAME"
API_OMS_K_USER_PROFILE_ID           = "PROFILEID"
API_OMS_K_USER_LOGIN_ID             = "LOGINID"
API_OMS_K_USER_PAN_1                = "PANNO"
API_OMS_K_USER_STATUS_1             = "STATUS"
API_OMS_K_USER_DOB_1                = "DOB"
API_OMS_K_USER_TOKEN_ID             = "TOKENID"
API_OMS_K_USER_LAST_LOGOFF_DATE     = "LOGOFF_DATE"
API_OMS_K_USER_EM_EXCH_CLIENT_ID    = "EM_EXCH_CLIENT_ID"
API_OMS_K_USER_EM_STATUS            = "EM_STATUS"
API_OMS_K_USER_EMAIL_ID             = "EMAIL_ID"
API_OMS_K_USER_LAST_LOGIN_TIME      = "LAST_LOGIN_TIME"
API_OMS_K_USER_LAST_PWD_CHANGE      = "LAST_PWD_CHANGE_DATE"
API_OMS_K_USER_AC_CODE              = "ACCCODE"
API_OMS_K_USER_UM_EXCH_ALLOWED      = "UM_EXCH_ALLOWED"
API_OMS_K_USER_UM_ENTITY_TYPE       = "UM_ENTITY_TYPE"
API_OMS_K_USER_EM_ENTITY_MANAG_TYPE = "EM_ENTITY_MANAGER_TYPE"
API_OMS_K_USER_BANK_DETAILS         = "bank_account_details"
# API_OMS_K_USER_BANK_AC_TYPE       = "AcctType"
API_OMS_K_USER_BANK_AC_TYPE         = "acc_type"
# API_OMS_K_USER_BANK_AC_NUM            = "AccNo"
API_OMS_K_USER_BANK_AC_NUM          = "acc_no"
# API_OMS_K_USER_BANK_ID                = "BankId"
API_OMS_K_USER_BANK_ID              = "bank_id"
# API_OMS_K_USER_BANK_NAME          = "BankName"
API_OMS_K_USER_BANK_NAME            = "bank_name"
# API_OMS_K_USER_BANK_IFSC          = "IfscCode"
API_OMS_K_USER_BANK_IFSC            = "ifsc"
API_OMS_K_USER_FLAGS_1              = "flags"
API_OMS_K_USER_FLAGS_TNC            = "TNC_FLAG"
API_OMS_K_USER_FLAGS_SUB            = "SUBSCRIBE_FLAG"
API_OMS_K_USER_FLAGS_ACTIVATE       = "ACTIVATE_FLAG"
API_OMS_K_POA_FLAG                  = "POA_FLAG"
API_OMS_K_AES_KEY                   = "AES_KEY"
API_OMS_K_USER_MOBILE_NO            = "MOBILE_NO"

API_OMS_K_SECURITY_ID               = "security_id"
API_OMS_K_PRODUCT_ID                = "product_id"
API_OMS_K_EXCHANE                   = "exch_id"
API_OMS_K_TOTAL_REDEEM_QTY          = "totalremqty"
API_OMS_K_PRICE                     = "price"
API_OMS_K_BUYSELL                   = "buysell"
API_OMS_K_TRIGGER_PRICE             = "trigger_price"

API_OMS_K_FT_CLIENT_ID_1            = "rp_clientid"
API_OMS_K_FT_AMOUNT                 = "amount"
API_OMS_K_FT_BANK_AC_NO             = "acc_no"
API_OMS_K_FT_BANK_AC_NO_2           = "account_no"
API_OMS_K_FT_MODE                   = "payment_mode"
API_OMS_K_FT_BANK_IFSC              = "ifsc_code"
API_OMS_K_FT_ACC_TYPE               = "acc_type"
API_OMS_K_FT_ACC_TYPE_2             = "limit_type"

API_OMS_K_WL_NAME                   = "WL_NAME"
API_OMS_K_WL_ID                     = "WL_ID"
API_OMS_K_BO_ID                     = "BO_ID"
API_OMS_K_DP_NAME                   = "DP_NAME"
API_OMS_K_PWD_EXPIRY_DAYS           = "Passwd_Expry_Days"
API_K_FCM_TOPIC                     = "notif_topic"


#Saurce
API_OMS_V_DEFAULT_REQ_SOURCE            = "I"
API_OMS_V_DEFAULT_REQ_SOURCE_WEB        = "W"
API_OMS_V_DEFAULT_REQ_SOURCE_MOBILE     = "M"

API_OMS_V_DEFAULT_REQ_SOURCE_FYERS_ONE  = "R"
API_OMS_V_DEFAULT_REQ_SOURCE_ADMIN      = "A"

INTERNAL_TECH_SHA256_SECRET_KEY         = "73E874098A80B60Dbdb97A99D4A1Dd4020B5B9Ed998Ceecf36Cec2F4Bc0Ea57"

#New User data dictionary keys
API_K_DB_FY_ID                          = "FY_ID"
API_K_DB_PAN                            = "PAN"
API_K_DB_DOB                            = "DOB"
API_K_DB_EMAIL_ID                       = "EMAIL_ID"
API_K_DB_MOBILE_NO                      = "MOBILE_NO"
API_K_DB_NAME                           = "EM_NAME"
ERROR_M_MF_INV_TOKEN_ID             = "Invalid token"
# OPEN ACCOUNT
OPEN_ACCOUNT_HASHING_SECRET_KEY         = "c038b6b0ab79c4e688ac92abdaf72660db548e681565f54a068ecfbe99bde9ef"

# USER AGENTS
USER_AGENT_OPEN_ACCOUNT                 = "open_account"

#RupeeSeed SHA256 Secret KEY
RS_HASHING_SECRET_KEY                   = "a3f802a7d1b281c1c3c1efa2e1ddbfef6a2e1b253d28e4b83548d1c26f45c04"

#Keys used to create the hash of the entire request sent
MOB_HASH_KEY_VALUE                      = "B9iATNUdovwG95u" 
WEB_HASH_KEY_VALUE                      = "H6MYSqKb6XeNq1G"
MOB_HASH_KEY_VALUE_2                    = "a7lW99Mbn0AKWUQ" 

#LMS
LMS_API_K_ATTR                          = "Attribute"
LMS_API_K_VAL                           = "Value"
LMS_API_K_EMAIL                         = "EmailAddress"
LMS_API_K_FNAME                         = "FirstName"
LMS_API_K_MOB_NUM                       = "Mobile"
LMS_API_K_SRC                           = "Source"
LMS_API_K_SEARCHBY                      = "SearchBy"

## LMS credentials
LMS_ACCESS_KEY                          = "u$r34d1c69da6302abc9b10ee58e355b2aa"
LMS_SECRET_KEY                          = "c1b37c05bd4a9e8e2d76c180aca93d9d1a665e42"

#Guest User
GUEST_CLIENT_ID                         = ["ZZ0001","ZZ0002","ZZ0003","ZZ0004"]
FCM_TOPIC_DEMO_USER                     = "user-demo"

# APP IDs RELATED
APPID_TRADE_FYERS                       = "2"
APP_SECRET_KEY_TRADE_FYERS              = "trade_v2.fyers.in"

APPID_SECRETKEY_SPLITTER                = "|" # This will be used while creating the app secret key

APPID_RS_MOBILE                         = "3"
APP_SECRET_KEY_RS_MOBILE                = "rupeeseedMobile"

APPID_MOBILE_FYERS                      = "4"
APP_SECRET_KEY_MOBILE_FYERS             = "fyersMobile"

ERROR_M_TOKEN_EXPIRED   = "token is expired"
ERROR_M_TOKEN_INVALID   = "token is invalid"
ERROR_M_TOKEN_INVALID_D = "wrong token"

HASH_INP_SPLITTER                       = "|"  # This will be used while creating the string that needs to be hashed
# Regular expression format to check for desired format
STRING_FORMAT_FYERSID       = "^[A-Z]{2}[0-9]{3,5}$"

APP = "" # app object will be saved in this variable from server.py file
IP_ADDRESS = ""
# TEST_EMAIL = "yashas@fyers.in"
# TEST_EMAIL = "ajay@fyers.in"
TEST_EMAIL = "vinodr@fyers.in"
# TEST_EMAIL = "rushbh@fyers.in"

TEST_MOBILE = "9096339183"
# TEST_MOBILE = "9096339183"
# TEST_MOBILE = "9096339183"
# TEST_MOBILE = "9096339183"

UNIT_TEST = False
CACHE_REDIS_1_URL = "fyers-trading-redis.jb5agw.ng.0001.aps1.cache.amazonaws.com" 
SECRET_KEY                      = "n&(0k+j$2av*)r7htz(4g0@g18$u^+jgtdpwm-m_e71mvdf+yi"
DB_TRADING_BRIDGE       = "fyers_trading_bridge"
FY_ENCRYPT_DB_AESKEY_1          = "fyAuth91537"
TBL_OMS_AUTH_V2         = "fyers_oms_auth_v2"
TBL_OMS_AUTH_V4         = "fyers_oms_auth_v4"
# FYERS_DB_READER_TEST = "fyers-testing-db.cluster-cvghve20lauv.ap-south-1.rds.amazonaws.com" # testing
# FYERS_DB_WRITER_TEST = "fyers-testing-db.cluster-cvghve20lauv.ap-south-1.rds.amazonaws.com" # testing

FYERS_DB_WRITER_LIVE = "fyers-trading-db-cluster.cluster-cvghve20lauv.ap-south-1.rds.amazonaws.com"    # live
FYERS_DB_READER_LIVE = "fyers-trading-db-cluster.cluster-ro-cvghve20lauv.ap-south-1.rds.amazonaws.com" # live


# DB_TRADE_WEB_USER = "fy_master_test"  # testingdb
# DB_TRADE_WEB_PWD = "HEIP8NyvaIfBoQqmHX7K" # testing

DB_TRADE_WEB_USER = "fy_dbmaster_1329"  # live
DB_TRADE_WEB_PWD = "fyersDbAdmin1329" # live

#defines
LOG_STATUS_ERROR_1      = "ERROR"
LOG_STATUS_SUCCESS_1    = "SUCCESS"
API_V_SUCCESS                   = "ok"
API_V_ERROR                     = "error"
API_V_DISPLAY_MSG_TYPE_NEUTRAL     = 1
API_V_DISPLAY_MSG_TYPE_SUCCESS     = 2
API_V_DISPLAY_MSG_TYPE_WARNING     = -1
API_V_DISPLAY_MSG_TYPE_ERROR       = -2
ERROR_C_UNKNOWN                     = -99
ERROR_C_FY_DECRYPTION               = -103
ERROR_C_INVALID_TOKEN_2             = -18
ERROR_C_INV_TOKEN_1                 = "-1"
ERROR_C_TOKEN_1                     = -12
ERROR_C_TOKEN_CREATE                = -13
ERROR_C_TOKEN_INVALID               = -15
ERROR_C_TOKEN_INVALID_DUMMY_VALUES  = -15
ERROR_C_INVALID_TOKEN_2             = -18
ERROR_C_INVALID_TOKEN_3             = -19
ERROR_C_INVALID_TOKEN_4             = -20
ERROR_C_INVALID_TOKEN_5             = -21
ERROR_C_INVALID_TOKEN_6             = -22
ERROR_C_TOKEN_SPLIT                 = -16
ERROR_C_TOKEN_CACHE_NOT_FOUND       = -17
ERROR_C_TOKEN_NO_JSON               = -30
ERROR_C_TOKEN_INVALID_APP           = -31
ERROR_C_TOKEN_AUTH                  = -105

#return msgs
ERROR_M_TOKEN_NOT_USED              = 'access token should be used here'
ERROR_M_RELOGIN                     = "user should relogin"
ERROR_M_DB_CONNECTION               = "db connection error"
ERROR_M_UNKNOWN_1                   = "something went wrong"
ERROR_M_INV_USER_NAME_NO_DATA       = "invalid username, no data found"
ERROR_M_INV_TOKEN_AUTH_FAIL         = "invalid token, user auth failed"


# DB_LINK_T = "mysql+pymysql://" + DB_TRADE_WEB_USER + ":" +DB_TRADE_WEB_PWD + "@" + FYERS_DB_WRITER_TEST
DB_LINK_L = "mysql+pymysql://" + DB_TRADE_WEB_USER + ":" +DB_TRADE_WEB_PWD + "@" + FYERS_DB_WRITER_LIVE
# redis_conn = redis.Redis(host=CACHE_REDIS_1_URL, port=6379, db=0)
redis_conn = CACHE_REDIS_TRADING


def INTERNAL_splitTokenHash(tokenHash, callingFuncName = ""):
    """
        [FUNCTION]
            INTERNAL_splitTokenHash : Get the status of a particular order by User and OrderID
            [PARAMS]
            tokenHash    :
            [RETURN]
                Success : [SUCCESS_C_1,[fyId,appId,randomKey],""]
                Failure : [ERROR_C_1,errorCode,errorMessage]
    """
    funcName = "INTERNAL_splitTokenHash"
    try:
        # Check for fyId, appId and randomKey from redis first
        redis_resp_json = redis_conn.get(tokenHash)
        if redis_resp_json is not None:
            redis_resp = json.loads(redis_resp_json)
            resp_list = redis_resp.split('-')
            fyId = resp_list[0].upper()
            appId = resp_list[1]
            randomKey = resp_list[2]
            return [SUCCESS_C_1, [fyId, appId, randomKey, redis_resp], ""]            

        else:
            from vagator_decryptWithKey import INTERNAL_decreptWithKey
            inputTokenHash = INTERNAL_decreptWithKey(tokenHash,FY_ENCRYPT_TOKENID,callingFuncName=callingFuncName)
            if inputTokenHash[0] == ERROR_C_1:
                return inputTokenHash
            if isinstance(inputTokenHash[1], bytes):
                a = inputTokenHash[1].decode("utf-8").split("-")
            else:
                a = inputTokenHash[1].split("-")
            fyId = a[0].upper()
            appId = a[1]
            randomKey = a[2]

            # store result in redis 
            result_str = fyId + "-" + appId + "-" + randomKey
            redis_conn.set(tokenHash, json.dumps(result_str), 10800)

            return [SUCCESS_C_1, [fyId, appId, randomKey, inputTokenHash[1]], ""]
    except Exception as e:
        logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, e, ERROR_C_UNKNOWN, tokenHash)
        return [ERROR_C_1, ERROR_C_UNKNOWN, ""]


# def INTERNAL_decreptWithKey(encryptedText, decryptionKey, callingFuncName = ""):
#     """
#         [FUNCTION]
#         INTERNAL_decreptWithKey : Will decrypt the input text with the input decryption key
#         [PARAMS]    :
#             encryptedText : The text which needs to be decrypted
#             decryptionKey: The decryptionKey key which will be used
#         [RETURN]
#             Success : [SUCCESS_C_1,deryptedText,""]
#             Failure : [ERROR_C_1,ERROR_C_FY_DECRYPTION,""]
#     """
#     funcName = "INTERNAL_decreptWithKey"
#     try:
#         cipher = Fernet(decryptionKey)
#         encryptedText = encryptedText.encode('utf-8')
#         decryptBytes = cipher.decrypt(encryptedText)
#         decryptBytes = decryptBytes.decode('utf-8')
#         return [SUCCESS_C_1, decryptBytes, ""]
#     except Exception as e:
#         logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, e, ERROR_C_UNKNOWN,
#                       encryptedText, decryptionKey)
#     return [ERROR_C_1, ERROR_C_FY_DECRYPTION, ERROR_M_MF_INV_TOKEN_ID, ""]


def INTERNAL_validate_access_token(access_token, callingFuncName=""):
    """This function takes the following parameters and verify token, it token is valid the user will logged in
    and if not valid the user have to relogin.

    Args:
        access_token        : access_token to verify the user.
        attrs               : This is a class object of class VerifyToken.
        request             : Request object.
        api_name            : Api name to store in log report.

    Returns:
        [SUCCESS]
            Response body with success message.

        [FAILED]
            Response body with failed message.
    """
    funcName = "validate_access_token"
    try:
        logger = get_logger()
        user_loggedin = False
        msg = "user is not logged in"
        if access_token != None:
            try:
                decoded_access = jwt.decode(access_token, SECRET_KEY, issuer=JWT_CLAIMS_V_ISSUER_DEFAULT, algorithms='HS256', options={"verify_signature": True, "verify_aud": False, "verify_iss": True, "verify_exp": True, "verify_nbf": True})
            except jwt.exceptions.ExpiredSignatureError:
                logger.exception(f"ExpiredSignatureError - {access_token} {moduleName} {funcName}")
                return [ERROR_C_1, ERROR_C_INVALID_TOKEN_2, ERROR_M_TOKEN_EXPIRED, ""]
                
            except jwt.exceptions.InvalidSignatureError:
                logger.exception(f"InvalidSignatureError - {access_token} {moduleName} {funcName}")
                return [ERROR_C_1, ERROR_C_INVALID_TOKEN_3, ERROR_M_TOKEN_INVALID, ""]
                
            except jwt.exceptions.DecodeError:
                logger.exception(f"DecodeError - {access_token} {moduleName} {funcName}")
                return [ERROR_C_1, ERROR_C_INVALID_TOKEN_3, ERROR_M_TOKEN_INVALID_D, ""]
                
            except Exception as e:
                logger.exception(f"Access Token Error - {access_token} {moduleName} {funcName}")
                return [ERROR_C_1, ERROR_C_TOKEN_INVALID, ERROR_M_TOKEN_INVALID_D, ""]
            token_id = decoded_access['at_hash']

        utc_timestamp = int(time.time())
        if not decoded_access['sub'] == 'access_token':
            logger.error("access_token subject error - %s - %s - %s" %(decoded_access, funcName, callingFuncName))
            return [ERROR_C_1, ERROR_C_INVALID_TOKEN_4, ERROR_M_TOKEN_NOT_USED, ""]

        if utc_timestamp >= decoded_access['exp']:
            logger.error("access_token expired exp error - %s - %s - %s" %(decoded_access, funcName, callingFuncName))
            return [ERROR_C_1, RELOGIN_REQUIRED, ERROR_M_RELOGIN, ""]

        splited_token_hash = INTERNAL_splitTokenHash(token_id, callingFuncName= funcName)[1]
        
        fy_id = decoded_access['fy_id']
        app_id = splited_token_hash[1]
        jwt_token_hash = splited_token_hash[3]
                    
        vagator_cache_key = "vagator_token-" + fy_id + "-" + app_id
        redis_resp = redis_conn.get(vagator_cache_key)

        if redis_resp != None:
            if redis_resp != -1:
                redis_resp = json.loads(redis_resp)
                if redis_resp["auth_token"] == jwt_token_hash:
                    msg = "user is logged in"
                    user_loggedin = True

                    return [
                        SUCCESS_C_1, 
                        USER_VERIFIED_CODE, 
                        msg, 
                        [
                            redis_resp["fy_id"], 
                            redis_resp["userOmsTokenId"], 
                            redis_resp["aesKeyRecv"]
                        ], 
                        {
                            "user_loggedin": user_loggedin, 
                            "decoded_access": decoded_access
                        }
                    ]
                    
                    
                else:
                    return [ERROR_C_1, USER_NOT_VERIFIED_CODE, msg, fy_id, {"user_loggedin": user_loggedin, "decoded_access": decoded_access}]
                    

        # if token hash is not in redis then check in database
        try:
            from vagator_sqlalchemy import create_sql_alchemy_engine
            #engine = create_engine(DB_LINK_L, echo=False)
            engine = create_sql_alchemy_engine(DB_LINK_L, echo=False)

            conn = engine.connect()

            select_query = f"SELECT FY_ID, AES_DECRYPT(TOKEN_HASH, '{FY_ENCRYPT_DB_AESKEY_1}'), CAST(AES_DECRYPT(OMS_TOKEN_ID, '{FY_ENCRYPT_DB_AESKEY_1}') AS CHAR), CAST(AES_DECRYPT(DESCRIPTION, '{FY_ENCRYPT_DB_AESKEY_1}') AS CHAR) FROM {DB_TRADING_BRIDGE}.{TBL_OMS_AUTH_V4} WHERE FY_ID = '{fy_id}';"

            print(f"Hitting DB-=-=-=-=-{DB_LINK_L}-=-=-=-=-{select_query}")

            queryResult = conn.execute(select_query).fetchall()
        # except OperationalError as op:
        #     exception_type, exception_object, exception_traceback = sys.exc_info()
        #     line_number = exception_traceback.tb_lineno
        #     logger.exception("%s - %s - %s - error on line %s - %s"
        #           %(moduleName, funcName, str(op), line_number, traceback.format_exc()))
        #     return [ERROR_C_1, EXCEPT_SOMETHING_WENT_WRONG, ERROR_M_DB_CONNECTION, ""]

        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            line_number = exception_traceback.tb_lineno
            logger.exception("%s - %s - %s - error on line %s - %s"
                  %(moduleName, funcName, e, line_number, traceback.format_exc()))
            return [ERROR_C_1, EXCEPT_SOMETHING_WENT_WRONG, ERROR_M_UNKNOWN_1, ""]

        if not queryResult:
            logger.error("queryResult is null:", queryResult)
            return [ERROR_C_1, INVALID_USER, ERROR_M_INV_USER_NAME_NO_DATA, ""]

        token_hash = {}
        if queryResult[0][1]:
            token_hash = json.loads(queryResult[0][1])
        
        userOmsTokenId = queryResult[0][2]
        aesKeyRecv = queryResult[0][3]
        if token_hash.get(app_id):

            if token_hash[app_id] == jwt_token_hash:
                msg = "user is logged in"
                user_loggedin = True
                
                redis_resp = {
                        "fy_id" : fy_id,
                        "userOmsTokenId" : userOmsTokenId,
                        "aesKeyRecv"  : aesKeyRecv,
                        "auth_token" : token_hash[app_id]
                        }
                redis_conn.set(vagator_cache_key, json.dumps(redis_resp), T_CACHE_24)

                return [
                    SUCCESS_C_1, 
                    USER_VERIFIED_CODE, 
                    msg, 
                    [
                        fy_id, 
                        userOmsTokenId, 
                        aesKeyRecv
                    ], 
                    {
                        "user_loggedin": user_loggedin, 
                        "decoded_access": decoded_access
                    }
                ]

            else:
                return [ERROR_C_1, USER_NOT_VERIFIED_CODE, msg, fy_id, {"user_loggedin": user_loggedin, "decoded_access": decoded_access}]                
        else:
            return [ERROR_C_1, USER_NOT_VERIFIED_CODE, msg, fy_id, {"user_loggedin": user_loggedin, "decoded_access": decoded_access}]
            
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        line_number = exception_traceback.tb_lineno
        logger.exception("%s - %s - %s - error on line %s - %s" %(moduleName, funcName, e, line_number, traceback.format_exc()))
        return [ERROR_C_1, ERROR_C_UNKNOWN, ERROR_M_INV_TOKEN_AUTH_FAIL, ""]


if __name__ == "__main__":
    
    token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL2xvZ2luLmZ5ZXJzLmluIiwiaWF0IjoxNjM4MjU5NzQwLCJleHAiOjE2MzgzMTg2MDAsIm5iZiI6MTYzODI1OTc0MCwiYXVkIjpbIng6MCJdLCJzdWIiOiJhY2Nlc3NfdG9rZW4iLCJhdF9oYXNoIjoiZ0FBQUFBQmhwZHdjcV95QXpnVjFpSUgyVHhTa2pkV0NqSFBXd3VQcWNkWG1EUjJ2cTJyN3hseS1na18xSGd2VnhJQlBhRWtZMWVnLS00R1ROeWRGOUllenA0cmNMNmhKS1VZSTZfTHZ3eHlWbFhoM3RKczQ4Z1E9IiwiZGlzcGxheV9uYW1lIjoiWUFTSEFTIE4gSyIsImZ5X2lkIjoiRlkwMDAxIiwiYXBwVHlwZSI6MTAxLCJwb2FfZmxhZyI6Ik4ifQ.EHI_SB6SNmL_UNAXtK0BtlrghxOSrTr6nrfv8YP_jnY"

    print(INTERNAL_validate_access_token(token))
