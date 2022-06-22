# JWT RELATED
JWT_DEFAULT_DECODE_OPTIONS      = {"require_exp":True,"require_sub":True,"require_aud":True,
                                   "require_iss":True, "verify_aud": False}
JWT_DEFAULT_SECRET_KEY          = "HonoluluVacation"
JWT_DEFAULT_HASHING_ALGORITHM   = "HS256"
JWT_DEFAULT_EXPIRY_DAYS         = 30
JWT_DEFAULT_AUDIENCE_APPID      = "0"

JWT_CLAIMS_V_ISSUER_DEFAULT     = "https://login.fyers.in"
JWT_CLAIMS_V_AUDIENCE_DEFAULT   = ["1","2"]
JWT_CLAIMS_V_SUBJECT_CLIENT     = "1"
JWT_CLAIMS_V_SUBJECT_GUEST      = "2"

JWT_CLAIMS_K_EXPIRY             = "exp"
JWT_CLAIMS_K_NOT_BEFORE_TIME    = "nbf"
JWT_CLAIMS_K_ISSUED_AT_TIME     = "iat"
JWT_CLAIMS_K_ISSUER             = "iss"
JWT_CLAIMS_K_AUDIENCE_LIST      = "aud"
JWT_CLAIMS_K_TOKEN_HASH         = "at_hash"
JWT_CLAIMS_K_SUBJECT            = "sub"
JWT_CLAIMS_K_DISPLAY_NAME       = "display_name"

# COOKIE RELATED
COOKIE_NAME_MAIN_1              = "_FYERS"
COOKIE_DOMAIN_MAIN_1            = ".fyers.in"

# Encrypt Key
FY_ENCRYPT_TOKENID      = "nH0XGfTyDxSiGMGEDC874L8_3NF_VJFIbZswYVP7AGY="
FY_ENCRYPT_PWD		    = "1ZVz97Tonb98M6XbObTvjRr1LkWZe1ZsonQArNHYprM="
FY_ENCRYPT_APP_SECRETKEY    = "UIQ4vLk6AVwo3YDL015dZGowp_uqiD1d7-KPJYw1pCI="
FY_ENCRYPT_TIME         = "ksZnSWwe_2qPKlsBqR58fCwhgBFbJUGPETtCGUg_dCU="

# APP IDs RELATED
APPID_TRADE_FYERS = "2"
APP_SECRET_KEY_TRADE_FYERS  = "trade_v2.fyers.in"

APPID_SECRETKEY_SPLITTER = "|" # This will be used while creating the app secret key

APPID_RS_MOBILE     = "3"
APP_SECRET_KEY_RS_MOBILE    = "rupeeseedMobile"

APPID_MOBILE_FYERS	= "4"
APP_SECRET_KEY_MOBILE_FYERS = "fyersMobile"

APPID_ALL = {APPID_TRADE_FYERS:APP_SECRET_KEY_TRADE_FYERS,
             APPID_RS_MOBILE: APP_SECRET_KEY_RS_MOBILE,
             APPID_MOBILE_FYERS: APP_SECRET_KEY_MOBILE_FYERS}

#Keys used to create the hash of the entire request sent
MOB_HASH_KEY_VALUE = "B9iATNUdovwG95u"   #Khyati
WEB_HASH_KEY_VALUE = "H6MYSqKb6XeNq1G"   #Khyati
MOB_HASH_KEY_VALUE_2 = "a7lW99Mbn0AKWUQ"

HASH_INP_SPLITTER = "|" # This will be used while creating the string that needs to be hashed

FCM_FYERS_MOBILE_V2_SERVER_KEY = "AAAA9bAXOEI:APA91bGuLb_gtyz5oeVXzscyJfSa_rL61BRquQuMwe-nutYC8rp-9nk34ZnJ4yDMrJ7HEsdlnW6lAYJ8htrK3A5-7lFBmyHyRbYP1-zvsrc6LglXH8nC4ljv_vEhYUTEvTfLldR72ccP"

FYERS_APP_OTP_SMS_HASH_KEY = "0C9UOqeylJa"

## LMS credentials
LMS_ACCESS_KEY = "u$r34d1c69da6302abc9b10ee58e355b2aa"
LMS_SECRET_KEY = "c1b37c05bd4a9e8e2d76c180aca93d9d1a665e42"

TECH_ADMIN_HASH_KEY_VALUE = "inTerNaltEChdAshboArdaPi2021"
MOB_IMEI_HASH_KEY_VALUE = "acd78430-19dd-11ec-ba2c-d43b0451d1a0"
