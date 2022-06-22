moduleName = "fy_trading_internal_functions_orders_POST"
try:
    import sys

    from fy_base_defines import LOG_STATUS_ERROR_1
    from fy_base_success_error_codes import ERROR_C_1, \
     ERROR_C_UNKNOWN, ERROR_C_INV_ORDER_QTY, ERROR_C_INV_ORDER_TRIG_PRICE, \
     ERROR_C_INV_EXCHANGE, ERROR_C_INV_SEGMENT, ERROR_C_INV_ORDER_PRODUCT, \
     ERROR_C_INV_ORDER_TYPE_CO, ERROR_C_INV_ORDER_SIDE, \
     ERROR_C_INV_ORDER_TARGET_VAL, ERROR_C_INV_ORDER_STOP_LOSS_VAL, \
     ERROR_C_INV_ORDER_TRAILING_SL_VAL, ERROR_C_INV_ORDER_TYPE_BO, \
     ERROR_C_INV_ORDER_LMT_PRICE, ERROR_C_INV_ORDER_STOP_LMT_PRICE, ERROR_C_INV_ORDER_TYPE
    from fy_base_success_error_messages import ERROR_M_INV_ORDER_QTY, \
     ERROR_M_INV_ORDER_TRIG_PRICE, ERROR_M_INV_EXCHANGE, ERROR_M_INV_SEGMENT, \
     ERROR_M_INV_ORDER_PRODUCT, ERROR_M_INV_ORDER_TYPE_CO, \
     ERROR_M_INV_ORDER_SIDE, ERROR_M_INV_ORDER_TYPE, \
     ERROR_M_INV_ORDER_TARGET_VAL, ERROR_M_INV_ORDER_STOP_LOSS_VAL, \
     ERROR_M_INV_ORDER_TRAILING_SL_VAL, ERROR_M_INV_ORDER_LMT_PRICE, \
     ERROR_M_INV_ORDER_STP_LMT_PRICE, ERROR_M_INV_ORDER_TYPE_BO_2
    from fy_common_api_keys_values import API_V_ORDER_TYPE_MKT_1, \
     API_V_ORDER_TYPE_MKT_2, API_V_ORDER_TYPE_LMT_1, API_V_ORDER_TYPE_LMT_2, \
     API_V_ORDER_SIDE_BUY_1, API_V_ORDER_SIDE_SELL_1, API_V_ORDER_TYPE_STP_MKT, \
     API_V_ORDER_TYPE_STP_LMT
    from fy_data_and_trade_defines import EXCHANGE_CODE_NSE, \
     EXCHANGE_CODE_BSE, SYM_SEGMENT_CM, SYM_SEGMENT_FO, SYM_SEGMENT_CD, \
     EXCHANGE_CODE_MCX, SYM_SEGMENT_COM, EXCHANGE_NAME_NSE, EXCHANGE_NAME_MCX_1, \
     EXCHANGE_NAME_BSE
    from fy_trading_defines import API_OMS_K_REQ_SOURCE, \
     API_OMS_V_ORDER_PROD_CO_2, \
     API_OMS_V_ORDER_PROD_BO_2, API_OMS_V_SEG_CD_1, API_OMS_V_ORDER_PROD_CO_1, \
     API_OMS_V_DEFAULT_ORDER_VALIDITY, API_OMS_V_DEFAULT_ORDER_DISC_QTY, \
     API_OMS_V_DEFAULT_ORDER_OFFLINE_FLAG_2, API_OMS_V_SEG_CM_2, \
     API_OMS_V_SEG_FO_2, API_OMS_V_SEG_COM_1, API_OMS_V_ORDER_SIDE_BUY_1, \
     API_OMS_V_ORDER_SIDE_SELL_1, API_OMS_V_ORDER_LEG_VALUE_2, API_OMS_V_DEFAULT_MARKET_PRO_FLAG, \
     API_OMS_V_DEFAULT_MARKET_PRO_VAL, API_OMS_V_DEFAULT_GTC_FLAG, \
     API_OMS_V_DEFAULT_ENCASH_FLAG, API_OMS_K_PAN_1, REQ_URL_OMS_MAIN_1, \
     API_OMS_REQ_PATH_CO_PLACE, API_OMS_V_ORDER_LEG_VALUE_3, \
     API_OMS_REQ_PATH_BO_PLACE, API_OMS_V_ORDER_PROD_BO_1

    from fy_connections import connectRedis
    from fy_base_functions import logEntryFunc2
    from fy_common_internal_functions import INTERNAL_checkSymbolNameOrToken, \
     INTERNAL_getSymExAndSegment
    from fy_trading_common_functions import INTERNAL_fy_getNecessaryOMSData_withID
    from fy_trading_internal_functions import INTERNAL_createAndSendOmsRequest, \
     INTERNAL_decryptOmsResponse, INTERNAL_readOmsDecryptedResponse

except Exception as e:
    print("ERR : %s : %s : %s" % (moduleName, "Could not import module", e))
    sys.exit()


def INTERNAL_placeCoverOrder(tokenHash, symbol, transType, ordType, qty, price, trigPrice,
            prodList=API_OMS_V_ORDER_PROD_CO_1, valType=API_OMS_V_DEFAULT_ORDER_VALIDITY,
            discQty=API_OMS_V_DEFAULT_ORDER_DISC_QTY, offlineFlag=API_OMS_V_DEFAULT_ORDER_OFFLINE_FLAG_2,
            callingFuncName="",userIp=""):
    """
    Place a cover order
        :param tokenHash: The encrypted token id which is inside the cookie
        :param symbol: The symbol string. Eg: "NSE:RELIANCE-EQ"
        :param transType: Whether buy/side;
        :param ordType: Whether market/limit;
        :param qty:
        :param price:
        :param trigPrice: The stop loss/trigger price for the second leg of the order
        :param prodList: Default is CO. Do not input anything to this
        :param valType: Default is Day.
        :param discQty: Default is 0
        :param offlineFlag: This should always be false. CO offline orders should not be allowed
        :param callingFuncName: Function which calling this function.
    :return:
        Success => [SUCCESS_C_1, Code, "message", "orderId"]
        Error   => [ERROR_C_1, ErrorCode, "errorMessage", "orderId"]
    """
    funcName = "INTERNAL_placeCoverOrder"
    try:
        localMemory = connectRedis(callingFuncName=callingFuncName)
        # Check if qty is correct or not
        try:
            qty = int(float(qty))
        except Exception as e:
            return [ERROR_C_1, ERROR_C_INV_ORDER_QTY, ERROR_M_INV_ORDER_QTY]

        # Check if stop loss/ trigger price is correct or not
        try:
            trigPrice = float(trigPrice)
        except Exception as e:
            return [ERROR_C_1, ERROR_C_INV_ORDER_TRIG_PRICE, ERROR_M_INV_ORDER_TRIG_PRICE]

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

        # Converting symbol name to token
        checkSymbolList = INTERNAL_checkSymbolNameOrToken(symbol, localMemory=localMemory,callingFuncName=callingFuncName)
        if checkSymbolList[0] == ERROR_C_1:
            return checkSymbolList

        # Splitting the token to get the exchange, segment and scripCode
        symbolList = INTERNAL_getSymExAndSegment(checkSymbolList[1][0], callingFuncName=callingFuncName)
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
        if (prodList == API_OMS_V_ORDER_PROD_CO_2) or (prodList == API_OMS_V_ORDER_PROD_CO_1):
            prodList = API_OMS_V_ORDER_PROD_CO_1
        else:
            return [ERROR_C_1, ERROR_C_INV_ORDER_PRODUCT, ERROR_M_INV_ORDER_PRODUCT]

        # Check if order type is in the correct format
        try:
            ordType = int(ordType)
        except Exception as e:
            return [ERROR_C_1, ERROR_C_INV_ORDER_TYPE_CO, ERROR_M_INV_ORDER_TYPE_CO]

        # Rupeeseed has different codes for order type like LMT/MKT
        if ordType == API_V_ORDER_TYPE_MKT_1:
            ordType = API_V_ORDER_TYPE_MKT_2

        elif ordType == API_V_ORDER_TYPE_LMT_1:
            ordType = API_V_ORDER_TYPE_LMT_2

        else:
            return [ERROR_C_1, ERROR_C_INV_ORDER_TYPE_CO, ERROR_M_INV_ORDER_TYPE_CO]

        # Check if order side is valid
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

        paramsPayload = {
            "user_type": OMSUserType,
            "offline_flag": offlineFlag,
            "disclosequantity": str(discQty),
            "fTriggerPrice2": trigPrice,
            "token_id": OMStoken,
            "securityid": symbolList[1][2],
            "iNoOfLeg": API_OMS_V_ORDER_LEG_VALUE_2,
            "productlist": prodList,
            "inst_type": symType,
            "buysell": transType,
            API_OMS_K_REQ_SOURCE: source,
            "order_validity": valType,
            "user_id": OMSUserID,
            "quantity": str(qty),
            "client_id": OMSid,
            "exchange": symExcg,
            "order_type": ordType,
            "marketProflag": API_OMS_V_DEFAULT_MARKET_PRO_FLAG,
            "marketProVal": API_OMS_V_DEFAULT_MARKET_PRO_VAL,
            "ParticipantType": "",
            "settlor": "",
            "Gtcflag": API_OMS_V_DEFAULT_GTC_FLAG,
            "EncashFlag": API_OMS_V_DEFAULT_ENCASH_FLAG,
            API_OMS_K_PAN_1: pan
        }
        # Create a paramDict to send to the OMS
        # Based on order type, we will update the price to the paramsdict
        if (ordType == API_V_ORDER_TYPE_LMT_2):
            paramsPayload["price"] = str(price)
        elif (ordType == API_V_ORDER_TYPE_MKT_2):
            # If the ordertype is market, oms does not want price field to be present in params
            None
        else:
            return [ERROR_C_1, ERROR_C_INV_ORDER_TYPE, ERROR_M_INV_ORDER_TYPE]
        # Send the request to the OMS
        urlForRequest = REQ_URL_OMS_MAIN_1 + API_OMS_REQ_PATH_CO_PLACE
        sendReqFuncRet = INTERNAL_createAndSendOmsRequest(OMSid, OMStoken, aesKey, paramsPayload, urlForRequest, callingFuncName=callingFuncName,userIp=userIp)
        if sendReqFuncRet[0] == ERROR_C_1:
            return sendReqFuncRet
        omsResponse = sendReqFuncRet[1]

        # Decrypt the response received from the OMS
        readOmsResponseFuncRet = INTERNAL_decryptOmsResponse(omsResponse, aesKey, callingFuncName=callingFuncName)
        if readOmsResponseFuncRet[0] == ERROR_C_1:
            return readOmsResponseFuncRet
        userInfoList = readOmsResponseFuncRet[1]

        # Check for user invalidation. If yes, re-send the request
        readOmsResponseFuncRet2 = INTERNAL_readOmsDecryptedResponse(userInfoList, tokenHash, paramsPayload,urlForRequest,fyId=OMSid, localMemory=localMemory,callingFuncName=callingFuncName, orderPlacement=True,userIp=userIp)
        if len(readOmsResponseFuncRet2) > 3:
            if readOmsResponseFuncRet2[3] != "":
                readOmsResponseFuncRet2[3] = "%s-%s-%s"%(readOmsResponseFuncRet2[3],API_OMS_V_ORDER_PROD_CO_2,1)
        return readOmsResponseFuncRet2
    except Exception as e:
        logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, e,
                      ERROR_C_UNKNOWN)
        return [ERROR_C_1, ERROR_C_UNKNOWN, e]


def INTERNAL_placeBracketOrder(tokenHash, symbol, transType, ordType, qty, price, trigPrice,targetAbsVal,stopLossAbsVal, trailAbsVal=0,prodList=API_OMS_V_ORDER_PROD_BO_2, valType=API_OMS_V_DEFAULT_ORDER_VALIDITY, discQty=API_OMS_V_DEFAULT_ORDER_DISC_QTY, offlineFlag=API_OMS_V_DEFAULT_ORDER_OFFLINE_FLAG_2, callingFuncName="",userIp=""):
    """
    Place a bracket order
        :param tokenHash: The encrypted token id which is inside the cookie
        :param symbol: The symbol string. Eg: "NSE:RELIANCE-EQ"
        :param transType: Whether buy/side;
        :param ordType: Whether market/limit;
        :param qty:
        :param price: This is the limitPrice
        :param trigPrice: Currently not used. Could be used in the future
        :param targetAbsVal: The difference in target price in rupees
        :param stopLossAbsVal: The difference in stop loss price in rupees
        :param trailAbsVal: The difference in trailing value in rupees
        :param prodList: Default is CO. Do not input anything to this
        :param valType: Default is Day.
        :param discQty: Default is 0
        :param offlineFlag: This should always be false. CO offline orders should not be allowed
        :param callingFuncName: Function which calling this function.
    :return:
        Success => [SUCCESS_C_1, Code, "message", "orderId"]
        Error   => [ERROR_C_1, ErrorCode, "errorMessage", "orderId"]
    """
    funcName = "INTERNAL_placeBracketOrder"
    try:
        localMemory = connectRedis(callingFuncName=callingFuncName)
        # Check if qty is correct or not
        try:
            qty = int(float(qty))
        except Exception as e:
            return [ERROR_C_1, ERROR_C_INV_ORDER_QTY, ERROR_M_INV_ORDER_QTY]

        # Currently trigger price is not used.
        try:
            trigPrice = float(trigPrice)
        except Exception as e:
            return [ERROR_C_1, ERROR_C_INV_ORDER_TRIG_PRICE, ERROR_M_INV_ORDER_TRIG_PRICE]

        # Check if target value is correct or not
        try:
            targetAbsVal = float(targetAbsVal)
        except Exception as e:
            return [ERROR_C_1, ERROR_C_INV_ORDER_TARGET_VAL, ERROR_M_INV_ORDER_TARGET_VAL]

        # Check if stop loss value is correct or not
        try:
            stopLossAbsVal = float(stopLossAbsVal)
        except Exception as e:
            return [ERROR_C_1, ERROR_C_INV_ORDER_STOP_LOSS_VAL, ERROR_M_INV_ORDER_STOP_LOSS_VAL]

        # Check if trailing stop loss value is correct or not
        try:
            trailAbsVal = float(trailAbsVal)
        except Exception as e:
            return [ERROR_C_1, ERROR_C_INV_ORDER_TRAILING_SL_VAL, ERROR_M_INV_ORDER_TRAILING_SL_VAL]

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

        # Converting symbol name to token
        checkSymbolList = INTERNAL_checkSymbolNameOrToken(symbol, localMemory=localMemory,callingFuncName=callingFuncName)
        if checkSymbolList[0] == ERROR_C_1:
            return checkSymbolList

        # Splitting the token to get the exchange, segment and scripCode
        symbolList = INTERNAL_getSymExAndSegment(checkSymbolList[1][0], callingFuncName=callingFuncName)
        if symbolList[0] == ERROR_C_1:
            return symbolList
        ## Check exchange
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
        if (prodList == API_OMS_V_ORDER_PROD_BO_2) or (prodList == API_OMS_V_ORDER_PROD_BO_1):
            prodList = API_OMS_V_ORDER_PROD_BO_1
        else:
            return [ERROR_C_1, ERROR_C_INV_ORDER_PRODUCT, ERROR_M_INV_ORDER_PRODUCT]

        # Check if order type is in the correct format
        try:
            ordType = int(ordType)
        except Exception as e:
            return [ERROR_C_1, ERROR_C_INV_ORDER_TYPE_BO, ERROR_M_INV_ORDER_TYPE_CO]

        # Check if order price is in the correct formal
        try:
            price = float(price)
        except Exception as e:
            return [ERROR_C_1, ERROR_C_INV_ORDER_LMT_PRICE, ERROR_M_INV_ORDER_LMT_PRICE]

        # Rupeeseed has different codes for order type like LMT/MKT
        if ordType == API_V_ORDER_TYPE_MKT_1:
            ordType     = API_V_ORDER_TYPE_MKT_2
            # We are making the price as 0 in case it is a market order type
            price       = 0
            trigPrice   = 0

        elif ordType == API_V_ORDER_TYPE_LMT_1:
            ordType     = API_V_ORDER_TYPE_LMT_2
            trigPrice   = 0

        elif ordType == API_V_ORDER_TYPE_STP_MKT:
            ordType = API_V_ORDER_TYPE_MKT_2
            # We are making the price as 0 in case it is a stop (SL-M) order type
            price   = 0
            """
            # If order type is stop then we need to check price. If price is 0, then order is market and if price != 0 then order type is limit
            if price == 0:
                ordType = API_V_ORDER_TYPE_MKT_2
            else:
                ordType = API_V_ORDER_TYPE_LMT_2
            """

        elif ordType == API_V_ORDER_TYPE_STP_LMT:
            # If order type is stoplimit then we need to check price. If price is 0, stopLimit order is invalid
            if price == 0:
                return [ERROR_C_1, ERROR_C_INV_ORDER_STOP_LMT_PRICE, ERROR_M_INV_ORDER_STP_LMT_PRICE]
            ordType = API_V_ORDER_TYPE_LMT_2
        else:
            return [ERROR_C_1, ERROR_C_INV_ORDER_TYPE_BO, ERROR_M_INV_ORDER_TYPE_BO_2]

        # Check if order side is valid
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

        paramsPayload = {
            "user_type":        OMSUserType,
            "offline_flag":     offlineFlag,
            "disclosequantity": str(discQty),
            "securityid":       symbolList[1][2],
            "iNoOfLeg":         API_OMS_V_ORDER_LEG_VALUE_3,
            "productlist":      prodList,
            "inst_type":        symType,
            "buysell":          transType,
            API_OMS_K_REQ_SOURCE: source,
            "order_validity":   valType,
            "user_id":          OMSUserID,
            "quantity":         str(qty),
            "client_id":        OMSid,
            "exchange":         symExcg,
            "order_type":       ordType,
            "fPBTikAbsValue":   str(targetAbsVal),
            "fSLTikAbsValue":   str(stopLossAbsVal),
            "fTrailingSLValue": str(trailAbsVal),
            "token_id":         OMStoken,

            "marketProflag":    API_OMS_V_DEFAULT_MARKET_PRO_FLAG,
            "marketProVal":     API_OMS_V_DEFAULT_MARKET_PRO_VAL,
            "ParticipantType":  "B",
            "settlor":          "",
            "Gtcflag":          API_OMS_V_DEFAULT_GTC_FLAG,
            "EncashFlag":       API_OMS_V_DEFAULT_ENCASH_FLAG,
            API_OMS_K_PAN_1:    pan,
            "triggerprice":     str(trigPrice),
            "price":            str(price)
        }
        """
        # Create a paramDict to send to the OMS
        # Based on order type, we will update the price to the paramsdict
        if (ordType == API_V_ORDER_TYPE_LMT_2):
            paramsPayload["price"] = str(price)
        elif (ordType == API_V_ORDER_TYPE_MKT_2):
            # If if the order type is market, then the price should not be part of the params
            None
        else:
            return [ERROR_C_1, ERROR_C_INV_ORDER_TYPE, ERROR_M_INV_ORDER_TYPE]
        """
        # Send the request to the OMS
        urlForRequest = REQ_URL_OMS_MAIN_1 + API_OMS_REQ_PATH_BO_PLACE
        sendReqFuncRet = INTERNAL_createAndSendOmsRequest(OMSid, OMStoken, aesKey, paramsPayload, urlForRequest, callingFuncName=callingFuncName,userIp=userIp)
        if sendReqFuncRet[0] == ERROR_C_1:
            return sendReqFuncRet
        omsResponse = sendReqFuncRet[1]

        # Decrypt the response received from the OMS
        readOmsResponseFuncRet = INTERNAL_decryptOmsResponse(omsResponse, aesKey, callingFuncName=callingFuncName)
        if readOmsResponseFuncRet[0] == ERROR_C_1:
            return readOmsResponseFuncRet
        userInfoList = readOmsResponseFuncRet[1]

        # Check for user invalidation. If yes, re-send the request
        readOmsResponseFuncRet2 = INTERNAL_readOmsDecryptedResponse(userInfoList, tokenHash, paramsPayload,
                        urlForRequest,fyId=OMSid, localMemory=localMemory,callingFuncName=callingFuncName, orderPlacement=True,userIp=userIp)
        if len(readOmsResponseFuncRet2) > 3:
            if readOmsResponseFuncRet2[3] != "":
                readOmsResponseFuncRet2[3] = "%s-%s-%s"%(readOmsResponseFuncRet2[3],API_OMS_V_ORDER_PROD_BO_2,1)
        return readOmsResponseFuncRet2
    except Exception as e:
        logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, e,
                      ERROR_C_UNKNOWN)
        return [ERROR_C_1, ERROR_C_UNKNOWN, e]


def main():
    None


if __name__ == "__main__":
    main()
