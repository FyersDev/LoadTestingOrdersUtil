moduleName = "fy_trading_internal_functions_holdings"
try:
    import sys

    from fy_base_defines import LOG_STATUS_ERROR_1
    from fy_base_success_error_codes import ERROR_C_1, SUCCESS_C_1, \
     ERROR_C_DEMO_USER, ERROR_C_UNKNOWN, \
     ERROR_C_OMS_1, ERROR_C_DB_NOT_FOUND, ERROR_C_OMS_STRING_CONVERSION_FAIL
     
    from fy_data_and_trade_defines import BEWARE_CLIENTS_LIST, EXCHANGE_CODE_NSE, \
     EXCHANGE_CODE_BSE, SYM_SEGMENT_CM, SYM_ADDITIONAL_PADDING     
    from fy_trading_defines import API_OMS_K_TOKEN_ID_2, API_OMS_K_CLIENT_ID_1, \
     API_OMS_K_REQ_SOURCE, API_OMS_K_ROW_START, API_OMS_V_PAGINATION_START, \
     API_OMS_K_ROW_END, API_OMS_V_PAGINATION_END, REQ_URL_OMS_MAIN_2, \
     API_OMS_REQ_PATH_HOLDINGS, API_OMS_V_EXCH_NSE, API_OMS_V_EXCH_BSE

    from fy_base_functions import logEntryFunc2
    from fy_connections import connectRedis
    from fy_common_internal_functions import getSymbolsFromSymbolMasterCache, \
     INTERNAL_getSymbolTickersForFyTokensList
    from fy_trading_internal_functions import INTERNAL_getToken_checkStatus, \
     INTERNAL_createAndSendOmsRequest, INTERNAL_decryptOmsResponse, \
     INTERNAL_readOmsDecryptedResponse
    from fy_trading_common_functions import INTERNAL_getDemoResponse
     
except Exception as e:
    print("ERR : %s : %s : %s" % (moduleName, "Could not import module", e))
    sys.exit()


def INTERNAL_getHoldings_withID4(tokenHash,callingFuncName="",userIp="", fyId=""):
    """
    [FUNCTION]
        Get Holdings for a specific UserID
    [PARAMS]
            tokenHash       : This is a hash of (fyId + AppId)
    [RETURN]
            Success : [SUCCESS_C_1,[{..},{..},{..}],""] Each trade is a seperate dict in the list
                {
                    "holdingType":
                    "quantity":
                    "remainingQuantity":
                    "symbolLtp":
                    "id":
                    "fyToken":
                }
        Failure : [ERROR_C_1, errorCode,"error message"]
    """
    funcName = "INTERNAL_getHoldings_withID4"
    try:
        tokenHash = str(tokenHash)
        localMemory = connectRedis(callingFuncName=callingFuncName)

        fyTokenList = INTERNAL_getToken_checkStatus(tokenHash, localMemory=localMemory,callingFuncName=callingFuncName,userIp=userIp,inputFyId=fyId)
        if fyTokenList[0] == ERROR_C_1:
            # If the user is a guest
            if fyTokenList[1] == ERROR_C_DEMO_USER:
                ##send the demo response
                demoRespFunc = INTERNAL_getDemoResponse(3,localMemory=localMemory,callingFuncName=callingFuncName)
                return demoRespFunc
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
        paramsForEncryption = {API_OMS_K_TOKEN_ID_2: omsTokenId, API_OMS_K_CLIENT_ID_1: fyId, API_OMS_K_REQ_SOURCE: source, API_OMS_K_ROW_START: API_OMS_V_PAGINATION_START, API_OMS_K_ROW_END: API_OMS_V_PAGINATION_END}
        urlForRequest = REQ_URL_OMS_MAIN_2 + API_OMS_REQ_PATH_HOLDINGS
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
        readOmsResponseFuncRet2 = INTERNAL_readOmsDecryptedResponse(userInfoList,tokenHash, paramsForEncryption,urlForRequest,fyId=fyId, localMemory=localMemory,callingFuncName=callingFuncName, userIp=userIp)
        if (readOmsResponseFuncRet2[0] == ERROR_C_1) or (readOmsResponseFuncRet2[0] == ERROR_C_OMS_1):
            return readOmsResponseFuncRet2
        userInfoList = readOmsResponseFuncRet2[1]
        returnList          = []
        fyTokenDict         = {}
        totalQty            = 0
        totalRemainingQty   = 0
        # total values added in response - Khyati - 20200312
        totalInvestment = 0
        totalCurrentValue = 0
        totalPnl = 0
        overallDict = {"count_total":0, "total_investment":totalInvestment,"total_current_value": totalCurrentValue,"total_pl":totalPnl, "pnl_perc":0}
        if (len(userInfoList) != 0):
            count = 0
            for i in userInfoList:
                rowDict     = {}
                nseScripCode   = i["NSE_SCRIP_CODE"]
                bseScripCode   = i["BSE_SCRIP_CODE"]
                exchange    = i["SEM_EXM_EXCH_ID"]
                isin        = i["ISIN_CODE"]
                hldType     = i["SECURITY_SOURCE_TYPE"]
                quantity    = i["QTY"]
                remQuantity = i["REM_QTY"]
                ltp         = i["LTP"]
                # securityId  = i["SECURITY_ID"] 
                row         = i["R"]
                costPrice   = i["COST_PRICE"]
                qtyUtilized = i["QTY_UTILIZED"]
                collateral  = i["COLLATERAL"]
                marketVal   = i["MARKET_VALUE"]

                # String conversion where ever necessary
                try:
                    quantity = int(quantity)
                    remQuantity = int(remQuantity)
                    ltp = float(ltp)
                    costPrice = float(costPrice)
                    marketVal = float(marketVal)
                except AttributeError:
                    logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, i, err_msg="AttributeError", code=ERROR_C_OMS_STRING_CONVERSION_FAIL,fyId=fyId)
                    continue
                except Exception as e:
                    logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, i, err_msg=e, code=ERROR_C_OMS_STRING_CONVERSION_FAIL,fyId=fyId)
                    continue

                if exchange == API_OMS_V_EXCH_NSE:
                    exCode      = EXCHANGE_CODE_NSE
                    securityId  = nseScripCode
                elif exchange == API_OMS_V_EXCH_BSE:
                    exCode      = EXCHANGE_CODE_BSE
                    securityId  = bseScripCode
                elif exchange == "ALL":
                    exCode      = EXCHANGE_CODE_NSE
                    securityId  = nseScripCode
                else:
                    exCode = EXCHANGE_CODE_NSE
                    securityId = nseScripCode

                fyToken = "%s%s%s%s" % (exCode, SYM_SEGMENT_CM, SYM_ADDITIONAL_PADDING, securityId)
                fyTokenDict[fyToken] = ""

                count += 1
                # total values added in response - Khyati - 20200312
                totalInvestment += (costPrice * remQuantity)
                totalCurrentValue += marketVal
                pnl = marketVal - (costPrice * remQuantity)
                totalPnl += pnl

                rowDict = {"holdingType": hldType, "quantity": quantity, "costPrice": costPrice,
                           "remainingQuantity": remQuantity, "symbolLtp": ltp, "id": count,"fyToken":fyToken,"exchange":exchange,"marketVal":marketVal,"pl":round(pnl,2), "isin":isin} ##isin,exchange, marketVal, pl added in response - Khyati

                returnList.append(rowDict)
                totalQty += quantity
                totalRemainingQty += remQuantity

            symbolTickersDict = INTERNAL_getSymbolTickersForFyTokensList(list(fyTokenDict.keys()),localMemory=localMemory, callingFuncName=callingFuncName)
            if symbolTickersDict[0] == ERROR_C_1:
                return symbolTickersDict

            symbolDetailsRet = getSymbolsFromSymbolMasterCache(symbolTickersDict[1].values())
            symbolsDetails = {}
            if symbolDetailsRet[0] == SUCCESS_C_1:
                symbolsDetails = symbolDetailsRet[1][1]

            for i in returnList:
                try:
                    i["symbol"] = symbolTickersDict[1][i["fyToken"]]
                    i["ex_sym"] = symbolsDetails[i["symbol"]]["underSym"]
                    i["description"] = symbolsDetails[i["symbol"]]["symbolDesc"]
                    i["lot_size"] = symbolsDetails[i["symbol"]]["minLotSize"]
                    i["tick_size"] = symbolsDetails[i["symbol"]]["tickSize"]
                except Exception as e:
                    i["symbol"] = ""        # This will happen if the fyToken does not exist in the db.
                    i["ex_sym"] = ""
                    i["description"] = ""
                    i["lot_size"] = 0
                    i["tick_size"] = 0.0
                    logEntryFunc2(LOG_STATUS_ERROR_1, moduleName,funcName,callingFuncName, i, i["fyToken"], err_msg=e, code=ERROR_C_DB_NOT_FOUND,fyId=fyId)
                    
            ## Added keys ex_sym,description,lot_size,tick_size - 2021-07-30

            # total values added in response - Khyati - 20200312
            totalInvestment = round(totalInvestment,2)
            totalCurrentValue = round(totalCurrentValue,2)
            totalPnl = round(totalPnl,2)
            overallDict["count_total"] = count
            overallDict["total_investment"] = totalInvestment
            overallDict["total_current_value"] = totalCurrentValue
            overallDict["total_pl"] = totalPnl
            if totalInvestment == 0 or totalRemainingQty == 0:
                overallDict["pnl_perc"] = 0.0
            else:
                overallDict["pnl_perc"] = round((totalPnl/totalInvestment)*100,4)

            return [SUCCESS_C_1, [returnList,overallDict], userInfoList]

        # If the holdings is empty
        else:
            if fyId == 'FM0224':
                returnList = [
                                {
                                    "ex_sym": "MTARTECH",
                                    "description": "MTAR TECHNOLOGIES LIMITED",
                                    "exchange": "ALL",
                                    "symbol": "NSE:MTARTECH-EQ",
                                    "lot_size": 1,
                                    "marketVal": 28863.0,
                                    "fyToken": "10100000002709",
                                    "id": 1,
                                    "tick_size": 0.05,
                                    "remainingQuantity": 20,
                                    "symbolLtp": 1443.15,
                                    "holdingType": "HLD",
                                    "costPrice": 1082.15,
                                    "isin": "INE864I01014",
                                    "pl": 7220.0,
                                    "quantity": 20
                                },
                                {
                                    "ex_sym": "YESBANK",
                                    "description": "YES BANK LIMITED",
                                    "exchange": "ALL",
                                    "symbol": "NSE:YESBANK-EQ",
                                    "lot_size": 1,
                                    "marketVal": 5202.0,
                                    "fyToken": "101000000011915",
                                    "id": 2,
                                    "tick_size": 0.05,
                                    "remainingQuantity": 408,
                                    "symbolLtp": 12.75,
                                    "holdingType": "HLD",
                                    "costPrice": 14.7,
                                    "isin": "INE528G01035",
                                    "pl": -795.5999999999995,
                                    "quantity": 408
                                },
                                {
                                    "ex_sym": "TITAN",
                                    "description": "TITAN COMPANY LIMITED",
                                    "exchange": "ALL",
                                    "symbol": "NSE:TITAN-EQ",
                                    "lot_size": 1,
                                    "marketVal": 6858.2,
                                    "fyToken": "10100000003506",
                                    "id": 3,
                                    "tick_size": 0.05,
                                    "remainingQuantity": 4,
                                    "symbolLtp": 1714.55,
                                    "holdingType": "HLD",
                                    "costPrice": 1065.95,
                                    "isin": "INE280A01028",
                                    "pl": 2594.3999999999996,
                                    "quantity": 4
                                },
                                {
                                    "ex_sym": "HINDUNILVR",
                                    "description": "HINDUSTAN UNILEVER LTD.",
                                    "exchange": "ALL",
                                    "symbol": "NSE:HINDUNILVR-EQ",
                                    "lot_size": 1,
                                    "marketVal": 6999.9,
                                    "fyToken": "10100000001394",
                                    "id": 4,
                                    "tick_size": 0.05,
                                    "remainingQuantity": 3,
                                    "symbolLtp": 2333.3,
                                    "holdingType": "HLD",
                                    "costPrice": 2219.33,
                                    "isin": "INE030A01027",
                                    "pl": 341.90999999999985,
                                    "quantity": 3
                                },
                                {
                                    "ex_sym": "HDFC",
                                    "description": "HDFC LTD",
                                    "exchange": "ALL",
                                    "symbol": "NSE:HDFC-EQ",
                                    "lot_size": 1,
                                    "marketVal": 9764.6,
                                    "fyToken": "10100000001330",
                                    "id": 5,
                                    "tick_size": 0.05,
                                    "remainingQuantity": 4,
                                    "symbolLtp": 2441.15,
                                    "holdingType": "HLD",
                                    "costPrice": 2062.28,
                                    "isin": "INE001A01036",
                                    "pl": 1515.4799999999996,
                                    "quantity": 4
                                },
                                {
                                    "ex_sym": "SETFNIF50",
                                    "description": "SBI-ETF NIFTY 50",
                                    "exchange": "NSE",
                                    "symbol": "NSE:SETFNIF50-EQ",
                                    "lot_size": 1,
                                    "marketVal": 12685.03,
                                    "fyToken": "101000000010176",
                                    "id": 6,
                                    "tick_size": 0.01,
                                    "remainingQuantity": 79,
                                    "symbolLtp": 160.57,
                                    "holdingType": "HLD",
                                    "costPrice": 139.02,
                                    "isin": "INF200KA1FS1",
                                    "pl": 1702.4500000000007,
                                    "quantity": 79
                                },
                                {
                                    "ex_sym": "MSPL",
                                    "description": "MSP STEEL & POWER LTD.",
                                    "exchange": "ALL",
                                    "symbol": "NSE:MSPL-EQ",
                                    "lot_size": 1,
                                    "marketVal": 11.85,
                                    "fyToken": "101000000011919",
                                    "id": 7,
                                    "tick_size": 0.05,
                                    "remainingQuantity": 1,
                                    "symbolLtp": 11.85,
                                    "holdingType": "HLD",
                                    "costPrice": 11.5,
                                    "isin": "INE752G01015",
                                    "pl": 0.34999999999999964,
                                    "quantity": 1
                                },
                                {
                                    "ex_sym": "TCS",
                                    "description": "TATA CONSULTANCY SERV LT",
                                    "exchange": "ALL",
                                    "symbol": "NSE:TCS-EQ",
                                    "lot_size": 1,
                                    "marketVal": 6334.9,
                                    "fyToken": "101000000011536",
                                    "id": 8,
                                    "tick_size": 0.05,
                                    "remainingQuantity": 2,
                                    "symbolLtp": 3167.45,
                                    "holdingType": "HLD",
                                    "costPrice": 2287.9,
                                    "isin": "INE467B01029",
                                    "pl": 1759.0999999999995,
                                    "quantity": 2
                                },
                                {
                                    "ex_sym": "IMAGICAA",
                                    "description": "IMAGICAAWORLD ENT LTD",
                                    "exchange": "ALL",
                                    "symbol": "NSE:IMAGICAA-EQ",
                                    "lot_size": 1,
                                    "marketVal": 8.7,
                                    "fyToken": "10100000007672",
                                    "id": 9,
                                    "tick_size": 0.05,
                                    "remainingQuantity": 1,
                                    "symbolLtp": 8.7,
                                    "holdingType": "HLD",
                                    "costPrice": 4.0,
                                    "isin": "INE172N01012",
                                    "pl": 4.699999999999999,
                                    "quantity": 1
                                },
                                {
                                    "ex_sym": "LT",
                                    "description": "LARSEN & TOUBRO LTD.",
                                    "exchange": "ALL",
                                    "symbol": "NSE:LT-EQ",
                                    "lot_size": 1,
                                    "marketVal": 6405.8,
                                    "fyToken": "101000000011483",
                                    "id": 10,
                                    "tick_size": 0.05,
                                    "remainingQuantity": 4,
                                    "symbolLtp": 1601.45,
                                    "holdingType": "HLD",
                                    "costPrice": 956.2,
                                    "isin": "INE018A01030",
                                    "pl": 2581.0,
                                    "quantity": 4
                                },
                                {
                                    "ex_sym": "MON100",
                                    "description": "MOTILAL OS NASDAQ100 ETF",
                                    "exchange": "ALL",
                                    "symbol": "NSE:MON100-EQ",
                                    "lot_size": 1,
                                    "marketVal": 32853.0,
                                    "fyToken": "101000000022739",
                                    "id": 11,
                                    "tick_size": 0.01,
                                    "remainingQuantity": 300,
                                    "symbolLtp": 109.51,
                                    "holdingType": "HLD",
                                    "costPrice": 99.78,
                                    "isin": "INF247L01AP3",
                                    "pl": 2919.0,
                                    "quantity": 300
                                },
                                {
                                    "ex_sym": "KOTAKBKETF",
                                    "description": "KOTAKMAMC-KOTAKBKETF",
                                    "exchange": "NSE",
                                    "symbol": "NSE:KOTAKBKETF-EQ",
                                    "lot_size": 1,
                                    "marketVal": 27285.18,
                                    "fyToken": "10100000005851",
                                    "id": 12,
                                    "tick_size": 0.01,
                                    "remainingQuantity": 78,
                                    "symbolLtp": 349.81,
                                    "holdingType": "HLD",
                                    "costPrice": 278.2,
                                    "isin": "INF174K01F59",
                                    "pl": 5585.580000000002,
                                    "quantity": 78
                                },
                                {
                                    "ex_sym": "IDEA",
                                    "description": "VODAFONE IDEA LIMITED",
                                    "exchange": "ALL",
                                    "symbol": "NSE:IDEA-EQ",
                                    "lot_size": 1,
                                    "marketVal": 3291.75,
                                    "fyToken": "101000000014366",
                                    "id": 13,
                                    "tick_size": 0.05,
                                    "remainingQuantity": 399,
                                    "symbolLtp": 8.25,
                                    "holdingType": "HLD",
                                    "costPrice": 8.99,
                                    "isin": "INE669E01016",
                                    "pl": -295.2600000000002,
                                    "quantity": 399
                                },
                                {
                                    "ex_sym": "BAJFINANCE",
                                    "description": "BAJAJ FINANCE LIMITED",
                                    "exchange": "ALL",
                                    "symbol": "NSE:BAJFINANCE-EQ",
                                    "lot_size": 1,
                                    "marketVal": 6228.1,
                                    "fyToken": "1010000000317",
                                    "id": 14,
                                    "tick_size": 0.05,
                                    "remainingQuantity": 1,
                                    "symbolLtp": 6228.1,
                                    "holdingType": "HLD",
                                    "costPrice": 3443.45,
                                    "isin": "INE296A01024",
                                    "pl": 2784.6500000000005,
                                    "quantity": 1
                                },
                                {
                                    "ex_sym": "HDFCBANK",
                                    "description": "HDFC BANK LTD",
                                    "exchange": "ALL",
                                    "symbol": "NSE:HDFCBANK-EQ",
                                    "lot_size": 1,
                                    "marketVal": 5705.8,
                                    "fyToken": "10100000001333",
                                    "id": 15,
                                    "tick_size": 0.05,
                                    "remainingQuantity": 4,
                                    "symbolLtp": 1426.45,
                                    "holdingType": "HLD",
                                    "costPrice": 1066.9,
                                    "isin": "INE040A01034",
                                    "pl": 1438.1999999999998,
                                    "quantity": 4
                                },
                                {
                                    "ex_sym": "RELIANCE",
                                    "description": "RELIANCE INDUSTRIES LTD",
                                    "exchange": "ALL",
                                    "symbol": "NSE:RELIANCE-EQ",
                                    "lot_size": 1,
                                    "marketVal": 4070.6,
                                    "fyToken": "10100000002885",
                                    "id": 16,
                                    "tick_size": 0.05,
                                    "remainingQuantity": 2,
                                    "symbolLtp": 2035.3,
                                    "holdingType": "HLD",
                                    "costPrice": 2136.25,
                                    "isin": "INE002A01018",
                                    "pl": -201.9000000000001,
                                    "quantity": 2
                                },
                                {
                                    "ex_sym": "GOLDBEES",
                                    "description": "NIP IND ETF GOLD BEES",
                                    "exchange": "ALL",
                                    "symbol": "NSE:GOLDBEES-EQ",
                                    "lot_size": 1,
                                    "marketVal": 11402.24,
                                    "fyToken": "101000000014428",
                                    "id": 17,
                                    "tick_size": 0.01,
                                    "remainingQuantity": 272,
                                    "symbolLtp": 41.92,
                                    "holdingType": "HLD",
                                    "costPrice": 42.65,
                                    "isin": "INF204KB17I5",
                                    "pl": -198.5599999999995,
                                    "quantity": 272
                                }
                            ]

                overallDict = {
                                    "total_pl": 28955.5,
                                    "total_investment": 145015.15,
                                    "pnl_perc": 0.0126,
                                    "count_total": 17,
                                    "total_current_value": 173970.65
                            }

            return [SUCCESS_C_1, [returnList,overallDict], userInfoList]

    except Exception as e:
        logEntryFunc2(LOG_STATUS_ERROR_1, moduleName,funcName,callingFuncName, e, ERROR_C_UNKNOWN, tokenHash)
        return [ERROR_C_1, ERROR_C_UNKNOWN, ""]


def main():
    None


if __name__ == "__main__":
    main()
