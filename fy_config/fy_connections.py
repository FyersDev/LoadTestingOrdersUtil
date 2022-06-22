moduleName = "fy_connections"
try:
    import pymysql
    import sys
    import redis

except Exception as e:
    print("ERR : %s : %s : %s" % (moduleName, "Could not import module", e))

try:
    from fy_config.fy_connections_defines import CACHE_REDIS_1_URL, \
     CACHE_REDIS_TRADING, FYERS_DB_READER, FYERS_DB_WRITER, MYSQL_CONNECTION_PORT, \
     DB_TRADE_MOB_USER, DB_TRADE_MOB_PWD, REDIS_CONNECTION_PORT
    from fy_config.fy_base_defines import LOG_STATUS_ERROR_1
    from fy_config.fy_base_success_error_codes import ERROR_C_UNKNOWN, ERROR_C_DB_1
    from fy_config.fy_data_and_trade_defines import EXCHANGE_CODE_MCX, SYM_SEGMENT_COM, \
     EXCHANGE_CODE_BSE

    from fy_config.fy_base_functions import logEntryFunc2

except Exception as e:
    print("ERR : %s : %s : %s" % (moduleName, "Could not import module", e))
    sys.exit()


class rConn():
    redPool = redis.ConnectionPool(host=CACHE_REDIS_1_URL, port=6379, db=0)


def connectRedis(redisEP=CACHE_REDIS_1_URL, port=6379, db=0, callingFuncName=""):
    """
    [Function]  :   This will connect to redis instance and return radis_instance
    [Input]     :   redisEP     -> End point of redis cluster.
                    port        -> Port of radis cluster
                    db          -> Db ssociated with it.
    [Output]    :   Fail: {comnDef.K_FUNCT_STAT : comnDef.V_FUNCT_FAIL_N_1, comnDef.K_FUN_DATA:[], comnDef.K_ERR_MSG:"Error message"}
                    Success: {comnDef.K_FUNCT_STAT : comnDef.V_FUNCT_SUCCESS_1, , comnDef.K_FUN_DATA:[], comnDef.K_ERR_MSG:"name of the service connected"}
    """
    funcName = "connectRedis"

    try:        
        CACHE_REDIS_TRADING.ping()
        return CACHE_REDIS_TRADING

    except redis.ConnectionError:
        logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, e,ERROR_C_UNKNOWN,redisEP)
        CACHE_REDIS_TRADING_RECONNECT = redis.Redis(CACHE_REDIS_1_URL, REDIS_CONNECTION_PORT)
        return CACHE_REDIS_TRADING_RECONNECT


def dbConnect(dbType=0, exchange=0, segment=0, readOnly=1, callingFuncName=""):
    """
    dbType == 1 => eodData
    dbType == 2 => 1minData
    dbType == 3 => tradingApi
    readOnly == 1 => Connect to read-replica
    readOnly == 0 => Connect to normal DB
    """
    funcName = "dbConnect"
    if dbType == 0:
        logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, "Invalid dbType",
                      ERROR_C_DB_1, dbType, exchange, segment, readOnly)
        return None, None
    dbName = ""
    if dbType == 1:
        if exchange == 10:
            if segment == 1:
                dbName = "fyers_eod_data_nse_cm"
            elif segment == 2:
                dbName = "fyers_eod_data_nse_fo"
            elif segment == 3:
                dbName = "fyers_eod_data_nse_cd"
            else:
                logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, "Unknown segment",
                              ERROR_C_DB_1, dbType, exchange, segment, readOnly)
                return None, None
        ## ************** New Ajay 2018-09-03 **************
        elif exchange == EXCHANGE_CODE_MCX:
            if segment == SYM_SEGMENT_COM:
                dbName = "fyers_eod_data_mcx_v1"
            else:
                logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, "Unknown segment", ERROR_C_DB_1, exchange, segment)
                return None, None
        ## ************** END:New Ajay 2018-09-03 **************
        ## ************** Edit for BSE 20190529 - Palash **************
        elif exchange == EXCHANGE_CODE_BSE:
            if segment == 1:
                dbName = "fyers_eod_data_bse_cm_v1"
            elif segment == 2:
                dbName = "fyers_eod_data_bse_fo_v1"
            elif segment == 3:
                dbName = "fyers_eod_data_bse_cd_v1"
            else:
                logEntryFunc2(LOG_STATUS_ERROR_1, moduleName,
                              funcName, callingFuncName, "Unknown segment", ERROR_C_DB_1, exchange, segment)
                return None, None
        ## ************** END::Edit for BSE 20190529 - Palash **************
        else:
            logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, "Unknown exchange",
                          ERROR_C_DB_1, dbType, exchange, segment, readOnly)
            return None, None
    elif dbType == 2:
        if exchange == 10:
            if segment == 1:
                dbName = "fyers_1min_data_nse_cm"
            elif segment == 2:
                dbName = "fyers_1min_data_nse_fo"
            elif segment == 3:
                dbName = "fyers_1min_data_nse_cd"
            else:
                logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, "Unknown segment",
                              ERROR_C_DB_1, dbType, exchange, segment, readOnly)
                return None, None
        ## ************** New Ajay 2018-09-03 **************
        elif exchange == EXCHANGE_CODE_MCX:
            if segment == SYM_SEGMENT_COM:
                dbName = "fyers_1min_data_mcx_v1"
            else:
                logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, "Unknown segment", ERROR_C_DB_1, exchange, segment)
                return None, None
        ## ************** END: New Ajay 2018-09-03 **************
        ## ************** Change for bse 20190529 - Palash **************
        elif exchange == EXCHANGE_CODE_BSE:
            if segment == 1:
                dbName = "fyers_1min_data_bse_cm_v1"
            elif segment == 2:
                dbName = "fyers_1min_data_bse_fo_v1"
            elif segment == 3:
                dbName = "fyers_1min_data_bse_cd_v1"
            else:
                logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, "Unknown segment", ERROR_C_DB_1, exchange, segment)
                return None, None
        ## ************** END::Change for bse 20190529 - Palash **************
        else:
            logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, "Unknown exchange",
                          ERROR_C_DB_1, dbType, exchange, segment, readOnly)
            return None, None
    elif dbType == 3:
        dbName = "fyers_trading_bridge"
    elif dbType == 4:  # New Change for doodleblue api integration - Palash 20190506
        dbName = "fyers_api"
    else:
        logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, "Invalid dbType",
                      ERROR_C_DB_1, dbType, exchange, segment, readOnly)
        return None, None

    connection = ""
    if readOnly == 1:
        connection = FYERS_DB_READER
    else:
        connection = FYERS_DB_WRITER
    connectionPort = MYSQL_CONNECTION_PORT
    uName = "fy_dbmaster_1329"
    passwd = "fyersDbAdmin1329"

    try:
        db = pymysql.connect(host=connection, user=DB_TRADE_MOB_USER, passwd=DB_TRADE_MOB_PWD, db=dbName, port=connectionPort)
        cursor = db.cursor()
        return db, cursor
    except Exception as e:
        logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, e,
                      ERROR_C_UNKNOWN, dbType, exchange, segment, readOnly)
        None
    return None, None
