from symbolmaster_handler import SYMBOL_MASTER_S3_TICKER

moduleName = "fy_common_internal_functions"
try:
    import sys
    import time
    import datetime
    import calendar
    import json

    from fy_base_success_error_codes import SUCCESS_C_1, ERROR_C_1, \
     ERROR_C_UNKNOWN, ERROR_C_INV_FYSYMBOL, ERROR_C_DB_NOT_FOUND, ERROR_C_DB_1, \
     ERROR_C_INV_EXCHANGE
    from fy_base_success_error_messages import ERROR_M_INV_EXCHANGE
    from fy_base_defines import LOG_STATUS_ERROR_1, CACHE_T_2
    from fy_data_and_trade_defines import CACHE_K_FNO_EX_WEEK_0, CACHE_K_FNO_EX_WEEK_1, \
     CACHE_K_FNO_EX_WEEK_2, CACHE_K_FNO_EX_WEEK_11, CACHE_K_FNO_EX_WEEK_12 ,\
     CACHE_K_FNO_EX_MNTH_0, CACHE_K_FNO_EX_MNTH_1, CACHE_K_FNO_EX_MNTH_2, \
     CACHE_K_FNO_EX_MNTH_11, CACHE_K_FNO_EX_MNTH_12, CACHE_K_SYM_DETAILS, EXCHANGE_NAME_NSE, \
     EXCHANGE_CODE_NSE, EXCHANGE_NAME_MCX_1, EXCHANGE_CODE_MCX, EXCHANGE_NAME_BSE, \
     EXCHANGE_CODE_BSE
    from fy_connections_defines import TBL_SYM_MASTER

    from fy_connections import connectRedis, dbConnect
    from fy_base_functions import logEntryFunc2

except Exception as e:
    print("ERR : %s : %s : %s" % (moduleName, "Could not import module", e))
    sys.exit()

startTime = time.time()
todayDate = datetime.datetime.now().date()
todayTimestamp = int(calendar.timegm(todayDate.timetuple()))
LOG_STR_INTERNAL_splitTokenString = "splitTokenString"


def getSymbolsFromSymbolMasterCache(inputSymbolsList, localMemory=None, callingFuncName=""):
    """
    This function will filter the symbols which are expired / invalid
    And give the details of all the symbols in input
    INPUTS: 
            inputSymbolsList : list of symbols
    RETURN:
            validSymbolList : list of symbols which are actually valid
            returnSymbolData : details of all the symbols in inputSymbolsList present in redis
    """
    funcName = "getSymbolsFromSymbolMasterCache"
    try:
        inputSymbolsList = list(inputSymbolsList)
        if localMemory == None:
            localMemory = connectRedis(callingFuncName=funcName)

        validSymbolList = []
        returnSymbolData = {}

        if len(inputSymbolsList) > 0:
            ##Check in symbol mapper redis key
            # fetchSymbolMap = abstract_hmget(inputSymbolsList)
            fetchSymbolMap = localMemory.hmget("symbol_master", inputSymbolsList)
            for i in range(len(fetchSymbolMap)):
                #If mapping present in redis
                if fetchSymbolMap[i] != None:
                    # data = fetchSymbolMap[i]
                    data = json.loads(fetchSymbolMap[i])
                    #Check Trade Status
                    if data["tradeStatus"] == 1:
                        validSymbolList.append(inputSymbolsList[i])
                    returnSymbolData[inputSymbolsList[i]] = data

        return [SUCCESS_C_1, [validSymbolList, returnSymbolData], ""]
        
    except Exception as e:
        logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, e)
        return [ERROR_C_1, ERROR_C_UNKNOWN, ""]


def INTERNAL_getSymExAndSegment(fyToken, callingFuncName=""):
    """
        [FUNCTION]
        INTERNAL_getSymExAndSegment :
        [PARAMS]
            fyToken : Unique code of fyers for each symbol => Format is %s%s%s %(exchange,segment,token)
        [RETURN]
            Success :
            Failure :
    """
    funcName = "INTERNAL_getSymExAndSegment"
    try:
        fyToken = str(fyToken)
        if len(fyToken) <= 10:
            return [ERROR_C_1, ERROR_C_INV_FYSYMBOL, ""]
        fyEx = fyToken[0:2]
        fySeg = fyToken[2:4]
        fyExpiry = fyToken[4:10]
        scripCode = fyToken[10:]
        return [SUCCESS_C_1, [fyEx, fySeg, scripCode,fyExpiry], ""]

    except Exception as e:
        logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, e)
        return (ERROR_C_1, ERROR_C_UNKNOWN, "")

def abstract_hmget(symbolList):
    return [SYMBOL_MASTER_S3_TICKER[key] for key in symbolList if key in SYMBOL_MASTER_S3_TICKER]


def INTERNAL_getScriptNameFromTicket(tickerInp):
    try:
        listExch = tickerInp.split(':')
        if len(listExch) <= 1:
            return [ERROR_C_1, ERROR_C_UNKNOWN, "Invalid ticker:%s" % (tickerInp)]
        listscript = listExch[1].split('-')
        if len(listscript) > 2:
            listscript = ["-".join(listscript[:-1]), listscript[-1]]
        return [SUCCESS_C_1, [listExch] + listscript, ""]
    except Exception as e:
        return [ERROR_C_1, ERROR_C_UNKNOWN, e]
    return [ERROR_C_1, ERROR_C_UNKNOWN, "Unknown"]


def internal_getExpiryForUnderlying(underlyingFyToken, expiryType, expiryTime, expiryAfter=0, db=None, cursor=None, localMemory=None, callingFuncName=""):
    """
    Get the desired expiry date in unix timestamp
        :param underlyingFyToken: The underlying symbol's fytoken. Eg: 101000000026000(Nifty50-Index)
        :param expiryType: Are you looking for weekly expiry or monthly expiry? 1-> Weekly; 2-> Monthly
        :param expiryTime: Which expiry do we want? 0-> Near; 1-> Next; 2-> Far; -1 -> Furthest expiry; -2 -> Second further expiry
        :param expiryAfter: Will look for expiry after the provided input date.
        :param db:
        :param cursor:
        :param localMemory:
        :param callingFuncName:

        :return:
            Success => [SUCCESS_C_1, expiryDate, ""]
            Error   => [ERROR_C_1, errorCode, "error message"]
    """
    funcName = "internal_getExpiryForUnderlying"
    try:
        ## Cache added to remove db hits 20190925 Palash
        if localMemory == None:
            localMemory = connectRedis()

        ##Cache Key changes - 20200212 - Khyati
        cacheFunRet = createCacheKeyFno(underlyingFyToken, expiryType, expiryTime)
        if cacheFunRet[0] != ERROR_C_1:
            cacheKey = cacheFunRet[1]
        else:
            return cacheFunRet

        cacheDataList = localMemory.get(cacheKey)
        if cacheDataList is not None:
            cacheDataList = json.loads(cacheDataList)
            return [SUCCESS_C_1, cacheDataList, ""]
        else:
            logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, underlyingFyToken, expiryType, expiryTime, expiryAfter, cacheKey, "watchlist expiry not found in redis")
            return [ERROR_C_1, "", ""]

    except Exception as e:
        exc_type, exc_obj, tb = sys.exc_info()
        logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, e, ERROR_C_UNKNOWN, "Line No: " % tb.tb_lineno)
        return [ERROR_C_1, ERROR_C_UNKNOWN, ""]


## Create new cache keys based on expiryType and expiryTime for fno predefined watchlists - as previously the keys were duplicated for some lists - 20200212 - Khyati
def createCacheKeyFno(underlyingFyToken, expiryType, expiryTime):
    funcName = "createCacheKeyFno"
    try:
        if expiryType == 1:
            if expiryTime == 0:
                cacheKey = "%s%s" % (underlyingFyToken, CACHE_K_FNO_EX_WEEK_0)
            elif expiryTime == 1:
                cacheKey = "%s%s" % (underlyingFyToken, CACHE_K_FNO_EX_WEEK_1)
            elif expiryTime == 2:
                cacheKey = "%s%s" % (underlyingFyToken, CACHE_K_FNO_EX_WEEK_2)
            elif expiryTime == -1:
                cacheKey = "%s%s" % (underlyingFyToken, CACHE_K_FNO_EX_WEEK_11)
            elif expiryTime == -2:
                cacheKey = "%s%s" % (underlyingFyToken, CACHE_K_FNO_EX_WEEK_12)
        elif expiryType == 2:
            if expiryTime == 0:
                cacheKey = "%s%s" % (underlyingFyToken, CACHE_K_FNO_EX_MNTH_0)
            elif expiryTime == 1:
                cacheKey = "%s%s" % (underlyingFyToken, CACHE_K_FNO_EX_MNTH_1)
            elif expiryTime == 2:
                cacheKey = "%s%s" % (underlyingFyToken, CACHE_K_FNO_EX_MNTH_2)
            elif expiryTime == -1:
                cacheKey = "%s%s" % (underlyingFyToken, CACHE_K_FNO_EX_MNTH_11)
            elif expiryTime == -2:
                cacheKey = "%s%s" % (underlyingFyToken, CACHE_K_FNO_EX_MNTH_12)
        return [SUCCESS_C_1, cacheKey, ""]
    except Exception as e:
        logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, "", e, ERROR_C_UNKNOWN)
        return [ERROR_C_1, ERROR_C_UNKNOWN, ""]


def INTERNAL_getSymbolTickersForFyTokensList(inputTokenList, db=None, cursor=None, localMemory=None, callingFuncName=""):
    """
        [FUNCTION]
        INTERNAL_getSymbolTickersForFyTokensList :
        [PARAMS]
            inputTokenList : List of symbols for which we want fy_token
        [RETURN]
            Success : [SUCCESS_C_1,["inputTicker":"fy_token"],""]
            Failure : [ERROR_C_1,errorCode,errorMessage]
    """
    funcName = "INTERNAL_getSymbolTickersForFyTokensList"
    try:
        if localMemory == None:
            localMemory = connectRedis(callingFuncName=callingFuncName)
        inputTokenListCount = len(inputTokenList)
        fyTokenList = {}
        getDBTokensList = []
        valueList = localMemory.mget(inputTokenList)
        for tokenIndex in range(0, len(valueList)):
            if valueList[tokenIndex] == None:
                getDBTokensList.append(inputTokenList[tokenIndex])
            else:
                fyTokenList[inputTokenList[tokenIndex]] = valueList[tokenIndex].decode("utf-8")

        if fyTokenList != {}:
            if len(fyTokenList) == len(inputTokenList):
                return [SUCCESS_C_1, fyTokenList, ""]

        symbolsString = ""
        for i in getDBTokensList:
            symbolsString += "'%s'," % (i)
        symbolsString = symbolsString[:-1]
        sqlQuery = "SELECT FY_TOKEN,SYMBOL_TICKER FROM `%s` WHERE FY_TOKEN IN (%s);" % (
        TBL_SYM_MASTER, symbolsString)

        if db == None or cursor == None:
            db, cursor = dbConnect(dbType=3, readOnly=1, callingFuncName=callingFuncName)
            if db == None or cursor == None:
                return [ERROR_C_1, ERROR_C_DB_NOT_FOUND, ""]

        try:
            cursor.execute(sqlQuery)
            symbolTokens = cursor.fetchall()
            if symbolTokens == ():
                # If we did not receive any data from cache and db, then we will return an error
                if len(fyTokenList) <= 0:
                    return [ERROR_C_1, ERROR_C_DB_NOT_FOUND, ""]
                else:
                    # We will return success with whatever tokens we have data for
                    return [SUCCESS_C_1, fyTokenList, ""]

            for i in symbolTokens:
                try:
                    fyTokenList[str(i[0])] = "%s" % (i[1])
                    localMemory.set(str(i[0]), str(i[1]), CACHE_T_2)
                except Exception as e:
                    logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, e, ERROR_C_UNKNOWN, i)
                    continue
            return [SUCCESS_C_1, fyTokenList, ""]
        except Exception as e:
            logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, e, ERROR_C_UNKNOWN, inputTokenList)
            return [ERROR_C_1, ERROR_C_DB_1, e]

    except Exception as e:
        logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, e, ERROR_C_UNKNOWN, inputTokenList)
        return [ERROR_C_1, ERROR_C_UNKNOWN, ""]


def INTERNAL_checkSymbolNameOrToken(symbol, db=None, cursor=None, localMemory=None, callingFuncName=""):
    funcName = "INTERNAL_checkSymbolNameOrToken"
    try:
        symbol = str(symbol)
        if localMemory == None:
            localMemory = connectRedis(callingFuncName=callingFuncName)
        returnListJson = localMemory.get("%s%s" % (symbol, CACHE_K_SYM_DETAILS))
        if returnListJson != None:
            return [SUCCESS_C_1, json.loads(returnListJson), ""]

        # Check if the input is an integer
        if symbol.isdigit() == True:
            sqlQuery = "SELECT FY_TOKEN,SYM_DETAILS,EX_SYMBOL_NAME FROM `%s` WHERE FY_TOKEN = %s AND TRADE_STATUS = 1" % (
                TBL_SYM_MASTER, symbol)

        # If not an integer
        else:
            # Check if the format is Exchange:Symbolname. For example, NSE:RELIANCE-EQ
            if ":" in symbol:
                symbolSplitList = symbol.split(":")
                if symbolSplitList[0] == EXCHANGE_NAME_NSE:
                    exCode = EXCHANGE_CODE_NSE
                elif symbolSplitList[0] == EXCHANGE_NAME_MCX_1:
                    exCode = EXCHANGE_CODE_MCX
                elif symbolSplitList[0] == EXCHANGE_NAME_BSE:
                    exCode = EXCHANGE_CODE_BSE
                else:
                    return [ERROR_C_1, ERROR_C_INV_EXCHANGE, ERROR_M_INV_EXCHANGE]
            else:
                return [ERROR_C_1, ERROR_C_INV_FYSYMBOL, ""]

            # Db query in case the input is a string in the desired format
            sqlQuery = "SELECT FY_TOKEN,SYM_DETAILS,EX_SYMBOL_NAME FROM `%s` WHERE SYMBOL_TICKER = '%s' AND TRADE_STATUS = 1 AND EX = %s;" % (
                TBL_SYM_MASTER, symbol, exCode)

        # Here we are checking whether the passed parameters are None. If it is none, we will make a fresh db connection
        if db == None or cursor == None:
            db, cursor = dbConnect(dbType=3, readOnly=1, callingFuncName=callingFuncName)
            # Even after a new db connection, if we get none, then we will return an error
            if db == None or cursor == None:
                return [ERROR_C_1, ERROR_C_DB_1, ""]
        cursor.execute(sqlQuery)
        fyTokenTuple = cursor.fetchall()

        if fyTokenTuple == ():
            return [ERROR_C_1, ERROR_C_INV_FYSYMBOL, ""]
        returnList = [int(fyTokenTuple[0][0]), fyTokenTuple[0][1], fyTokenTuple[0][2]]
        localMemory.set("%s%s" % (symbol, CACHE_K_SYM_DETAILS), json.dumps(returnList), CACHE_T_2)
        return [SUCCESS_C_1, returnList, ""]

    except Exception as e:
        logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName,e, ERROR_C_UNKNOWN, symbol)
        return [ERROR_C_1, ERROR_C_UNKNOWN, ""]


def main():
    None


if __name__ == "__main__":
    main()
