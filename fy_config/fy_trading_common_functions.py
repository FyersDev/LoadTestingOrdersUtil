moduleName = "fy_trading_common_functions"
try:
    import sys
    import datetime
    import json
    import time
    import hashlib
    import hmac
    import urllib3

    from fy_auth_defines import APPID_TRADE_FYERS, APPID_MOBILE_FYERS
    from fy_base_defines import LOG_STATUS_ERROR_1, CACHE_T_2
    from fy_base_success_error_codes import ERROR_C_1, SUCCESS_C_1, \
     ERROR_C_UNKNOWN, ERROR_C_DB_1, ERROR_C_DB_NOT_FOUND, ERROR_C_DEMO_USER, ERROR_C_INV_ORDER_QTY, ERROR_C_INV_ORDER_DISC_QTY, \
     ERROR_C_INV_ORDER_VALIDITY, ERROR_C_INV_ORDER_OFFLINE_FLAG, \
     ERROR_C_INV_EXCHANGE, ERROR_C_INV_SEGMENT, ERROR_C_INV_ORDER_STOP_LMT_PRICE, \
     ERROR_C_INV_ORDER_PRODUCT, ERROR_C_INV_ORDER_TYPE, ERROR_C_INV_ORDER_SIDE, \
     ERROR_C_INV_ORDER_ID, ERROR_C_OMS_1, ERROR_C_OMS_ORDERBOOK_EMPTY
    from fy_base_success_error_messages import ERROR_M_DEMO_USER, ERROR_M_INV_ORDER_QTY, \
     ERROR_M_INV_ORDER_DISC_QTY, ERROR_M_INV_ORDER_VALIDITY, ERROR_M_INV_ORDER_OFFLINE_FLAG, \
     ERROR_M_INV_EXCHANGE, ERROR_M_INV_SEGMENT, ERROR_M_INV_ORDER_STP_LMT_PRICE, \
     ERROR_M_INV_ORDER_PRODUCT, ERROR_M_INV_ORDER_TYPE, ERROR_M_INV_ORDER_SIDE, \
     ERROR_M_INV_ORDER_ID     
    from fy_common_api_keys_values import API_K_DATA_PRICE_CHANGE, \
     API_K_DATA_PERC_CHANGE, API_K_DATA_LTP, API_V_ORDER_TYPE_MKT_1, \
     API_V_ORDER_TYPE_MKT_2, API_V_ORDER_TYPE_LMT_1, API_V_ORDER_TYPE_LMT_2, \
     API_V_ORDER_TYPE_STP_MKT, API_V_ORDER_TYPE_STP_LMT, API_V_ORDER_SIDE_BUY_1, \
     API_V_ORDER_SIDE_SELL_1
    from fy_connections_defines import TBL_OLD_NEW_TOKENS
    from fy_demo_defines import DEMO_ORDERBOOK, DEMO_POSITIONS, DEMO_HOLDINGS
    from fy_data_and_trade_defines import GUEST_CLIENT_ID, EXCHANGE_NAME_NSE, EXCHANGE_NAME_MCX_1, EXCHANGE_NAME_BSE, \
     EXCHANGE_CODE_NSE, EXCHANGE_CODE_MCX, EXCHANGE_CODE_BSE, SYM_SEGMENT_CM, SYM_SEGMENT_FO, \
     SYM_SEGMENT_CD, SYM_SEGMENT_COM
    from fy_trading_defines import API_OMS_V_REQ_SOURCE_WEB, \
     API_OMS_V_REQ_SOURCE_MOBILE, API_OMS_V_DEFAULT_REQ_SOURCE, API_OMS_V_DEFAULT_ORDER_TRIGGER_PRICE, \
     API_OMS_V_DEFAULT_ORDER_VALIDITY, API_OMS_V_DEFAULT_ORDER_DISC_QTY, \
     API_OMS_V_ORDER_PROD_CNC_2, API_OMS_V_ORDER_PROD_CNC_1, API_OMS_V_ORDER_PROD_MARGIN_2, \
     API_OMS_V_ORDER_PROD_MARGIN_1, API_OMS_V_ORDER_PROD_INTRADAY_2, API_OMS_V_ORDER_PROD_INTRADAY_1, \
     API_OMS_REQ_PATH_ORDER_PLACE, API_OMS_V_SEG_CM_2, API_OMS_V_SEG_FO_2, \
     API_OMS_V_SEG_CD_1, API_OMS_V_SEG_COM_1, API_OMS_V_ORDER_SIDE_BUY_1, \
     API_OMS_V_ORDER_SIDE_SELL_1, API_OMS_K_REQ_SOURCE, API_OMS_K_ROW_START, \
     API_OMS_K_ROW_END, API_OMS_V_DEFAULT_MARKET_PRO_FLAG, API_OMS_V_DEFAULT_MARKET_PRO_VAL, \
     API_OMS_V_DEFAULT_GTC_FLAG, API_OMS_V_DEFAULT_ENCASH_FLAG, API_OMS_K_PAN_1, \
     REQ_URL_OMS_MAIN_1, API_OMS_K_TOKEN_ID_2, API_OMS_K_CLIENT_ID_1, \
     API_OMS_V_PAGINATION_START, API_OMS_V_PAGINATION_END, REQ_URL_OMS_MAIN_2, \
     API_OMS_REQ_PATH_ORDER_BOOK, API_OMS_V_DEFAULT_ORDER_OFFLINE_FLAG_2   

    from fy_auth_functions_splitTokenHash import INTERNAL_verifyTokenHash
    from fy_base_functions import logEntryFunc2
    from fy_connections import connectRedis, dbConnect
    from fy_common_internal_functions import getSymbolsFromSymbolMasterCache, INTERNAL_checkSymbolNameOrToken, \
     INTERNAL_getSymExAndSegment
    from fy_data_internal_functions import INTERNAL_getL1PricesForFyTokenDict_1
    from vagator_auth_check import INTERNAL_splitTokenHash
    from fy_trading_internal_functions import INTERNAL_createAndSendOmsRequest, \
     INTERNAL_decryptOmsResponse, INTERNAL_readOmsDecryptedResponse, \
     INTERNAL_getToken_checkStatus
     
except Exception as e:
    print("ERR : %s : %s : %s" % (moduleName, "Could not import module", e))
    sys.exit()


def INTERNAL_getDemoResponse(funcType,localMemory=None,callingFuncName=""):
    funcName = "INTERNAL_getDemoResponse"
    try:
        if localMemory == None:
            localMemory = connectRedis(callingFuncName=callingFuncName)

        db, cursor = dbConnect(dbType=3, readOnly=1)
        if db == None or cursor == None:
            return [ERROR_C_1, ERROR_C_DB_1, ""]
        #orderbook
        if funcType == 1:
            returnList = DEMO_ORDERBOOK
            fySymbolList = [i["symbol"] for i in returnList]

            symbolDetailsRet = getSymbolsFromSymbolMasterCache(fySymbolList,localMemory=localMemory)
            symbolsDetails = {}
            if symbolDetailsRet[0] == SUCCESS_C_1:
                symbolsDetails = symbolDetailsRet[1][1]

            symbolTickerToFyToken = {}
            for symbol in symbolDetailsRet[1][1]:
                symbolTickerToFyToken[symbol] = symbolDetailsRet[1][1][symbol]["fyToken"]

            l2DictRetList = INTERNAL_getL1PricesForFyTokenDict_1(symbolTickerToFyToken, localMemory=localMemory,callingFuncName=funcName)
            l2Dict = {}
            if l2DictRetList[0] != ERROR_C_1:
                for token in l2DictRetList[1]:
                    l2Dict[token] = json.loads(l2DictRetList[1][token])

            todayDate = datetime.datetime.today()

            for i in returnList:

                i["fyToken"] = symbolsDetails[i["symbol"]]["fyToken"]
                i["ex_sym"] = symbolsDetails[i["symbol"]]["underSym"]
                i["description"] = symbolsDetails[i["symbol"]]["symbolDesc"]
                i["lot_size"] = symbolsDetails[i["symbol"]]["minLotSize"]
                i["tick_size"] = symbolsDetails[i["symbol"]]["tickSize"]
                i["instrument"] = symbolsDetails[i["symbol"]]["exInstType"]
                i[API_K_DATA_PRICE_CHANGE] = l2Dict[i["fyToken"]]["204"]
                i[API_K_DATA_PERC_CHANGE] = l2Dict[i["fyToken"]]["215"]
                i[API_K_DATA_LTP] = l2Dict[i["fyToken"]]["201"]

                dayOpen = l2Dict[i["fyToken"]]["221"]

                if i["status"] == 5 and i["type"] == 1:
                    i["limitPrice"] = dayOpen

                if i["status"] == 2 and i["type"] == 2:
                    i["tradedPrice"] = dayOpen + 5

                if i["status"] == 2 and i["type"] == 1 and i["side"] == 1:
                    i["limitPrice"] = dayOpen - 5
                    i["tradedPrice"] = dayOpen - 6

                i["orderDateTime"] = todayDate.replace(hour=10).strftime('%d-%b-%Y %H:%M:%S')

            return [SUCCESS_C_1, returnList, ""]


        #positions
        elif funcType == 2:
            returnList = DEMO_POSITIONS
            fySymbolList = [i["symbol"] for i in returnList]

            symbolDetailsRet = getSymbolsFromSymbolMasterCache(fySymbolList,localMemory=localMemory)
            symbolsDetails = {}
            if symbolDetailsRet[0] == SUCCESS_C_1:
                symbolsDetails = symbolDetailsRet[1][1]

            symbolTickerToFyToken = {}
            for symbol in symbolDetailsRet[1][1]:
                symbolTickerToFyToken[symbol] = symbolDetailsRet[1][1][symbol]["fyToken"]

            l2DictRetList = INTERNAL_getL1PricesForFyTokenDict_1(symbolTickerToFyToken, localMemory=localMemory,callingFuncName=funcName)
            l2Dict = {}
            if l2DictRetList[0] != ERROR_C_1:
                for token in l2DictRetList[1]:
                    l2Dict[token] = json.loads(l2DictRetList[1][token])

            total_pl = 0
            total_realized = 0
            total_unrealized = 0

            for i in returnList:
                i["fyToken"] = symbolTickerToFyToken[i["symbol"]]
                i["ltp"] = l2Dict[i["fyToken"]]["201"]
                i["ex_sym"] = symbolsDetails[i["symbol"]]["underSym"]
                i["description"] = symbolsDetails[i["symbol"]]["symbolDesc"]
                i["lot_size"] = symbolsDetails[i["symbol"]]["minLotSize"]
                i["tick_size"] = symbolsDetails[i["symbol"]]["tickSize"]
                dayOpen = l2Dict[i["fyToken"]]["221"]

                i["buyVal"] = (dayOpen+2)*5
                i["sellVal"] = (dayOpen+5)*5

                i["buyAvg"] = (dayOpen+2)
                i["sellAvg"] = (dayOpen+5)

                i["pl"] = i["sellVal"] - i["buyVal"]
                i["realized_profit"] = i["pl"]
                total_pl += i["pl"]
                total_realized += i["realized_profit"]
                total_unrealized += i["unrealized_profit"]


            overallDict = {}
            overallDict["count_total"] = len(returnList)
            overallDict["count_open"] = 0
            overallDict["pl_total"] = total_pl
            overallDict["pl_realized"] = total_realized
            overallDict["pl_unrealized"] = total_unrealized

            return [SUCCESS_C_1, [returnList,overallDict], ""]

        #holdings
        elif funcType == 3:
            returnList = DEMO_HOLDINGS
            fySymbolList = [i["symbol"] for i in returnList]

            symbolDetailsRet = getSymbolsFromSymbolMasterCache(fySymbolList,localMemory=localMemory)
            symbolsDetails = {}
            if symbolDetailsRet[0] == SUCCESS_C_1:
                symbolsDetails = symbolDetailsRet[1][1]

            symbolTickerToFyToken = {}
            for symbol in symbolDetailsRet[1][1]:
                symbolTickerToFyToken[symbol] = symbolDetailsRet[1][1][symbol]["fyToken"]

            l2DictRetList = INTERNAL_getL1PricesForFyTokenDict_1(symbolTickerToFyToken, localMemory=localMemory,callingFuncName=funcName)
            l2Dict = {}
            if l2DictRetList[0] != ERROR_C_1:
                for token in l2DictRetList[1]:
                    l2Dict[token] = json.loads(l2DictRetList[1][token])

            totalInvestment = 0
            totalCurrentValue = 0
            totalPnl = 0
            totalRemainingQty = 0

            for i in returnList:

                i["fyToken"] = symbolTickerToFyToken[i["symbol"]]
                i["symbolLtp"] = l2Dict[i["fyToken"]]["201"]
                i["ex_sym"] = symbolsDetails[i["symbol"]]["underSym"]
                i["description"] = symbolsDetails[i["symbol"]]["symbolDesc"]
                i["lot_size"] = symbolsDetails[i["symbol"]]["minLotSize"]
                i["tick_size"] = symbolsDetails[i["symbol"]]["tickSize"]
                i["isin"] = symbolsDetails[i["symbol"]]["isin"]

                dayOpen = l2Dict[i["fyToken"]]["221"]

                i["marketVal"] = round((i["symbolLtp"] * i["remainingQuantity"]),2)
                i["costPrice"] = round(((dayOpen*90)/100),2)
                i["pl"] = round((i["marketVal"] - (i["costPrice"] * i["remainingQuantity"])),2)

                totalInvestment += (i["costPrice"] * i["remainingQuantity"])
                totalCurrentValue += i["marketVal"]
                totalPnl += i["pl"]
                totalRemainingQty += i["remainingQuantity"]

            overallDict = {}
            overallDict["count_total"] = len(returnList)
            overallDict["total_investment"] = round(totalInvestment,2)
            overallDict["total_current_value"] = round(totalCurrentValue,2)
            overallDict["total_pl"] = round(totalPnl,2)
            if totalInvestment == 0 or totalRemainingQty == 0:
                overallDict["pnl_perc"] = 0.0
            else:
                overallDict["pnl_perc"] = round((totalPnl/(totalInvestment*totalRemainingQty))*100,4)

            return [SUCCESS_C_1, [returnList,overallDict], ""]

    except Exception as e:
        logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, e, ERROR_C_UNKNOWN)
        return [ERROR_C_1, ERROR_C_UNKNOWN, ""]


def INTERNAL_getNewFyTokensFromOldfyTokensList(inputTokenList, db=None, cursor=None, localMemory=None,callingFuncName=""):
    """
        [FUNCTION]

        [PARAMS]
            inputTokenList : List of old fytokens for which we want new fyTokens
        [RETURN]
            Success : [SUCCESS_C_1,["oldFyToken":"newFyToken"],""]
            Failure : [ERROR_C_1,errorCode,errorMessage]
    """
    funcName = "INTERNAL_getNewFyTokensFromOldfyTokensList"
    try:
        if localMemory == None:
            localMemory = connectRedis(callingFuncName=callingFuncName)

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
                # None
            elif len(fyTokenList) < len(inputTokenList):
                getDBTokensList = list(set(inputTokenList) - set(fyTokenList.keys()))
        if len(getDBTokensList) == 0:
            getDBTokensList = inputTokenList

        oldFyTokensString = ""
        for i in getDBTokensList:
            oldFyTokensString += "'%s'," % (i)
        oldFyTokensString = oldFyTokensString[:-1]
        sqlQuery = "SELECT FY_OLD_TOKEN,FY_NEW_TOKEN FROM `%s` WHERE FY_OLD_TOKEN IN (%s);" % (
            TBL_OLD_NEW_TOKENS, oldFyTokensString)
        if db == None or cursor == None:
            db, cursor = dbConnect(dbType=3, readOnly=1)
            if db == None or cursor == None:
                return [ERROR_C_1, ERROR_C_DB_1, ""]

        try:
            cursor.execute(sqlQuery)
            symbolTokens = cursor.fetchall()
            if symbolTokens == ():
                # If we do not receive any data from cache and db then we will return an error
                if len(fyTokenList) <= 0:
                    return [ERROR_C_1, ERROR_C_DB_NOT_FOUND, ""]
                else:
                    # We will return success with whatever tokens we have data for
                    return [SUCCESS_C_1, fyTokenList, ""]
            for i in symbolTokens:
                try:
                    fyTokenList[str(i[0])] = "%s" % (i[1])
                    localMemory.set(str(i[0]),str(i[1]),CACHE_T_2)
                except Exception as e:
                    logEntryFunc2(LOG_STATUS_ERROR_1, moduleName,
                                  funcName,callingFuncName, e, ERROR_C_UNKNOWN,i)
                    continue
            for i in getDBTokensList:
                localMemory.set("%s" % (i),fyTokenList[i] ,CACHE_T_2)
            return [SUCCESS_C_1, fyTokenList, ""]
        except Exception as e:
            logEntryFunc2(LOG_STATUS_ERROR_1, moduleName,funcName,
                          callingFuncName, e, ERROR_C_UNKNOWN, inputTokenList)
            return [ERROR_C_1, ERROR_C_DB_1, e]

    except Exception as e:
        logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName,
                      callingFuncName, e, ERROR_C_UNKNOWN, inputTokenList)
        return [ERROR_C_1, ERROR_C_UNKNOWN, ""]


def INTERNAL_fy_getNecessaryOMSData_withID(tokenHash,db=None,cursor=None,localMemory=None,callingFuncName="",verifyFlag=1,inputFyId=None,inputAppId=None):
    """
    [FUNCTION]
        Get only the essential user OMS details which will be used while sending requests to the oms
    [PARAMS]
        tokenHash    : This is a hash of (fyId + AppId)
        verifyFlag   : If 1     => We will verify the tokenHash
                       If != 1  => Split the tokenHash, get the data and return it without tokenHash verification
    [RETURN]
        Success : [SUCCESS_C_1,[,,,,,,,,,,,,,],""]
        Failure : [ERROR_C_1,errorCode,""]
    """
    funcName = "INTERNAL_fy_getNecessaryOMSData_withID"
    try:
        if inputFyId == None or inputAppId == None:
            #change 20200717 Khyati
            # If we need to verify the tokenHash
            if verifyFlag == 1:
                tokenList = INTERNAL_verifyTokenHash(tokenHash,callingFuncName=callingFuncName)
                if tokenList[0] == ERROR_C_1:
                    return tokenList
            else:
                tokenList = INTERNAL_splitTokenHash(tokenHash,callingFuncName=callingFuncName)
                if tokenList[0] == ERROR_C_1:
                    return tokenList
            
            fyId = tokenList[1][0]
            appId = tokenList[1][1]
        else:
            fyId = inputFyId
            appId = inputAppId

        if fyId in GUEST_CLIENT_ID:
            return [ERROR_C_1, ERROR_C_DEMO_USER, ERROR_M_DEMO_USER]

        if localMemory == None:
            localMemory = connectRedis(callingFuncName=callingFuncName)

        omsAllDetailsCache = localMemory.get(f"oms_data-{fyId}-7830|")
        if omsAllDetailsCache != None:
            omsAllDetailsCache = json.loads(omsAllDetailsCache)

        else:
            funcRet = INTERNAL_sendReq_get_oms_data_v2(fyId)
            if funcRet[0] == SUCCESS_C_1:
                omsAllDetailsCache = funcRet[1]
            else:
                return funcRet

        if omsAllDetailsCache != None:
            newlist = [
                        omsAllDetailsCache["fy_id"],
                        omsAllDetailsCache["token_hash"],
                        omsAllDetailsCache["fy_pwd"],
                        omsAllDetailsCache["user_id"],
                        omsAllDetailsCache["um_user_type"],
                        omsAllDetailsCache["loginid"],
                        omsAllDetailsCache["pan"],
                        omsAllDetailsCache["dob"],
                        omsAllDetailsCache["oms_token_id"],
                        omsAllDetailsCache["um_entity_type"],
                        omsAllDetailsCache["em_exch_client_id"],
                        omsAllDetailsCache["description"],
                        omsAllDetailsCache["poa_flag"],
                        omsAllDetailsCache["bo_id"],
                    ]

            if appId == APPID_TRADE_FYERS:
                source = API_OMS_V_REQ_SOURCE_WEB
            elif appId == APPID_MOBILE_FYERS:
                source = API_OMS_V_REQ_SOURCE_MOBILE
            else:
                logEntryFunc2("DEBUG", moduleName, funcName, callingFuncName, fyId, appId, "App Id other than web or mobile")
                source = API_OMS_V_DEFAULT_REQ_SOURCE

            return [SUCCESS_C_1, newlist, appId, source]
        return [ERROR_C_1, ERROR_C_UNKNOWN, ""]
    except Exception as e:
        logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName,callingFuncName, tokenHash, err_msg=e, code=ERROR_C_UNKNOWN, fyId=fyId)
        return [ERROR_C_1, ERROR_C_UNKNOWN, ""]


def INTERNAL_sendReq_get_oms_data_v2(fyId, **kwargs):
    funcName = "INTERNAL_sendReq_get_oms_data_v2"
    try:
        timestamp = str(int(time.time()))
        user_agent = "api_v2_7085"
        msg = f"{user_agent}|{timestamp}|"
        checksum = generate_hash_key("e9t102a7d1b281c1c3c1efa2e1ddbfef6a2e1b253d28e4b83548d1c26f4d8q9", msg)
        if checksum[0] == ERROR_C_1:
            return checksum

        url = "https://api.fyers.in/vagator/v1/get_oms_data_v2"

        requestBody = {
                        "checksum": checksum[1],
                        "timestamp" : timestamp,
                        "user_agent" : user_agent,
                        "fy_id": fyId
                    }

        # response1 = requests.post(url, data=json.dumps(requestBody))
        # response = json.loads(response1.text)
        http_obj = urllib3.PoolManager()
        response1 = http_obj.request("POST", url=url, body=json.dumps(requestBody))
        response = json.loads(response1.data.decode("utf-8"))

        if "s" in response and response["s"] == "ok":
            try:
                return [SUCCESS_C_1, response["data"], ""]

            except Exception as e:
                logEntryFunc2(LOG_STATUS_ERROR_1,moduleName,funcName,"", ERROR_C_1,response1.status_code, response1.text, url,fyId=fyId,appId="",status_code=ERROR_C_1,code=ERROR_C_UNKNOWN,err_msg=e)
                return [ERROR_C_1, ERROR_C_UNKNOWN, ""]
        else:
            logEntryFunc2(LOG_STATUS_ERROR_1,moduleName,funcName,"", ERROR_C_1,response1.status_code, response1.text, url,fyId=fyId,appId="",status_code=ERROR_C_1,code=ERROR_C_UNKNOWN,err_msg=e)
            return [ERROR_C_1, ERROR_C_UNKNOWN, ""]

    except Exception as e:
        logEntryFunc2(LOG_STATUS_ERROR_1,moduleName,funcName,"", ERROR_C_1,fyId=fyId,status_code=ERROR_C_1,code=ERROR_C_UNKNOWN,err_msg=e,response="")
        return [ERROR_C_1, ERROR_C_UNKNOWN, ""]


def generate_hash_key(secret_key, message, callingFuncName=""):
    """This function created hash string which you can send as checksum through API.
    Returns:
        hashed string
    
    """
    funcName = "generate_hash_key"
    try:
        byte_key = bytes(secret_key, "utf-8")
        message = message.encode()
        hashed_msg = hmac.new(byte_key, message, hashlib.sha256).hexdigest()
        return [SUCCESS_C_1, hashed_msg.upper(),""]
    except Exception as e:
        logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName,callingFuncName,secret_key, message, err_msg=e, code=ERROR_C_UNKNOWN)
        return [ERROR_C_1, ERROR_C_UNKNOWN, ""]


def INTERNAL_placeOrder_withID(tokenHash, symbol, transType, ordType, qty, price, prodList, trigPrice=API_OMS_V_DEFAULT_ORDER_TRIGGER_PRICE, valType=API_OMS_V_DEFAULT_ORDER_VALIDITY, discQty=API_OMS_V_DEFAULT_ORDER_DISC_QTY, offlineFlag=API_OMS_V_DEFAULT_ORDER_OFFLINE_FLAG_2, callingFuncName="",userIp=""):
    """
    [FUNCTION]
        Get the status of a particular order by User and OrderID
    [PARAMS]
        tokenHash       : This is a hash of (fyId + AppId)
        symbol          : Eg: "NSE:TCS-EQ"
        transType       : (buy/sell)
        ordType         : (limit/stop/market/stoplimit)
        qty             : The qty to buy/sell
        price           : The price at which the order should be placed
        prodList        : (cnc,margin,intraday)
        trigPrice       : Default = 0
        valType         : Default = "DAY"
        discQty         : Default = 0
        offlineFlag     : Default = False

    [RETURN]
        Success : [SUCCESS_C_1,150,orderNumber]
        Failure : [CONST_function/oms_error,errorCode,"error message"]
    """
    funcName = "INTERNAL_placeOrder_withID"
    try:
        localMemory = connectRedis(callingFuncName=callingFuncName)

        # Check if qty is correct or not
        try:
            qty = int(float(qty))
        except Exception as e:
            return [ERROR_C_1,ERROR_C_INV_ORDER_QTY,ERROR_M_INV_ORDER_QTY]

        # Check if disclosedQty is correct or not
        try:
            discQty = int(discQty)
        except Exception as e:
            return [ERROR_C_1, ERROR_C_INV_ORDER_DISC_QTY, ERROR_M_INV_ORDER_DISC_QTY]

        # Check if validity is correct or not
        if valType == "":
            return [ERROR_C_1, ERROR_C_INV_ORDER_VALIDITY, ERROR_M_INV_ORDER_VALIDITY]
        valType = valType.upper()

        # Check offline flag is correct or not
        if offlineFlag == "":
            return [ERROR_C_1, ERROR_C_INV_ORDER_OFFLINE_FLAG, ERROR_M_INV_ORDER_OFFLINE_FLAG]
        offlineFlag = offlineFlag.lower()

        fyTokenList = INTERNAL_fy_getNecessaryOMSData_withID(tokenHash,localMemory=localMemory,
                                                             callingFuncName=callingFuncName)
        if fyTokenList[0] == ERROR_C_1:
            return fyTokenList
        OMStoken = fyTokenList[1][8]
        OMSid = fyTokenList[1][0]
        OMSClientType = fyTokenList[1][4]
        OMSExchClientId = fyTokenList[1][10]
        OMSUserID = fyTokenList[1][3]
        OMSUserType = fyTokenList[1][9]
        aesKey = fyTokenList[1][11]
        pan = fyTokenList[1][6]
        appId = fyTokenList[2]
        source = fyTokenList[3]

        # Converting symbol name to token
        checkSymbolList = INTERNAL_checkSymbolNameOrToken(symbol,localMemory=localMemory,callingFuncName=callingFuncName)
        if checkSymbolList[0] == ERROR_C_1:
            return checkSymbolList

        # Splitting the token to get the exchange, segment and scripCode
        symbolList = INTERNAL_getSymExAndSegment(checkSymbolList[1][0],callingFuncName=callingFuncName)
        if symbolList[0] == ERROR_C_1:
            return symbolList

        if symbolList[1][0] == str(EXCHANGE_CODE_NSE):
            symExcg = EXCHANGE_NAME_NSE
        elif symbolList[1][0] == str(EXCHANGE_CODE_MCX):
            symExcg = EXCHANGE_NAME_MCX_1
        elif symbolList[1][0] == str(EXCHANGE_CODE_BSE):
            symExcg = EXCHANGE_NAME_BSE
        else:
            return [ERROR_C_1, ERROR_C_INV_EXCHANGE, ERROR_M_INV_EXCHANGE]

        # Rupeeseed has different codes for each segment
        if symbolList[1][1] == str(SYM_SEGMENT_CM):
            symType = API_OMS_V_SEG_CM_2
        elif symbolList[1][1] == str(SYM_SEGMENT_FO):
            symType = API_OMS_V_SEG_FO_2
        elif symbolList[1][1] == str(SYM_SEGMENT_CD):
            symType = API_OMS_V_SEG_CD_1
        elif symbolList[1][1] == str(SYM_SEGMENT_COM):
            symType = API_OMS_V_SEG_COM_1
        else:
            return [ERROR_C_1, ERROR_C_INV_SEGMENT, ERROR_M_INV_SEGMENT]

        try:
            prodList = prodList.upper()
        except Exception as e:
            return [ERROR_C_1, ERROR_C_INV_ORDER_PRODUCT, ERROR_M_INV_ORDER_PRODUCT]

        # Rupeeseed has different codes for each product type
        if (prodList == API_OMS_V_ORDER_PROD_CNC_2) or (prodList == API_OMS_V_ORDER_PROD_CNC_1):
            prodList = API_OMS_V_ORDER_PROD_CNC_1
        elif (prodList == API_OMS_V_ORDER_PROD_MARGIN_2) or (prodList == API_OMS_V_ORDER_PROD_MARGIN_1):
            prodList = API_OMS_V_ORDER_PROD_MARGIN_1
        elif (prodList == API_OMS_V_ORDER_PROD_INTRADAY_2) or (prodList == API_OMS_V_ORDER_PROD_INTRADAY_1):
            prodList = API_OMS_V_ORDER_PROD_INTRADAY_1
        else:
            return [ERROR_C_1, ERROR_C_INV_ORDER_PRODUCT, ERROR_M_INV_ORDER_PRODUCT]

        try:
            ordType = int(ordType)
        except Exception as e:
            return [ERROR_C_1, ERROR_C_INV_ORDER_TYPE, ERROR_M_INV_ORDER_TYPE]

        # Rupeeseed has different codes for order type like LMT/MKT
        if ordType == API_V_ORDER_TYPE_MKT_1:
            ordType = API_V_ORDER_TYPE_MKT_2

        elif ordType == API_V_ORDER_TYPE_LMT_1:
            ordType = API_V_ORDER_TYPE_LMT_2

        elif ordType == API_V_ORDER_TYPE_STP_MKT:
            # If order type is stop then we need to check price. If price is 0, then order is market and if price != 0 then order type is limit
            if price == 0:
                ordType = API_V_ORDER_TYPE_MKT_2
            else:
                ordType = API_V_ORDER_TYPE_LMT_2

        elif ordType == API_V_ORDER_TYPE_STP_LMT:
            # If order type is stoplimit then we need to check price. If price is 0, stopLimit order is invalid
            if price == 0:
                return [ERROR_C_1, ERROR_C_INV_ORDER_STOP_LMT_PRICE, ERROR_M_INV_ORDER_STP_LMT_PRICE]
            ordType = API_V_ORDER_TYPE_LMT_2
        else:
            return [ERROR_C_1, ERROR_C_INV_ORDER_TYPE, ERROR_M_INV_ORDER_TYPE]

        try:
            transType = int(transType)
        except Exception as e:
            return [ERROR_C_1, ERROR_C_INV_ORDER_SIDE, ERROR_M_INV_ORDER_SIDE]

        # Rupeeseed has different codes for buy/sell like B/S
        if transType == API_V_ORDER_SIDE_BUY_1:
            transType = API_OMS_V_ORDER_SIDE_BUY_1
        elif transType == API_V_ORDER_SIDE_SELL_1:
            transType = API_OMS_V_ORDER_SIDE_SELL_1
        else:
            return [ERROR_C_1, ERROR_C_INV_ORDER_SIDE, ERROR_M_INV_ORDER_SIDE]

        # Create a paramDict to send to the OMS
        paramsPayload = {
            "token_id": OMStoken,
            "client_id": OMSid,
            API_OMS_K_REQ_SOURCE: source,
            "client_type": OMSClientType,
            "exch_client_id": OMSExchClientId,
            "user_id": OMSUserID,
            "user_type": OMSUserType,
            "securityid": symbolList[1][2],
            "inst_type": symType,
            "exchange": symExcg,
            "buysell": transType,
            "quantitytype": ordType,
            "quantity": str(qty),
            "productlist": prodList,
            "OrderType": valType,
            "offline_flag": offlineFlag,
            API_OMS_K_ROW_START:"",
            API_OMS_K_ROW_END:"",
            "triggerprice": str(trigPrice),
            "disclosequantity": str(discQty),
            "marketProflag": API_OMS_V_DEFAULT_MARKET_PRO_FLAG,
            "marketProVal": API_OMS_V_DEFAULT_MARKET_PRO_VAL,
            "ParticipantType": "B",
            "settlor": "",
            "Gtcflag": API_OMS_V_DEFAULT_GTC_FLAG,
            "EncashFlag": API_OMS_V_DEFAULT_ENCASH_FLAG,
            API_OMS_K_PAN_1: pan
        }

        # Based on order type, we will update the price to the paramsdict
        if (ordType == API_V_ORDER_TYPE_LMT_2):
            paramsPayload["price"] = str(price)
        elif (ordType == API_V_ORDER_TYPE_MKT_2):
            None # If the ordertype is market, oms does not want price field to be present in params
        else:
            return [ERROR_C_1, ERROR_C_INV_ORDER_TYPE, ERROR_M_INV_ORDER_TYPE]
        # Send the request to the OMS
        #urlForRequest = REQ_URL_OMS_MAIN_1 + API_OMS_REQ_PATH_ORDER_PLACE
        urlForRequest = 'http://tradeonline-uat.fyers.in:8080/RupeeSeedWS/orderEntry/index'
        #import pdb; pdb.set_trace()

        sendReqFuncRet = INTERNAL_createAndSendOmsRequest(OMSid, OMStoken, aesKey,paramsPayload, urlForRequest, callingFuncName=callingFuncName,userIp=userIp)

        if sendReqFuncRet[0] == ERROR_C_1:
            return sendReqFuncRet
        omsResponse = sendReqFuncRet[1]

        # Decrypt the response received from the OMS
        readOmsResponseFuncRet = INTERNAL_decryptOmsResponse(omsResponse, aesKey,callingFuncName=callingFuncName)
        if readOmsResponseFuncRet[0] == ERROR_C_1:
            return readOmsResponseFuncRet
        userInfoList = readOmsResponseFuncRet[1]

        # Check for user invalidation. If yes, re-send the request
        readOmsResponseFuncRet2 = INTERNAL_readOmsDecryptedResponse(userInfoList,tokenHash, paramsPayload,
                        urlForRequest,fyId=OMSid, localMemory=localMemory,callingFuncName=callingFuncName,orderPlacement=True, userIp=userIp)
        return readOmsResponseFuncRet2

    except Exception as e:
        logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName,callingFuncName, tokenHash, err_msg=e, code=ERROR_C_UNKNOWN)
        return [ERROR_C_1, ERROR_C_UNKNOWN, ""]


def INTERNAL_getOrderStatus_withID2(tokenHash, orderID, orderProductType=None,db=None,cursor=None,localMemory=None,callingFuncName="",userIp=""):
    """
    [FUNCTION]
        Get the status of a particular order by User and OrderID
    [PARAMS]
        tokenHash    : This is a hash of (fyId + AppId)
        orderID      : Order ID for which you need all the data from the oms
    [RETURN]
        Success : [SUCCESS_C_1,[,,,,,],""]
        Failure : [CONST_function/oms_error,errorCode,"error message"]
    """
    funcName = "INTERNAL_getOrderStatus_withID2"
    try:
        if orderProductType != None:
            orderID1 = orderID.split("-")
            orderID = orderID1[0]
            orderLegNumber = orderID1[-1]
        try:
            orderID = int(float(orderID))
        except Exception as e:
            return [ERROR_C_1, ERROR_C_INV_ORDER_ID, ERROR_M_INV_ORDER_ID]
        if localMemory == None:
            localMemory = connectRedis(callingFuncName=callingFuncName)

        fyTokenList = INTERNAL_getToken_checkStatus(tokenHash,localMemory=localMemory, callingFuncName=callingFuncName,userIp=userIp)
        if fyTokenList[0] == ERROR_C_1:
            return fyTokenList
        fyId = fyTokenList[1][0]
        omsTokenId = fyTokenList[1][1]
        aesKey = fyTokenList[1][2]
        appId = fyTokenList[2]
        source = fyTokenList[3]

        # Send the request to the OMS
        paramsForEncryption = {API_OMS_K_TOKEN_ID_2: omsTokenId, API_OMS_K_CLIENT_ID_1: fyId, API_OMS_K_REQ_SOURCE: source,
                               API_OMS_K_ROW_START: API_OMS_V_PAGINATION_START, API_OMS_K_ROW_END: API_OMS_V_PAGINATION_END}
        urlForRequest = REQ_URL_OMS_MAIN_2 + API_OMS_REQ_PATH_ORDER_BOOK

        sendReqFuncRet = INTERNAL_createAndSendOmsRequest(fyId, omsTokenId, aesKey,paramsForEncryption, urlForRequest,callingFuncName=callingFuncName,userIp=userIp)
        if sendReqFuncRet[0] == ERROR_C_1:
            return sendReqFuncRet
        omsResponse = sendReqFuncRet[1]

        # Decrypt the response received from the OMS
        readOmsResponseFuncRet = INTERNAL_decryptOmsResponse(omsResponse, aesKey,callingFuncName=callingFuncName)
        if readOmsResponseFuncRet[0] == ERROR_C_1:
            return readOmsResponseFuncRet
        userInfoList = readOmsResponseFuncRet[1]

        # Check for user invalidation. If yes, re-send the request
        readOmsResponseFuncRet2 = INTERNAL_readOmsDecryptedResponse(userInfoList,tokenHash, paramsForEncryption,
                                                urlForRequest,fyId=fyId, localMemory=localMemory,callingFuncName=callingFuncName,userIp=userIp)
        if (readOmsResponseFuncRet2[0] == ERROR_C_1) or (readOmsResponseFuncRet2[0] == ERROR_C_OMS_1):
            return readOmsResponseFuncRet2
        userInfoList = readOmsResponseFuncRet2[1]

        # If we have received data for orderbook
        if (len(userInfoList) != 0):
            for i in userInfoList:
                orderNumber = i["ORDER_NUMBER"]
                orderNumber1 = int(float(orderNumber))
                if (orderID == orderNumber1):
                    if orderProductType != None:
                        productType = i["PRODUCT"]
                        orderLegNumber2 = i["LEG_NO"]

                        # If productType is not the same as what we are looking for, then continue
                        if productType != orderProductType:
                            continue
                        # If order leg number does not match, then continue
                        if orderLegNumber != orderLegNumber2:
                            continue

                    # Get the data for the particular order
                    orderDateTime = i["ORDER_DATE_TIME"]
                    orderNumber = i["ORDER_NUMBER"]
                    exchange = i["EXCHANGE"]
                    tranType = i["BUY_SELL"]
                    segment = i["SEGMENT"]
                    instrument = i["INSTRUMENT"]
                    productType = i["PRODUCT"]
                    orderStatus = i["STATUS"]
                    orderQty = i["QUANTITY"]
                    remQuantity = i["REMAINING_QUANTITY"]
                    orderPrice = i["PRICE"]
                    trigPrice = i["TRG_PRICE"]
                    orderType = i["ORDER_TYPE"]
                    discloseQty = i["DISCLOSE_QTY"]
                    securityId = i["SEM_SECURITY_ID"]
                    orderValidity = i["ORDER_VALIDITY"]
                    tradedQty = i["TRADEDQTY"]
                    dqQtyRem = i["DQQTYREM"]
                    rowNum = i["R"]
                    exchangeOrdNum = i["EXCHORDERNO"]

                    pan = i["PAN_NO"]
                    participantType = i["PARTICIPANT_TYPE"]
                    marketProFlag = i["MKT_PROTECT_FLG"]
                    marketProVal = i["MKT_PROTECT_VAL"]
                    settlor = i["SETTLOR"]
                    gtcFlag = i["GTC_FLG"]
                    encashFlag = i["ENCASH_FLG"]
                    marketType = i["MKT_TYPE"]

                    clientId = i["CLIENT_ID"]
                    serialNumber = i["SERIALNO"]

                    algoOrderNum = i["ALGO_ORD_NO"]
                    takeProfitTrailGap = i["TAKE_PROFIT_TRAIL_GAP"]
                    advGroupRefNum = i["ADV_GROUP_REF_NO"]
                    trailingSlVal = i["TRAILING_SL_VALUE"]
                    slAbsTickValue = i["SL_ABSTICK_VALUE"]
                    prfAbsTickValue = i["PR_ABSTICK_VALUE"]
                    orderOffOn = i["ORDER_OFFON"]
                    childLegUnqId = i["CHILD_LEG_UNQ_ID"]

                    tradedPrice = i["TRADED_PRICE"]
                    orderLegValue = i["LEG_NO"]
                    remQtyTotalQty = i["REM_QTY_TOT_QTY"]
                    remQtyRatio = i["REM_QTY_TOT_QTY"]
                    serialNumber = i["SERIALNO"]
                    semNseRegLot = i["SEM_NSE_REGULAR_LOT"]
                    nseRegularLot = i["SEM_NSE_REGULAR_LOT"]
                    symbol = i["SYMBOL"]

                    # Check if order reason/message is provided or not
                    if "REASON_DESCRIPTION" in i:
                        orderMessage = i["REASON_DESCRIPTION"]
                    else:
                        orderMessage = ""

                    orderDetailsList = [clientId, orderDateTime, orderNumber1, exchange, tranType, segment, instrument,
                            symbol, productType, orderStatus, orderQty, remQuantity, orderPrice, trigPrice,
                            orderType, discloseQty, serialNumber, securityId, orderValidity, nseRegularLot,
                            remQtyRatio, takeProfitTrailGap, advGroupRefNum, tradedQty, dqQtyRem,
                            exchangeOrdNum, rowNum,trailingSlVal,tradedPrice,orderLegValue,slAbsTickValue,
                            prfAbsTickValue,algoOrderNum,orderOffOn]

                    return [SUCCESS_C_1,orderDetailsList,""]

            # If the order number does not exist in the orderbook
            return [ERROR_C_1,ERROR_C_INV_ORDER_ID,ERROR_M_INV_ORDER_ID]

        else:
            return [ERROR_C_1, ERROR_C_OMS_ORDERBOOK_EMPTY, ERROR_M_INV_ORDER_ID]

    except Exception as e:
        logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName,callingFuncName, e, ERROR_C_UNKNOWN, tokenHash)
        return [ERROR_C_1, ERROR_C_UNKNOWN, funcName]
