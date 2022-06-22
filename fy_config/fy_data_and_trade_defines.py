
# Symbol related defines
EXCHANGE_CODE_NSE 		= 10
EXCHANGE_CODE_MCX 		= 11
EXCHANGE_CODE_BSE       = 12
EXCHANGE_NAME_NSE 		= "NSE"
EXCHANGE_NAME_MCX_1     = "MCX"
EXCHANGE_NAME_BSE 		= "BSE"
EXCHANGE_NAME_NSE_CM     = "NSE"
EXCHANGE_NAME_NSE_FO     = "NFO"
EXCHANGE_NAME_NSE_CD     = "CDS"
EXCHANGE_FULLNAME_NSE 	= "National Stock Exchange"
EXCHANGE_SEGMENT_NFO   = "NFO"
EXCHANGE_SEGMENT_CDS   = "CDS"
EXCHANGE_INST_TYPE_FUTURES = "FUTURES"
EXCHANGE_INST_TYPE_OPTIONS = "OPTIONS"
OPTION_TYPE_CE          = "CE"
OPTION_TYPE_PE          = "PE"




# Symbol Details
SYM_ADDITIONAL_PADDING = "000000"

# Segment of the instrument
SYM_SEGMENT_CM = 10
SYM_SEGMENT_FO = 11
SYM_SEGMENT_CD = 12
SYM_SEGMENT_COM = 20

# Segment Name
SEGMENT_NAME_CM = 'CM'
SEGMENT_NAME_CD = 'CD'
SEGMENT_NAME_FO = 'FO'
SEGMENT_NAME_COM = 'COM'


# Instrument Types
SYM_INSTTYPE_SYMBOL = 10
SYM_INSTTYPE_INDEX 	= 11
# 	Cm Segments -
SYM_INSTTYPE_EQ 		  = 0
SYM_INSTTYPE_PREFSHARES	  = 1
SYM_INSTTYPE_DEBENTURES	  = 2
SYM_INSTTYPE_WARRANTS 	  = 3
SYM_INSTTYPE_MISC	 	  = 4
SYM_INSTTYPE_INDEX_2 	  = 10
# 	Fo segments
SYM_INSTTYPE_FUTIDX = 11
SYM_INSTTYPE_FUTIVX = 12
SYM_INSTTYPE_FUTSTK = 13
SYM_INSTTYPE_OPTIDX = 14
SYM_INSTTYPE_OPTSTK = 15
# 	Cd segments
SYM_INSTTYPE_FUTCUR = 16
SYM_INSTTYPE_FUTIRT = 17
SYM_INSTTYPE_FUTIRC = 18
SYM_INSTTYPE_OPTCUR = 19
SYM_INSTTYPE_UNDCUR = 20
SYM_INSTTYPE_UNDIRC = 21
SYM_INSTTYPE_UNDIRT = 22
SYM_INSTTYPE_UNDIRD = 23
SYM_INSTTYPE_INDEX_CD  = 24

#   COM segment
SYM_INSTTYPE_FUTCOM = 30
SYM_INSTTYPE_FUTOPT = 31


# Cache keys
CACHE_K_LEVEL2DATA 				= "-2001-"
CACHE_K_SYM_MIN_DATA 			= "-1005-"
CACHE_K_SYM_MIN_DATA_TODAY	 	= "-2003-"
CACHE_K_SYM_EOD_DATA_10DAYS 	= "-1011-"
CACHE_K_SYM_TICKER	 			= "-1009"
CACHE_K_SYM_TICKERONLY			= "-1028"
CACHE_K_SYM_DETAILS				= "-1008"
CACHE_K_SYM_INFO			 	= "-1027"
CACHE_K_SYM_INFO_1 				= "-1127"
CACHE_K_SYM_INFO_2 				= "-1128"
CACHE_K_OMS_DETAILS				= "-1100"
CACHE_K_OMS_ALLDETAILS		 	= "-1101"
CACHE_K_OMS_REAUTH_DETAILS	    = "-1102"
CACHE_K_OMS_FEW_DETAILS		 	= "-1103"
CACHE_K_SYM_MIN_QTY_DICT_1      = "-1104"
CACHE_K_SYM_INFO_DICT_1         = "-1105"
CACHE_K_SYM_INFO_DICT_2         = "-1110"
CACHE_K_WL_NIFTYFUT             = "NiftyNearFut-6105" ## Key changed from 6101 to 6105 while setting wl through cron
CACHE_K_WL_BANKNIFTYFUT         = "BankNiftyNearFut-6106" ## Key changed from 6102 to 6106 while setting wl through cron
CACHE_K_WL_CURRFUT              = "CurrencyNearFut-6107" ## Key changed from 6103 to 6107 while setting wl through cron
CACHE_K_WL_MCXFUT               = "MCXNearFut-6108" ## Key changed from 6104 to 6108 while setting wl through cron
CACHE_K_HIGHLOW                 = "-7007-"## Palash 20190520 High low api widget
CACHE_K_HIGHLOW_CONT_FUT        = "-7008-"## Palash 20190521 High low api widget
CACHE_K_FUTCHAIN                = "-7009-"## Palash 20190522 Futures chain api
CACHE_K_CONT_FUT_EOD            = "-5001" #Palash 20190123
CACHE_K_CONT_FUT_1MIN           = "-5002" #Palash 20190123
CACHE_K_TICK_DATA				= "-2004-"## Palash 20190604 Time and sales cache key
CACHE_K_CORP_ACTION             = "-5003" #Pragya 20190308
CACHE_K_CIRCUIT_VAL             = "-7005-"#Palash 20190509 - For Depth Box
CACHE_K_OHLCV_DATA              = "-7006-"#Palash 20190509 - For level 2 data multi sym
CACHE_K_UNDERLYING_EXP_WL       = "-6005"

CACHE_K_SPAN_CALC_SYMBOLS       = "-3001"

CACHE_K_WATCHLIST_PREDEFINED_FNO = "-3202" ## Key changed from 3102 to 3202 while setting wl through cron

## Cache Key for mobile chart symbol 20190925 Palash
CACHE_K_MOB_CHART_SYM           = "-6006"

SECONDS_1970_1980 = 315532800

BEWARE_CLIENTS_LIST 			= ["UK522","UK524","UK525","UK526","UK527","UK528","UK529"] ## Add later "FS0318",
# "FK0094" removed - 20210429

FY_SYMBOL_MAPPING = {"nifty50" : "nifty", "niftybank" : "banknifty", "niftymidcap50":"niftymid50"}

## Corp Action List 20190311 - Pragya
CORP_ACTION_LIST = ['S', 'B', 'D', 'R', '']

## watchlist move to lamdba - 20200120
# ## Save user watchlist to s3 - Khyati
# FILE_USER_WATCHLIST_CODE = "-9002-"
# FILE_USER_WATCHLIST_VALUE = "userWatchList.txt"
## Watchlists redis expiry
CACHE_WATCHLIST_EXPIRY = 43200

CACHE_KEY_PREDEF_WL_EXPIRY = 43200

##Cache Keys fno lists - 20200212 - Khyati
# EX TYPE = 1 (WEEK)
CACHE_K_FNO_EX_WEEK_0   = "-6206"
CACHE_K_FNO_EX_WEEK_1   = "-6306"
CACHE_K_FNO_EX_WEEK_2   = "-6406"
CACHE_K_FNO_EX_WEEK_11  = "-6506"
CACHE_K_FNO_EX_WEEK_12  = "-6606"
# EX TYPE = 2 (MONTH)
CACHE_K_FNO_EX_MNTH_0   = "-7206"
CACHE_K_FNO_EX_MNTH_1   = "-7306"
CACHE_K_FNO_EX_MNTH_2   = "-7406"
CACHE_K_FNO_EX_MNTH_11  = "-7506"
CACHE_K_FNO_EX_MNTH_12  = "-7606"
# Keys changed to -*06 while setting wl through cron

# Pragya MF - (20200710)
CACHE_K_MF_NAV_VALUES           = "_5004_"#Pragya 20191015 - For nav values in order book for mutual funds transaction apis
CACHE_K_MF_BSE_SCHEME_DATA		= "_5005_"#Pragya 20191129 - For bse scheme data in order due report for mutual funds transaction apis
CACHE_K_MF_OMS_AUTH				= "_5006"#Pragya 20191210 - For fetching user details from oms_auth db

CACHE_K_MOB_APP_VER		= "appVer-1000"
GUEST_CLIENT_ID = ["ZZ0001","ZZ0002","ZZ0003","ZZ0004"]
FCM_TOPIC_DEMO_USER = "user-demo"
FCM_TOPIC_FYERS_USER = "user-fyers"

REQ_TYPE_DASHBOARD	= 1
REQ_TYPE_ALERT_SERVER	= 2
ALL_NOTIF_REQ_TYPES = [REQ_TYPE_DASHBOARD,REQ_TYPE_ALERT_SERVER]

CACHE_K_FCM_TOKEN	= "-5600-FCM-TOKEN"

MAX_NUMBER_BASKETS = 10
MAX_NUMBER_BASKETS_ITEMS = 20

CUSTOM_WATCHLISTS_KEY = "custom-watchlist-key"
