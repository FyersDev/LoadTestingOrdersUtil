moduleName = "fy_data_internal_functions"
try:
    import sys
    import time
    import json

    from fy_base_defines import LOG_STATUS_ERROR_1, CACHE_T_3
    from fy_base_success_error_codes import ERROR_C_1, SUCCESS_C_1, ERROR_C_UNKNOWN, \
     ERROR_C_DB_1
    from fy_base_success_error_messages import ERROR_M_UNKNOWN_1
    from fy_data_and_trade_defines import CACHE_K_LEVEL2DATA, EXCHANGE_CODE_NSE, \
     SYM_SEGMENT_CM, FY_SYMBOL_MAPPING, SYM_SEGMENT_FO, SYM_SEGMENT_CD, EXCHANGE_CODE_MCX, \
     SYM_SEGMENT_COM, EXCHANGE_CODE_BSE
    from fy_connections_defines import DB_EOD_NSE_CM, DB_EOD_NSE_FO, DB_EOD_NSE_CD, \
     DB_EOD_MCX_COM, DB_EOD_BSE_CM
    from fy_common_api_keys_values import API_K_DATA_PRICE_CHANGE, API_K_DATA_PERC_CHANGE, \
     API_K_DATA_LTP
    
    from fy_connections import connectRedis, dbConnect
    from fy_common_internal_functions import INTERNAL_getSymExAndSegment, \
     INTERNAL_getScriptNameFromTicket
    from fy_base_functions import logEntryFunc2

except Exception as e:
    print("ERR : %s : %s : %s" % (moduleName, "Could not import module", e))
    sys.exit()


def INTERNAL_getL1PricesForFyTokenDict_1(fyTokenDict, db=None, cursor=None, localMemory=None, callingFuncName="", fytokenToTicker=False):
    """
        [FUNCTION]
        INTERNAL_getTokenForInputSymbols :
        [PARAMS]
            inputTokenList : List of symbols for which we want fy_token
        [RETURN]
            Success : [SUCCESS_C_1,['inputTicker':'fy_token'],""]
            Failure : [ERROR_C_1,errorCode,errorMessage]
    """
    funcName = "INTERNAL_getL1PricesForFyTokenDict"
    try:
        if localMemory == None:
            localMemory = connectRedis(callingFuncName=callingFuncName)
        todayTimestamp = int(time.time())
        todayTimestamp = todayTimestamp - (todayTimestamp % 86400)
        todayTimestamp = int(todayTimestamp)
        if fytokenToTicker:
            fyTokenList = list(fyTokenDict.keys())
        else:
            fyTokenList = list(fyTokenDict.values())
        l2SymbolKeysList = ["%s%s%s" % (i, CACHE_K_LEVEL2DATA, todayTimestamp) for i in fyTokenList]

        l2Dict = {}
        l2Val = localMemory.mget(l2SymbolKeysList)
        for eachKey in range(0, len(l2SymbolKeysList)):
            if l2Val[eachKey] != None:
                l2Dict[fyTokenList[eachKey]] = l2Val[eachKey]
        
        l2DictSymbols = list(l2Dict.keys())

        # If we have l2data is lesser than inputDict, then we will check for which symbol we did not get data
        if len(l2Dict) < len(fyTokenDict):
            dbName = None

            keyList, valList = [], []  # this is done because we need to map the token depending on the value in dict
            for eachItem in fyTokenDict:
                if fytokenToTicker:
                    keyList.append(fyTokenDict[eachItem])
                    valList.append(eachItem)
                else:
                    keyList.append(eachItem)
                    valList.append(fyTokenDict[eachItem])


            # Looping through the l2SymbolKeysList to see which key is missing
            for i in l2SymbolKeysList:
                if i in l2Dict:
                    continue
                # We need to split on '-' because the l2SymbolKey is fytoken-timestamp.
                fyToken = i.split('-')
                fyToken = fyToken[0]
                tableName = fyToken  # For CM the table name will change

                fyExSeg = INTERNAL_getSymExAndSegment(fyToken,callingFuncName=callingFuncName)
                if fyExSeg[0] == ERROR_C_1:
                    continue

                # Connect to the necessary db
                try:
                    if int(fyExSeg[1][0]) == int(EXCHANGE_CODE_NSE):
                        if int(fyExSeg[1][1]) == (SYM_SEGMENT_CM):
                            tickerName = keyList[valList.index(fyToken)]
                            retScrip = INTERNAL_getScriptNameFromTicket(tickerName)
                            if retScrip[0] != SUCCESS_C_1:
                                logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, retScrip[2], ERROR_C_UNKNOWN)
                                continue
                            else:
                                tableName = retScrip[1][1].lower()
                                if tableName in FY_SYMBOL_MAPPING.keys():
                                    tableName = FY_SYMBOL_MAPPING[tableName]
                                dbName = DB_EOD_NSE_CM
                        elif int(fyExSeg[1][1]) == (SYM_SEGMENT_FO):
                            dbName = DB_EOD_NSE_FO
                            tableName = fyToken
                        elif int(fyExSeg[1][1]) == (SYM_SEGMENT_CD):
                            dbName = DB_EOD_NSE_CD
                            tableName = fyToken
                        else:
                            continue
                    elif int(fyExSeg[1][0]) == int(EXCHANGE_CODE_MCX):
                        if int(fyExSeg[1][1]) == int(SYM_SEGMENT_COM):
                            dbName = DB_EOD_MCX_COM
                            tableName = fyToken
                        else:
                            continue
                    elif int(fyExSeg[1][0]) == int(EXCHANGE_CODE_BSE):
                        if int(fyExSeg[1][1]) == (SYM_SEGMENT_CM):
                            tickerName = keyList[valList.index(fyToken)]
                            retScrip = INTERNAL_getScriptNameFromTicket(tickerName)
                            if retScrip[0] != SUCCESS_C_1:
                                logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, retScrip[2], ERROR_C_UNKNOWN)
                                continue
                            else:
                                tableName = retScrip[1][1].lower()
                                if tableName in FY_SYMBOL_MAPPING.keys():
                                    tableName = FY_SYMBOL_MAPPING[tableName]
                                dbName = DB_EOD_BSE_CM
                        else:
                            continue
                    else:
                        continue
                except ValueError:
                    continue
                except Exception as e:
                    logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, e, ERROR_C_UNKNOWN)
                    continue

                if dbName == None:
                    continue

                try:
                    # We will hit the db and get the data
                    sqlGetPrevCloseData = "SELECT OPEN,HIGH,LOW,CLOSE,VOLUME FROM %s.`%s` ORDER BY IDATE DESC LIMIT 2;" % (dbName, tableName)
                    try:
                        if db == None or cursor == None:
                            db, cursor = dbConnect(dbType=3, readOnly=1, callingFuncName=funcName)
                            if db == None or cursor == None:
                                return [ERROR_C_1, ERROR_C_DB_1, ""]
                        cursor.execute(sqlGetPrevCloseData)
                        prevCloseData = cursor.fetchall()
                    except:  # If there are no entries in table/table does not exist
                        prevCloseData = ()
                    
                    spread = 0
                    bidPr = 0
                    askPr = 0
                    if len(prevCloseData) > 1:             # if there are more than 1 row in the table
                    # Calculating essential parameters which needs to be returned
                        priceChange = round(float(prevCloseData[0][3] - prevCloseData[1][3]), 4)
                        percentageChange = (priceChange / prevCloseData[1][3]) * 100
                        percentageChange = round(percentageChange, 2)

                        # Creating a dictionary to set to cache
                        updateCacheDict = {'601': askPr, '401': bidPr,
                                        '201': prevCloseData[0][3],
                                        '204': priceChange,
                                        '207': prevCloseData[0][4],
                                        '221': prevCloseData[0][0],
                                        '222': prevCloseData[0][1],
                                        '223': prevCloseData[0][2],
                                        '220': prevCloseData[1][3],  
                                        '215': percentageChange,
                                        '224': spread}
                        
                    elif len(prevCloseData) == 1:          # if there exists a single row in the table
                        priceChange = 0
                        percentageChange = 0    

                        # Creating a dictionary to set to cache
                        updateCacheDict = {'601': askPr, '401': bidPr,
                                        '201': prevCloseData[0][3],
                                        '204': priceChange,
                                        '207': prevCloseData[0][4],
                                        '221': prevCloseData[0][0],
                                        '222': prevCloseData[0][1],
                                        '223': prevCloseData[0][2],
                                        '220': prevCloseData[0][3],
                                        '215': percentageChange,
                                        '224': spread}
                    
                    # elif len(prevCloseData) == 0 :
                    else:                               # If there are no entries in table/table does not exist
                        # Creating a dictionary to set to cache
                        updateCacheDict = {'601': askPr, '401': bidPr,
                                        '201': 0,
                                        '204': 0,
                                        '207': 0,
                                        '221': 0,
                                        '222': 0,
                                        '223': 0,
                                        '220': 0,  
                                        '215': 0,
                                        '224': spread}
                    # Setting to cache so that next time we would not have to hit the db
                    updateCacheDict = json.dumps(updateCacheDict)
                    localMemory.set("%s%s%s" % (fyToken, CACHE_K_LEVEL2DATA, todayTimestamp), updateCacheDict, CACHE_T_3) ## Commented for testing 2018-09-19

                    # Appending the dictionary to the existing dictionary which will get returned
                    l2Dict[i] = updateCacheDict
                    continue
                except Exception as e:
                    continue

        return [SUCCESS_C_1, l2Dict, ""]

    except Exception as e:
        logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, e, ERROR_C_UNKNOWN, fyTokenDict)
        return [ERROR_C_1, ERROR_C_UNKNOWN, ERROR_M_UNKNOWN_1]


def INTERNAL_updateQuoteDetails(watchList, l2Dict):
    funcName = "INTERNAL_updateQuoteDetails"
    try:
        key = watchList["sym_token"]
        l2dict = json.loads(l2Dict[key])
        watchList[API_K_DATA_PRICE_CHANGE] = float(l2dict["204"])
        watchList[API_K_DATA_PERC_CHANGE] = float(l2dict["215"])
        watchList[API_K_DATA_LTP] = float(l2dict["201"])
        return
    except Exception as e:
        return
    

def INTERNAL_updateQuoteDetailsToOrderBook(orderDict, l2Dict):
    funcName = "INTERNAL_updateQuoteDetailsToOrderBook"
    try:
        key = orderDict["fyToken"]
        l2dict = json.loads(l2Dict[key])
        orderDict[API_K_DATA_PRICE_CHANGE] = float(l2dict["204"])
        orderDict[API_K_DATA_PERC_CHANGE] = float(l2dict["215"])
        orderDict[API_K_DATA_LTP] = float(l2dict["201"])
        return
    except Exception as e:
        orderDict[API_K_DATA_PRICE_CHANGE] = 0.0
        orderDict[API_K_DATA_PERC_CHANGE] = 0.0
        orderDict[API_K_DATA_LTP] = 0.0
        return


def main():
    None


if __name__ == "__main__":
    main()

