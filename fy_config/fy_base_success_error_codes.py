# SUCCESS RESPONSES
SUCCESS_C_1 					= 1
SUCCESS_C_HIST_DATA_PARTIAL  	= 50

# SUCCESS CODES WHICH WE HAVE BEEN INTERCEPTED FROM THE OMS BEFORE RETURNING TO THE FRONT END
SUCCESS_C_OMS 					= 2
SUCCESS_C_OMS_PWD_RESET 		= 1001
SUCCESS_C_OMS_PWD_CHANGE 		= 1002
SUCCESS_C_OMS_UNLOCK 			= 1003
SUCCESS_C_OMS_LOGOUT 			= 1004
SUCCESS_C_OMS_ORDER_PLACE		= 1101
SUCCESS_C_OMS_ORDER_MODIFY		= 1102
SUCCESS_C_OMS_ORDER_CANCEL     	= 1103
SUCCESS_C_OMS_FT_OUTWARD        = 1005
SUCCESS_C_WATCHLIST_DELETE      = 2001


# ERROR RESPONSES
ERROR_C_1        					= -1
ERROR_C_FILE_DOES_NOT_EXIST			= -3 # Used in delete chart from S3
ERROR_C_URL_1     					= -1
ERROR_C_DB_1      					= -10
ERROR_C_DB_NOT_FOUND 				= -11
ERROR_C_DB_UPDATE_FAILED 		    = -12
ERROR_C_DB_SELECT_FAILED            = -13
ERROR_C_DB_NOT_FOUND_APP_ID 		= -14
ERROR_C_DB_DATA_NOT_FOUND           = -15
ERROR_C_DB_NOT_FOUND_OMS_DETAILS 	= -19

# JWT ERRORS
ERROR_C_JWT_INV_EXPIRED       = -11
ERROR_C_JWT_INV_AUDIENCE      = -12
ERROR_C_JWT_INV_PREMATURE     = -13
ERROR_C_JWT_INV_MISSING_PARAM = -14
ERROR_C_JWT_INV_ISSUER        = -15
ERROR_C_JWT_INV_TOKEN         = -16
ERROR_C_JWT_INV_DECODE        = -17
ERROR_C_JWT_INV_KEY           = -18
ERROR_C_JWT_INV_ALGORITHM     = -19
ERROR_C_JWT_MISSING_TOKEN     = -20

# COOKIE ERRORS
ERROR_C_COOKIE_INV_LENGTH       = -23
ERROR_C_COOKIE_INV_NOT_FOUND    = -24



ERROR_C_INV_TOKEN_1					= "-1"
ERROR_C_TOKEN_1						= -12
ERROR_C_TOKEN_CREATE				= -13
ERROR_C_TOKEN_INVALID 				= -15
ERROR_C_TOKEN_INVALID_DUMMY_VALUES 	= -15
ERROR_C_INVALID_TOKEN_2             = -18
ERROR_C_INVALID_TOKEN_3             = -19
ERROR_C_INVALID_TOKEN_4             = -20
ERROR_C_INVALID_TOKEN_5             = -21
ERROR_C_INVALID_TOKEN_6             = -22
ERROR_C_TOKEN_SPLIT 				= -16
ERROR_C_TOKEN_CACHE_NOT_FOUND 		= -17
ERROR_C_TOKEN_NO_JSON               = -30
ERROR_C_TOKEN_INVALID_APP           = -31
ERROR_C_TOKEN_AUTH 					= -105

ERROR_C_FY_ENCRYPTION				= -102
ERROR_C_FY_DECRYPTION				= -103
ERROR_C_CACHE_1 					= -106
ERROR_C_LEVEL2DATA_UNAVAILABLE 		= -2006

ERROR_C_UNKNOWN 					= -99


# INVALID INPUT ERRORS
ERROR_C_INV_FYERSID			= -200
ERROR_C_INV_EXISTPWD 		= -201
ERROR_C_INV_NEWPWD 			= -202
ERROR_C_INV_PAN 			= -203
ERROR_C_INV_DOB 			= -204
ERROR_C_INV_PWD2 			= -207
ERROR_C_INV_TOKENHASH 		= -208
ERROR_C_INV_APPID 			= -205
ERROR_C_INV_SECRET_KEY 		= -206
ERROR_C_INV_COOKIE          = -209
ERROR_C_INV_EMAIL           = -210
ERROR_C_INV_WATCHLIST_NAME  = -600
ERROR_C_INV_LUT             = -601

ERROR_C_INV_INP 			= -50
ERROR_C_INV_SEARCHSYMBOL 	= -210
ERROR_C_INV_SEARCHEX 		= -211
ERROR_C_INV_SEARCHTYPE 		= -212
ERROR_C_INV_BANKAC 			= -213
ERROR_C_INV_BANKDETAILS     = -215
ERROR_C_INV_FT_AMT 			= -214 # NOT USED
ERROR_C_INV_FYSYMBOL 		= -300
ERROR_C_INV_FYSYMBOLS 		= -310
ERROR_C_INV_SYMBOL 			= -307 # NOT USED
ERROR_C_INV_DATA_RESOLUTION	= -301
ERROR_C_INV_DATA_FROM 		= -302
ERROR_C_INV_DATA_TO 		= -303
ERROR_C_INV_EXCHANGE 		= -304
ERROR_C_INV_SEGMENT 		= -305
ERROR_C_INV_OPT_TYPE        = -306
ERROR_C_INV_STRING_FORMAT   = -307

ERROR_C_INV_ORDER_ID 		    = -209
ERROR_C_INV_ORDER_TYPE 		    = -101
ERROR_C_INV_ORDER_TYPE_CO 		= -305
ERROR_C_INV_ORDER_TYPE_BO 		= -323
ERROR_C_INV_ORDER_TRAN_TYPE     = -306 # NOT USED
ERROR_C_INV_ORDER_LMT_PRICE     = -308
ERROR_C_INV_ORDER_STP_PRICE     = -309
ERROR_C_INV_ORDER_QTY 		    = -310
ERROR_C_INV_ORDER_TRIG_PRICE    = -311
ERROR_C_INV_ORDER_SIDE 		    = -313
ERROR_C_INV_ORDER_PRODUCT       = -314
ERROR_C_INV_ORDER_STOP_LMT_PRICE 	= -315
ERROR_C_INV_ORDER_STOP_LOSS 	= -316
ERROR_C_INV_ORDER_STOP_LOSS_VAL 		= -323
ERROR_C_INV_ORDER_TRAILING_SL_VAL 		= -324
ERROR_C_INV_ORDER_TARGET_VAL 		    = -325
ERROR_C_INV_ORDER_VALIDITY              = -326
ERROR_C_INV_ORDER_DISC_QTY              = -327
ERROR_C_INV_ORDER_OFFLINE_FLAG          = -328
ERROR_C_INV_ORDER_SHOW_NOTICE           = -399

ERROR_C_INV_WATCHLIST		    = -317
ERROR_C_INV_INST_TYPE           = -318
ERROR_C_INV_TIME_1              = -319
CONST_C_INV_FYSYMBOL_LIST 	    = -2003 # NOT USED
ERROR_C_INV_GET_TOKEN_FOR_SYMBOLS 	= -2005
ERROR_C_INV_SQL_INJECTION       = -999
ERROR_C_INV_LAST_UPDATED_TIME   = -320
ERROR_C_INV_EXPIRY_TYPE         = -321
ERROR_C_EXPIRY_NOT_FOUND        = -322

# ERROR RESPONSES INTERCEPTED FROM OMS BEFORE RETURNING TO THE FRONT END
ERROR_C_OMS_1             			= -2
ERROR_C_OMS_UNKNOWN      			= -99
ERROR_C_OMS_AUTHFAIL 				= -100
ERROR_C_OMS_STRING_CONVERSION_FAIL  = -101

ERROR_C_OMS_URL_CONNECTION 			= -201
ERROR_C_OMS_URL_TIMEOUT 			= -202
ERROR_C_OMS_URL_READ_TIMEOUT 		= -203
ERROR_C_OMS_URL_HTTP				= -204
ERROR_C_OMS_URL_STATUS_CODE 		= -205 
ERROR_C_OMS_URL_INV_RESP_TYPE		= -206
ERROR_C_OMS_URL_PAYIN_NO_RESP		= -18

ERROR_C_OMS_INV_BANKAC 				= -20
ERROR_C_OMS_INV_FT_LESS_THAN_MIN	= -21
ERROR_C_OMS_INV_PWD   				= -102
ERROR_C_OMS_INV_PWD2     			= -103
ERROR_C_OMS_INV_DOB 				= -111
ERROR_C_OMS_INV_PAN 				= -112
ERROR_C_OMS_INV_ALPHANUM_REQ 		= -150
ERROR_C_OMS_INV_EXIST_PWD 			= -151
ERROR_C_OMS_INV_SAME_AS_EXIST_PWD 	= -152
ERROR_C_OMS_INV_PWD_NOT_MATCHING 	= -153
ERROR_C_OMS_INV_PWD_TOO_SHORT 		= -154
ERROR_C_OMS_INV_FYERSID_1 			= -155
ERROR_C_OMS_INV_FYERSID_2     		= -101
ERROR_C_OMS_INV_REQUEST 			= -156
ERROR_C_OMS_INV_USER_INFO_RESP 		= -157
ERROR_C_OMS_INV_DATE_FORMAT			= -158
ERROR_C_OMS_INV_MANDATORY_MISSING 	= -110

ERROR_C_OMS_STATUS_LOCKED        	= -104
ERROR_C_OMS_STATUS_DISABLED      	= -106
ERROR_C_OMS_STATUS_SUSPENDED     	= -107
ERROR_C_OMS_STATUS_PWD_EXPIRED		= -105
ERROR_C_OMS_STATUS_ALREADY_UNLOCKED = -108
ERROR_C_OMS_STATUS_MAX_ATTEMPTS 	= -109
ERROR_C_OMS_STATUS_NOT_SUBSCRIBED 	= -158
ERROR_C_OMS_STATUS_CHANGE_PWD_TEMP_TABLE 	= -160

ERROR_C_OMS_ORDERBOOK_EMPTY 		= -159
ERROR_C_OMS_ORDER_ALREADY_CANCELLED = -161
ERROR_C_OMS_ORDER_ALREADY_TRADED 	= -162
ERROR_C_OMS_ORDER_MODIFY_FAILED 	= -163
ERROR_C_OMS_ORDER_ALREADY_REJECTED 	= -164


ERROR_C_OMS_ORDER_FAIL_INV_FYID_DATA  		= -165
ERROR_C_OMS_ORDER_FAIL_1 					= -166
ERROR_C_OMS_ORDER_FAIL_INV_INST_TYPE 		= -167
ERROR_C_OMS_ORDER_FAIL_INV_QTY_NOT_NUM 		= -168
ERROR_C_OMS_ORDER_FAIL_INV_TRG_PRICE 		= -169
ERROR_C_OMS_ORDER_FAIL_INV_DISC_QTY			= -170
ERROR_C_OMS_ORDER_FAIL_LIMIT_NOT_AVAILABLE 	= -171
ERROR_C_OMS_ORDER_FAIL_INV_EXCH 			= -172
ERROR_C_OMS_ORDER_NOT_CONNECTED             = -173
ERROR_C_OMS_MARKET_OFFLINE                  = -174

# Pragya 20200117
ERROR_C_OMS_PASSWD_SAME_PREV_5				= -175

## Pragya - 20190125
#For fund transfer page (add and withdraw funds)
ERROR_C_INTERNAL_FUND_TRANSFER_FUNCTION = -250
ERROR_C_INTERNAL_BANK_DETAILS_FUNCTION = -251
ERROR_C_INTERNAL_FUND_TRANSFER_OUTWARD_FUNCTION = -252
ERROR_C_INTERNAL_LIMIT4_FUNCTION = -253

ERROR_C_INTERNAL_NO_BANK = -254
ERROR_C_INTERNAL_ADD_FUND = -255
ERROR_C_INTERNAL_WITHDRAW_FUND = -256

## Pragya Login API 2019-02-07
ERROR_C_UNLOCK_USER 				= -257
ERROR_C_RESET_PASSWORD 				= -258
ERROR_C_CHANGE_PASSWORD 			= -259
ERROR_C_AUTH_USER_LOGIN 			= -260
ERROR_C_RESET_PASSWORD_AFTER_EMAIL 	= -261

# Pragya 20190227
# For Corp Action
ERROR_C_CORP_ACTION                 = -257

## Snapshot gallery 20190614 Palash
ERROR_C_S3_SNAPSHOT = -700
ERROR_C_S3_SNAPSHOT_DELETE = -701
ERROR_C_INV_INVALID_IMAGE = -702
ERROR_C_CF_INVALIDATION = -703
SUCCESS_C_S3_SNAPSHOT_DELETE = 801
SUCCESS_C_CF_INVALIDATION = 802

ERROR_C_INV_USER_CHART_SETTINGS = -330 ## Save settings to server 20190506 - Palash
ERROR_C_INV_USER_CHART          = -340 ## Save settings to server 20190506 - Palash
ERROR_C_INV_USER_CHART_METHOD   = -350 ## Save settings to server 20190506 - Palash

ERROR_C_INV_POSITION_ID		= -351		#exit positions 20200117 Khyati
ERROR_C_NO_OPEN_POS			= -352

ERROR_C_INV_IMEI		= -355
ERROR_C_INV_PWD_TYPE	= -356

ERROR_C_FETCH_DATA             = 442

# Fund transfer upi (Pragya - 20200411)
ERROR_C_INV_PAYMENT_OPTION = -353
ERROR_C_INV_UPI_ID = -354

# MF - Pragya (2020710)
SUCCESS_C_OMS_MF_ADD_FUND_LIMIT     = 270
SUCCESS_C_OMS_MF_ORDER              = 271 # Place/modify/cancel order, register mandate, place/cancel SIP

ERROR_C_OMS_MF_ORDER_FAILED 	            = -510
ERROR_C_OMS_MF_INV_PLACE_ORDER_MIN_VALUE    = -511
ERROR_C_OMS_MF_INV_ADD_FUND_LIMIT_MIN_VALUE = -512
ERROR_C_OMS_MF_ORDER_NOT_FOUND              = -513
ERROR_C_OMS_MF_AMOUNT_ERR                   = -514
ERROR_C_OMS_MF_INV_SCHEME                   = -515
ERROR_C_OMS_MF_GENERATE_MANDATE_ID          = -516
ERROR_C_OMS_MF_PLACE_SIP_ORDER              = -517

ERROR_C_MF_INV_AMOUNT               = -400
ERROR_C_MF_INV_REQUEST_TYPE         = -401
ERROR_C_MF_INV_SCHEME               = -402
ERROR_C_MF_INV_BUY_SELL_TYPE        = -405
ERROR_C_MF_INV_BUY_SELL             = -406
ERROR_C_MF_INV_QTY                  = -407
ERROR_C_MF_INV_ORDER_ID             = -408
ERROR_C_MF_INV_DATE                 = -409
ERROR_C_MF_INV_FREQUENCY            = -410
ERROR_C_MF_INV_INSTALLMENTS         = -411
ERROR_C_MF_INV_MANDATE_ID           = -412
ERROR_C_MF_INV_FOT_FLAG             = -413
ERROR_C_MF_INV_ORDER_STATUS         = -414
ERROR_C_MF_INV_PURCHASE_QTY         = -415
ERROR_C_MF_INV_INP_REDEEMALLUNITS   = -416
ERROR_C_MF_INV_AMOUNT_1             = -417
ERROR_C_MF_INV_START_DATE           = -418
ERROR_C_MF_INV_END_DATE             = -419
ERROR_C_MF_INV_SIP_FREQUENCY        = -420
ERROR_C_MF_INV_SIP_INSTALLMENTS     = -421
ERROR_C_MF_INV_ORDER_TYPE           = -422
ERROR_C_MF_INV_TRANSACTION_TYPE     = -423
ERROR_C_MF_INV_PAYMENT_MODE         = -424
ERROR_C_MF_INV_FOLIO_NO             = -425
ERROR_C_MF_INV_ORDER_VALIDITY       = -426
ERROR_C_MF_INV_PAYMENT_STATUS       = -427
ERROR_C_MF_INV_URL_MADATE			= -428
ERROR_C_MF_INV_IMG_MADATE			= -429
ERROR_C_MF_INV_TOKEN_ID				= -430
ERROR_C_MF_RESEND_EMAIL_FLAG		= -431
ERROR_C_MF_INV_MANDATE_TYPE         = -432

ERROR_C_INV_USER_PHONE_NO			= -433
ERROR_C_INV_USER_NAME				= -434
ERROR_C_S3_IMAGE_NOT_FOUND			= -435

SUCCESS_C_2 = 200	##success code value for all APIs - 20200724 - Khyati
ERROR_C_DEMO_USER = -357
ERROR_C_INV_OTP = -358

# EDIS - 20200722
ERROR_C_INV_ISIN					= -436
ERROR_C_EDIS_INV_REQ				= -437
ERROR_C_EDIS_RECORD_LST				= -438
ERROR_C_EDIS_INV_TXN_ID				= -439

RUPEE_SEED_ERROR                = -1041

#GTT Order
ERROR_C_GTT_ORDER_INFO = -701
ERROR_C_NO_LEG = -702
ERROR_C_NO_LEG_TO_MODIFY = -703

ERROR_C_S3_GET_FAILED = -440