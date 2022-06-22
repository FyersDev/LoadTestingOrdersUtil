moduleName = "fy_trading_internal_functions_positions_GET"
try:
    import sys

    from fy_base_defines import LOG_STATUS_ERROR_1
    from fy_base_success_error_codes import ERROR_C_1, SUCCESS_C_1, \
     ERROR_C_DEMO_USER, ERROR_C_UNKNOWN, \
     ERROR_C_OMS_1, ERROR_C_OMS_STRING_CONVERSION_FAIL
    from fy_common_api_keys_values import API_V_ORDER_SIDE_BUY_1, \
     API_V_ORDER_SIDE_SELL_1
    from fy_data_and_trade_defines import BEWARE_CLIENTS_LIST, EXCHANGE_CODE_NSE, \
     EXCHANGE_CODE_BSE, SYM_SEGMENT_CM, SYM_SEGMENT_FO, SYM_SEGMENT_CD, \
     EXCHANGE_CODE_MCX, SYM_SEGMENT_COM
    from fy_trading_defines import API_OMS_K_TOKEN_ID_2, API_OMS_K_CLIENT_ID_1, \
     API_OMS_K_REQ_SOURCE, API_OMS_K_ROW_START, API_OMS_V_PAGINATION_START, \
     API_OMS_K_ROW_END, API_OMS_V_PAGINATION_END, REQ_URL_OMS_MAIN_2, \
     API_OMS_V_EXCH_NSE, API_OMS_V_EXCH_BSE, API_OMS_REQ_PATH_POSITIONS, \
     API_OMS_V_ORDER_PROD_CNC_1, API_OMS_V_ORDER_PROD_CNC_2, API_OMS_V_ORDER_PROD_MARGIN_1, \
     API_OMS_V_ORDER_PROD_MARGIN_2, API_OMS_V_ORDER_PROD_INTRADAY_1, \
     API_OMS_V_ORDER_PROD_INTRADAY_2, API_OMS_V_ORDER_PROD_CO_1, API_OMS_V_ORDER_PROD_CO_2, \
     API_OMS_V_ORDER_PROD_BO_1, API_OMS_V_ORDER_PROD_BO_2, API_OMS_V_SEG_CM_1, \
     API_OMS_V_SEG_FO_1, API_OMS_V_SEG_CD_1, API_OMS_V_EXCH_MCX

    from fy_connections import connectRedis
    from fy_base_functions import logEntryFunc2
    from fy_trading_internal_functions import INTERNAL_getToken_checkStatus, \
     INTERNAL_createAndSendOmsRequest, INTERNAL_decryptOmsResponse, \
     INTERNAL_readOmsDecryptedResponse
    from fy_common_internal_functions import getSymbolsFromSymbolMasterCache, \
     INTERNAL_getSymbolTickersForFyTokensList
    from fy_trading_common_functions import INTERNAL_getDemoResponse
    from fy_trading_common_functions import INTERNAL_getNewFyTokensFromOldfyTokensList

except Exception as e:
    print("ERR : %s : %s : %s" % (moduleName, "Could not import module", e))
    sys.exit()


def INTERNAL_getNetPositions_withID4(tokenHash,callingFuncName="",userIp="", fyId=""):
    """
    [FUNCTION]
        Get net positions for a specific UserID
    [PARAMS]
        tokenHash       : This is a hash of (fyId + AppId)
    [RETURN]
        Success : [SUCCESS_C_1,[{..},{..},{..}],""] Each trade is a seperate dict in the list
                {
                    "netQty":
                    "qty":
                    "net_price":
                    "avg_price":
                    "side":
                    "productType":
                    "realized_profit":
                    "pl":
                    "totalPnl":
                    "buyQty":
                    "ltp":
                    "buyAvg":
                    "sellQty":
                    "sellAvg":
                    "slNo":
                    "fyToken":
                }
        Failure : [ERROR_C_1, errorCode,"error message"]
    """
    funcName = "INTERNAL_getNetPositions_withID4"

    try:
        localMemory = connectRedis(callingFuncName=callingFuncName)

        tokenHash = str(tokenHash)
        fyTokenList = INTERNAL_getToken_checkStatus(tokenHash,localMemory=localMemory,callingFuncName=callingFuncName,userIp=userIp,inputFyId=fyId)
        if fyTokenList[0] == ERROR_C_1:
            # If the user is a guest
            if fyTokenList[1] == ERROR_C_DEMO_USER:
                ##send the demo response
                demoRespFunc = INTERNAL_getDemoResponse(2,localMemory=localMemory,callingFuncName=callingFuncName)
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
        paramsForEncryption = {API_OMS_K_TOKEN_ID_2: omsTokenId, API_OMS_K_CLIENT_ID_1: fyId, API_OMS_K_REQ_SOURCE: source,
                               API_OMS_K_ROW_START: API_OMS_V_PAGINATION_START, API_OMS_K_ROW_END: API_OMS_V_PAGINATION_END}
        urlForRequest = REQ_URL_OMS_MAIN_2 + API_OMS_REQ_PATH_POSITIONS
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
        readOmsResponseFuncRet2 = INTERNAL_readOmsDecryptedResponse(userInfoList, tokenHash, paramsForEncryption,
                                           urlForRequest,fyId=fyId, localMemory=localMemory,callingFuncName=callingFuncName, userIp=userIp)
        if (readOmsResponseFuncRet2[0] == ERROR_C_1) or (readOmsResponseFuncRet2[0] == ERROR_C_OMS_1):
            return readOmsResponseFuncRet2
        userInfoList = readOmsResponseFuncRet2[1]

        returnList = []
        fyTokenDict = {}
        oldFyTokensDict = {}
        rowCount = 0
        # added for overall values - Khyati
        open_count = 0
        total_pl = 0
        total_realized = 0
        total_unrealized = 0
        overallDict = {"count_total":rowCount, "count_open":open_count,"pl_total": total_pl,"pl_realized":total_realized, "pl_unrealized":total_unrealized}
        if (len(userInfoList) != 0):
            for i in userInfoList:
                rowDict = {}
                clientId = i["CLIENT_ID"]
                securityId = i["SECURITY_ID"]
                instrument = i["INSTRUMENT"]
                symSecId = i["SYMB_SECID"]
                exchange = i["EXCH_ID"]
                expiryDate = i["EXPIRY_DATE"]
                strikePrice = i["STRIKE_PRICE"]
                optionType = i["OPTION_TYPE"]
                totalBuyQty = i["TOT_BUY_QTY"]
                totalBuyVal = i["TOT_BUY_VAL"]
                buyAverage = i["BUY_AVG"]
                totalSellQty = i["TOT_SELL_QTY"]
                totalSellVal = i["TOT_SELL_VAL"]
                sellAverage = i["SELL_AVG"]
                netQty = i["NET_QTY"]
                netVal = i["NET_VAL"]
                netAvg = i["NET_AVG"]
                grossQty = i["GROSS_QTY"]
                grossVal = i["GROSS_VAL"]
                segment = i["SEGMNT"]
                marketType = i["MKT_TYPE"]
                productType = i["PROD_ID"]
                regular_lot = i["SEM_NSE_REGULAR_LOT"]
                ltp = i["LAST_TRADED_PRICE"]
                realizedPnl = i["REALISED_PROFIT"]
                mtm = i["MTM"]
                rbiReferenceRate = i["RBI_REFERENCE_RATE"]
                crossCurrencyFlag = i["CROSS_CUR_FLAG"]
                rowNumber = rowCount
                qtyMultiplierComm = i["COMM_MULTIPLIER"]

                if clientId != fyId:
                    logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, f"clientId:{clientId}", f"fyId:{fyId}", i, err_msg="Invalid Client Id response from RS",fyId=fyId)
                    continue

                # Change the product type
                if productType == API_OMS_V_ORDER_PROD_CNC_1:
                    productType = API_OMS_V_ORDER_PROD_CNC_2
                elif productType == API_OMS_V_ORDER_PROD_MARGIN_1:
                    productType = API_OMS_V_ORDER_PROD_MARGIN_2
                elif productType == API_OMS_V_ORDER_PROD_INTRADAY_1:
                    productType = API_OMS_V_ORDER_PROD_INTRADAY_2
                elif productType == API_OMS_V_ORDER_PROD_CO_1:
                    productType = API_OMS_V_ORDER_PROD_CO_2
                elif productType == API_OMS_V_ORDER_PROD_BO_1:
                    productType = API_OMS_V_ORDER_PROD_BO_2

                # String conversion where ever necessary
                try:
                    netQty = int(netQty)
                    qty = abs(netQty)
                    realizedPnl = float(realizedPnl)
                    mtm = float(mtm)
                    ltp = float(ltp) ##ltp added - 20200221 - Khyati
                    productType = productType.upper()
                    totalBuyQty = int(totalBuyQty)
                    buyAverage = float(buyAverage)
                    totalSellQty = int(totalSellQty)
                    sellAverage = float(sellAverage)
                    rowNumber = int(rowNumber)
                    rbiReferenceRate = float(rbiReferenceRate)
                    totalBuyVal = float(totalBuyVal)
                    totalSellVal = float(totalSellVal)
                    # None
                except AttributeError:
                    logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, i, err_msg="AttributeError", code=ERROR_C_OMS_STRING_CONVERSION_FAIL,fyId=fyId)
                    continue
                except Exception as e:
                    logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, i, err_msg=e, code=ERROR_C_OMS_STRING_CONVERSION_FAIL,fyId=fyId)
                    continue

                totalPnl = realizedPnl + mtm
                if netQty > 0:
                    positionSide    = API_V_ORDER_SIDE_BUY_1
                    avgPrice        = buyAverage
                elif netQty < 0:
                    positionSide    = API_V_ORDER_SIDE_SELL_1
                    avgPrice        = sellAverage
                else:
                    positionSide    = 0  ##positionSide changed to 0 instead of "" - Khyati
                    avgPrice        = 0

                # Creating our own fyToken for each symbol
                fyToken = ""
                if exchange in [API_OMS_V_EXCH_NSE, API_OMS_V_EXCH_BSE]:
                    if exchange == API_OMS_V_EXCH_NSE:
                        exchangeCode = EXCHANGE_CODE_NSE
                    if exchange == API_OMS_V_EXCH_BSE:
                        exchangeCode = EXCHANGE_CODE_BSE
                    if segment == API_OMS_V_SEG_CM_1:

                        fyToken = "%s%s%s" % (
                            exchangeCode, SYM_SEGMENT_CM, securityId)
                    elif segment == API_OMS_V_SEG_FO_1:
                        fyToken = "%s%s%s" % (exchangeCode, SYM_SEGMENT_FO, securityId)
                    elif segment == API_OMS_V_SEG_CD_1:
                        fyToken = "%s%s%s" % (exchangeCode, SYM_SEGMENT_CD, securityId)
                    else:
                        continue
                elif exchange == API_OMS_V_EXCH_MCX:
                    fyToken = "%s%s%s" % (EXCHANGE_CODE_MCX, SYM_SEGMENT_COM, securityId)
                else:
                    continue
                oldFyTokensDict[fyToken] = ""
                fyTokenDict[fyToken] = ""
                rowCount += 1
                # added for overall values - Khyati
                if netQty != 0:
                    open_count += 1

                total_pl += totalPnl
                total_realized += realizedPnl
                total_unrealized += mtm

                rowDict = {"netQty": netQty, "qty": qty,
                           "avgPrice": avgPrice, "netAvg": netAvg,
                           "side": positionSide, "productType": productType,
                           "realized_profit": realizedPnl, "unrealized_profit": mtm, "pl": totalPnl,
                           "buyQty": totalBuyQty, "buyAvg": buyAverage,
                           "sellQty": totalSellQty, "sellAvg": sellAverage,
                           "buyVal":totalBuyVal,"sellVal":totalSellVal,
                           "slNo": rowNumber, "fyToken": fyToken, "dummy": "          ",
                           "crossCurrency": crossCurrencyFlag, "rbiRefRate": rbiReferenceRate,
                           "qtyMulti_com": qtyMultiplierComm, "segment" : segment, "ltp":ltp} ##ltp added - 20200221 - Khyati - buyVal sellVal added - 20200422
                returnList.append(rowDict)

            # Need to convert old fyTokens to new fyTokens
            fyTokensRet = INTERNAL_getNewFyTokensFromOldfyTokensList(list(oldFyTokensDict.keys()),
                                                                     localMemory=localMemory,
                                                                     callingFuncName=callingFuncName)
            if fyTokensRet[0] == ERROR_C_1:
                return fyTokensRet
            fyTokenDict = {}
            for i in returnList:
                oldFyToken = i["fyToken"]
                i["fyToken"] = fyTokensRet[1][oldFyToken]
                fyTokenDict[i["fyToken"]] = ""

            # This will get returned
            symbolTickersDict = INTERNAL_getSymbolTickersForFyTokensList(list(fyTokenDict.keys()),localMemory=localMemory,
                                                                         callingFuncName=callingFuncName)
            if symbolTickersDict[0] == ERROR_C_1:
                return symbolTickersDict

            symbolDetailsRet = getSymbolsFromSymbolMasterCache(symbolTickersDict[1].values())
            symbolsDetails = {}
            if symbolDetailsRet[0] == SUCCESS_C_1:
                symbolsDetails = symbolDetailsRet[1][1]

            for i in returnList:
                i["symbol"] = symbolTickersDict[1][i["fyToken"]]
                i["id"] = "%s-%s" % (i["symbol"], i["productType"])
                try:
                    i["ex_sym"] = symbolsDetails[i["symbol"]]["underSym"]
                    i["description"] = symbolsDetails[i["symbol"]]["symbolDesc"]
                    i["lot_size"] = symbolsDetails[i["symbol"]]["minLotSize"]
                    i["tick_size"] = symbolsDetails[i["symbol"]]["tickSize"]
                except Exception as e:
                    i["ex_sym"] = ""
                    i["description"] = ""
                    i["lot_size"] = 0
                    i["tick_size"] = 0.0
                    logEntryFunc2(LOG_STATUS_ERROR_1, moduleName,funcName,callingFuncName, i, err_msg=e,fyId=fyId)

            # added for overall values - Khyati
            overallDict["count_total"] = rowCount
            overallDict["count_open"] = open_count
            overallDict["pl_total"] = round(total_pl,2)
            overallDict["pl_realized"] = round(total_realized,2)
            overallDict["pl_unrealized"] = round(total_unrealized,2)

            return [SUCCESS_C_1, [returnList,overallDict], userInfoList]

        # If the netpositions is empty
        else:
            if fyId == 'FM0224':
                returnList = [
                                    {
                                        "ex_sym": "IOC",
                                        "crossCurrency": "N",
                                        "qty": 0,
                                        "lot_size": 1,
                                        "realized_profit": -1.05,
                                        "id": "NSE:IOC-EQ-INTRADAY",
                                        "tick_size": 0.05,
                                        "unrealized_profit": 0.0,
                                        "buyQty": 1,
                                        "sellAvg": 103.0,
                                        "sellQty": 1,
                                        "buyAvg": 104.05,
                                        "buyVal": 104.05,
                                        "description": "INDIAN OIL CORP LTD",
                                        "sellVal": 103.0,
                                        "symbol": "NSE:IOC-EQ",
                                        "fyToken": "10100000001624",
                                        "slNo": 0,
                                        "avgPrice": 0,
                                        "segment": "E",
                                        "dummy": "          ",
                                        "ltp": 103.15,
                                        "rbiRefRate": 1.0,
                                        "side": 0,
                                        "netQty": 0,
                                        "pl": -1.05,
                                        "productType": "INTRADAY",
                                        "netAvg": 0.0,
                                        "qtyMulti_com": 1.0
                                    },
                                    {
                                        "ex_sym": "IOC",
                                        "crossCurrency": "N",
                                        "qty": 0,
                                        "lot_size": 1,
                                        "realized_profit": 0.1,
                                        "id": "NSE:IOC-EQ-CO",
                                        "tick_size": 0.05,
                                        "unrealized_profit": 0.0,
                                        "buyQty": 1,
                                        "sellAvg": 103.85,
                                        "sellQty": 1,
                                        "buyAvg": 103.75,
                                        "buyVal": 103.75,
                                        "description": "INDIAN OIL CORP LTD",
                                        "sellVal": 103.85,
                                        "symbol": "NSE:IOC-EQ",
                                        "fyToken": "10100000001624",
                                        "slNo": 1,
                                        "avgPrice": 0,
                                        "segment": "E",
                                        "dummy": "          ",
                                        "ltp": 103.15,
                                        "rbiRefRate": 1.0,
                                        "side": 0,
                                        "netQty": 0,
                                        "pl": 0.1,
                                        "productType": "CO",
                                        "netAvg": 0.0,
                                        "qtyMulti_com": 1.0
                                    },
                                    {
                                        "ex_sym": "ITC",
                                        "crossCurrency": "N",
                                        "qty": 0,
                                        "lot_size": 1,
                                        "realized_profit": 0.2,
                                        "id": "NSE:ITC-EQ-INTRADAY",
                                        "tick_size": 0.05,
                                        "unrealized_profit": 0.0,
                                        "buyQty": 1,
                                        "sellAvg": 206.0,
                                        "sellQty": 1,
                                        "buyAvg": 205.8,
                                        "buyVal": 205.8,
                                        "description": "ITC LTD",
                                        "sellVal": 206.0,
                                        "symbol": "NSE:ITC-EQ",
                                        "fyToken": "10100000001660",
                                        "slNo": 2,
                                        "avgPrice": 0,
                                        "segment": "E",
                                        "dummy": "          ",
                                        "ltp": 204.95,
                                        "rbiRefRate": 1.0,
                                        "side": 0,
                                        "netQty": 0,
                                        "pl": 0.2,
                                        "productType": "INTRADAY",
                                        "netAvg": 0.0,
                                        "qtyMulti_com": 1.0
                                    },
                                    {
                                        "ex_sym": "IRFC",
                                        "crossCurrency": "N",
                                        "qty": 0,
                                        "lot_size": 1,
                                        "realized_profit": -0.05,
                                        "id": "NSE:IRFC-EQ-CNC",
                                        "tick_size": 0.05,
                                        "unrealized_profit": 0.0,
                                        "buyQty": 1,
                                        "sellAvg": 22.9,
                                        "sellQty": 1,
                                        "buyAvg": 22.95,
                                        "buyVal": 22.95,
                                        "description": "INDIAN RAILWAY FIN CORP L",
                                        "sellVal": 22.9,
                                        "symbol": "NSE:IRFC-EQ",
                                        "fyToken": "10100000002029",
                                        "slNo": 3,
                                        "avgPrice": 0,
                                        "segment": "E",
                                        "dummy": "          ",
                                        "ltp": 23.0,
                                        "rbiRefRate": 1.0,
                                        "side": 0,
                                        "netQty": 0,
                                        "pl": -0.05,
                                        "productType": "CNC",
                                        "netAvg": 0.0,
                                        "qtyMulti_com": 1.0
                                    },
                                    {
                                        "ex_sym": "GOLDPETAL",
                                        "crossCurrency": "N",
                                        "qty": 0,
                                        "lot_size": 1,
                                        "realized_profit": -1.0,
                                        "id": "MCX:GOLDPETAL21AUGFUT-INTRADAY",
                                        "tick_size": "1.0000",
                                        "unrealized_profit": 0.0,
                                        "buyQty": 1,
                                        "sellAvg": 4801.0,
                                        "sellQty": 1,
                                        "buyAvg": 4802.0,
                                        "buyVal": 4802.0,
                                        "description": "21 Aug 31 FUT",
                                        "sellVal": 4801.0,
                                        "symbol": "MCX:GOLDPETAL21AUGFUT",
                                        "fyToken": "1120210831229420",
                                        "slNo": 4,
                                        "avgPrice": 0,
                                        "segment": "M",
                                        "dummy": "          ",
                                        "ltp": 4811.0,
                                        "rbiRefRate": 1.0,
                                        "side": 0,
                                        "netQty": 0,
                                        "pl": -1.0,
                                        "productType": "INTRADAY",
                                        "netAvg": 0.0,
                                        "qtyMulti_com": 1.0
                                    },
                                    {
                                        "ex_sym": "ONGC",
                                        "crossCurrency": "N",
                                        "qty": 0,
                                        "lot_size": 1,
                                        "realized_profit": -0.05,
                                        "id": "NSE:ONGC-EQ-CO",
                                        "tick_size": 0.05,
                                        "unrealized_profit": 0.0,
                                        "buyQty": 1,
                                        "sellAvg": 114.55,
                                        "sellQty": 1,
                                        "buyAvg": 114.6,
                                        "buyVal": 114.6,
                                        "description": "OIL AND NATURAL GAS CORP.",
                                        "sellVal": 114.55,
                                        "symbol": "NSE:ONGC-EQ",
                                        "fyToken": "10100000002475",
                                        "slNo": 5,
                                        "avgPrice": 0,
                                        "segment": "E",
                                        "dummy": "          ",
                                        "ltp": 115.3,
                                        "rbiRefRate": 1.0,
                                        "side": 0,
                                        "netQty": 0,
                                        "pl": -0.05,
                                        "productType": "CO",
                                        "netAvg": 0.0,
                                        "qtyMulti_com": 1.0
                                    },
                                    {
                                        "ex_sym": "SAIL",
                                        "crossCurrency": "N",
                                        "qty": 0,
                                        "lot_size": 1,
                                        "realized_profit": 0.65,
                                        "id": "NSE:SAIL-EQ-BO",
                                        "tick_size": 0.05,
                                        "unrealized_profit": 0.0,
                                        "buyQty": 1,
                                        "sellAvg": 142.65,
                                        "sellQty": 1,
                                        "buyAvg": 142.0,
                                        "buyVal": 142.0,
                                        "description": "STEEL AUTHORITY OF INDIA",
                                        "sellVal": 142.65,
                                        "symbol": "NSE:SAIL-EQ",
                                        "fyToken": "10100000002963",
                                        "slNo": 6,
                                        "avgPrice": 0,
                                        "segment": "E",
                                        "dummy": "          ",
                                        "ltp": 142.05,
                                        "rbiRefRate": 1.0,
                                        "side": 0,
                                        "netQty": 0,
                                        "pl": 0.65,
                                        "productType": "BO",
                                        "netAvg": 0.0,
                                        "qtyMulti_com": 1.0
                                    },
                                    {
                                        "ex_sym": "SBIN",
                                        "crossCurrency": "N",
                                        "qty": 0,
                                        "lot_size": 1,
                                        "realized_profit": 0.1,
                                        "id": "NSE:SBIN-EQ-INTRADAY",
                                        "tick_size": 0.05,
                                        "unrealized_profit": 0.0,
                                        "buyQty": 1,
                                        "sellAvg": 438.0,
                                        "sellQty": 1,
                                        "buyAvg": 437.9,
                                        "buyVal": 437.9,
                                        "description": "STATE BANK OF INDIA",
                                        "sellVal": 438.0,
                                        "symbol": "NSE:SBIN-EQ",
                                        "fyToken": "10100000003045",
                                        "slNo": 7,
                                        "avgPrice": 0,
                                        "segment": "E",
                                        "dummy": "          ",
                                        "ltp": 431.8,
                                        "rbiRefRate": 1.0,
                                        "side": 0,
                                        "netQty": 0,
                                        "pl": 0.1,
                                        "productType": "INTRADAY",
                                        "netAvg": 0.0,
                                        "qtyMulti_com": 1.0
                                    },
                                    {
                                        "ex_sym": "NIFTY",
                                        "crossCurrency": "N",
                                        "qty": 0,
                                        "lot_size": 50,
                                        "realized_profit": -2.5,
                                        "id": "NSE:NIFTY2180515000PE-INTRADAY",
                                        "tick_size": 0.05,
                                        "unrealized_profit": 0.0,
                                        "buyQty": 50,
                                        "sellAvg": 3.8,
                                        "sellQty": 50,
                                        "buyAvg": 3.85,
                                        "buyVal": 192.5,
                                        "description": "21 Aug 05 15000 PE",
                                        "sellVal": 190.0,
                                        "symbol": "NSE:NIFTY2180515000PE",
                                        "fyToken": "101121080539541",
                                        "slNo": 8,
                                        "avgPrice": 0,
                                        "segment": "D",
                                        "dummy": "          ",
                                        "ltp": 2.3,
                                        "rbiRefRate": 1.0,
                                        "side": 0,
                                        "netQty": 0,
                                        "pl": -2.5,
                                        "productType": "INTRADAY",
                                        "netAvg": 0.0,
                                        "qtyMulti_com": 1.0
                                    },
                                    {
                                        "ex_sym": "GAIL",
                                        "crossCurrency": "N",
                                        "qty": 0,
                                        "lot_size": 1,
                                        "realized_profit": -0.1,
                                        "id": "NSE:GAIL-EQ-BO",
                                        "tick_size": 0.05,
                                        "unrealized_profit": 0.0,
                                        "buyQty": 1,
                                        "sellAvg": 138.85,
                                        "sellQty": 1,
                                        "buyAvg": 138.95,
                                        "buyVal": 138.95,
                                        "description": "GAIL (INDIA) LTD",
                                        "sellVal": 138.85,
                                        "symbol": "NSE:GAIL-EQ",
                                        "fyToken": "10100000004717",
                                        "slNo": 9,
                                        "avgPrice": 0,
                                        "segment": "E",
                                        "dummy": "          ",
                                        "ltp": 139.55,
                                        "rbiRefRate": 1.0,
                                        "side": 0,
                                        "netQty": 0,
                                        "pl": -0.1,
                                        "productType": "BO",
                                        "netAvg": 0.0,
                                        "qtyMulti_com": 1.0
                                    },
                                    {
                                        "ex_sym": "ZOMATO",
                                        "crossCurrency": "N",
                                        "qty": 0,
                                        "lot_size": 1,
                                        "realized_profit": -0.1,
                                        "id": "NSE:ZOMATO-EQ-CNC",
                                        "tick_size": 0.05,
                                        "unrealized_profit": 0.0,
                                        "buyQty": 1,
                                        "sellAvg": 138.4,
                                        "sellQty": 1,
                                        "buyAvg": 138.5,
                                        "buyVal": 138.5,
                                        "description": "ZOMATO LIMITED",
                                        "sellVal": 138.4,
                                        "symbol": "NSE:ZOMATO-EQ",
                                        "fyToken": "10100000005097",
                                        "slNo": 10,
                                        "avgPrice": 0,
                                        "segment": "E",
                                        "dummy": "          ",
                                        "ltp": 133.5,
                                        "rbiRefRate": 1.0,
                                        "side": 0,
                                        "netQty": 0,
                                        "pl": -0.1,
                                        "productType": "CNC",
                                        "netAvg": 0.0,
                                        "qtyMulti_com": 1.0
                                    },
                                    {
                                        "ex_sym": "USDINR",
                                        "crossCurrency": "N",
                                        "qty": 0,
                                        "lot_size": 1,
                                        "realized_profit": -5.0,
                                        "id": "NSE:USDINR21AUGFUT-INTRADAY",
                                        "tick_size": 0.0025,
                                        "unrealized_profit": 0.0,
                                        "buyQty": 1,
                                        "sellAvg": 74.485,
                                        "sellQty": 1,
                                        "buyAvg": 74.49,
                                        "buyVal": 74490.0,
                                        "description": "21 Aug 27 FUT",
                                        "sellVal": 74485.0,
                                        "symbol": "NSE:USDINR21AUGFUT",
                                        "fyToken": "10122108277395",
                                        "slNo": 11,
                                        "avgPrice": 0,
                                        "segment": "C",
                                        "dummy": "          ",
                                        "ltp": 74.5825,
                                        "rbiRefRate": 1.0,
                                        "side": 0,
                                        "netQty": 0,
                                        "pl": -5.0,
                                        "productType": "INTRADAY",
                                        "netAvg": 0.0,
                                        "qtyMulti_com": 1.0
                                    }
                                ]

                overallDict =  {
                                    "pl_unrealized": 0.0,
                                    "count_open": 0,
                                    "pl_total": -8.8,
                                    "count_total": 12,
                                    "pl_realized": -8.8
                                }

            return [SUCCESS_C_1, [returnList,overallDict], userInfoList]

    except Exception as e:
        logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName,callingFuncName, e, ERROR_C_UNKNOWN, tokenHash)
        return [ERROR_C_1, ERROR_C_UNKNOWN, ""]


def main():
    pass  # Test here


if __name__ == "__main__":
    main()
