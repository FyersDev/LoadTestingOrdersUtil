moduleName = "fy_trading_internal_functions_tradebook"
try:
    import sys

    from fy_base_defines import LOG_STATUS_ERROR_1
    from fy_base_success_error_codes import ERROR_C_1, SUCCESS_C_1, \
     ERROR_C_UNKNOWN, ERROR_C_OMS_1, ERROR_C_OMS_STRING_CONVERSION_FAIL
    from fy_data_and_trade_defines import BEWARE_CLIENTS_LIST, EXCHANGE_CODE_NSE, \
     EXCHANGE_CODE_BSE, SYM_SEGMENT_CM, SYM_SEGMENT_FO, SYM_SEGMENT_CD, \
     EXCHANGE_CODE_MCX, SYM_SEGMENT_COM
    from fy_trading_defines import API_OMS_K_TOKEN_ID_2, API_OMS_K_CLIENT_ID_1, \
     API_OMS_K_REQ_SOURCE, API_OMS_K_ROW_START, API_OMS_V_PAGINATION_START, \
     API_OMS_K_ROW_END, API_OMS_V_PAGINATION_END, REQ_URL_OMS_MAIN_2, \
     API_OMS_V_EXCH_NSE, API_OMS_V_EXCH_BSE, API_OMS_V_SEG_CM_1, \
     API_OMS_V_SEG_FO_1, API_OMS_V_SEG_CD_1, API_OMS_V_EXCH_MCX, \
     API_OMS_REQ_PATH_TRADES

    from fy_connections import connectRedis
    from fy_base_functions import logEntryFunc2
    from fy_trading_internal_functions import INTERNAL_getToken_checkStatus, \
     INTERNAL_createAndSendOmsRequest, INTERNAL_decryptOmsResponse, \
     INTERNAL_readOmsDecryptedResponse
    from fy_common_internal_functions import INTERNAL_getSymbolTickersForFyTokensList
    from fy_trading_common_functions import INTERNAL_getNewFyTokensFromOldfyTokensList

except Exception as e:
    print("ERR : %s : %s : %s" % (moduleName, "Could not import module", e))
    sys.exit()


def INTERNAL_getTradeBook_withID4(tokenHash,callingFuncName="",userIp="", fyId=""):
    """
    [FUNCTION]
        Get entire trade book for a specific UserID in tradingview required format
    [PARAMS]
        tokenHash       : This is a hash of (fyId + AppId)
    [RETURN]
        Success : [SUCCESS_C_1,[{..},{..},{..}],""] Each trade is a seperate dict in the list
        {
            "clientId"      :
            "orderDateTime" :
            "orderNumber"   :
            "exchangeOrderNo":
            "exchange"      :
            "transactionType":
            "segment"       :
            "orderType"     :
            "symbol"        :
            "productType"   :
            "tradedQty"     :
            "tradePrice"    :
            "tradeValue"    :
            "tradeNumber"   :
            "id"            :
        }
        Failure : [ERROR_C_1, errorCode,"error message"]
    """
    funcName = "INTERNAL_getTradeBook_withID4"
    try:
        tokenHash = str(tokenHash)
        localMemory = connectRedis(callingFuncName=callingFuncName)

        fyTokenList = INTERNAL_getToken_checkStatus(tokenHash,localMemory=localMemory,callingFuncName=callingFuncName,userIp=userIp,inputFyId=fyId)
        if fyTokenList[0] == ERROR_C_1:
            return fyTokenList
        fyId = fyTokenList[1][0]
        omsTokenId = fyTokenList[1][1]
        aesKey = fyTokenList[1][2]
        appId       = fyTokenList[2]
        source      = fyTokenList[3]

        # If fyId is in beware list
        if fyId in BEWARE_CLIENTS_LIST:
            return [SUCCESS_C_1, [], ""]

        # Send the request to the OMS
        paramsForEncryption = {API_OMS_K_TOKEN_ID_2: omsTokenId, API_OMS_K_CLIENT_ID_1: fyId, API_OMS_K_REQ_SOURCE: source,
                               API_OMS_K_ROW_START: API_OMS_V_PAGINATION_START, API_OMS_K_ROW_END: API_OMS_V_PAGINATION_END}
        urlForRequest = REQ_URL_OMS_MAIN_2 + API_OMS_REQ_PATH_TRADES
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
        readOmsResponseFuncRet2 = INTERNAL_readOmsDecryptedResponse(userInfoList,tokenHash,paramsForEncryption,
                                            urlForRequest,fyId=fyId,localMemory=localMemory,callingFuncName = callingFuncName, userIp=userIp)
        if (readOmsResponseFuncRet2[0] == ERROR_C_1) or (readOmsResponseFuncRet2[0] == ERROR_C_OMS_1):
            return readOmsResponseFuncRet2
        userInfoList = readOmsResponseFuncRet2[1]

        returnList = []
        oldFyTokensDict = {}
        fyTokenDict = {}
        if (len(userInfoList) != 0):
            for i in userInfoList:
                clientId        = i["CLIENT_ID"]
                orderDateTime   = i["ORDER_DATE_TIME"]
                orderNumber     = i["ORDER_NUMBER"]
                exchangeOrderNo = i["EXCH_ORDER_NUMBER"]
                exchange        = i["EXCHANGE"]
                tranType        = i["BUY_SELL"]
                segment         = i["SEGMENT"]
                orderType       = i["ORDER_TYPE"]
                rsSymbol        = i["SYMBOL"]
                productType     = i["PRODUCT"]
                tradedQty       = i["QUANTITY"]
                tradePrice      = i["PRICE"]
                tradeValue      = i["TRADE_VALUE"]
                tradeNumber     = i["TRADE_NUMBER"]
                rowNumber       = i["R"]
                securityId      = i["SEC_ID"]
                pan             = i["PAN_NO"]
                participantType = i["PARTICIPANT_TYPE"]
                marketProFlag   = i["MKT_PROTECT_FLG"]
                marketProVal    = i["MKT_PROTECT_VAL"]
                settlor         = i["SETTLOR"]
                gtcFlag         = i["GTC_FLG"]
                encashFlag      = i["ENCASH_FLG"]
                marketType      = i["MKT_TYPE"]


                if clientId != fyId:
                    logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, f"clientId:{clientId}", f"fyId:{fyId}", i, err_msg="Invalid Client Id response from RS",fyId=fyId)
                    continue

                # String conversion where ever necessary
                try:
                    orderNumber = str(int(float(orderNumber)))
                    rowNumber = int(rowNumber)
                except AttributeError:
                    logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, i, err_msg="AttributeError", code=ERROR_C_OMS_STRING_CONVERSION_FAIL,fyId=fyId)
                    continue
                except Exception as e:
                    logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, i, err_msg=e, code=ERROR_C_OMS_STRING_CONVERSION_FAIL,fyId=fyId)
                    continue

                # Creating our own fyToken for each symbol
                fyToken = ""
                if exchange in [API_OMS_V_EXCH_NSE, API_OMS_V_EXCH_BSE]:
                    if exchange == API_OMS_V_EXCH_NSE:
                        exCode = EXCHANGE_CODE_NSE
                    if exchange == API_OMS_V_EXCH_BSE:
                        exCode = EXCHANGE_CODE_BSE
                    if segment == API_OMS_V_SEG_CM_1:
                        fyToken = "%s%s%s" % (exCode, SYM_SEGMENT_CM, securityId)
                    elif segment == API_OMS_V_SEG_FO_1:
                        fyToken = "%s%s%s" % (exCode, SYM_SEGMENT_FO, securityId)
                    elif segment == API_OMS_V_SEG_CD_1:
                        fyToken = "%s%s%s" % (exCode, SYM_SEGMENT_CD, securityId)
                    else:
                        continue
                elif exchange == API_OMS_V_EXCH_MCX:
                    fyToken = "%s%s%s" %(EXCHANGE_CODE_MCX, SYM_SEGMENT_COM, securityId)
                else:
                    continue
                oldFyTokensDict[fyToken] = ""

                # Pragya - 20191122
                rowDict = {"clientId": clientId, "orderDateTime": orderDateTime, "orderNumber": orderNumber,
                           "exchangeOrderNo": exchangeOrderNo, "exchange": exchange,
                           "transactionType": tranType, "segment": segment, "orderType": orderType,
                           "fyToken":fyToken,
                           "productType": productType, "tradedQty": tradedQty, "tradePrice": tradePrice,
                           "tradeValue": tradeValue, "tradeNumber": tradeNumber, "id": tradeNumber, "row": rowNumber}

                returnList.append(rowDict)

            # Need to convert old fyTokens to new fyTokens
            fyTokensRet = INTERNAL_getNewFyTokensFromOldfyTokensList(list(oldFyTokensDict.keys()),localMemory=localMemory,
                                            callingFuncName = callingFuncName)
            if fyTokensRet[0] == ERROR_C_1:
                return fyTokensRet
            for i in returnList:
                oldFyToken = i["fyToken"]
                i["fyToken"] = fyTokensRet[1][oldFyToken]
                fyTokenDict[i["fyToken"]] = ""

            symbolTickersDict = INTERNAL_getSymbolTickersForFyTokensList(list(fyTokenDict.keys()),localMemory=localMemory,
                                                                         callingFuncName=callingFuncName)
            # symbolTickersDict = INTERNAL_getSymbolTickersForFyTokensList(list(oldFyTokensDict.keys()),localMemory=localMemory,
            #                                                     callingFuncName=callingFuncName)
            if symbolTickersDict[0] == ERROR_C_1:
                return symbolTickersDict
            for i in returnList:
                i["symbol"] = symbolTickersDict[1][i["fyToken"]]
            return [SUCCESS_C_1, returnList, userInfoList]

        else:
            return [SUCCESS_C_1,returnList,userInfoList]


    except Exception as e:
        logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName,callingFuncName, ERROR_C_UNKNOWN, tokenHash, err_msg=e)
        return [ERROR_C_1, ERROR_C_UNKNOWN, ""]


def main():
    pass  # Test here


if __name__ == "__main__":
    main()
