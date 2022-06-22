
# Table names
TBL_SYM_MASTER_NSE 		= "nse_symbol_master"
TBL_SYM_MASTER 			= "symbol_master"
TBL_OMS_AUTH_V1			= "fyers_oms_auth"
# TBL_OMS_AUTH_V2 		= "fyers_oms_auth_v2"
TBL_OMS_AUTH_V2 		= "fyers_oms_auth_v4"
TBL_USER_CHART_LAYOUT   = "save_chart_layout"
TBL_USER_WATCHLIST	 	= "user_watchlist"
TBL_OLD_NEW_TOKENS 		= "fy_oldtokens_newtokens"
TBL_TEMP_CHANGEPWD 		= "fy_change_pwd_temp_v1"
TBL_FYERS_OFFER_1       = "fy_offer_1"
# TBL_USER_WATCHLIST_2    = "user_watchlist_v1"
TBL_USER_WATCHLIST_2    = "user_watchlist_v2"

TBL_GUEST_USER = "fyers_guest_users"

TBL_COL_LOGIN_FAIL 		= "ERR_COUNT"
TBL_COL_FYERS_ID 		= "FY_ID"


AWS_ACCESS_KEY 					= "AKIAJSY34JQX3URXV72Q"
AWS_SECRET_KEY 					= "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"
AWS_SERVICE_S3    				= "s3"
AWS_S3_FOLDER_PATH_USER_CHARTS 	= "userCharts"
AWS_S3_BUCKET_NAME_USER_CHARTS 	= "fyers.save.chart.v1"

## Snapshot gallery defines 20190614 Palash
AWS_SERVICE_CLOUDFRONT = "cloudfront"
AWS_SNAPSHOT_DIST_ID = "E2V6G1VHAFBANV"
AWS_S3_SNAPSHOT_FOLDER_PATH     = "snapshot"
AWS_S3_SNAPSHOT_BUCKET_NAME     = "user-chart-snapshot"
AWS_S3_SNAPSHOT_BUCKET_URL_PREFIX = "https://charts.fyers.in/"

# Ports
MYSQL_CONNECTION_PORT = 3306
REDIS_CONNECTION_PORT = 6379

# Used for Db Aes Encryption
FY_ENCRYPT_DB_AESKEY_1 		= "fyAuth91537"

# Connection End Points
# CACHE_REDIS_1_URL           = "fyers-trading-redis.jb5agw.0001.aps1.cache.amazonaws.com"
CACHE_REDIS_1_URL			= "fyers-trading-redis.jb5agw.ng.0001.aps1.cache.amazonaws.com" ##new
# CACHE_REDIS_1_URL           = "127.0.0.1"
# CACHE_REDIS_1_URL           = "fyers-testing-redis.jb5agw.ng.0001.aps1.cache.amazonaws.com"

FYERS_DB_WRITER = "fyers-trading-db-cluster.cluster-cvghve20lauv.ap-south-1.rds.amazonaws.com"
FYERS_DB_READER = "fyers-trading-db-cluster.cluster-ro-cvghve20lauv.ap-south-1.rds.amazonaws.com"

DB_TRADE_WEB_USER = "fy_tradeweb_user"
DB_TRADE_WEB_PWD = "Zf3c2HHV2y93X9Lg"
DB_TRADE_MOB_USER = "fy_trademob_user"
DB_TRADE_MOB_PWD = "qfepPSAgvH5aPCqg"
DB_TRADE_API_USER = "fy_extapi_user"
DB_TRADE_API_PWD = "SY2U8y5MwHG54tdr"

DB_TRADING_BRIDGE 				= "fyers_trading_bridge"
DB_1MIN_NSE_CM					= "fyers_1min_data_nse_cm_v4"
DB_1MIN_NSE_FO					= "fyers_1min_data_nse_fo_v1"
DB_1MIN_NSE_CD					= "fyers_1min_data_nse_cd_v1"
DB_EOD_NSE_CM					= "fyers_eod_data_nse_cm_v2"
DB_EOD_NSE_FO					= "fyers_eod_data_nse_fo_v1"
DB_EOD_NSE_CD					= "fyers_eod_data_nse_cd_v1"

DB_1MIN_MCX_COM					= "fyers_1min_data_mcx_v1"
DB_EOD_MCX_COM					= "fyers_eod_data_mcx_v1"

DB_1MIN_BSE_CM					= "fyers_1min_data_bse_cm_v1"
DB_EOD_BSE_CM					= "fyers_eod_data_bse_cm_v1"

# ##Watchlist Bucket and path - 20200120 - Khyati
# AWS_S3_BUCKET_NAME_WATCHLIST        = "fyers.user.watchlist.v1"
# AWS_S3_FOLDER_PATH_USER_WATCHLIST   = "UserWatchlists/"
# AWS_S3_FOLDER_PATH_PREDEF_WATCHLIST = "PredefinedLists/"
# AWS_S3_FOLDER_PATH_WATCHLIST_INDICES = AWS_S3_FOLDER_PATH_PREDEF_WATCHLIST + "NiftyIndicesList.txt"

AWS_S3_BUCKET_USER_DATA = "fyers-user-data"
AWS_S3_FOLDER_PATH_PREDEF_WATCHLIST = "watchlist-v1/PredefinedLists/"
AWS_S3_FOLDER_PATH_USER_WATCHLIST   = "watchlist-v1/UserWatchlists/"
FILE_USER_WATCHLIST_SUFFIX = "-watchlist-v1.txt"
AWS_S3_FOLDER_PATH_WATCHLIST_INDICES = AWS_S3_FOLDER_PATH_PREDEF_WATCHLIST + "NiftyIndicesList.txt"

AWS_S3_FOLDER_PATH_USERSETTINGS = "settings-v1/"
FILE_USER_SETTINGS_SUFFIX = "-settings-v1.txt"

##User Baskets
AWS_S3_FOLDER_PATH_USER_BASKETS = "userBaskets-v1/"
FILE_USER_BASKETS_SUFFIX = "-baskets-v1.txt"

# 20200730 - Khyati
TBL_MOB_APP_VER		= "fy_mobile_app_versions"

# Pragya (20200710)
DB_MF_MASTER                    = "fyers_mf_master_v1"
TBL_MF_CURRENT_NAV              = "nav"
TBL_MF_SCHEME_MASTER_DETAILS    = "scheme_master_details"

S3_BUCKET_NAME_MANDATE_DOWNLOAD = "direct-mandate-image"
S3_FOLDER_NAME_MANDATE_DOWNLOAD = "mf-download-mandate"

MAIL_SERVER = "smtp.sendgrid.net"
MAIL_PORT = 587
MAIL_USE_SSL = False
MAIL_FROM = "no-reply@fyers.in"
MAIL_USERNAME = "apikey"
MAIL_PASSWORD = "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"
MAIL_SUBJECT = "FYERS Direct - Mutual Fund Mandate Registration"

S3_IMAGE_FOLDER = 'image/'
S3_USER_DETAILS_BUCKET = 'fyers-user-details'

TBL_PUSH_NOTIF = "fyers_push_notifications"

# Redis caching
import redis
CACHE_REDIS_TRADING = redis.Redis(CACHE_REDIS_1_URL, REDIS_CONNECTION_PORT)

# Define boto3 S3 connection
import boto3
AWS_BOTO3_S3_CONNECTION = boto3.client(AWS_SERVICE_S3)