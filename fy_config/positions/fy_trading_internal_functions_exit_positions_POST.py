moduleName = "fy_trading_internal_functions_exit_positions_POST"
try:
    import sys
    import time
    import functools

    from fy_base_defines import LOG_STATUS_ERROR_1, LOG_STATUS_SUCCESS_1
    from fy_base_success_error_codes import ERROR_C_1, \
     ERROR_C_UNKNOWN, SUCCESS_C_1, ERROR_C_INV_POSITION_ID, ERROR_C_OMS_1, \
     SUCCESS_C_2, ERROR_C_NO_OPEN_POS, \
     ERROR_C_DEMO_USER, ERROR_C_OMS_STRING_CONVERSION_FAIL, ERROR_C_OMS_ORDER_ALREADY_TRADED, \
     ERROR_C_INV_INST_TYPE, ERROR_C_INV_ORDER_SIDE, ERROR_C_INV_ORDER_TYPE, \
     ERROR_C_INV_ORDER_PRODUCT
    from fy_base_success_error_messages import ERROR_M_INV_POSITION_ID, \
     SUCCESS_M_EXIT_POS_REQ_SENT, ERROR_M_UNKNOWN_1, ERROR_M_NO_OPEN_POS, \
     ERROR_M_ORDER_ALREADY_TRADED, ERROR_M_INV_INST_TYPE, ERROR_M_INV_ORDER_SIDE, \
     ERROR_M_INV_ORDER_TYPE, ERROR_M_INV_ORDER_PRODUCT, SUCCESS_M_ALL_POSITIONS_CLOSED
    from fy_common_api_keys_values import API_V_PRODTYPE_CO, API_V_PRODTYPE_BO
    from fy_data_and_trade_defines import SYM_SEGMENT_CM, SYM_SEGMENT_FO, SYM_SEGMENT_CD, \
     SYM_SEGMENT_COM, BEWARE_CLIENTS_LIST, EXCHANGE_CODE_NSE, EXCHANGE_CODE_BSE, \
     EXCHANGE_CODE_MCX
    from fy_trading_defines import API_OMS_V_SEG_CM_1, API_OMS_V_SEG_FO_1, \
     API_OMS_V_SEG_CD_1, API_OMS_V_SEG_COM_1, API_V_ORDER_SIDE_SELL_1, FREEZE_QTY_BANKNIFTY, \
     FREEZE_QTY_FINNIFTY, FREEZE_QTY_NIFTY, API_OMS_K_TOKEN_ID_2, API_OMS_K_CLIENT_ID_1, \
     API_OMS_K_REQ_SOURCE, API_OMS_K_ROW_START, API_OMS_V_PAGINATION_START, \
     API_OMS_K_ROW_END, API_OMS_V_PAGINATION_END, REQ_URL_OMS_MAIN_2, API_OMS_REQ_PATH_ORDER_BOOK, \
     API_OMS_V_ORDER_PROD_CO_2, API_OMS_V_ORDER_PROD_BO_2, API_OMS_V_ORDER_LEG_VALUE_1, \
     API_OMS_V_EXCH_NSE, API_OMS_V_EXCH_BSE, API_OMS_V_EXCH_MCX, API_OMS_V_SEG_CM_2, \
     API_OMS_V_SEG_FO_2, API_OMS_V_ORDER_SIDE_BUY_1, API_OMS_V_ORDER_SIDE_BUY_2, \
     API_OMS_V_ORDER_SIDE_SELL_2, API_OMS_V_ORDER_SIDE_SELL_1, API_OMS_V_ORDER_TYPE_LMT_2, \
     API_OMS_V_ORDER_TYPE_LMT_1, API_OMS_V_ORDER_TYPE_MKT_2, API_OMS_V_ORDER_TYPE_MKT_1, \
     API_OMS_V_ORDER_PROD_CO_1, API_OMS_V_DEFAULT_ORDER_OFFLINE_FLAG_2, \
     API_OMS_V_DEFAULT_MARKET_PRO_FLAG, API_OMS_V_DEFAULT_MARKET_PRO_VAL, \
     API_OMS_V_DEFAULT_GTC_FLAG, API_OMS_V_DEFAULT_ENCASH_FLAG, API_OMS_K_PAN_1, \
     REQ_URL_OMS_MAIN_1, API_OMS_REQ_PATH_CO_EXIT, API_OMS_V_ORDER_PROD_BO_1, \
     API_OMS_REQ_PATH_BO_EXIT
    from fy_config.positions.fy_trading_internal_functions_positions_GET import \
     INTERNAL_getNetPositions_withID4
     
    from fy_base_functions import logEntryFunc2
    from fy_common_internal_functions import INTERNAL_getSymbolTickersForFyTokensList, \
     getSymbolsFromSymbolMasterCache
    from fy_connections import connectRedis
    from fy_data_internal_functions import INTERNAL_getL1PricesForFyTokenDict_1, \
     INTERNAL_updateQuoteDetailsToOrderBook
    from fy_trading_internal_functions import INTERNAL_getToken_checkStatus
    from fy_trading_common_functions import INTERNAL_getDemoResponse, \
     INTERNAL_getNewFyTokensFromOldfyTokensList, INTERNAL_fy_getNecessaryOMSData_withID, \
     INTERNAL_placeOrder_withID, INTERNAL_getOrderStatus_withID2
    from fy_trading_internal_functions import INTERNAL_createAndSendOmsRequest, \
     INTERNAL_decryptOmsResponse, INTERNAL_readOmsDecryptedResponse

except Exception as e:
    print("ERR : %s : %s : %s" % (moduleName, "Could not import module", e))
    sys.exit()


# Exit positions added - 20200117 - Khyati
def INTERNAL_exitPositions(tokenHash,positionIdList,callingFuncName="",userIp="", fyId=""):
    funcName = "INTERNAL_exitPositions"
    try:
        # Get all existing positions
        funcRet = INTERNAL_getNetPositions_withID4(tokenHash,callingFuncName=funcName,userIp=userIp,fyId=fyId)
        if funcRet[0] != SUCCESS_C_1:
            return [ERROR_C_1, funcRet[1], funcRet[2]]
        netpositions = funcRet[1][0]

        positionDict = {}

        # Get required position details
        for i in netpositions:

            if i["id"] in positionIdList and i["netQty"]!=0:
                # exclude CNC sell positions
                if i["productType"] == "CNC" and i["side"] == API_V_ORDER_SIDE_SELL_1:
                    continue
                positionDict[i["id"]] = i

        logEntryFunc2(LOG_STATUS_SUCCESS_1, moduleName, funcName, "exit_positions_2", positionDict,netpositions,fyId=fyId)

        if positionDict == {}:
            return [ERROR_C_1,ERROR_C_INV_POSITION_ID, ERROR_M_INV_POSITION_ID]

        for positionId in positionDict:
            orderSymbol = positionDict[positionId]["symbol"]
            productType = positionDict[positionId]["productType"]

            if productType == API_V_PRODTYPE_CO or productType == API_V_PRODTYPE_BO:
                getOrderRet = INTERNAL_getOrderBook_withID4(tokenHash,callingFuncName=funcName,userIp=userIp,fyId=fyId)
                if getOrderRet[0] != SUCCESS_C_1:
                    logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName,callingFuncName, getOrderRet,positionDict[positionId], fyId=fyId)
                    continue
                orderBook = getOrderRet[1]

                parentList = []
                orderList = []
                for i in orderBook:
                    if i["symbol"] == orderSymbol and i["productType"] == productType and i["status"] == 6:
                        if "parentId" in i:
                            if i["parentId"] not in parentList:
                                parentList.append(i["parentId"])
                                orderList.append(i["id"])
                        else:
                            if i["id"] in parentList:
                                continue
                            else:
                                parentList.append(i["id"])
                                orderList.append(i["id"])

                logEntryFunc2(LOG_STATUS_SUCCESS_1, moduleName, funcName, "", fyId, orderList, positionIdList)

                for cancelOrderId in orderList:
                    if productType == API_V_PRODTYPE_CO:
                        exitFuncRetList = INTERNAL_exitCoverOrder(tokenHash,cancelOrderId,callingFuncName=funcName,userIp=userIp)
                    elif productType == API_V_PRODTYPE_BO:
                        exitFuncRetList = INTERNAL_exitBracketOrder(tokenHash,cancelOrderId,callingFuncName=funcName,userIp=userIp)
                    if (exitFuncRetList[0] == ERROR_C_1) or (exitFuncRetList[0] == ERROR_C_OMS_1):
                        logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName,callingFuncName, exitFuncRetList,positionDict[positionId],cancelOrderId, fyId=fyId)
                        continue

            else:
                netQty = positionDict[positionId]["netQty"]
                side = positionDict[positionId]["side"]

                orderQty = abs(netQty)
                orderSide = side * -1
                orderType = 2

                orderPrice      = 0
                orderStopPrice  = 0
                disclosedQty    = 0
                validity        = "DAY"
                offlineFlag     = "false"

                if ("FUT" in orderSymbol or "CE" in orderSymbol or "PE" in orderSymbol) and ("NIFTY" in orderSymbol or "FINNIFTY" in orderSymbol or "BANKNIFTY" in orderSymbol):

                    if "BANKNIFTY" in orderSymbol:
                        freezeQty = FREEZE_QTY_BANKNIFTY
                    elif "FINNIFTY" in orderSymbol:
                        freezeQty = FREEZE_QTY_FINNIFTY
                    elif "NIFTY" in orderSymbol:
                        freezeQty = FREEZE_QTY_NIFTY

                    if orderQty > freezeQty:
                        orderQty1 = int(orderQty / freezeQty)
                        orderQty2 = orderQty % freezeQty

                        qtyList = [freezeQty] * orderQty1
                        if orderQty2 > 0:
                            qtyList.append(orderQty2)

                        logEntryFunc2(LOG_STATUS_SUCCESS_1, moduleName, funcName, callingFuncName, orderSymbol, f"orderQty > freezeQty;freezeQty: {freezeQty}; orderQty: {orderQty}; qtyList:{qtyList}", fyId=fyId)

                        for qty in qtyList:
                            funcRetList = INTERNAL_placeOrder_withID(tokenHash, orderSymbol, orderSide, orderType, qty,orderPrice, productType, trigPrice=orderStopPrice,callingFuncName=funcName,discQty=disclosedQty,valType=validity,offlineFlag=offlineFlag,userIp=userIp)

                    else:
                        logEntryFunc2(LOG_STATUS_SUCCESS_1, moduleName, funcName, callingFuncName, orderSymbol, f"orderQty < freezeQty;freezeQty: {freezeQty}; orderQty: {orderQty}", fyId=fyId)
                        funcRetList = INTERNAL_placeOrder_withID(tokenHash, orderSymbol, orderSide, orderType, orderQty,orderPrice, productType, trigPrice=orderStopPrice,callingFuncName=funcName,discQty=disclosedQty,valType=validity,offlineFlag=offlineFlag,userIp=userIp)

                else:
                    funcRetList = INTERNAL_placeOrder_withID(tokenHash, orderSymbol, orderSide, orderType, orderQty,orderPrice, productType, trigPrice=orderStopPrice,callingFuncName=funcName,discQty=disclosedQty,valType=validity,offlineFlag=offlineFlag,userIp=userIp)

                if (funcRetList[0] == ERROR_C_1) or (funcRetList[0] == ERROR_C_OMS_1):
                    logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName,callingFuncName, funcRetList,positionDict[positionId], fyId=fyId)
                    continue

        attempt = 0
        retry = True
        while attempt<10 and retry==True:
            closed = 0
            attempt += 1
            time.sleep(0.5)
            netPositionRet = INTERNAL_getNetPositions_withID4(tokenHash,callingFuncName=funcName,fyId=fyId)
            if netPositionRet[0] == SUCCESS_C_1:
                netPositionRet = netPositionRet[1][0]
                for i in netPositionRet:
                    if i["id"] in positionIdList:
                        if i["netQty"] == 0:
                            closed += 1
                        else:
                            logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName,"", fyId, "Position Not Closed", i["id"], i,positionDict,netPositionRet,fyId=fyId)
                if closed==len(positionDict):
                    retry = False
                else:
                    retry = True
            
        if retry:
            return [SUCCESS_C_1,SUCCESS_C_2,SUCCESS_M_EXIT_POS_REQ_SENT]
        else:
            return [SUCCESS_C_1,SUCCESS_C_2,SUCCESS_M_ALL_POSITIONS_CLOSED]

    except Exception as e:
        logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName,"", fyId, e, ERROR_C_UNKNOWN)
        return [ERROR_C_1, ERROR_C_UNKNOWN, ERROR_M_UNKNOWN_1]


# Exit all open positions - Khyati - 20200117
def INTERNAL_exitAllPositions(tokenHash, inputside=None, inputsegment=None, inputproductType=None, exitAll=False,callingFuncName="",userIp="", fyId=""):
    funcName = "INTERNAL_exitAllPositions"
    try:
        # Get all existing positions
        funcRet = INTERNAL_getNetPositions_withID4(tokenHash,callingFuncName=funcName,userIp=userIp,fyId=fyId)
        if funcRet[0] != SUCCESS_C_1:
            return [ERROR_C_1, funcRet[1], funcRet[2]]
        netpositions = funcRet[1][0]

        if netpositions == []:
            return [ERROR_C_1,ERROR_C_NO_OPEN_POS,ERROR_M_NO_OPEN_POS]

        positionDict = {}

        if exitAll:
            for i in netpositions:
                if i["netQty"] != 0:
                    # exclude CNC sell positions
                    if i["productType"] == "CNC" and i["side"] == API_V_ORDER_SIDE_SELL_1:
                        continue
                    positionDict[i["id"]] = i

        else:
            inputsegment2 = []
            segmentdict = {SYM_SEGMENT_CM:API_OMS_V_SEG_CM_1,SYM_SEGMENT_FO:API_OMS_V_SEG_FO_1,SYM_SEGMENT_CD:API_OMS_V_SEG_CD_1,SYM_SEGMENT_COM:API_OMS_V_SEG_COM_1}
            for i in range(len(inputsegment)):
                inputsegment2.append(segmentdict[inputsegment[i]])
            for i in netpositions:
                if i["netQty"] != 0:
                    if i["side"] in inputside and i["segment"] in inputsegment2 and i["productType"] in inputproductType:
                        # exclude CNC sell positions
                        if i["productType"] == "CNC" and i["side"] == API_V_ORDER_SIDE_SELL_1:
                            continue
                        positionDict[i["id"]] = i

        logEntryFunc2(LOG_STATUS_SUCCESS_1, moduleName, funcName, "exit_positions_2", positionDict,netpositions,fyId=fyId)

        if positionDict == {}:
            return [ERROR_C_1,ERROR_C_NO_OPEN_POS,ERROR_M_NO_OPEN_POS]

        for positionId in positionDict:
            orderSymbol = positionDict[positionId]["symbol"]
            productType = positionDict[positionId]["productType"]

            if productType == API_V_PRODTYPE_CO or productType == API_V_PRODTYPE_BO:
                getOrderRet = INTERNAL_getOrderBook_withID4(tokenHash,callingFuncName=funcName,userIp=userIp,fyId=fyId)
                if getOrderRet[0] != SUCCESS_C_1:
                    logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName,callingFuncName, getOrderRet,positionDict[positionId], fyId=fyId)
                    continue
                orderBook = getOrderRet[1]

                parentList = []
                orderList = []
                for i in orderBook:
                    if i["symbol"] == orderSymbol and i["productType"] == productType and i["status"] == 6:
                        if "parentId" in i:
                            if i["parentId"] not in parentList:
                                parentList.append(i["parentId"])
                                orderList.append(i["id"])
                        else:
                            if i["id"] in parentList:
                                continue
                            else:
                                parentList.append(i["id"])
                                orderList.append(i["id"])

                logEntryFunc2(LOG_STATUS_SUCCESS_1, moduleName, funcName, "", fyId, orderList)

                for cancelOrderId in orderList:
                    if productType == API_V_PRODTYPE_CO:
                        funcRetList = INTERNAL_exitCoverOrder(tokenHash,cancelOrderId,callingFuncName=funcName,userIp=userIp)
                    elif productType == API_V_PRODTYPE_BO:
                        funcRetList = INTERNAL_exitBracketOrder(tokenHash,cancelOrderId,callingFuncName=funcName,userIp=userIp)
                    if (funcRetList[0] == ERROR_C_1) or (funcRetList[0] == ERROR_C_OMS_1):
                        logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName,callingFuncName, funcRetList,positionDict[positionId],cancelOrderId, fyId=fyId)
                        continue

            else:
                netQty = positionDict[positionId]["netQty"]
                side = positionDict[positionId]["side"]

                orderQty = abs(netQty)  #abs(qty)
                orderSide = side * -1
                orderType = 2

                orderPrice      = 0
                orderStopPrice  = 0
                disclosedQty    = 0
                validity        = "DAY"
                offlineFlag     = "false"

                if ("FUT" in orderSymbol or "CE" in orderSymbol or "PE" in orderSymbol) and ("NIFTY" in orderSymbol or "FINNIFTY" in orderSymbol or "BANKNIFTY" in orderSymbol):

                    if "BANKNIFTY" in orderSymbol:
                        freezeQty = FREEZE_QTY_BANKNIFTY
                    elif "FINNIFTY" in orderSymbol:
                        freezeQty = FREEZE_QTY_FINNIFTY
                    elif "NIFTY" in orderSymbol:
                        freezeQty = FREEZE_QTY_NIFTY

                    if orderQty > freezeQty:
                        orderQty1 = int(orderQty / freezeQty)
                        orderQty2 = orderQty % freezeQty

                        qtyList = [freezeQty] * orderQty1
                        if orderQty2 > 0:
                            qtyList.append(orderQty2)

                        logEntryFunc2(LOG_STATUS_SUCCESS_1, moduleName, funcName, callingFuncName, orderSymbol, f"orderQty > freezeQty;freezeQty: {freezeQty}; orderQty: {orderQty}; qtyList:{qtyList}", fyId=fyId)

                        for qty in qtyList:
                            funcRetList = INTERNAL_placeOrder_withID(tokenHash, orderSymbol, orderSide, orderType, qty,orderPrice, productType, trigPrice=orderStopPrice,callingFuncName=funcName,discQty=disclosedQty,valType=validity,offlineFlag=offlineFlag,userIp=userIp)

                    else:
                        logEntryFunc2(LOG_STATUS_SUCCESS_1, moduleName, funcName, callingFuncName, orderSymbol, f"orderQty < freezeQty;freezeQty: {freezeQty}; orderQty: {orderQty}", fyId=fyId)
                        funcRetList = INTERNAL_placeOrder_withID(tokenHash, orderSymbol, orderSide, orderType, orderQty,orderPrice, productType, trigPrice=orderStopPrice,callingFuncName=funcName,discQty=disclosedQty,valType=validity,offlineFlag=offlineFlag,userIp=userIp)

                else:
                    funcRetList = INTERNAL_placeOrder_withID(tokenHash, orderSymbol, orderSide, orderType, orderQty,orderPrice, productType, trigPrice=orderStopPrice,callingFuncName=funcName,discQty=disclosedQty,valType=validity,offlineFlag=offlineFlag,userIp=userIp)

                if (funcRetList[0] == ERROR_C_1) or (funcRetList[0] == ERROR_C_OMS_1):
                    logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName,callingFuncName, funcRetList,positionDict[positionId], fyId=fyId)
                    continue

        attempt = 0
        retry = True
        while attempt<10 and retry==True:
            closed = 0
            attempt += 1
            time.sleep(0.5)
            netPositionRet = INTERNAL_getNetPositions_withID4(tokenHash,callingFuncName=funcName,fyId=fyId)
            if netPositionRet[0] == SUCCESS_C_1:
                netPositionRet = netPositionRet[1][0]
                for i in netPositionRet:
                    if i["id"] in positionDict:
                        if i["netQty"] == 0:
                            closed += 1
                        else:
                            logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName,"", fyId, "Position Not Closed", i["id"], i,positionDict,netPositionRet,fyId=fyId)
                if closed==len(positionDict):
                    retry = False
                else:
                    retry = True
            
        if retry:
            return [SUCCESS_C_1,SUCCESS_C_2,SUCCESS_M_EXIT_POS_REQ_SENT]
        else:
            return [SUCCESS_C_1,SUCCESS_C_2,SUCCESS_M_ALL_POSITIONS_CLOSED]
        
    except Exception as e:
        logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName,"",fyId, e, ERROR_C_UNKNOWN)
        return [ERROR_C_1, ERROR_C_UNKNOWN, ERROR_M_UNKNOWN_1]


def INTERNAL_getOrderBook_withID4(tokenHash,callingFuncName="",userIp="", fyId=""):
    """
    [FUNCTION]
        Get entire order book for a specific UserID
    [PARAMS]
            tokenHash       : This is a hash of (fyId + AppId)
    [RETURN]
            Success : [SUCCESS_C_1,[{..},{..},{..}],""] Each trade is a seperate dict in the list
            {
                "orderDateTime":
                "id":
                "side":
                "segment":
                "instrument":
                "productType":
                "status":
                "qty":
                "remainingQuantity":
                "filledQty":
                "limitPrice":
                "stopPrice":
                "type":
                "discloseQty":
                "orderValidity":
                "tradedQty":
                "dqQtyRem":
                "slNo":
                "fyToken":
            }
        Failure : [ERROR_C_1, errorCode,"error message"]
    """
    funcName = "INTERNAL_getOrderBook_withID4"

    try:
        tokenHash   = str(tokenHash)
        localMemory = connectRedis(callingFuncName=callingFuncName)

        fyTokenList = INTERNAL_getToken_checkStatus(tokenHash,localMemory=localMemory,callingFuncName=callingFuncName,userIp=userIp,inputFyId=fyId)
        if fyTokenList[0] == ERROR_C_1:
            # If the user is a guest
            if fyTokenList[1] == ERROR_C_DEMO_USER:
                ##send the demo response
                demoRespFunc = INTERNAL_getDemoResponse(1,localMemory=localMemory,callingFuncName=callingFuncName)
                return demoRespFunc
            return fyTokenList
        fyId        = fyTokenList[1][0]
        omsTokenId  = fyTokenList[1][1]
        aesKey      = fyTokenList[1][2]
        appId       = fyTokenList[2]
        source      = fyTokenList[3]

        # If fyId is in beware list
        if fyId in BEWARE_CLIENTS_LIST:
            return [SUCCESS_C_1, [], []]

        # Send the request to the OMS
        paramsForEncryption = {API_OMS_K_TOKEN_ID_2: omsTokenId, API_OMS_K_CLIENT_ID_1: fyId,API_OMS_K_REQ_SOURCE: source,API_OMS_K_ROW_START:API_OMS_V_PAGINATION_START,API_OMS_K_ROW_END:API_OMS_V_PAGINATION_END}
        urlForRequest       = REQ_URL_OMS_MAIN_2 + API_OMS_REQ_PATH_ORDER_BOOK
        sendReqFuncRet      = INTERNAL_createAndSendOmsRequest(fyId,omsTokenId,aesKey,paramsForEncryption,urlForRequest,callingFuncName=callingFuncName,userIp=userIp)
        if sendReqFuncRet[0] == ERROR_C_1:
            return sendReqFuncRet
        omsResponse = sendReqFuncRet[1]

        # Decrypt the response received from the OMS
        readOmsResponseFuncRet = INTERNAL_decryptOmsResponse(omsResponse, aesKey, callingFuncName=callingFuncName)
        if (readOmsResponseFuncRet[0] == ERROR_C_1):
            return readOmsResponseFuncRet
        userInfoList = readOmsResponseFuncRet[1]

        # Check for user invalidation. If yes, re-send the request
        readOmsResponseFuncRet2 = INTERNAL_readOmsDecryptedResponse(userInfoList, tokenHash, paramsForEncryption,
                                        urlForRequest,fyId=fyId, localMemory=localMemory,callingFuncName=callingFuncName, userIp=userIp)
        if (readOmsResponseFuncRet2[0] == ERROR_C_1) or (readOmsResponseFuncRet2[0] == ERROR_C_OMS_1):
            return readOmsResponseFuncRet2
        userInfoList = readOmsResponseFuncRet2[1]

        returnList = []
        oldFyTokensDict = {}
        fyTokenDict = {}
        if (len(userInfoList) != 0):
            for i in userInfoList:
                rowDict = {}
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
                rowNum  = i["R"]
                exchangeOrdNum = i["EXCHORDERNO"]

                pan             = i["PAN_NO"]
                participantType = i["PARTICIPANT_TYPE"]
                marketProFlag   = i["MKT_PROTECT_FLG"]
                marketProVal    = i["MKT_PROTECT_VAL"]
                settlor         = i["SETTLOR"]
                gtcFlag         = i["GTC_FLG"]
                encashFlag      = i["ENCASH_FLG"]
                marketType      = i["MKT_TYPE"]

                clientId        = i["CLIENT_ID"]
                serialNumber    = i["SERIALNO"]

                algoOrderNum    = i["ALGO_ORD_NO"]
                takeProfitTrailGap = i["TAKE_PROFIT_TRAIL_GAP"]
                advGroupRefNum  = i["ADV_GROUP_REF_NO"]
                trailingSlVal   = i["TRAILING_SL_VALUE"]
                slAbsTickValue  = i["SL_ABSTICK_VALUE"]
                prfAbsTickValue = i["PR_ABSTICK_VALUE"]
                orderOffOn      = i["ORDER_OFFON"]
                childLegUnqId   = i["CHILD_LEG_UNQ_ID"]

                tradedPrice     = i["TRADED_PRICE"]
                orderLegValue   = i["LEG_NO"]
                remQtyTotalQty  = i["REM_QTY_TOT_QTY"]
                serialNumber    = i["SERIALNO"]
                semNseRegLot    = i["SEM_NSE_REGULAR_LOT"]

                if clientId != fyId:
                    logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, f"clientId:{clientId}", f"fyId:{fyId}", i, err_msg="Invalid Client Id response from RS",fyId=fyId)
                    continue

                # Check if order reason/message is provided or not
                if "REASON_DESCRIPTION" in i:
                    orderMessage = i["REASON_DESCRIPTION"]
                else:
                    orderMessage = ""

                if orderPrice == "MKT":
                    orderPrice = 0

                # String conversion where ever necessary
                try:
                    tranType = tranType.lower()
                    orderStatus = orderStatus.lower()
                    orderPrice = float(orderPrice.replace(",",""))
                    orderType = orderType.lower()
                    productType = productType.upper()
                    tradedQty = int(tradedQty)
                    orderNumber = str(int(float(orderNumber)))
                    orderQty = int(orderQty)
                    remQuantity = int(remQuantity)
                    trigPrice = float(trigPrice)
                    discloseQty = int(discloseQty)
                    dqQtyRem = int(dqQtyRem)
                    rowNum = int(rowNum)
                except AttributeError:
                    logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, i,err_msg="AttributeError", code=ERROR_C_OMS_STRING_CONVERSION_FAIL,fyId=fyId)
                    continue
                except Exception as e:
                    logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, i, err_msg=e, code=ERROR_C_OMS_STRING_CONVERSION_FAIL,fyId=fyId)
                    continue

                if trigPrice != 0:
                    if (orderPrice == 0) or (orderType == "market"):
                        orderType = "stop"
                        orderPrice = 0
                    else:
                        orderType = "stoplimit"

                elif orderType == "stoploss":
                    if (orderPrice == 0):
                        orderType = "stop"
                    else:
                        orderType = "stoplimit"

                # If buy then 1, if sell then -1
                if (tranType == "buy"):
                    tranType = 1
                elif (tranType == "sell"):
                    tranType = -1

                offLineOrder = False

                if (orderStatus == "pending"):
                    orderStatus = 6
                elif orderStatus == "traded":
                    orderStatus = 2
                elif (orderStatus == "modified"):
                    orderStatus = 6
                elif (orderStatus == "cancelled"):
                    orderStatus = 1
                elif orderStatus == "rejected":
                    orderStatus = 5
                elif orderStatus == "part-traded":
                    orderStatus = 6
                elif (orderStatus == "o-pending") or (orderStatus == "o-modified"):
                    orderStatus = 6
                    offLineOrder = True
                elif (orderStatus == "o-cancelled"):
                    orderStatus = 1
                    offLineOrder = True
                elif orderStatus == "transit":
                    orderStatus = 4
                elif orderStatus == "triggered":
                    orderStatus = 6
                elif orderStatus == "expired":
                    orderStatus = 7

                # Order type
                if orderType == "limit":
                    orderType = 1
                elif orderType == "market":
                    orderType = 2
                elif orderType == "stop":
                    orderType = 3
                elif orderType == "stoplimit":
                    orderType = 4

                # If it is a cover order, we will create a new orderNumber string
                if productType == API_OMS_V_ORDER_PROD_CO_2:

                    # If the order leg is 2 then we will update the parent order id before returning
                    if orderLegValue == "2":
                        orderParentType = 1
                        orderParentId = "%s-%s-%s" % (orderNumber, API_OMS_V_ORDER_PROD_CO_2, 1)
                        rowDict.update({"parentType": orderParentType, "parentId": orderParentId})

                    # We are doing this after the if check because we are over writing the orderNumber below
                    orderNumber = "%s-%s-%s"%(orderNumber,API_OMS_V_ORDER_PROD_CO_2,orderLegValue)

                # If it is a bracket Order, we will create the orderNumber string and parent order Number
                elif productType == API_OMS_V_ORDER_PROD_BO_2:

                    # We are adding the product and leg value to the order number
                    orderNumber = "%s-%s-%s" % (orderNumber, API_OMS_V_ORDER_PROD_BO_2, orderLegValue)

                    # If algo order number is not -1, it means that the order is either leg 1 or leg 2
                    if algoOrderNum != -1:
                        orderParentType = 1
                        orderParentId = "%s-%s-%s" % (algoOrderNum, API_OMS_V_ORDER_PROD_BO_2, API_OMS_V_ORDER_LEG_VALUE_1)
                        rowDict.update({"parentType": orderParentType, "parentId": orderParentId})


                # Creating our own fyToken for each symbol
                fyToken = ""
                if exchange in [API_OMS_V_EXCH_NSE, API_OMS_V_EXCH_BSE]:
                    if exchange == API_OMS_V_EXCH_NSE:
                        exchangeCode = EXCHANGE_CODE_NSE
                    if exchange == API_OMS_V_EXCH_BSE:
                        exchangeCode = EXCHANGE_CODE_BSE
                    if segment == API_OMS_V_SEG_CM_1:
                        fyToken = "%s%s%s" % (exchangeCode, SYM_SEGMENT_CM, securityId)
                    elif segment == API_OMS_V_SEG_FO_1:
                        fyToken = "%s%s%s" % (exchangeCode, SYM_SEGMENT_FO, securityId)
                    elif segment == API_OMS_V_SEG_CD_1:
                        fyToken = "%s%s%s" % (exchangeCode, SYM_SEGMENT_CD, securityId)
                    else:
                        continue
                elif exchange == API_OMS_V_EXCH_MCX:
                    fyToken = "%s%s%s" %(EXCHANGE_CODE_MCX, SYM_SEGMENT_COM, securityId)
                else:
                    continue
                oldFyTokensDict[fyToken] = ""

                ## New change 20181228 - Palash
                orderNumStatus = orderNumber + ":" + str(orderStatus)

                # Updating the rowDict rather than assigning because we may have added some keys above already
                rowDict.update({"orderDateTime": orderDateTime, "id": orderNumber, "exchOrdId": exchangeOrdNum,
                           "side": tranType, "segment": segment,
                           "instrument": instrument, "productType": productType,
                           "status": orderStatus, "qty": orderQty,
                           "remainingQuantity": remQuantity, "filledQty": tradedQty,
                           "limitPrice": orderPrice, "stopPrice": trigPrice,
                           "type": orderType, "discloseQty": discloseQty, "dqQtyRem": dqQtyRem,
                           "orderValidity": orderValidity,
                           "slNo": rowNum, "fyToken": fyToken, "offlineOrder": offLineOrder, "message": orderMessage, "orderNumStatus": orderNumStatus, "tradedPrice":tradedPrice, "exchange":exchange, "pan":pan, "clientId":clientId}) ##Traded price added to response - 20200117 - Khyati
                            # exchange,pan,clientId added - mobile app changes - Khyati
                returnList.append(rowDict)

            # Need to convert old fyTokens to new fyTokens

            fyTokensRet = INTERNAL_getNewFyTokensFromOldfyTokensList(list(oldFyTokensDict.keys()),localMemory=localMemory,
                                                                     callingFuncName=callingFuncName)
            if fyTokensRet[0] == ERROR_C_1:
                return fyTokensRet
            for i in returnList:
                oldFyToken = i["fyToken"]
                i["fyToken"] = fyTokensRet[1][oldFyToken]
                fyTokenDict[i["fyToken"]] = ""


            symbolTickersDict = INTERNAL_getSymbolTickersForFyTokensList(list(fyTokenDict.keys()),localMemory=localMemory,
                                                                         callingFuncName=callingFuncName)

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
                    i["ex_sym"] = ""
                    i["description"] = ""
                    i["lot_size"] = 0
                    i["tick_size"] = 0.0
                    logEntryFunc2(LOG_STATUS_ERROR_1, moduleName,funcName,callingFuncName, i, err_msg=e,fyId=fyId)

            l2DictRetList = INTERNAL_getL1PricesForFyTokenDict_1(symbolTickersDict[1], localMemory=localMemory,callingFuncName=funcName, fytokenToTicker=True)
            l2Dict = {}
            if l2DictRetList[0] != ERROR_C_1:
                l2Dict = l2DictRetList[1]
            list(map(functools.partial(INTERNAL_updateQuoteDetailsToOrderBook,l2Dict=l2Dict),returnList))

            if fyId == 'FM0224':
                returnList1 = [
                                    {
                                        "status": 2,
                                        "ex_sym": "IOC",
                                        "ch": -0.75,
                                        "description": "INDIAN OIL CORP LTD",
                                        "exchange": "NSE",
                                        "symbol": "NSE:IOC-EQ",
                                        "limitPrice": 0.0,
                                        "qty": 1,
                                        "orderNumStatus": "1114222:2",
                                        "dqQtyRem": 0,
                                        "orderDateTime": "30-Jul-2021 15:16:19",
                                        "orderValidity": "DAY",
                                        "fyToken": "10100000001624",
                                        "slNo": 1,
                                        "message": "TRADE CONFIRMED",
                                        "segment": "E",
                                        "id": "1114222",
                                        "stopPrice": 0.0,
                                        "tick_size": 0.05,
                                        "exchOrdId": "1100000017416045",
                                        "remainingQuantity": 0,
                                        "lp": 103.15,
                                        "filledQty": 1,
                                        "clientId": "FM0224",
                                        "offlineOrder": False,
                                        "chp": -0.72,
                                        "instrument": "EQUITY",
                                        "lot_size": 1,
                                        "tradedPrice": 103.0,
                                        "productType": "INTRADAY",
                                        "type": 2,
                                        "side": -1,
                                        "pan": "AFKPY8867N",
                                        "discloseQty": 0
                                    },
                                    {
                                        "status": 5,
                                        "ex_sym": "ZEEL",
                                        "ch": 0.5,
                                        "description": "21 Aug 26 220 CE",
                                        "exchange": "NSE",
                                        "symbol": "NSE:ZEEL21AUG220CE",
                                        "limitPrice": 0.0,
                                        "qty": 3000,
                                        "orderNumStatus": "221073049203:5",
                                        "dqQtyRem": 0,
                                        "orderDateTime": "30-Jul-2021 10:18:56",
                                        "orderValidity": "DAY",
                                        "fyToken": "1011210826114396",
                                        "slNo": 2,
                                        "message": "RMS:221073049203:NSE,OPTSTK,114396,ZEEL-Aug2021-220.0000-CE,INTRADAY,,2021-08-26 00:00:00,FM0224,S,3000,I,2.4,FUND LIMIT INSUFFICIENT,AVAILABLE FUND =54976.64,ADDITIONAL REQUIRED FUND=75193.17,CALCULATED SPAN & EXPOSURE FOR ORDER=130169.81",
                                        "segment": "D",
                                        "id": "221073049203",
                                        "stopPrice": 0.0,
                                        "tick_size": 0.05,
                                        "exchOrdId": "0",
                                        "remainingQuantity": 3000,
                                        "lp": 3.25,
                                        "filledQty": 0,
                                        "clientId": "FM0224",
                                        "offlineOrder": False,
                                        "chp": 18.18,
                                        "instrument": "OPTSTK",
                                        "lot_size": 3000,
                                        "tradedPrice": 0.0,
                                        "productType": "INTRADAY",
                                        "type": 2,
                                        "side": -1,
                                        "pan": "AFKPY8867N",
                                        "discloseQty": 0
                                    },
                                    {
                                        "status": 2,
                                        "ex_sym": "NIFTY",
                                        "ch": -1.15,
                                        "description": "21 Aug 05 15000 PE",
                                        "exchange": "NSE",
                                        "symbol": "NSE:NIFTY2180515000PE",
                                        "limitPrice": 0.0,
                                        "qty": 50,
                                        "orderNumStatus": "221073045263:2",
                                        "dqQtyRem": 0,
                                        "orderDateTime": "30-Jul-2021 10:13:58",
                                        "orderValidity": "DAY",
                                        "fyToken": "101121080539541",
                                        "slNo": 4,
                                        "message": "TRADE CONFIRMED",
                                        "segment": "D",
                                        "id": "221073045263",
                                        "stopPrice": 0.0,
                                        "tick_size": 0.05,
                                        "exchOrdId": "1000000012464322",
                                        "remainingQuantity": 0,
                                        "lp": 2.3,
                                        "filledQty": 50,
                                        "clientId": "FM0224",
                                        "offlineOrder": False,
                                        "chp": -33.33,
                                        "instrument": "OPTIDX",
                                        "lot_size": 50,
                                        "tradedPrice": 3.8,
                                        "productType": "INTRADAY",
                                        "type": 2,
                                        "side": -1,
                                        "pan": "AFKPY8867N",
                                        "discloseQty": 0
                                    },
                                    {
                                        "status": 2,
                                        "ex_sym": "NIFTY",
                                        "ch": -1.15,
                                        "description": "21 Aug 05 15000 PE",
                                        "exchange": "NSE",
                                        "symbol": "NSE:NIFTY2180515000PE",
                                        "limitPrice": 3.9,
                                        "qty": 50,
                                        "orderNumStatus": "221073044413:2",
                                        "dqQtyRem": 0,
                                        "orderDateTime": "30-Jul-2021 10:11:51",
                                        "orderValidity": "DAY",
                                        "fyToken": "101121080539541",
                                        "slNo": 5,
                                        "message": "TRADE CONFIRMED",
                                        "segment": "D",
                                        "id": "221073044413",
                                        "stopPrice": 0.0,
                                        "tick_size": 0.05,
                                        "exchOrdId": "1000000012254631",
                                        "remainingQuantity": 0,
                                        "lp": 2.3,
                                        "filledQty": 50,
                                        "clientId": "FM0224",
                                        "offlineOrder": False,
                                        "chp": -33.33,
                                        "instrument": "OPTIDX",
                                        "lot_size": 50,
                                        "tradedPrice": 3.85,
                                        "productType": "INTRADAY",
                                        "type": 1,
                                        "side": 1,
                                        "pan": "AFKPY8867N",
                                        "discloseQty": 0
                                    },
                                    {
                                        "status": 2,
                                        "ex_sym": "GOLDPETAL",
                                        "ch": 4.0,
                                        "description": "21 Aug 31 FUT",
                                        "exchange": "MCX",
                                        "symbol": "MCX:GOLDPETAL21AUGFUT",
                                        "limitPrice": 0.0,
                                        "qty": 1,
                                        "orderNumStatus": "807307306051:2",
                                        "dqQtyRem": 0,
                                        "orderDateTime": "30-Jul-2021 10:06:27",
                                        "orderValidity": "DAY",
                                        "fyToken": "1120210831229420",
                                        "slNo": 6,
                                        "message": "TRADE CONFIRMED",
                                        "segment": "M",
                                        "id": "807307306051",
                                        "stopPrice": 0.0,
                                        "tick_size": "1.0000",
                                        "exchOrdId": "362121100014181",
                                        "remainingQuantity": 0,
                                        "lp": 4811.0,
                                        "filledQty": 1,
                                        "clientId": "FM0224",
                                        "offlineOrder": False,
                                        "chp": 0.08,
                                        "instrument": "FUTCOM",
                                        "lot_size": 1,
                                        "tradedPrice": 4801.0,
                                        "productType": "INTRADAY",
                                        "type": 2,
                                        "side": -1,
                                        "pan": "AFKPY8867N",
                                        "discloseQty": 0
                                    },
                                    {
                                        "status": 2,
                                        "ex_sym": "GOLDPETAL",
                                        "ch": 4.0,
                                        "description": "21 Aug 31 FUT",
                                        "exchange": "MCX",
                                        "symbol": "MCX:GOLDPETAL21AUGFUT",
                                        "limitPrice": 0.0,
                                        "qty": 1,
                                        "orderNumStatus": "807307306041:2",
                                        "dqQtyRem": 0,
                                        "orderDateTime": "30-Jul-2021 10:06:15",
                                        "orderValidity": "DAY",
                                        "fyToken": "1120210831229420",
                                        "slNo": 7,
                                        "message": "TRADE CONFIRMED",
                                        "segment": "M",
                                        "id": "807307306041",
                                        "stopPrice": 0.0,
                                        "tick_size": "1.0000",
                                        "exchOrdId": "362121100014144",
                                        "remainingQuantity": 0,
                                        "lp": 4811.0,
                                        "filledQty": 1,
                                        "clientId": "FM0224",
                                        "offlineOrder": False,
                                        "chp": 0.08,
                                        "instrument": "FUTCOM",
                                        "lot_size": 1,
                                        "tradedPrice": 4802.0,
                                        "productType": "INTRADAY",
                                        "type": 2,
                                        "side": 1,
                                        "pan": "AFKPY8867N",
                                        "discloseQty": 0
                                    },
                                    {
                                        "status": 5,
                                        "ex_sym": "GOLDPETAL",
                                        "ch": 3.0,
                                        "description": "21 Jul 30 FUT",
                                        "exchange": "MCX",
                                        "symbol": "MCX:GOLDPETAL21JULFUT",
                                        "limitPrice": 0.0,
                                        "qty": 1,
                                        "orderNumStatus": "807307306031:5",
                                        "dqQtyRem": 0,
                                        "orderDateTime": "30-Jul-2021 10:06:01",
                                        "orderValidity": "DAY",
                                        "fyToken": "1120210730228846",
                                        "slNo": 8,
                                        "message": "RMS:807307306031:MCX,FUTCOM,228846,GOLDPETAL-Jul2021-FUT,INTRADAY,,2021-07-30 00:00:00,FM0224,B,1,I,4847,TRANSACTIONS ARE BLOCKED FOR THIS SCRIP (GLOBAL LEVEL)",
                                        "segment": "M",
                                        "id": "807307306031",
                                        "stopPrice": 0.0,
                                        "tick_size": "1.0000",
                                        "exchOrdId": "0",
                                        "remainingQuantity": 1,
                                        "lp": 4850.0,
                                        "filledQty": 0,
                                        "clientId": "FM0224",
                                        "offlineOrder": False,
                                        "chp": 0.06,
                                        "instrument": "FUTCOM",
                                        "lot_size": 1,
                                        "tradedPrice": 0.0,
                                        "productType": "INTRADAY",
                                        "type": 2,
                                        "side": 1,
                                        "pan": "AFKPY8867N",
                                        "discloseQty": 0
                                    },
                                    {
                                        "status": 5,
                                        "ex_sym": "SILVERMIC",
                                        "ch": -245.0,
                                        "description": "21 Aug 31 FUT",
                                        "exchange": "MCX",
                                        "symbol": "MCX:SILVERMIC21AUGFUT",
                                        "limitPrice": 0.0,
                                        "qty": 1,
                                        "orderNumStatus": "807307305981:5",
                                        "dqQtyRem": 0,
                                        "orderDateTime": "30-Jul-2021 10:05:41",
                                        "orderValidity": "DAY",
                                        "fyToken": "1120210831226204",
                                        "slNo": 9,
                                        "message": "RMS:807307305981:MCX,FUTCOM,226204,SILVERMIC-Aug2021-FUT,INTRADAY,,2021-08-31 00:00:00,FM0224,B,1,I,68082,FUND LIMIT INSUFFICIENT,AVAILABLE FUND =4995.75,ADDITIONAL REQUIRED FUND=772.52,CALCULATED SPAN & EXPOSURE FOR ORDER=5768.27|E0001|772.52",
                                        "segment": "M",
                                        "id": "807307305981",
                                        "stopPrice": 0.0,
                                        "tick_size": "1.0000",
                                        "exchOrdId": "0",
                                        "remainingQuantity": 1,
                                        "lp": 68155.0,
                                        "filledQty": 0,
                                        "clientId": "FM0224",
                                        "offlineOrder": False,
                                        "chp": -0.36,
                                        "instrument": "FUTCOM",
                                        "lot_size": 1,
                                        "tradedPrice": 0.0,
                                        "productType": "INTRADAY",
                                        "type": 2,
                                        "side": 1,
                                        "pan": "AFKPY8867N",
                                        "discloseQty": 0
                                    },
                                    {
                                        "status": 2,
                                        "ex_sym": "USDINR",
                                        "ch": 0.0925,
                                        "description": "21 Aug 27 FUT",
                                        "exchange": "NSE",
                                        "symbol": "NSE:USDINR21AUGFUT",
                                        "limitPrice": 0.0,
                                        "qty": 1,
                                        "orderNumStatus": "321073007481:2",
                                        "dqQtyRem": 0,
                                        "orderDateTime": "30-Jul-2021 10:05:22",
                                        "orderValidity": "DAY",
                                        "fyToken": "10122108277395",
                                        "slNo": 10,
                                        "message": "TRADE CONFIRMED",
                                        "segment": "C",
                                        "id": "321073007481",
                                        "stopPrice": 0.0,
                                        "tick_size": 0.0025,
                                        "exchOrdId": "1000000000478157",
                                        "remainingQuantity": 0,
                                        "lp": 74.5825,
                                        "filledQty": 1,
                                        "clientId": "FM0224",
                                        "offlineOrder": False,
                                        "chp": 0.12,
                                        "instrument": "FUTCUR",
                                        "lot_size": 1,
                                        "tradedPrice": 74.485,
                                        "productType": "INTRADAY",
                                        "type": 2,
                                        "side": -1,
                                        "pan": "AFKPY8867N",
                                        "discloseQty": 0
                                    },
                                    {
                                        "status": 2,
                                        "ex_sym": "USDINR",
                                        "ch": 0.0925,
                                        "description": "21 Aug 27 FUT",
                                        "exchange": "NSE",
                                        "symbol": "NSE:USDINR21AUGFUT",
                                        "limitPrice": 0.0,
                                        "qty": 1,
                                        "orderNumStatus": "321073007471:2",
                                        "dqQtyRem": 0,
                                        "orderDateTime": "30-Jul-2021 10:05:11",
                                        "orderValidity": "DAY",
                                        "fyToken": "10122108277395",
                                        "slNo": 11,
                                        "message": "TRADE CONFIRMED",
                                        "segment": "C",
                                        "id": "321073007471",
                                        "stopPrice": 0.0,
                                        "tick_size": 0.0025,
                                        "exchOrdId": "1000000000477293",
                                        "remainingQuantity": 0,
                                        "lp": 74.5825,
                                        "filledQty": 1,
                                        "clientId": "FM0224",
                                        "offlineOrder": False,
                                        "chp": 0.12,
                                        "instrument": "FUTCUR",
                                        "lot_size": 1,
                                        "tradedPrice": 74.49,
                                        "productType": "INTRADAY",
                                        "type": 2,
                                        "side": 1,
                                        "pan": "AFKPY8867N",
                                        "discloseQty": 0
                                    },
                                    {
                                        "status": 2,
                                        "ex_sym": "ZOMATO",
                                        "ch": -8.05,
                                        "description": "ZOMATO LIMITED",
                                        "exchange": "NSE",
                                        "symbol": "NSE:ZOMATO-EQ",
                                        "limitPrice": 0.0,
                                        "qty": 1,
                                        "orderNumStatus": "135402:2",
                                        "dqQtyRem": 0,
                                        "orderDateTime": "30-Jul-2021 10:04:54",
                                        "orderValidity": "DAY",
                                        "fyToken": "10100000005097",
                                        "slNo": 12,
                                        "message": "TRADE CONFIRMED",
                                        "segment": "E",
                                        "id": "135402",
                                        "stopPrice": 0.0,
                                        "tick_size": 0.05,
                                        "exchOrdId": "1300000005733873",
                                        "remainingQuantity": 0,
                                        "lp": 133.5,
                                        "filledQty": 1,
                                        "clientId": "FM0224",
                                        "offlineOrder": False,
                                        "chp": -5.69,
                                        "instrument": "EQUITY",
                                        "lot_size": 1,
                                        "tradedPrice": 138.4,
                                        "productType": "CNC",
                                        "type": 2,
                                        "side": -1,
                                        "pan": "AFKPY8867N",
                                        "discloseQty": 0
                                    },
                                    {
                                        "status": 2,
                                        "ex_sym": "ZOMATO",
                                        "ch": -8.05,
                                        "description": "ZOMATO LIMITED",
                                        "exchange": "NSE",
                                        "symbol": "NSE:ZOMATO-EQ",
                                        "limitPrice": 0.0,
                                        "qty": 1,
                                        "orderNumStatus": "135262:2",
                                        "dqQtyRem": 0,
                                        "orderDateTime": "30-Jul-2021 10:04:38",
                                        "orderValidity": "DAY",
                                        "fyToken": "10100000005097",
                                        "slNo": 13,
                                        "message": "TRADE CONFIRMED",
                                        "segment": "E",
                                        "id": "135262",
                                        "stopPrice": 0.0,
                                        "tick_size": 0.05,
                                        "exchOrdId": "1300000005713152",
                                        "remainingQuantity": 0,
                                        "lp": 133.5,
                                        "filledQty": 1,
                                        "clientId": "FM0224",
                                        "offlineOrder": False,
                                        "chp": -5.69,
                                        "instrument": "EQUITY",
                                        "lot_size": 1,
                                        "tradedPrice": 138.5,
                                        "productType": "CNC",
                                        "type": 2,
                                        "side": 1,
                                        "pan": "AFKPY8867N",
                                        "discloseQty": 0
                                    },
                                    {
                                        "status": 5,
                                        "ex_sym": "ZOMATO",
                                        "ch": -8.05,
                                        "description": "ZOMATO LIMITED",
                                        "exchange": "NSE",
                                        "symbol": "NSE:ZOMATO-EQ",
                                        "limitPrice": 0.0,
                                        "qty": 1,
                                        "orderNumStatus": "134812:5",
                                        "dqQtyRem": 0,
                                        "orderDateTime": "30-Jul-2021 10:03:39",
                                        "orderValidity": "DAY",
                                        "fyToken": "10100000005097",
                                        "slNo": 14,
                                        "message": "RMS:134812:NSE,EQUITY,5097,ZOMATO,INTRADAY,,EQ,FM0224,B,1,I,138.20000,TRANSACTIONS ARE BLOCKED FOR THIS SCRIP (GLOBAL LEVEL)",
                                        "segment": "E",
                                        "id": "134812",
                                        "stopPrice": 0.0,
                                        "tick_size": 0.05,
                                        "exchOrdId": "0",
                                        "remainingQuantity": 1,
                                        "lp": 133.5,
                                        "filledQty": 0,
                                        "clientId": "FM0224",
                                        "offlineOrder": False,
                                        "chp": -5.69,
                                        "instrument": "EQUITY",
                                        "lot_size": 1,
                                        "tradedPrice": 0.0,
                                        "productType": "INTRADAY",
                                        "type": 2,
                                        "side": 1,
                                        "pan": "AFKPY8867N",
                                        "discloseQty": 0
                                    },
                                    {
                                        "status": 2,
                                        "ex_sym": "SAIL",
                                        "ch": 0.1,
                                        "description": "STEEL AUTHORITY OF INDIA",
                                        "exchange": "NSE",
                                        "symbol": "NSE:SAIL-EQ",
                                        "limitPrice": 0.0,
                                        "qty": 1,
                                        "orderNumStatus": "117437-BO-2:2",
                                        "dqQtyRem": 0,
                                        "parentType": 1,
                                        "orderValidity": "DAY",
                                        "fyToken": "10100000002963",
                                        "slNo": 15,
                                        "message": "TRADE CONFIRMED",
                                        "segment": "E",
                                        "id": "117437-BO-2",
                                        "stopPrice": 0.0,
                                        "tick_size": 0.05,
                                        "filledQty": 1,
                                        "exchOrdId": "1300000002884206",
                                        "remainingQuantity": 0,
                                        "lp": 142.05,
                                        "orderDateTime": "30-Jul-2021 09:35:11",
                                        "clientId": "FM0224",
                                        "offlineOrder": False,
                                        "chp": 0.07,
                                        "instrument": "EQUITY",
                                        "lot_size": 1,
                                        "tradedPrice": 142.0,
                                        "productType": "BO",
                                        "parentId": "116312-BO-1",
                                        "type": 2,
                                        "side": 1,
                                        "pan": "AFKPY8867N",
                                        "discloseQty": 0
                                    },
                                    {
                                        "status": 1,
                                        "ex_sym": "SAIL",
                                        "ch": 0.1,
                                        "description": "STEEL AUTHORITY OF INDIA",
                                        "exchange": "NSE",
                                        "symbol": "NSE:SAIL-EQ",
                                        "limitPrice": 140.85,
                                        "qty": 1,
                                        "orderNumStatus": "117447-BO-3:1",
                                        "dqQtyRem": 0,
                                        "parentType": 1,
                                        "orderValidity": "DAY",
                                        "fyToken": "10100000002963",
                                        "slNo": 16,
                                        "message": "CONFIRMED",
                                        "segment": "E",
                                        "id": "117447-BO-3",
                                        "stopPrice": 0.0,
                                        "tick_size": 0.05,
                                        "filledQty": 0,
                                        "exchOrdId": "1300000002884226",
                                        "remainingQuantity": 0,
                                        "lp": 142.05,
                                        "orderDateTime": "30-Jul-2021 09:35:10",
                                        "clientId": "FM0224",
                                        "offlineOrder": False,
                                        "chp": 0.07,
                                        "instrument": "EQUITY",
                                        "lot_size": 1,
                                        "tradedPrice": 0.0,
                                        "productType": "BO",
                                        "parentId": "116312-BO-1",
                                        "type": 1,
                                        "side": 1,
                                        "pan": "AFKPY8867N",
                                        "discloseQty": 0
                                    },
                                    {
                                        "status": 2,
                                        "ex_sym": "ONGC",
                                        "ch": 0.55,
                                        "description": "OIL AND NATURAL GAS CORP.",
                                        "exchange": "NSE",
                                        "symbol": "NSE:ONGC-EQ",
                                        "limitPrice": 0.0,
                                        "qty": 1,
                                        "orderNumStatus": "116022-CO-2:2",
                                        "dqQtyRem": 0,
                                        "parentType": 1,
                                        "orderValidity": "DAY",
                                        "fyToken": "10100000002475",
                                        "slNo": 17,
                                        "message": "TRADE CONFIRMED",
                                        "segment": "E",
                                        "id": "116022-CO-2",
                                        "stopPrice": 0.0,
                                        "tick_size": 0.05,
                                        "filledQty": 1,
                                        "exchOrdId": "1200000002200248",
                                        "remainingQuantity": 0,
                                        "lp": 115.3,
                                        "orderDateTime": "30-Jul-2021 09:35:10",
                                        "clientId": "FM0224",
                                        "offlineOrder": False,
                                        "chp": 0.48,
                                        "instrument": "EQUITY",
                                        "lot_size": 1,
                                        "tradedPrice": 114.6,
                                        "productType": "CO",
                                        "parentId": "116022-CO-1",
                                        "type": 2,
                                        "side": 1,
                                        "pan": "AFKPY8867N",
                                        "discloseQty": 0
                                    },
                                    {
                                        "status": 2,
                                        "ex_sym": "IRFC",
                                        "ch": 0.15,
                                        "description": "INDIAN RAILWAY FIN CORP L",
                                        "exchange": "NSE",
                                        "symbol": "NSE:IRFC-EQ",
                                        "limitPrice": 0.0,
                                        "qty": 1,
                                        "orderNumStatus": "117622:2",
                                        "dqQtyRem": 0,
                                        "orderDateTime": "30-Jul-2021 09:34:27",
                                        "orderValidity": "DAY",
                                        "fyToken": "10100000002029",
                                        "slNo": 18,
                                        "message": "TRADE CONFIRMED",
                                        "segment": "E",
                                        "id": "117622",
                                        "stopPrice": 0.0,
                                        "tick_size": 0.05,
                                        "exchOrdId": "1100000002292086",
                                        "remainingQuantity": 0,
                                        "lp": 23.0,
                                        "filledQty": 1,
                                        "clientId": "FM0224",
                                        "offlineOrder": False,
                                        "chp": 0.66,
                                        "instrument": "EQUITY",
                                        "lot_size": 1,
                                        "tradedPrice": 22.9,
                                        "productType": "CNC",
                                        "type": 2,
                                        "side": -1,
                                        "pan": "AFKPY8867N",
                                        "discloseQty": 0
                                    },
                                    {
                                        "status": 2,
                                        "ex_sym": "IOC",
                                        "ch": -0.75,
                                        "description": "INDIAN OIL CORP LTD",
                                        "exchange": "NSE",
                                        "symbol": "NSE:IOC-EQ",
                                        "limitPrice": 0.0,
                                        "qty": 1,
                                        "orderNumStatus": "115902-CO-2:2",
                                        "dqQtyRem": 0,
                                        "parentType": 1,
                                        "orderValidity": "DAY",
                                        "fyToken": "10100000001624",
                                        "slNo": 19,
                                        "message": "TRADE CONFIRMED",
                                        "segment": "E",
                                        "id": "115902-CO-2",
                                        "stopPrice": 0.0,
                                        "tick_size": 0.05,
                                        "filledQty": 1,
                                        "exchOrdId": "1100000002072697",
                                        "remainingQuantity": 0,
                                        "lp": 103.15,
                                        "orderDateTime": "30-Jul-2021 09:34:09",
                                        "clientId": "FM0224",
                                        "offlineOrder": False,
                                        "chp": -0.72,
                                        "instrument": "EQUITY",
                                        "lot_size": 1,
                                        "tradedPrice": 103.85,
                                        "productType": "CO",
                                        "parentId": "115902-CO-1",
                                        "type": 2,
                                        "side": -1,
                                        "pan": "AFKPY8867N",
                                        "discloseQty": 0
                                    },
                                    {
                                        "status": 2,
                                        "ex_sym": "ITC",
                                        "ch": -1.1,
                                        "description": "ITC LTD",
                                        "exchange": "NSE",
                                        "symbol": "NSE:ITC-EQ",
                                        "limitPrice": 0.0,
                                        "qty": 1,
                                        "orderNumStatus": "117232:2",
                                        "dqQtyRem": 0,
                                        "orderDateTime": "30-Jul-2021 09:33:58",
                                        "orderValidity": "DAY",
                                        "fyToken": "10100000001660",
                                        "slNo": 20,
                                        "message": "TRADE CONFIRMED",
                                        "segment": "E",
                                        "id": "117232",
                                        "stopPrice": 0.0,
                                        "tick_size": 0.05,
                                        "exchOrdId": "1100000002248546",
                                        "remainingQuantity": 0,
                                        "lp": 204.95,
                                        "filledQty": 1,
                                        "clientId": "FM0224",
                                        "offlineOrder": False,
                                        "chp": -0.53,
                                        "instrument": "EQUITY",
                                        "lot_size": 1,
                                        "tradedPrice": 206.0,
                                        "productType": "INTRADAY",
                                        "type": 2,
                                        "side": -1,
                                        "pan": "AFKPY8867N",
                                        "discloseQty": 0
                                    },
                                    {
                                        "status": 2,
                                        "ex_sym": "SBIN",
                                        "ch": -9.75,
                                        "description": "STATE BANK OF INDIA",
                                        "exchange": "NSE",
                                        "symbol": "NSE:SBIN-EQ",
                                        "limitPrice": 0.0,
                                        "qty": 1,
                                        "orderNumStatus": "117032:2",
                                        "dqQtyRem": 0,
                                        "orderDateTime": "30-Jul-2021 09:33:43",
                                        "orderValidity": "DAY",
                                        "fyToken": "10100000003045",
                                        "slNo": 21,
                                        "message": "TRADE CONFIRMED",
                                        "segment": "E",
                                        "id": "117032",
                                        "stopPrice": 0.0,
                                        "tick_size": 0.05,
                                        "exchOrdId": "1300000003027452",
                                        "remainingQuantity": 0,
                                        "lp": 431.8,
                                        "filledQty": 1,
                                        "clientId": "FM0224",
                                        "offlineOrder": False,
                                        "chp": -2.21,
                                        "instrument": "EQUITY",
                                        "lot_size": 1,
                                        "tradedPrice": 437.9,
                                        "productType": "INTRADAY",
                                        "type": 2,
                                        "side": 1,
                                        "pan": "AFKPY8867N",
                                        "discloseQty": 0
                                    },
                                    {
                                        "status": 2,
                                        "ex_sym": "GAIL",
                                        "ch": 2.05,
                                        "description": "GAIL (INDIA) LTD",
                                        "exchange": "NSE",
                                        "symbol": "NSE:GAIL-EQ",
                                        "limitPrice": 0.0,
                                        "qty": 1,
                                        "orderNumStatus": "116389-BO-2:2",
                                        "dqQtyRem": 0,
                                        "parentType": 1,
                                        "orderValidity": "DAY",
                                        "fyToken": "10100000004717",
                                        "slNo": 22,
                                        "message": "TRADE CONFIRMED",
                                        "segment": "E",
                                        "id": "116389-BO-2",
                                        "stopPrice": 0.0,
                                        "tick_size": 0.05,
                                        "filledQty": 1,
                                        "exchOrdId": "1100000002134733",
                                        "remainingQuantity": 0,
                                        "lp": 139.55,
                                        "orderDateTime": "30-Jul-2021 09:33:32",
                                        "clientId": "FM0224",
                                        "offlineOrder": False,
                                        "chp": 1.49,
                                        "instrument": "EQUITY",
                                        "lot_size": 1,
                                        "tradedPrice": 138.85,
                                        "productType": "BO",
                                        "parentId": "116422-BO-1",
                                        "type": 2,
                                        "side": -1,
                                        "pan": "AFKPY8867N",
                                        "discloseQty": 0
                                    },
                                    {
                                        "status": 1,
                                        "ex_sym": "GAIL",
                                        "ch": 2.05,
                                        "description": "GAIL (INDIA) LTD",
                                        "exchange": "NSE",
                                        "symbol": "NSE:GAIL-EQ",
                                        "limitPrice": 140.75,
                                        "qty": 1,
                                        "orderNumStatus": "116399-BO-3:1",
                                        "dqQtyRem": 0,
                                        "parentType": 1,
                                        "orderValidity": "DAY",
                                        "fyToken": "10100000004717",
                                        "slNo": 23,
                                        "message": "CONFIRMED",
                                        "segment": "E",
                                        "id": "116399-BO-3",
                                        "stopPrice": 0.0,
                                        "tick_size": 0.05,
                                        "filledQty": 0,
                                        "exchOrdId": "1100000002134762",
                                        "remainingQuantity": 0,
                                        "lp": 139.55,
                                        "orderDateTime": "30-Jul-2021 09:33:32",
                                        "clientId": "FM0224",
                                        "offlineOrder": False,
                                        "chp": 1.49,
                                        "instrument": "EQUITY",
                                        "lot_size": 1,
                                        "tradedPrice": 0.0,
                                        "productType": "BO",
                                        "parentId": "116422-BO-1",
                                        "type": 1,
                                        "side": -1,
                                        "pan": "AFKPY8867N",
                                        "discloseQty": 0
                                    },
                                    {
                                        "status": 2,
                                        "ex_sym": "IRFC",
                                        "ch": 0.15,
                                        "description": "INDIAN RAILWAY FIN CORP L",
                                        "exchange": "NSE",
                                        "symbol": "NSE:IRFC-EQ",
                                        "limitPrice": 0.0,
                                        "qty": 1,
                                        "orderNumStatus": "116842:2",
                                        "dqQtyRem": 0,
                                        "orderDateTime": "30-Jul-2021 09:33:17",
                                        "orderValidity": "DAY",
                                        "fyToken": "10100000002029",
                                        "slNo": 24,
                                        "message": "TRADE CONFIRMED",
                                        "segment": "E",
                                        "id": "116842",
                                        "stopPrice": 0.0,
                                        "tick_size": 0.05,
                                        "exchOrdId": "1100000002193510",
                                        "remainingQuantity": 0,
                                        "lp": 23.0,
                                        "filledQty": 1,
                                        "clientId": "FM0224",
                                        "offlineOrder": False,
                                        "chp": 0.66,
                                        "instrument": "EQUITY",
                                        "lot_size": 1,
                                        "tradedPrice": 22.95,
                                        "productType": "CNC",
                                        "type": 2,
                                        "side": 1,
                                        "pan": "AFKPY8867N",
                                        "discloseQty": 0
                                    },
                                    {
                                        "status": 2,
                                        "ex_sym": "GAIL",
                                        "ch": 2.05,
                                        "description": "GAIL (INDIA) LTD",
                                        "exchange": "NSE",
                                        "symbol": "NSE:GAIL-EQ",
                                        "limitPrice": 0.0,
                                        "qty": 1,
                                        "orderNumStatus": "116422-BO-1:2",
                                        "dqQtyRem": 0,
                                        "orderDateTime": "30-Jul-2021 09:32:36",
                                        "orderValidity": "DAY",
                                        "fyToken": "10100000004717",
                                        "slNo": 25,
                                        "message": "TRADE CONFIRMED",
                                        "segment": "E",
                                        "id": "116422-BO-1",
                                        "stopPrice": 0.0,
                                        "tick_size": 0.05,
                                        "exchOrdId": "1100000002134632",
                                        "remainingQuantity": 0,
                                        "lp": 139.55,
                                        "filledQty": 1,
                                        "clientId": "FM0224",
                                        "offlineOrder": False,
                                        "chp": 1.49,
                                        "instrument": "EQUITY",
                                        "lot_size": 1,
                                        "tradedPrice": 138.95,
                                        "productType": "BO",
                                        "type": 2,
                                        "side": 1,
                                        "pan": "AFKPY8867N",
                                        "discloseQty": 0
                                    },
                                    {
                                        "status": 2,
                                        "ex_sym": "SAIL",
                                        "ch": 0.1,
                                        "description": "STEEL AUTHORITY OF INDIA",
                                        "exchange": "NSE",
                                        "symbol": "NSE:SAIL-EQ",
                                        "limitPrice": 0.0,
                                        "qty": 1,
                                        "orderNumStatus": "116312-BO-1:2",
                                        "dqQtyRem": 0,
                                        "orderDateTime": "30-Jul-2021 09:32:30",
                                        "orderValidity": "DAY",
                                        "fyToken": "10100000002963",
                                        "slNo": 26,
                                        "message": "TRADE CONFIRMED",
                                        "segment": "E",
                                        "id": "116312-BO-1",
                                        "stopPrice": 0.0,
                                        "tick_size": 0.05,
                                        "exchOrdId": "1300000002884130",
                                        "remainingQuantity": 0,
                                        "lp": 142.05,
                                        "filledQty": 1,
                                        "clientId": "FM0224",
                                        "offlineOrder": False,
                                        "chp": 0.07,
                                        "instrument": "EQUITY",
                                        "lot_size": 1,
                                        "tradedPrice": 142.65,
                                        "productType": "BO",
                                        "type": 2,
                                        "side": -1,
                                        "pan": "AFKPY8867N",
                                        "discloseQty": 0
                                    },
                                    {
                                        "status": 2,
                                        "ex_sym": "ITC",
                                        "ch": -1.1,
                                        "description": "ITC LTD",
                                        "exchange": "NSE",
                                        "symbol": "NSE:ITC-EQ",
                                        "limitPrice": 0.0,
                                        "qty": 1,
                                        "orderNumStatus": "116232:2",
                                        "dqQtyRem": 0,
                                        "orderDateTime": "30-Jul-2021 09:32:16",
                                        "orderValidity": "DAY",
                                        "fyToken": "10100000001660",
                                        "slNo": 27,
                                        "message": "TRADE CONFIRMED",
                                        "segment": "E",
                                        "id": "116232",
                                        "stopPrice": 0.0,
                                        "tick_size": 0.05,
                                        "exchOrdId": "1100000002105499",
                                        "remainingQuantity": 0,
                                        "lp": 204.95,
                                        "filledQty": 1,
                                        "clientId": "FM0224",
                                        "offlineOrder": False,
                                        "chp": -0.53,
                                        "instrument": "EQUITY",
                                        "lot_size": 1,
                                        "tradedPrice": 205.8,
                                        "productType": "INTRADAY",
                                        "type": 2,
                                        "side": 1,
                                        "pan": "AFKPY8867N",
                                        "discloseQty": 0
                                    },
                                    {
                                        "status": 2,
                                        "ex_sym": "SBIN",
                                        "ch": -9.75,
                                        "description": "STATE BANK OF INDIA",
                                        "exchange": "NSE",
                                        "symbol": "NSE:SBIN-EQ",
                                        "limitPrice": 0.0,
                                        "qty": 1,
                                        "orderNumStatus": "116152:2",
                                        "dqQtyRem": 0,
                                        "orderDateTime": "30-Jul-2021 09:32:11",
                                        "orderValidity": "DAY",
                                        "fyToken": "10100000003045",
                                        "slNo": 28,
                                        "message": "TRADE CONFIRMED",
                                        "segment": "E",
                                        "id": "116152",
                                        "stopPrice": 0.0,
                                        "tick_size": 0.05,
                                        "exchOrdId": "1300000002849821",
                                        "remainingQuantity": 0,
                                        "lp": 431.8,
                                        "filledQty": 1,
                                        "clientId": "FM0224",
                                        "offlineOrder": False,
                                        "chp": -2.21,
                                        "instrument": "EQUITY",
                                        "lot_size": 1,
                                        "tradedPrice": 438.0,
                                        "productType": "INTRADAY",
                                        "type": 2,
                                        "side": -1,
                                        "pan": "AFKPY8867N",
                                        "discloseQty": 0
                                    },
                                    {
                                        "status": 2,
                                        "ex_sym": "ONGC",
                                        "ch": 0.55,
                                        "description": "OIL AND NATURAL GAS CORP.",
                                        "exchange": "NSE",
                                        "symbol": "NSE:ONGC-EQ",
                                        "limitPrice": 0.0,
                                        "qty": 1,
                                        "orderNumStatus": "116022-CO-1:2",
                                        "dqQtyRem": 0,
                                        "orderDateTime": "30-Jul-2021 09:32:03",
                                        "orderValidity": "DAY",
                                        "fyToken": "10100000002475",
                                        "slNo": 29,
                                        "message": "TRADE CONFIRMED",
                                        "segment": "E",
                                        "id": "116022-CO-1",
                                        "stopPrice": 0.0,
                                        "tick_size": 0.05,
                                        "exchOrdId": "1200000002200234",
                                        "remainingQuantity": 0,
                                        "lp": 115.3,
                                        "filledQty": 1,
                                        "clientId": "FM0224",
                                        "offlineOrder": False,
                                        "chp": 0.48,
                                        "instrument": "EQUITY",
                                        "lot_size": 1,
                                        "tradedPrice": 114.55,
                                        "productType": "CO",
                                        "type": 2,
                                        "side": -1,
                                        "pan": "AFKPY8867N",
                                        "discloseQty": 0
                                    },
                                    {
                                        "status": 2,
                                        "ex_sym": "IOC",
                                        "ch": -0.75,
                                        "description": "INDIAN OIL CORP LTD",
                                        "exchange": "NSE",
                                        "symbol": "NSE:IOC-EQ",
                                        "limitPrice": 0.0,
                                        "qty": 1,
                                        "orderNumStatus": "115902-CO-1:2",
                                        "dqQtyRem": 0,
                                        "orderDateTime": "30-Jul-2021 09:31:54",
                                        "orderValidity": "DAY",
                                        "fyToken": "10100000001624",
                                        "slNo": 30,
                                        "message": "TRADE CONFIRMED",
                                        "segment": "E",
                                        "id": "115902-CO-1",
                                        "stopPrice": 0.0,
                                        "tick_size": 0.05,
                                        "exchOrdId": "1100000002072691",
                                        "remainingQuantity": 0,
                                        "lp": 103.15,
                                        "filledQty": 1,
                                        "clientId": "FM0224",
                                        "offlineOrder": False,
                                        "chp": -0.72,
                                        "instrument": "EQUITY",
                                        "lot_size": 1,
                                        "tradedPrice": 103.75,
                                        "productType": "CO",
                                        "type": 2,
                                        "side": 1,
                                        "pan": "AFKPY8867N",
                                        "discloseQty": 0
                                    }
                              ]
                
                returnList.extend(returnList1)


            return [SUCCESS_C_1, returnList, userInfoList]

        # If the orderbook is empty
        else:
            if fyId == 'FM0224':
                returnList = [
                                    {
                                        "status": 2,
                                        "ex_sym": "IOC",
                                        "ch": -0.75,
                                        "description": "INDIAN OIL CORP LTD",
                                        "exchange": "NSE",
                                        "symbol": "NSE:IOC-EQ",
                                        "limitPrice": 0.0,
                                        "qty": 1,
                                        "orderNumStatus": "1114222:2",
                                        "dqQtyRem": 0,
                                        "orderDateTime": "30-Jul-2021 15:16:19",
                                        "orderValidity": "DAY",
                                        "fyToken": "10100000001624",
                                        "slNo": 1,
                                        "message": "TRADE CONFIRMED",
                                        "segment": "E",
                                        "id": "1114222",
                                        "stopPrice": 0.0,
                                        "tick_size": 0.05,
                                        "exchOrdId": "1100000017416045",
                                        "remainingQuantity": 0,
                                        "lp": 103.15,
                                        "filledQty": 1,
                                        "clientId": "FM0224",
                                        "offlineOrder": False,
                                        "chp": -0.72,
                                        "instrument": "EQUITY",
                                        "lot_size": 1,
                                        "tradedPrice": 103.0,
                                        "productType": "INTRADAY",
                                        "type": 2,
                                        "side": -1,
                                        "pan": "AFKPY8867N",
                                        "discloseQty": 0
                                    },
                                    {
                                        "status": 5,
                                        "ex_sym": "ZEEL",
                                        "ch": 0.5,
                                        "description": "21 Aug 26 220 CE",
                                        "exchange": "NSE",
                                        "symbol": "NSE:ZEEL21AUG220CE",
                                        "limitPrice": 0.0,
                                        "qty": 3000,
                                        "orderNumStatus": "221073049203:5",
                                        "dqQtyRem": 0,
                                        "orderDateTime": "30-Jul-2021 10:18:56",
                                        "orderValidity": "DAY",
                                        "fyToken": "1011210826114396",
                                        "slNo": 2,
                                        "message": "RMS:221073049203:NSE,OPTSTK,114396,ZEEL-Aug2021-220.0000-CE,INTRADAY,,2021-08-26 00:00:00,FM0224,S,3000,I,2.4,FUND LIMIT INSUFFICIENT,AVAILABLE FUND =54976.64,ADDITIONAL REQUIRED FUND=75193.17,CALCULATED SPAN & EXPOSURE FOR ORDER=130169.81",
                                        "segment": "D",
                                        "id": "221073049203",
                                        "stopPrice": 0.0,
                                        "tick_size": 0.05,
                                        "exchOrdId": "0",
                                        "remainingQuantity": 3000,
                                        "lp": 3.25,
                                        "filledQty": 0,
                                        "clientId": "FM0224",
                                        "offlineOrder": False,
                                        "chp": 18.18,
                                        "instrument": "OPTSTK",
                                        "lot_size": 3000,
                                        "tradedPrice": 0.0,
                                        "productType": "INTRADAY",
                                        "type": 2,
                                        "side": -1,
                                        "pan": "AFKPY8867N",
                                        "discloseQty": 0
                                    },
                                    {
                                        "status": 2,
                                        "ex_sym": "NIFTY",
                                        "ch": -1.15,
                                        "description": "21 Aug 05 15000 PE",
                                        "exchange": "NSE",
                                        "symbol": "NSE:NIFTY2180515000PE",
                                        "limitPrice": 0.0,
                                        "qty": 50,
                                        "orderNumStatus": "221073045263:2",
                                        "dqQtyRem": 0,
                                        "orderDateTime": "30-Jul-2021 10:13:58",
                                        "orderValidity": "DAY",
                                        "fyToken": "101121080539541",
                                        "slNo": 4,
                                        "message": "TRADE CONFIRMED",
                                        "segment": "D",
                                        "id": "221073045263",
                                        "stopPrice": 0.0,
                                        "tick_size": 0.05,
                                        "exchOrdId": "1000000012464322",
                                        "remainingQuantity": 0,
                                        "lp": 2.3,
                                        "filledQty": 50,
                                        "clientId": "FM0224",
                                        "offlineOrder": False,
                                        "chp": -33.33,
                                        "instrument": "OPTIDX",
                                        "lot_size": 50,
                                        "tradedPrice": 3.8,
                                        "productType": "INTRADAY",
                                        "type": 2,
                                        "side": -1,
                                        "pan": "AFKPY8867N",
                                        "discloseQty": 0
                                    },
                                    {
                                        "status": 2,
                                        "ex_sym": "NIFTY",
                                        "ch": -1.15,
                                        "description": "21 Aug 05 15000 PE",
                                        "exchange": "NSE",
                                        "symbol": "NSE:NIFTY2180515000PE",
                                        "limitPrice": 3.9,
                                        "qty": 50,
                                        "orderNumStatus": "221073044413:2",
                                        "dqQtyRem": 0,
                                        "orderDateTime": "30-Jul-2021 10:11:51",
                                        "orderValidity": "DAY",
                                        "fyToken": "101121080539541",
                                        "slNo": 5,
                                        "message": "TRADE CONFIRMED",
                                        "segment": "D",
                                        "id": "221073044413",
                                        "stopPrice": 0.0,
                                        "tick_size": 0.05,
                                        "exchOrdId": "1000000012254631",
                                        "remainingQuantity": 0,
                                        "lp": 2.3,
                                        "filledQty": 50,
                                        "clientId": "FM0224",
                                        "offlineOrder": False,
                                        "chp": -33.33,
                                        "instrument": "OPTIDX",
                                        "lot_size": 50,
                                        "tradedPrice": 3.85,
                                        "productType": "INTRADAY",
                                        "type": 1,
                                        "side": 1,
                                        "pan": "AFKPY8867N",
                                        "discloseQty": 0
                                    },
                                    {
                                        "status": 2,
                                        "ex_sym": "GOLDPETAL",
                                        "ch": 4.0,
                                        "description": "21 Aug 31 FUT",
                                        "exchange": "MCX",
                                        "symbol": "MCX:GOLDPETAL21AUGFUT",
                                        "limitPrice": 0.0,
                                        "qty": 1,
                                        "orderNumStatus": "807307306051:2",
                                        "dqQtyRem": 0,
                                        "orderDateTime": "30-Jul-2021 10:06:27",
                                        "orderValidity": "DAY",
                                        "fyToken": "1120210831229420",
                                        "slNo": 6,
                                        "message": "TRADE CONFIRMED",
                                        "segment": "M",
                                        "id": "807307306051",
                                        "stopPrice": 0.0,
                                        "tick_size": "1.0000",
                                        "exchOrdId": "362121100014181",
                                        "remainingQuantity": 0,
                                        "lp": 4811.0,
                                        "filledQty": 1,
                                        "clientId": "FM0224",
                                        "offlineOrder": False,
                                        "chp": 0.08,
                                        "instrument": "FUTCOM",
                                        "lot_size": 1,
                                        "tradedPrice": 4801.0,
                                        "productType": "INTRADAY",
                                        "type": 2,
                                        "side": -1,
                                        "pan": "AFKPY8867N",
                                        "discloseQty": 0
                                    },
                                    {
                                        "status": 2,
                                        "ex_sym": "GOLDPETAL",
                                        "ch": 4.0,
                                        "description": "21 Aug 31 FUT",
                                        "exchange": "MCX",
                                        "symbol": "MCX:GOLDPETAL21AUGFUT",
                                        "limitPrice": 0.0,
                                        "qty": 1,
                                        "orderNumStatus": "807307306041:2",
                                        "dqQtyRem": 0,
                                        "orderDateTime": "30-Jul-2021 10:06:15",
                                        "orderValidity": "DAY",
                                        "fyToken": "1120210831229420",
                                        "slNo": 7,
                                        "message": "TRADE CONFIRMED",
                                        "segment": "M",
                                        "id": "807307306041",
                                        "stopPrice": 0.0,
                                        "tick_size": "1.0000",
                                        "exchOrdId": "362121100014144",
                                        "remainingQuantity": 0,
                                        "lp": 4811.0,
                                        "filledQty": 1,
                                        "clientId": "FM0224",
                                        "offlineOrder": False,
                                        "chp": 0.08,
                                        "instrument": "FUTCOM",
                                        "lot_size": 1,
                                        "tradedPrice": 4802.0,
                                        "productType": "INTRADAY",
                                        "type": 2,
                                        "side": 1,
                                        "pan": "AFKPY8867N",
                                        "discloseQty": 0
                                    },
                                    {
                                        "status": 5,
                                        "ex_sym": "GOLDPETAL",
                                        "ch": 3.0,
                                        "description": "21 Jul 30 FUT",
                                        "exchange": "MCX",
                                        "symbol": "MCX:GOLDPETAL21JULFUT",
                                        "limitPrice": 0.0,
                                        "qty": 1,
                                        "orderNumStatus": "807307306031:5",
                                        "dqQtyRem": 0,
                                        "orderDateTime": "30-Jul-2021 10:06:01",
                                        "orderValidity": "DAY",
                                        "fyToken": "1120210730228846",
                                        "slNo": 8,
                                        "message": "RMS:807307306031:MCX,FUTCOM,228846,GOLDPETAL-Jul2021-FUT,INTRADAY,,2021-07-30 00:00:00,FM0224,B,1,I,4847,TRANSACTIONS ARE BLOCKED FOR THIS SCRIP (GLOBAL LEVEL)",
                                        "segment": "M",
                                        "id": "807307306031",
                                        "stopPrice": 0.0,
                                        "tick_size": "1.0000",
                                        "exchOrdId": "0",
                                        "remainingQuantity": 1,
                                        "lp": 4850.0,
                                        "filledQty": 0,
                                        "clientId": "FM0224",
                                        "offlineOrder": False,
                                        "chp": 0.06,
                                        "instrument": "FUTCOM",
                                        "lot_size": 1,
                                        "tradedPrice": 0.0,
                                        "productType": "INTRADAY",
                                        "type": 2,
                                        "side": 1,
                                        "pan": "AFKPY8867N",
                                        "discloseQty": 0
                                    },
                                    {
                                        "status": 5,
                                        "ex_sym": "SILVERMIC",
                                        "ch": -245.0,
                                        "description": "21 Aug 31 FUT",
                                        "exchange": "MCX",
                                        "symbol": "MCX:SILVERMIC21AUGFUT",
                                        "limitPrice": 0.0,
                                        "qty": 1,
                                        "orderNumStatus": "807307305981:5",
                                        "dqQtyRem": 0,
                                        "orderDateTime": "30-Jul-2021 10:05:41",
                                        "orderValidity": "DAY",
                                        "fyToken": "1120210831226204",
                                        "slNo": 9,
                                        "message": "RMS:807307305981:MCX,FUTCOM,226204,SILVERMIC-Aug2021-FUT,INTRADAY,,2021-08-31 00:00:00,FM0224,B,1,I,68082,FUND LIMIT INSUFFICIENT,AVAILABLE FUND =4995.75,ADDITIONAL REQUIRED FUND=772.52,CALCULATED SPAN & EXPOSURE FOR ORDER=5768.27|E0001|772.52",
                                        "segment": "M",
                                        "id": "807307305981",
                                        "stopPrice": 0.0,
                                        "tick_size": "1.0000",
                                        "exchOrdId": "0",
                                        "remainingQuantity": 1,
                                        "lp": 68155.0,
                                        "filledQty": 0,
                                        "clientId": "FM0224",
                                        "offlineOrder": False,
                                        "chp": -0.36,
                                        "instrument": "FUTCOM",
                                        "lot_size": 1,
                                        "tradedPrice": 0.0,
                                        "productType": "INTRADAY",
                                        "type": 2,
                                        "side": 1,
                                        "pan": "AFKPY8867N",
                                        "discloseQty": 0
                                    },
                                    {
                                        "status": 2,
                                        "ex_sym": "USDINR",
                                        "ch": 0.0925,
                                        "description": "21 Aug 27 FUT",
                                        "exchange": "NSE",
                                        "symbol": "NSE:USDINR21AUGFUT",
                                        "limitPrice": 0.0,
                                        "qty": 1,
                                        "orderNumStatus": "321073007481:2",
                                        "dqQtyRem": 0,
                                        "orderDateTime": "30-Jul-2021 10:05:22",
                                        "orderValidity": "DAY",
                                        "fyToken": "10122108277395",
                                        "slNo": 10,
                                        "message": "TRADE CONFIRMED",
                                        "segment": "C",
                                        "id": "321073007481",
                                        "stopPrice": 0.0,
                                        "tick_size": 0.0025,
                                        "exchOrdId": "1000000000478157",
                                        "remainingQuantity": 0,
                                        "lp": 74.5825,
                                        "filledQty": 1,
                                        "clientId": "FM0224",
                                        "offlineOrder": False,
                                        "chp": 0.12,
                                        "instrument": "FUTCUR",
                                        "lot_size": 1,
                                        "tradedPrice": 74.485,
                                        "productType": "INTRADAY",
                                        "type": 2,
                                        "side": -1,
                                        "pan": "AFKPY8867N",
                                        "discloseQty": 0
                                    },
                                    {
                                        "status": 2,
                                        "ex_sym": "USDINR",
                                        "ch": 0.0925,
                                        "description": "21 Aug 27 FUT",
                                        "exchange": "NSE",
                                        "symbol": "NSE:USDINR21AUGFUT",
                                        "limitPrice": 0.0,
                                        "qty": 1,
                                        "orderNumStatus": "321073007471:2",
                                        "dqQtyRem": 0,
                                        "orderDateTime": "30-Jul-2021 10:05:11",
                                        "orderValidity": "DAY",
                                        "fyToken": "10122108277395",
                                        "slNo": 11,
                                        "message": "TRADE CONFIRMED",
                                        "segment": "C",
                                        "id": "321073007471",
                                        "stopPrice": 0.0,
                                        "tick_size": 0.0025,
                                        "exchOrdId": "1000000000477293",
                                        "remainingQuantity": 0,
                                        "lp": 74.5825,
                                        "filledQty": 1,
                                        "clientId": "FM0224",
                                        "offlineOrder": False,
                                        "chp": 0.12,
                                        "instrument": "FUTCUR",
                                        "lot_size": 1,
                                        "tradedPrice": 74.49,
                                        "productType": "INTRADAY",
                                        "type": 2,
                                        "side": 1,
                                        "pan": "AFKPY8867N",
                                        "discloseQty": 0
                                    },
                                    {
                                        "status": 2,
                                        "ex_sym": "ZOMATO",
                                        "ch": -8.05,
                                        "description": "ZOMATO LIMITED",
                                        "exchange": "NSE",
                                        "symbol": "NSE:ZOMATO-EQ",
                                        "limitPrice": 0.0,
                                        "qty": 1,
                                        "orderNumStatus": "135402:2",
                                        "dqQtyRem": 0,
                                        "orderDateTime": "30-Jul-2021 10:04:54",
                                        "orderValidity": "DAY",
                                        "fyToken": "10100000005097",
                                        "slNo": 12,
                                        "message": "TRADE CONFIRMED",
                                        "segment": "E",
                                        "id": "135402",
                                        "stopPrice": 0.0,
                                        "tick_size": 0.05,
                                        "exchOrdId": "1300000005733873",
                                        "remainingQuantity": 0,
                                        "lp": 133.5,
                                        "filledQty": 1,
                                        "clientId": "FM0224",
                                        "offlineOrder": False,
                                        "chp": -5.69,
                                        "instrument": "EQUITY",
                                        "lot_size": 1,
                                        "tradedPrice": 138.4,
                                        "productType": "CNC",
                                        "type": 2,
                                        "side": -1,
                                        "pan": "AFKPY8867N",
                                        "discloseQty": 0
                                    },
                                    {
                                        "status": 2,
                                        "ex_sym": "ZOMATO",
                                        "ch": -8.05,
                                        "description": "ZOMATO LIMITED",
                                        "exchange": "NSE",
                                        "symbol": "NSE:ZOMATO-EQ",
                                        "limitPrice": 0.0,
                                        "qty": 1,
                                        "orderNumStatus": "135262:2",
                                        "dqQtyRem": 0,
                                        "orderDateTime": "30-Jul-2021 10:04:38",
                                        "orderValidity": "DAY",
                                        "fyToken": "10100000005097",
                                        "slNo": 13,
                                        "message": "TRADE CONFIRMED",
                                        "segment": "E",
                                        "id": "135262",
                                        "stopPrice": 0.0,
                                        "tick_size": 0.05,
                                        "exchOrdId": "1300000005713152",
                                        "remainingQuantity": 0,
                                        "lp": 133.5,
                                        "filledQty": 1,
                                        "clientId": "FM0224",
                                        "offlineOrder": False,
                                        "chp": -5.69,
                                        "instrument": "EQUITY",
                                        "lot_size": 1,
                                        "tradedPrice": 138.5,
                                        "productType": "CNC",
                                        "type": 2,
                                        "side": 1,
                                        "pan": "AFKPY8867N",
                                        "discloseQty": 0
                                    },
                                    {
                                        "status": 5,
                                        "ex_sym": "ZOMATO",
                                        "ch": -8.05,
                                        "description": "ZOMATO LIMITED",
                                        "exchange": "NSE",
                                        "symbol": "NSE:ZOMATO-EQ",
                                        "limitPrice": 0.0,
                                        "qty": 1,
                                        "orderNumStatus": "134812:5",
                                        "dqQtyRem": 0,
                                        "orderDateTime": "30-Jul-2021 10:03:39",
                                        "orderValidity": "DAY",
                                        "fyToken": "10100000005097",
                                        "slNo": 14,
                                        "message": "RMS:134812:NSE,EQUITY,5097,ZOMATO,INTRADAY,,EQ,FM0224,B,1,I,138.20000,TRANSACTIONS ARE BLOCKED FOR THIS SCRIP (GLOBAL LEVEL)",
                                        "segment": "E",
                                        "id": "134812",
                                        "stopPrice": 0.0,
                                        "tick_size": 0.05,
                                        "exchOrdId": "0",
                                        "remainingQuantity": 1,
                                        "lp": 133.5,
                                        "filledQty": 0,
                                        "clientId": "FM0224",
                                        "offlineOrder": False,
                                        "chp": -5.69,
                                        "instrument": "EQUITY",
                                        "lot_size": 1,
                                        "tradedPrice": 0.0,
                                        "productType": "INTRADAY",
                                        "type": 2,
                                        "side": 1,
                                        "pan": "AFKPY8867N",
                                        "discloseQty": 0
                                    },
                                    {
                                        "status": 2,
                                        "ex_sym": "SAIL",
                                        "ch": 0.1,
                                        "description": "STEEL AUTHORITY OF INDIA",
                                        "exchange": "NSE",
                                        "symbol": "NSE:SAIL-EQ",
                                        "limitPrice": 0.0,
                                        "qty": 1,
                                        "orderNumStatus": "117437-BO-2:2",
                                        "dqQtyRem": 0,
                                        "parentType": 1,
                                        "orderValidity": "DAY",
                                        "fyToken": "10100000002963",
                                        "slNo": 15,
                                        "message": "TRADE CONFIRMED",
                                        "segment": "E",
                                        "id": "117437-BO-2",
                                        "stopPrice": 0.0,
                                        "tick_size": 0.05,
                                        "filledQty": 1,
                                        "exchOrdId": "1300000002884206",
                                        "remainingQuantity": 0,
                                        "lp": 142.05,
                                        "orderDateTime": "30-Jul-2021 09:35:11",
                                        "clientId": "FM0224",
                                        "offlineOrder": False,
                                        "chp": 0.07,
                                        "instrument": "EQUITY",
                                        "lot_size": 1,
                                        "tradedPrice": 142.0,
                                        "productType": "BO",
                                        "parentId": "116312-BO-1",
                                        "type": 2,
                                        "side": 1,
                                        "pan": "AFKPY8867N",
                                        "discloseQty": 0
                                    },
                                    {
                                        "status": 1,
                                        "ex_sym": "SAIL",
                                        "ch": 0.1,
                                        "description": "STEEL AUTHORITY OF INDIA",
                                        "exchange": "NSE",
                                        "symbol": "NSE:SAIL-EQ",
                                        "limitPrice": 140.85,
                                        "qty": 1,
                                        "orderNumStatus": "117447-BO-3:1",
                                        "dqQtyRem": 0,
                                        "parentType": 1,
                                        "orderValidity": "DAY",
                                        "fyToken": "10100000002963",
                                        "slNo": 16,
                                        "message": "CONFIRMED",
                                        "segment": "E",
                                        "id": "117447-BO-3",
                                        "stopPrice": 0.0,
                                        "tick_size": 0.05,
                                        "filledQty": 0,
                                        "exchOrdId": "1300000002884226",
                                        "remainingQuantity": 0,
                                        "lp": 142.05,
                                        "orderDateTime": "30-Jul-2021 09:35:10",
                                        "clientId": "FM0224",
                                        "offlineOrder": False,
                                        "chp": 0.07,
                                        "instrument": "EQUITY",
                                        "lot_size": 1,
                                        "tradedPrice": 0.0,
                                        "productType": "BO",
                                        "parentId": "116312-BO-1",
                                        "type": 1,
                                        "side": 1,
                                        "pan": "AFKPY8867N",
                                        "discloseQty": 0
                                    },
                                    {
                                        "status": 2,
                                        "ex_sym": "ONGC",
                                        "ch": 0.55,
                                        "description": "OIL AND NATURAL GAS CORP.",
                                        "exchange": "NSE",
                                        "symbol": "NSE:ONGC-EQ",
                                        "limitPrice": 0.0,
                                        "qty": 1,
                                        "orderNumStatus": "116022-CO-2:2",
                                        "dqQtyRem": 0,
                                        "parentType": 1,
                                        "orderValidity": "DAY",
                                        "fyToken": "10100000002475",
                                        "slNo": 17,
                                        "message": "TRADE CONFIRMED",
                                        "segment": "E",
                                        "id": "116022-CO-2",
                                        "stopPrice": 0.0,
                                        "tick_size": 0.05,
                                        "filledQty": 1,
                                        "exchOrdId": "1200000002200248",
                                        "remainingQuantity": 0,
                                        "lp": 115.3,
                                        "orderDateTime": "30-Jul-2021 09:35:10",
                                        "clientId": "FM0224",
                                        "offlineOrder": False,
                                        "chp": 0.48,
                                        "instrument": "EQUITY",
                                        "lot_size": 1,
                                        "tradedPrice": 114.6,
                                        "productType": "CO",
                                        "parentId": "116022-CO-1",
                                        "type": 2,
                                        "side": 1,
                                        "pan": "AFKPY8867N",
                                        "discloseQty": 0
                                    },
                                    {
                                        "status": 2,
                                        "ex_sym": "IRFC",
                                        "ch": 0.15,
                                        "description": "INDIAN RAILWAY FIN CORP L",
                                        "exchange": "NSE",
                                        "symbol": "NSE:IRFC-EQ",
                                        "limitPrice": 0.0,
                                        "qty": 1,
                                        "orderNumStatus": "117622:2",
                                        "dqQtyRem": 0,
                                        "orderDateTime": "30-Jul-2021 09:34:27",
                                        "orderValidity": "DAY",
                                        "fyToken": "10100000002029",
                                        "slNo": 18,
                                        "message": "TRADE CONFIRMED",
                                        "segment": "E",
                                        "id": "117622",
                                        "stopPrice": 0.0,
                                        "tick_size": 0.05,
                                        "exchOrdId": "1100000002292086",
                                        "remainingQuantity": 0,
                                        "lp": 23.0,
                                        "filledQty": 1,
                                        "clientId": "FM0224",
                                        "offlineOrder": False,
                                        "chp": 0.66,
                                        "instrument": "EQUITY",
                                        "lot_size": 1,
                                        "tradedPrice": 22.9,
                                        "productType": "CNC",
                                        "type": 2,
                                        "side": -1,
                                        "pan": "AFKPY8867N",
                                        "discloseQty": 0
                                    },
                                    {
                                        "status": 2,
                                        "ex_sym": "IOC",
                                        "ch": -0.75,
                                        "description": "INDIAN OIL CORP LTD",
                                        "exchange": "NSE",
                                        "symbol": "NSE:IOC-EQ",
                                        "limitPrice": 0.0,
                                        "qty": 1,
                                        "orderNumStatus": "115902-CO-2:2",
                                        "dqQtyRem": 0,
                                        "parentType": 1,
                                        "orderValidity": "DAY",
                                        "fyToken": "10100000001624",
                                        "slNo": 19,
                                        "message": "TRADE CONFIRMED",
                                        "segment": "E",
                                        "id": "115902-CO-2",
                                        "stopPrice": 0.0,
                                        "tick_size": 0.05,
                                        "filledQty": 1,
                                        "exchOrdId": "1100000002072697",
                                        "remainingQuantity": 0,
                                        "lp": 103.15,
                                        "orderDateTime": "30-Jul-2021 09:34:09",
                                        "clientId": "FM0224",
                                        "offlineOrder": False,
                                        "chp": -0.72,
                                        "instrument": "EQUITY",
                                        "lot_size": 1,
                                        "tradedPrice": 103.85,
                                        "productType": "CO",
                                        "parentId": "115902-CO-1",
                                        "type": 2,
                                        "side": -1,
                                        "pan": "AFKPY8867N",
                                        "discloseQty": 0
                                    },
                                    {
                                        "status": 2,
                                        "ex_sym": "ITC",
                                        "ch": -1.1,
                                        "description": "ITC LTD",
                                        "exchange": "NSE",
                                        "symbol": "NSE:ITC-EQ",
                                        "limitPrice": 0.0,
                                        "qty": 1,
                                        "orderNumStatus": "117232:2",
                                        "dqQtyRem": 0,
                                        "orderDateTime": "30-Jul-2021 09:33:58",
                                        "orderValidity": "DAY",
                                        "fyToken": "10100000001660",
                                        "slNo": 20,
                                        "message": "TRADE CONFIRMED",
                                        "segment": "E",
                                        "id": "117232",
                                        "stopPrice": 0.0,
                                        "tick_size": 0.05,
                                        "exchOrdId": "1100000002248546",
                                        "remainingQuantity": 0,
                                        "lp": 204.95,
                                        "filledQty": 1,
                                        "clientId": "FM0224",
                                        "offlineOrder": False,
                                        "chp": -0.53,
                                        "instrument": "EQUITY",
                                        "lot_size": 1,
                                        "tradedPrice": 206.0,
                                        "productType": "INTRADAY",
                                        "type": 2,
                                        "side": -1,
                                        "pan": "AFKPY8867N",
                                        "discloseQty": 0
                                    },
                                    {
                                        "status": 2,
                                        "ex_sym": "SBIN",
                                        "ch": -9.75,
                                        "description": "STATE BANK OF INDIA",
                                        "exchange": "NSE",
                                        "symbol": "NSE:SBIN-EQ",
                                        "limitPrice": 0.0,
                                        "qty": 1,
                                        "orderNumStatus": "117032:2",
                                        "dqQtyRem": 0,
                                        "orderDateTime": "30-Jul-2021 09:33:43",
                                        "orderValidity": "DAY",
                                        "fyToken": "10100000003045",
                                        "slNo": 21,
                                        "message": "TRADE CONFIRMED",
                                        "segment": "E",
                                        "id": "117032",
                                        "stopPrice": 0.0,
                                        "tick_size": 0.05,
                                        "exchOrdId": "1300000003027452",
                                        "remainingQuantity": 0,
                                        "lp": 431.8,
                                        "filledQty": 1,
                                        "clientId": "FM0224",
                                        "offlineOrder": False,
                                        "chp": -2.21,
                                        "instrument": "EQUITY",
                                        "lot_size": 1,
                                        "tradedPrice": 437.9,
                                        "productType": "INTRADAY",
                                        "type": 2,
                                        "side": 1,
                                        "pan": "AFKPY8867N",
                                        "discloseQty": 0
                                    },
                                    {
                                        "status": 2,
                                        "ex_sym": "GAIL",
                                        "ch": 2.05,
                                        "description": "GAIL (INDIA) LTD",
                                        "exchange": "NSE",
                                        "symbol": "NSE:GAIL-EQ",
                                        "limitPrice": 0.0,
                                        "qty": 1,
                                        "orderNumStatus": "116389-BO-2:2",
                                        "dqQtyRem": 0,
                                        "parentType": 1,
                                        "orderValidity": "DAY",
                                        "fyToken": "10100000004717",
                                        "slNo": 22,
                                        "message": "TRADE CONFIRMED",
                                        "segment": "E",
                                        "id": "116389-BO-2",
                                        "stopPrice": 0.0,
                                        "tick_size": 0.05,
                                        "filledQty": 1,
                                        "exchOrdId": "1100000002134733",
                                        "remainingQuantity": 0,
                                        "lp": 139.55,
                                        "orderDateTime": "30-Jul-2021 09:33:32",
                                        "clientId": "FM0224",
                                        "offlineOrder": False,
                                        "chp": 1.49,
                                        "instrument": "EQUITY",
                                        "lot_size": 1,
                                        "tradedPrice": 138.85,
                                        "productType": "BO",
                                        "parentId": "116422-BO-1",
                                        "type": 2,
                                        "side": -1,
                                        "pan": "AFKPY8867N",
                                        "discloseQty": 0
                                    },
                                    {
                                        "status": 1,
                                        "ex_sym": "GAIL",
                                        "ch": 2.05,
                                        "description": "GAIL (INDIA) LTD",
                                        "exchange": "NSE",
                                        "symbol": "NSE:GAIL-EQ",
                                        "limitPrice": 140.75,
                                        "qty": 1,
                                        "orderNumStatus": "116399-BO-3:1",
                                        "dqQtyRem": 0,
                                        "parentType": 1,
                                        "orderValidity": "DAY",
                                        "fyToken": "10100000004717",
                                        "slNo": 23,
                                        "message": "CONFIRMED",
                                        "segment": "E",
                                        "id": "116399-BO-3",
                                        "stopPrice": 0.0,
                                        "tick_size": 0.05,
                                        "filledQty": 0,
                                        "exchOrdId": "1100000002134762",
                                        "remainingQuantity": 0,
                                        "lp": 139.55,
                                        "orderDateTime": "30-Jul-2021 09:33:32",
                                        "clientId": "FM0224",
                                        "offlineOrder": False,
                                        "chp": 1.49,
                                        "instrument": "EQUITY",
                                        "lot_size": 1,
                                        "tradedPrice": 0.0,
                                        "productType": "BO",
                                        "parentId": "116422-BO-1",
                                        "type": 1,
                                        "side": -1,
                                        "pan": "AFKPY8867N",
                                        "discloseQty": 0
                                    },
                                    {
                                        "status": 2,
                                        "ex_sym": "IRFC",
                                        "ch": 0.15,
                                        "description": "INDIAN RAILWAY FIN CORP L",
                                        "exchange": "NSE",
                                        "symbol": "NSE:IRFC-EQ",
                                        "limitPrice": 0.0,
                                        "qty": 1,
                                        "orderNumStatus": "116842:2",
                                        "dqQtyRem": 0,
                                        "orderDateTime": "30-Jul-2021 09:33:17",
                                        "orderValidity": "DAY",
                                        "fyToken": "10100000002029",
                                        "slNo": 24,
                                        "message": "TRADE CONFIRMED",
                                        "segment": "E",
                                        "id": "116842",
                                        "stopPrice": 0.0,
                                        "tick_size": 0.05,
                                        "exchOrdId": "1100000002193510",
                                        "remainingQuantity": 0,
                                        "lp": 23.0,
                                        "filledQty": 1,
                                        "clientId": "FM0224",
                                        "offlineOrder": False,
                                        "chp": 0.66,
                                        "instrument": "EQUITY",
                                        "lot_size": 1,
                                        "tradedPrice": 22.95,
                                        "productType": "CNC",
                                        "type": 2,
                                        "side": 1,
                                        "pan": "AFKPY8867N",
                                        "discloseQty": 0
                                    },
                                    {
                                        "status": 2,
                                        "ex_sym": "GAIL",
                                        "ch": 2.05,
                                        "description": "GAIL (INDIA) LTD",
                                        "exchange": "NSE",
                                        "symbol": "NSE:GAIL-EQ",
                                        "limitPrice": 0.0,
                                        "qty": 1,
                                        "orderNumStatus": "116422-BO-1:2",
                                        "dqQtyRem": 0,
                                        "orderDateTime": "30-Jul-2021 09:32:36",
                                        "orderValidity": "DAY",
                                        "fyToken": "10100000004717",
                                        "slNo": 25,
                                        "message": "TRADE CONFIRMED",
                                        "segment": "E",
                                        "id": "116422-BO-1",
                                        "stopPrice": 0.0,
                                        "tick_size": 0.05,
                                        "exchOrdId": "1100000002134632",
                                        "remainingQuantity": 0,
                                        "lp": 139.55,
                                        "filledQty": 1,
                                        "clientId": "FM0224",
                                        "offlineOrder": False,
                                        "chp": 1.49,
                                        "instrument": "EQUITY",
                                        "lot_size": 1,
                                        "tradedPrice": 138.95,
                                        "productType": "BO",
                                        "type": 2,
                                        "side": 1,
                                        "pan": "AFKPY8867N",
                                        "discloseQty": 0
                                    },
                                    {
                                        "status": 2,
                                        "ex_sym": "SAIL",
                                        "ch": 0.1,
                                        "description": "STEEL AUTHORITY OF INDIA",
                                        "exchange": "NSE",
                                        "symbol": "NSE:SAIL-EQ",
                                        "limitPrice": 0.0,
                                        "qty": 1,
                                        "orderNumStatus": "116312-BO-1:2",
                                        "dqQtyRem": 0,
                                        "orderDateTime": "30-Jul-2021 09:32:30",
                                        "orderValidity": "DAY",
                                        "fyToken": "10100000002963",
                                        "slNo": 26,
                                        "message": "TRADE CONFIRMED",
                                        "segment": "E",
                                        "id": "116312-BO-1",
                                        "stopPrice": 0.0,
                                        "tick_size": 0.05,
                                        "exchOrdId": "1300000002884130",
                                        "remainingQuantity": 0,
                                        "lp": 142.05,
                                        "filledQty": 1,
                                        "clientId": "FM0224",
                                        "offlineOrder": False,
                                        "chp": 0.07,
                                        "instrument": "EQUITY",
                                        "lot_size": 1,
                                        "tradedPrice": 142.65,
                                        "productType": "BO",
                                        "type": 2,
                                        "side": -1,
                                        "pan": "AFKPY8867N",
                                        "discloseQty": 0
                                    },
                                    {
                                        "status": 2,
                                        "ex_sym": "ITC",
                                        "ch": -1.1,
                                        "description": "ITC LTD",
                                        "exchange": "NSE",
                                        "symbol": "NSE:ITC-EQ",
                                        "limitPrice": 0.0,
                                        "qty": 1,
                                        "orderNumStatus": "116232:2",
                                        "dqQtyRem": 0,
                                        "orderDateTime": "30-Jul-2021 09:32:16",
                                        "orderValidity": "DAY",
                                        "fyToken": "10100000001660",
                                        "slNo": 27,
                                        "message": "TRADE CONFIRMED",
                                        "segment": "E",
                                        "id": "116232",
                                        "stopPrice": 0.0,
                                        "tick_size": 0.05,
                                        "exchOrdId": "1100000002105499",
                                        "remainingQuantity": 0,
                                        "lp": 204.95,
                                        "filledQty": 1,
                                        "clientId": "FM0224",
                                        "offlineOrder": False,
                                        "chp": -0.53,
                                        "instrument": "EQUITY",
                                        "lot_size": 1,
                                        "tradedPrice": 205.8,
                                        "productType": "INTRADAY",
                                        "type": 2,
                                        "side": 1,
                                        "pan": "AFKPY8867N",
                                        "discloseQty": 0
                                    },
                                    {
                                        "status": 2,
                                        "ex_sym": "SBIN",
                                        "ch": -9.75,
                                        "description": "STATE BANK OF INDIA",
                                        "exchange": "NSE",
                                        "symbol": "NSE:SBIN-EQ",
                                        "limitPrice": 0.0,
                                        "qty": 1,
                                        "orderNumStatus": "116152:2",
                                        "dqQtyRem": 0,
                                        "orderDateTime": "30-Jul-2021 09:32:11",
                                        "orderValidity": "DAY",
                                        "fyToken": "10100000003045",
                                        "slNo": 28,
                                        "message": "TRADE CONFIRMED",
                                        "segment": "E",
                                        "id": "116152",
                                        "stopPrice": 0.0,
                                        "tick_size": 0.05,
                                        "exchOrdId": "1300000002849821",
                                        "remainingQuantity": 0,
                                        "lp": 431.8,
                                        "filledQty": 1,
                                        "clientId": "FM0224",
                                        "offlineOrder": False,
                                        "chp": -2.21,
                                        "instrument": "EQUITY",
                                        "lot_size": 1,
                                        "tradedPrice": 438.0,
                                        "productType": "INTRADAY",
                                        "type": 2,
                                        "side": -1,
                                        "pan": "AFKPY8867N",
                                        "discloseQty": 0
                                    },
                                    {
                                        "status": 2,
                                        "ex_sym": "ONGC",
                                        "ch": 0.55,
                                        "description": "OIL AND NATURAL GAS CORP.",
                                        "exchange": "NSE",
                                        "symbol": "NSE:ONGC-EQ",
                                        "limitPrice": 0.0,
                                        "qty": 1,
                                        "orderNumStatus": "116022-CO-1:2",
                                        "dqQtyRem": 0,
                                        "orderDateTime": "30-Jul-2021 09:32:03",
                                        "orderValidity": "DAY",
                                        "fyToken": "10100000002475",
                                        "slNo": 29,
                                        "message": "TRADE CONFIRMED",
                                        "segment": "E",
                                        "id": "116022-CO-1",
                                        "stopPrice": 0.0,
                                        "tick_size": 0.05,
                                        "exchOrdId": "1200000002200234",
                                        "remainingQuantity": 0,
                                        "lp": 115.3,
                                        "filledQty": 1,
                                        "clientId": "FM0224",
                                        "offlineOrder": False,
                                        "chp": 0.48,
                                        "instrument": "EQUITY",
                                        "lot_size": 1,
                                        "tradedPrice": 114.55,
                                        "productType": "CO",
                                        "type": 2,
                                        "side": -1,
                                        "pan": "AFKPY8867N",
                                        "discloseQty": 0
                                    },
                                    {
                                        "status": 2,
                                        "ex_sym": "IOC",
                                        "ch": -0.75,
                                        "description": "INDIAN OIL CORP LTD",
                                        "exchange": "NSE",
                                        "symbol": "NSE:IOC-EQ",
                                        "limitPrice": 0.0,
                                        "qty": 1,
                                        "orderNumStatus": "115902-CO-1:2",
                                        "dqQtyRem": 0,
                                        "orderDateTime": "30-Jul-2021 09:31:54",
                                        "orderValidity": "DAY",
                                        "fyToken": "10100000001624",
                                        "slNo": 30,
                                        "message": "TRADE CONFIRMED",
                                        "segment": "E",
                                        "id": "115902-CO-1",
                                        "stopPrice": 0.0,
                                        "tick_size": 0.05,
                                        "exchOrdId": "1100000002072691",
                                        "remainingQuantity": 0,
                                        "lp": 103.15,
                                        "filledQty": 1,
                                        "clientId": "FM0224",
                                        "offlineOrder": False,
                                        "chp": -0.72,
                                        "instrument": "EQUITY",
                                        "lot_size": 1,
                                        "tradedPrice": 103.75,
                                        "productType": "CO",
                                        "type": 2,
                                        "side": 1,
                                        "pan": "AFKPY8867N",
                                        "discloseQty": 0
                                    }
                              ]
            return [SUCCESS_C_1, returnList, userInfoList]

    except Exception as e:
        logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName,callingFuncName, e, ERROR_C_UNKNOWN, tokenHash)
        return [ERROR_C_1, ERROR_C_UNKNOWN, e]


def INTERNAL_exitCoverOrder(tokenHash, orderID, callingFuncName="",userIp=""):
    """
    [FUNCTION]
        Get the status of a particular order by User and OrderID
    [PARAMS]
        tokenHash       : This is a hash of (fyId + AppId)
        orderID         : Order Id to be modified
    [RETURN]
        Success : [SUCCESS_C_1,successCode,"success message"]
        Failure : [CONST_function/oms_error,errorCode,"error message"]
    """
    funcName = "INTERNAL_exitCoverOrder"
    try:
        orderID2 = orderID.split("-")
        orderID1 = orderID2[0]
        orderLegNumber = orderID2[-1]
        localMemory = connectRedis(callingFuncName=callingFuncName)

        fyTokenList = INTERNAL_fy_getNecessaryOMSData_withID(tokenHash, localMemory=localMemory,
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

        # Get order details of the particular order
        entireOrderDetails1 = INTERNAL_getOrderStatus_withID2(tokenHash, orderID,localMemory=localMemory, orderProductType=API_OMS_V_ORDER_PROD_CO_2,callingFuncName=callingFuncName,userIp=userIp)
        if (entireOrderDetails1[0] == ERROR_C_1) or (entireOrderDetails1[0] == ERROR_C_OMS_1):
            return entireOrderDetails1
        entireOrderDetails = entireOrderDetails1[1]
        count = 0

        modOrderSerialNumber = entireOrderDetails[16]
        modSecurityId = entireOrderDetails[17]
        modTradedQty = entireOrderDetails[23]
        modQtyRem = entireOrderDetails[11]
        modInstrumentType = entireOrderDetails[5]
        modifiedTrigPrice = entireOrderDetails[12]
        orderStatus = entireOrderDetails[9].lower()

        ## Edit for order status - Palash 20181220
        if orderStatus == "traded":
            return [ERROR_C_1, ERROR_C_OMS_ORDER_ALREADY_TRADED, ERROR_M_ORDER_ALREADY_TRADED]

        try:
            modInstrumentType = modInstrumentType.upper()
        except Exception as e:
            return [ERROR_C_1, ERROR_C_INV_INST_TYPE, ERROR_M_INV_INST_TYPE]

        # Rupeeseed requires the segments sent to them differently
        if modInstrumentType == API_OMS_V_SEG_CM_1:
            modInstrumentType = API_OMS_V_SEG_CM_2
        elif modInstrumentType == API_OMS_V_SEG_FO_1:
            modInstrumentType = API_OMS_V_SEG_FO_2
        elif modInstrumentType == API_OMS_V_SEG_CD_1:
            None
        elif modInstrumentType == API_OMS_V_SEG_COM_1:
            None
        else:
            return [ERROR_C_1, ERROR_C_INV_INST_TYPE, ERROR_M_INV_INST_TYPE]

        modExchange = entireOrderDetails[3]
        modScripName = entireOrderDetails[7]

        try:
            transactionType = entireOrderDetails[4].upper()
            if transactionType == API_OMS_V_ORDER_SIDE_BUY_2 or transactionType == API_OMS_V_ORDER_SIDE_BUY_1:
                transactionType = API_OMS_V_ORDER_SIDE_BUY_1
            elif transactionType == API_OMS_V_ORDER_SIDE_SELL_2 or transactionType == API_OMS_V_ORDER_SIDE_SELL_1:
                transactionType = API_OMS_V_ORDER_SIDE_SELL_1
            else:
                return [ERROR_C_1, ERROR_C_INV_ORDER_SIDE, ERROR_M_INV_ORDER_SIDE]
        except Exception as e:
            return [ERROR_C_1, ERROR_C_INV_ORDER_SIDE, ERROR_M_INV_ORDER_SIDE]
        modifiedQty = entireOrderDetails[11]

        modifiedPrice = entireOrderDetails[12]

        try:
            orderType = entireOrderDetails[14].upper()
            if orderType == API_OMS_V_ORDER_TYPE_LMT_2:
                orderType = API_OMS_V_ORDER_TYPE_LMT_1
            elif orderType == API_OMS_V_ORDER_TYPE_MKT_2 or orderType == "SL-M":
                orderType = API_OMS_V_ORDER_TYPE_MKT_1
        except Exception as e:
            return [ERROR_C_1, ERROR_C_INV_ORDER_TYPE,ERROR_M_INV_ORDER_TYPE]

        modifiedProduct = entireOrderDetails[8]

        try:
            modifiedProduct = modifiedProduct.upper()
            if modifiedProduct == API_OMS_V_ORDER_PROD_CO_2 or modifiedProduct == API_OMS_V_ORDER_PROD_CO_1:
                modifiedProduct = API_OMS_V_ORDER_PROD_CO_1
            else:
                return [ERROR_C_1, ERROR_C_INV_ORDER_PRODUCT, ERROR_M_INV_ORDER_PRODUCT]
        except Exception as e:
            return [ERROR_C_1, ERROR_C_INV_ORDER_PRODUCT, ERROR_M_INV_ORDER_PRODUCT]

        modifiedValidity = entireOrderDetails[18]

        modifiedDiscQty = entireOrderDetails[15]

        offlineFlag = API_OMS_V_DEFAULT_ORDER_OFFLINE_FLAG_2

        # If its an offline order, we should change the offline flag to true
        if "o-" in orderStatus:
            offlineFlag = "true"

        paramsPayload = {
            "user_type": OMSUserType,
            "modorder_validity": modifiedValidity,
            "modorder_number": str(orderID1),
            "modproductlist": modifiedProduct,
            "modfTriggerPrice": str(modifiedTrigPrice),
            "offline_flag": offlineFlag,
            "disclosequantity": str(modifiedDiscQty),
            "token_id": OMStoken,
            "quantitytype": orderType,
            "modtraded_qty": modTradedQty,
            "securityid": str(modSecurityId),
            "modquantity": str(modifiedQty),
            "inst_type": modInstrumentType,
            "buysell": transactionType,
            "modorder_type": orderType,
            "modorder_serial_number": str(modOrderSerialNumber),
            API_OMS_K_REQ_SOURCE: source,
            "iLegValue": orderLegNumber,
            "user_id": OMSUserID,
            "client_id": OMSid,
            "modqty_remng": str(modQtyRem),
            "modprice": str(modifiedPrice),
            "fillQty": "",
            "exchange": modExchange,
            "marketProflag": API_OMS_V_DEFAULT_MARKET_PRO_FLAG,
            "marketProVal": API_OMS_V_DEFAULT_MARKET_PRO_VAL,
            "ParticipantType": "",
            "settlor": "",
            "Gtcflag": API_OMS_V_DEFAULT_GTC_FLAG,
            "EncashFlag": API_OMS_V_DEFAULT_ENCASH_FLAG,
            API_OMS_K_PAN_1: pan
        }
        # Send request to the OMS
        urlForRequest = REQ_URL_OMS_MAIN_1 + API_OMS_REQ_PATH_CO_EXIT
        sendReqFuncRet = INTERNAL_createAndSendOmsRequest(OMSid, OMStoken, aesKey,paramsPayload, urlForRequest,callingFuncName=callingFuncName,userIp=userIp)
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
                                            urlForRequest,fyId=OMSid, localMemory=localMemory,callingFuncName=callingFuncName,userIp=userIp)
        return readOmsResponseFuncRet2

    except Exception as e:
        logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName,
                      callingFuncName, e, ERROR_C_UNKNOWN, tokenHash)
        return [ERROR_C_1, ERROR_C_UNKNOWN, ""]


def INTERNAL_exitBracketOrder(tokenHash, orderID, callingFuncName="",userIp=""):
    """
    Exit bracket order
    [PARAMS]
        tokenHash       : This is a hash of (fyId + AppId)
        orderID         : Order Id to be modified
    [RETURN]
        Success : [SUCCESS_C_1,successCode,"success message"]
        Failure : [ERROR_C_1/ERROR_C_OMS_1,errorCode,"error message"]
    """
    funcName = "INTERNAL_exitBracketOrder"
    try:
        orderID2 = orderID.split("-")
        orderID1 = orderID2[0]
        orderLegNumber = orderID2[-1]
        localMemory = connectRedis(callingFuncName=callingFuncName)

        fyTokenList = INTERNAL_fy_getNecessaryOMSData_withID(tokenHash, localMemory=localMemory,
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

        # Get order details of the particular order
        entireOrderDetails1 = INTERNAL_getOrderStatus_withID2(tokenHash, orderID,localMemory=localMemory, orderProductType=API_OMS_V_ORDER_PROD_BO_2,callingFuncName=callingFuncName,userIp=userIp)
        if (entireOrderDetails1[0] == ERROR_C_1) or (entireOrderDetails1[0] == ERROR_C_OMS_1):
            return entireOrderDetails1
        entireOrderDetails = entireOrderDetails1[1]
        count = 0

        modOrderSerialNumber = entireOrderDetails[16]
        modSecurityId = entireOrderDetails[17]
        modTradedQty = entireOrderDetails[23]
        modQtyRem = entireOrderDetails[11]
        modInstrumentType = entireOrderDetails[5]
        modifiedTrigPrice = entireOrderDetails[13]
        orderStatus = entireOrderDetails[9].lower()
        orderLegNumber = entireOrderDetails[29]
        slAbsTickValue = entireOrderDetails[30]
        prfAbsTickValue = entireOrderDetails[31]
        algoOrderNum = entireOrderDetails[32]
        orderOffOn = entireOrderDetails[33]

        ##Edit for order status - Palash 20181220
        if orderStatus == "traded":
            return [ERROR_C_1, ERROR_C_OMS_ORDER_ALREADY_TRADED, ERROR_M_ORDER_ALREADY_TRADED]

        try:
            modInstrumentType = modInstrumentType.upper()
        except Exception as e:
            return [ERROR_C_1, ERROR_C_INV_INST_TYPE, ERROR_M_INV_INST_TYPE]

        # Rupeeseed requires the segments sent to them differently
        if modInstrumentType == API_OMS_V_SEG_CM_1:
            modInstrumentType = API_OMS_V_SEG_CM_2
        elif modInstrumentType == API_OMS_V_SEG_FO_1:
            modInstrumentType = API_OMS_V_SEG_FO_2
        elif modInstrumentType == API_OMS_V_SEG_CD_1:
            None
        elif modInstrumentType == API_OMS_V_SEG_COM_1:
            None
        else:
            return [ERROR_C_1, ERROR_C_INV_INST_TYPE, ERROR_M_INV_INST_TYPE]

        modExchange = entireOrderDetails[3]
        modScripName = entireOrderDetails[7]

        try:
            transactionType = entireOrderDetails[4].upper()
            if transactionType == API_OMS_V_ORDER_SIDE_BUY_2 or transactionType == API_OMS_V_ORDER_SIDE_BUY_1:
                transactionType = API_OMS_V_ORDER_SIDE_BUY_1
            elif transactionType == API_OMS_V_ORDER_SIDE_SELL_2 or transactionType == API_OMS_V_ORDER_SIDE_SELL_1:
                transactionType = API_OMS_V_ORDER_SIDE_SELL_1
            else:
                return [ERROR_C_1, ERROR_C_INV_ORDER_SIDE, ERROR_M_INV_ORDER_SIDE]
        except Exception as e:
            return [ERROR_C_1, ERROR_C_INV_ORDER_SIDE, ERROR_M_INV_ORDER_SIDE]
        modifiedQty = entireOrderDetails[11]

        modifiedPrice = entireOrderDetails[12]

        try:
            orderType = entireOrderDetails[14].upper()
            if orderType == API_OMS_V_ORDER_TYPE_LMT_2:
                orderType = API_OMS_V_ORDER_TYPE_LMT_1
            elif orderType == API_OMS_V_ORDER_TYPE_MKT_2:
                orderType = API_OMS_V_ORDER_TYPE_MKT_1
            elif orderType == "SL-M":
                orderType = API_OMS_V_ORDER_TYPE_MKT_1 #"SL-M"
            elif orderType == "SL-L" or orderType == "SL":
                orderType = API_OMS_V_ORDER_TYPE_LMT_1 #"SL"
        except Exception as e:
            return [ERROR_C_1, ERROR_C_INV_ORDER_TYPE,ERROR_M_INV_ORDER_TYPE]

        modifiedProduct = entireOrderDetails[8]

        try:
            modifiedProduct = modifiedProduct.upper()
            if modifiedProduct == API_OMS_V_ORDER_PROD_BO_2 or modifiedProduct == API_OMS_V_ORDER_PROD_BO_1:
                modifiedProduct = API_OMS_V_ORDER_PROD_BO_1
            else:
                return [ERROR_C_1, ERROR_C_INV_ORDER_PRODUCT, ERROR_M_INV_ORDER_PRODUCT]
        except Exception as e:
            return [ERROR_C_1, ERROR_C_INV_ORDER_PRODUCT, ERROR_M_INV_ORDER_PRODUCT]

        modifiedValidity = entireOrderDetails[18]

        modifiedDiscQty = entireOrderDetails[15]

        offlineFlag = API_OMS_V_DEFAULT_ORDER_OFFLINE_FLAG_2

        # If its an offline order, we should change the offline flag to true
        if "o-" in orderStatus:
            offlineFlag = "true"

        paramsPayload = {
            "user_type": OMSUserType,
            "modorder_validity": modifiedValidity,
            "modorder_number": str(orderID1),
            "modproductlist": modifiedProduct,
            "modfTriggerPrice": str(modifiedTrigPrice),
            "offline_flag": offlineFlag,
            "disclosequantity": str(modifiedDiscQty),
            "modtraded_qty": modTradedQty,
            "securityid": str(modSecurityId),
            "modquantity": str(modifiedQty),
            "inst_type": modInstrumentType,
            "buysell": transactionType,
            "modorder_type": orderType,
            "modorder_serial_number": str(modOrderSerialNumber),
            "iLegValue": orderLegNumber,
            "user_id": OMSUserID,
            "client_id": OMSid,
            "modqty_remng": str(modQtyRem),
            "modprice": str(modifiedPrice),
            "exchange": modExchange,
            "fPBTikAbsValue": str(prfAbsTickValue),
            "fSLTikAbsValue": str(slAbsTickValue),
            API_OMS_K_REQ_SOURCE: source,
            "mod_fTrailingSLValue": str(0),
            "mod_algo_ord_number": str(algoOrderNum),

            "token_id": OMStoken,
            "quantitytype": orderType,
            "fillQty": "",

            "marketProflag": API_OMS_V_DEFAULT_MARKET_PRO_FLAG,
            "marketProVal": API_OMS_V_DEFAULT_MARKET_PRO_VAL,
            "ParticipantType": "B",
            "settlor": "",
            "Gtcflag": API_OMS_V_DEFAULT_GTC_FLAG,
            "EncashFlag": API_OMS_V_DEFAULT_ENCASH_FLAG,
            API_OMS_K_PAN_1: pan
        }
        # Send request to the OMS
        urlForRequest = REQ_URL_OMS_MAIN_1 + API_OMS_REQ_PATH_BO_EXIT
        sendReqFuncRet = INTERNAL_createAndSendOmsRequest(OMSid, OMStoken, aesKey,paramsPayload, urlForRequest,callingFuncName=callingFuncName,userIp=userIp)
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
                                            urlForRequest,fyId=OMSid, localMemory=localMemory,callingFuncName=callingFuncName,userIp=userIp)
        return readOmsResponseFuncRet2

    except Exception as e:
        logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, e, ERROR_C_UNKNOWN, tokenHash)
        return [ERROR_C_1, ERROR_C_UNKNOWN, ""]


def main():
    None


if __name__ == "__main__":
    main()
