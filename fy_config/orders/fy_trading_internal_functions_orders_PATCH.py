moduleName = "fy_trading_internal_functions_orders_PATCH"
try:
    import sys
    from fy_base_defines import LOG_STATUS_ERROR_1
    from fy_base_success_error_codes import ERROR_C_1, \
     ERROR_C_UNKNOWN, \
     ERROR_C_INV_ORDER_PRODUCT, \
     ERROR_C_INV_ORDER_SIDE, \
     ERROR_C_INV_ORDER_LMT_PRICE, \
     ERROR_C_OMS_1, ERROR_C_OMS_ORDER_ALREADY_CANCELLED, \
     ERROR_C_OMS_ORDER_ALREADY_TRADED, ERROR_C_OMS_ORDER_ALREADY_REJECTED, \
     ERROR_C_INV_INST_TYPE, ERROR_C_INV_ORDER_STP_PRICE, ERROR_C_INV_ORDER_ID, \
     ERROR_C_INV_ORDER_TYPE
    from fy_base_success_error_messages import \
     ERROR_M_INV_ORDER_PRODUCT, \
     ERROR_M_INV_ORDER_SIDE, ERROR_M_INV_ORDER_TYPE, \
     ERROR_M_INV_ORDER_LMT_PRICE, \
     ERROR_M_ORDER_ALREADY_CANCELLED, \
     ERROR_M_ORDER_ALREADY_TRADED, ERROR_M_ORDER_ALREADY_REJECTED, \
     ERROR_M_INV_INST_TYPE, ERROR_M_INV_ORDER_STP_PRICE, ERROR_M_INV_ORDER_ID
    from fy_common_api_keys_values import API_V_ORDER_TYPE_MKT_1, \
     API_V_ORDER_TYPE_MKT_2, API_V_ORDER_TYPE_LMT_1, API_V_ORDER_TYPE_LMT_2, \
     API_V_ORDER_SIDE_BUY_1, API_V_ORDER_SIDE_SELL_1, API_V_ORDER_TYPE_STP_MKT, \
     API_V_ORDER_TYPE_STP_LMT
    from fy_trading_defines import API_OMS_K_REQ_SOURCE, \
     API_OMS_V_ORDER_PROD_CO_2, \
     API_OMS_V_ORDER_PROD_BO_2, API_OMS_V_SEG_CD_1, API_OMS_V_ORDER_PROD_CO_1, \
     API_OMS_V_DEFAULT_ORDER_OFFLINE_FLAG_2, API_OMS_V_SEG_CM_2, \
     API_OMS_V_SEG_FO_2, API_OMS_V_SEG_COM_1, API_OMS_V_ORDER_SIDE_BUY_1, \
     API_OMS_V_ORDER_SIDE_SELL_1, API_OMS_V_ORDER_LEG_VALUE_2, API_OMS_V_DEFAULT_MARKET_PRO_FLAG, \
     API_OMS_V_DEFAULT_MARKET_PRO_VAL, API_OMS_V_DEFAULT_GTC_FLAG, \
     API_OMS_V_DEFAULT_ENCASH_FLAG, API_OMS_K_PAN_1, REQ_URL_OMS_MAIN_1, \
     API_OMS_V_ORDER_LEG_VALUE_3, \
     API_OMS_V_ORDER_PROD_CNC_2, API_OMS_V_ORDER_PROD_CNC_1, \
     API_OMS_V_ORDER_PROD_MARGIN_2, API_OMS_V_ORDER_PROD_MARGIN_1, \
     API_OMS_V_ORDER_PROD_INTRADAY_2, API_OMS_V_ORDER_PROD_INTRADAY_1, \
     API_OMS_V_SEG_CM_1, API_OMS_V_SEG_FO_1, \
     API_OMS_REQ_PATH_ORDER_MODIFY, API_OMS_V_ORDER_SIDE_BUY_2, API_OMS_V_ORDER_SIDE_SELL_2, \
     API_OMS_V_ORDER_LEG_VALUE_1, API_OMS_V_ORDER_TYPE_LMT_2, API_OMS_V_ORDER_TYPE_LMT_1, \
     API_OMS_V_ORDER_TYPE_MKT_2, API_OMS_V_ORDER_TYPE_MKT_1, API_OMS_REQ_PATH_CO_MODIFY, \
     API_OMS_REQ_PATH_BO_MODIFY, API_OMS_V_ORDER_PROD_BO_1

    from fy_connections import connectRedis
    from fy_base_functions import logEntryFunc2
    from fy_trading_common_functions import INTERNAL_fy_getNecessaryOMSData_withID, \
     INTERNAL_getOrderStatus_withID2
    from fy_trading_internal_functions import INTERNAL_createAndSendOmsRequest, \
     INTERNAL_decryptOmsResponse, INTERNAL_readOmsDecryptedResponse

except Exception as e:
    print("ERR : %s : %s : %s" % (moduleName, "Could not import module", e))
    sys.exit()


def INTERNAL_modifyOrder_withID(tokenHash, orderID, kwargs,callingFuncName="",userIp=""):
    """
    [FUNCTION]
        Get the status of a particular order by User and OrderID
    [PARAMS]
        tokenHash       : This is a hash of (fyId + AppId)
        orderID         : Order Id to be modified
            kwargs => If any of the kwargs is not provided, then it will be taken from the order details and sent to the oms
                transactionType     : buy/sell
                orderType           : limit/stop/market/stoplimit
                modifiedQty         : The new quantity
                modifiedPrice       : The new price
                modifiedTrigPrice   : The new trigger price
                modifiedProduct     : The product ** This should not be changed
                modifiedValidity    : DAY/IOC
                modifiedDiscQty     : The new disclosed qty
                offlineFlag         : True/False
    [RETURN]
        Success : [SUCCESS_C_1,successCode,"success message"]
        Failure : [CONST_function/oms_error,errorCode,"error message"]
    """
    funcName = "INTERNAL_modifyOrder_withID"
    try:
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
        entireOrderDetails1 = INTERNAL_getOrderStatus_withID2(tokenHash, orderID,localMemory=localMemory, callingFuncName=callingFuncName,userIp=userIp)
        if (entireOrderDetails1[0] == ERROR_C_1) or (entireOrderDetails1[0] == ERROR_C_OMS_1):
            return entireOrderDetails1
        entireOrderDetails = entireOrderDetails1[1]
        count = 0

        modOrderSerialNumber = entireOrderDetails[16]
        modSecurityId = entireOrderDetails[17]
        modTradedQty = entireOrderDetails[23]
        modQtyRem = entireOrderDetails[11]
        modInstrumentType = entireOrderDetails[5]
        orderStatus = entireOrderDetails[9].lower()
        originalOrderQty = entireOrderDetails[10]

        # If orderStatus is already Cancelled, we will return from here itself
        if orderStatus == "cancelled" or orderStatus == "o-cancelled":
            return [ERROR_C_1, ERROR_C_OMS_ORDER_ALREADY_CANCELLED, ERROR_M_ORDER_ALREADY_CANCELLED]
        # If orderStatus is already filed, we will return from here itself
        elif orderStatus == "traded":
            return [ERROR_C_1, ERROR_C_OMS_ORDER_ALREADY_TRADED, ERROR_M_ORDER_ALREADY_TRADED]
        # If orderStatus is already rejected, we will return from here itself
        elif orderStatus == "rejected":
            return [ERROR_C_1, ERROR_C_OMS_ORDER_ALREADY_REJECTED, ERROR_M_ORDER_ALREADY_REJECTED]

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

        if "side" in kwargs:
            try:
                transactionType = int(kwargs["side"])
            except Exception as e:
                return [ERROR_C_1, ERROR_C_INV_ORDER_SIDE, ERROR_M_INV_ORDER_SIDE]

            # Rupeeseed has different codes for buy/sell like B/S
            if transactionType == API_V_ORDER_SIDE_BUY_1:
                transactionType = API_OMS_V_ORDER_SIDE_BUY_1
            elif transactionType == API_V_ORDER_SIDE_SELL_1:
                transactionType = API_OMS_V_ORDER_SIDE_SELL_1
            else:
                return [ERROR_C_1, ERROR_C_INV_ORDER_SIDE, ERROR_M_INV_ORDER_SIDE]
        else:
            transactionType = entireOrderDetails[4]

        modifiedQty = entireOrderDetails[11]
        # If qty has been given as an input parameter
        if "qty" in kwargs:
            modifiedQty = modQtyRem
            inputQty = str(kwargs["qty"])
            # Only if inputQty is not equal to original order quantity, we will consider it
            if inputQty != modQtyRem:
                modifiedQty = inputQty

        if "limitPrice" in kwargs:
            modifiedPrice = float(kwargs["limitPrice"])
        else:
            modifiedPrice = entireOrderDetails[12]
            try:
                modifiedPrice = float(modifiedPrice)
            except Exception as e:
                modifiedPrice = 0

        if "stopPrice" in kwargs:
            modifiedTrigPrice = float(kwargs["stopPrice"])
        else:
            modifiedTrigPrice = entireOrderDetails[13]

        try:
            orderType = int(kwargs["type"])
        except Exception as e:
            return [ERROR_C_1, ERROR_C_INV_ORDER_TYPE, ERROR_M_INV_ORDER_TYPE]
        # Rupeeseed has different codes for order type like LMT/MKT
        if orderType == API_V_ORDER_TYPE_MKT_1:
            orderType = API_V_ORDER_TYPE_MKT_2

        elif orderType == API_V_ORDER_TYPE_LMT_1:
            orderType = API_V_ORDER_TYPE_LMT_2

        elif orderType == API_V_ORDER_TYPE_STP_MKT:
            # If order type is stop then we need to check price. If price is 0, then order is market and if price != then order type is limit
            if modifiedPrice == 0:
                orderType = API_V_ORDER_TYPE_MKT_2
            else:
                orderType = API_V_ORDER_TYPE_LMT_2

        elif orderType == API_V_ORDER_TYPE_STP_LMT:
            # If order type is stoplimit then we need to check price. If price is 0, then order is market and if price != then order type is limit
            if modifiedPrice == 0:
                orderType = API_V_ORDER_TYPE_MKT_2
            else:
                orderType = API_V_ORDER_TYPE_LMT_2
        else:
            return [ERROR_C_1, ERROR_C_INV_ORDER_TYPE, ERROR_M_INV_ORDER_TYPE]

        if "modifiedProduct" in kwargs:
            modifiedProduct = kwargs["modifiedProduct"]
        else:
            modifiedProduct = entireOrderDetails[8]

        try:
            modifiedProduct = modifiedProduct.upper()
        except Exception as e:
            return [ERROR_C_1, ERROR_C_INV_ORDER_PRODUCT, ERROR_M_INV_ORDER_PRODUCT]

        # Rupeeseed has different codes for each product type
        if modifiedProduct == API_OMS_V_ORDER_PROD_CNC_2:
            modifiedProduct = API_OMS_V_ORDER_PROD_CNC_1
        elif modifiedProduct == API_OMS_V_ORDER_PROD_MARGIN_2:
            modifiedProduct = API_OMS_V_ORDER_PROD_MARGIN_1
        elif modifiedProduct == API_OMS_V_ORDER_PROD_INTRADAY_2:
            modifiedProduct = API_OMS_V_ORDER_PROD_INTRADAY_1
        else:
            return [ERROR_C_1, ERROR_C_INV_ORDER_PRODUCT, ERROR_M_INV_ORDER_PRODUCT]

        if "modifiedValidity" in kwargs:
            modifiedValidity = kwargs["modifiedValidity"]
        else:
            modifiedValidity = entireOrderDetails[18]

        if "modifiedDiscQty" in kwargs:
            modifiedDiscQty = kwargs["modifiedDiscQty"]
        else:
            modifiedDiscQty = entireOrderDetails[15]

        if "offlineFlag" in kwargs:
            offlineFlag = kwargs["offlineFlag"]
        else:
            offlineFlag = API_OMS_V_DEFAULT_ORDER_OFFLINE_FLAG_2

        # If its an offline order, we should change the offline flag to true
        if "o-" in orderStatus:
            offlineFlag = "true"

        paramsPayload = {
            "token_id": OMStoken,
            "client_id": OMSid,
            API_OMS_K_REQ_SOURCE: source,
            "client_type": OMSClientType,
            "exch_client_id": OMSExchClientId,
            "user_id": OMSUserID,
            "user_type": OMSUserType,
            "modqty_remng": str(modifiedQty),
            "modorder_serial_number": str(modOrderSerialNumber),
            "modorder_number": str(orderID),
            "modsecurityid": str(modSecurityId),
            "modinst_type": modInstrumentType,
            "modexchange": modExchange,
            "modscripname": "",
            "modbuysell": transactionType,
            "modquantitytype": orderType,
            "modquantity": str(modifiedQty), # Rupeeseed said that the mod quantity should be the same as remaining qty
            "modtriggerprice": str(modifiedTrigPrice),
            "modproductlist": modifiedProduct,
            "modOrderType": modifiedValidity,
            "moddisclosequantity": str(modifiedDiscQty),
            "modtraded_qty": modTradedQty,
            "ord_status": orderStatus,
            "offline_flag": offlineFlag,
            "modprice": str(modifiedPrice),
            "marketProflag": API_OMS_V_DEFAULT_MARKET_PRO_FLAG,
            "marketProVal": API_OMS_V_DEFAULT_MARKET_PRO_VAL,
            "ParticipantType": "",
            "settlor": "",
            "Gtcflag": API_OMS_V_DEFAULT_GTC_FLAG,
            "EncashFlag": API_OMS_V_DEFAULT_ENCASH_FLAG,
            API_OMS_K_PAN_1: pan
        }

        # Send request to the OMS
        urlForRequest = REQ_URL_OMS_MAIN_1 + API_OMS_REQ_PATH_ORDER_MODIFY
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
        readOmsResponseFuncRet2 = INTERNAL_readOmsDecryptedResponse(userInfoList,tokenHash, paramsPayload,urlForRequest,fyId=OMSid, localMemory=localMemory,callingFuncName=callingFuncName, userIp=userIp)
        return readOmsResponseFuncRet2

    except Exception as e:
        logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName,callingFuncName, e, ERROR_C_UNKNOWN, tokenHash)
        return [ERROR_C_1, ERROR_C_UNKNOWN, ""]


def INTERNAL_modifyCoverOrder(tokenHash, orderID, kwargs,callingFuncName="",userIp=""):
    """
    [FUNCTION]
        Get the status of a particular order by User and OrderID
    [PARAMS]
        tokenHash       : This is a hash of (fyId + AppId)
        orderID         : Order Id to be modified - xxxxxxxxxxxx-CO-x
            kwargs => If any of the kwargs is not provided, then it will be taken from the order details and sent to the oms
                limitPrice      : The limit price for the leg 1 order. This is applicable only if leg 1 was a limit order
                stopPrice       : The stop loss price of the stop loss order
    [RETURN]
        Success : [SUCCESS_C_1,successCode,"success message"]
        Failure : [CONST_function/oms_error,errorCode,"error message"]
    """
    funcName = "INTERNAL_modifyCoverOrder"
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
        orderStatus = entireOrderDetails[9].lower()
        modifiedTrigPrice = entireOrderDetails[13]

        # If orderStatus is already Cancelled, we will return from here itself
        if orderStatus == "cancelled" or orderStatus == "o-cancelled":
            return [ERROR_C_1, ERROR_C_OMS_ORDER_ALREADY_CANCELLED, ERROR_M_ORDER_ALREADY_CANCELLED]
        # If orderStatus is already filed, we will return from here itself
        elif orderStatus == "traded":
            return [ERROR_C_1, ERROR_C_OMS_ORDER_ALREADY_TRADED, ERROR_M_ORDER_ALREADY_TRADED]
        # If orderStatus is already rejected, we will return from here itself
        elif orderStatus == "rejected":
            return [ERROR_C_1, ERROR_C_OMS_ORDER_ALREADY_REJECTED, ERROR_M_ORDER_ALREADY_REJECTED]

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

        # If order leg is 1, then we can modify limit price if it is a limit order entry
        if orderLegNumber == API_OMS_V_ORDER_LEG_VALUE_1:
            if "limitPrice" in kwargs:
                modifiedPrice = kwargs["limitPrice"]

        # If order leg is 2, then we will try to modify the trigger price only. Nothing else
        elif orderLegNumber == API_OMS_V_ORDER_LEG_VALUE_2:
            if "stopPrice" in kwargs:
                modifiedTrigPrice = kwargs["stopPrice"]
            else:
                return [ERROR_C_1, ERROR_C_INV_ORDER_STP_PRICE, ERROR_M_INV_ORDER_STP_PRICE]

        # If some other leg number is given, then we will reject the request
        else:
            return [ERROR_C_1, ERROR_C_INV_ORDER_ID, ERROR_M_INV_ORDER_ID]

        try:
            orderType = entireOrderDetails[14].upper()
            if orderType == API_OMS_V_ORDER_TYPE_LMT_2:
                orderType = API_OMS_V_ORDER_TYPE_LMT_1
            elif orderType == API_OMS_V_ORDER_TYPE_MKT_2 or orderType == "SL-M":
                orderType = API_OMS_V_ORDER_TYPE_MKT_1
        except Exception as e:
            return [ERROR_C_1, ERROR_C_INV_ORDER_TYPE,ERROR_M_INV_ORDER_TYPE]

        try:
            modifiedProduct = entireOrderDetails[8].upper()
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
            "fillQty": str(modTradedQty),
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
        urlForRequest = REQ_URL_OMS_MAIN_1 + API_OMS_REQ_PATH_CO_MODIFY
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
        readOmsResponseFuncRet2 = INTERNAL_readOmsDecryptedResponse(userInfoList,tokenHash, paramsPayload,urlForRequest,fyId=OMSid, localMemory=localMemory,callingFuncName=callingFuncName,orderPlacement=True,userIp=userIp)
        return readOmsResponseFuncRet2

    except Exception as e:
        logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, e, ERROR_C_UNKNOWN, tokenHash)
        return [ERROR_C_1, ERROR_C_UNKNOWN, ""]


def INTERNAL_modifyBracketOrder(tokenHash, orderID, kwargs,callingFuncName="",userIp=""):
    """
    Modify a bracket order
    [PARAMS]
        tokenHash       : This is a hash of (fyId + AppId)
        orderID         : Order Id to be modified - xxxxxxxxxxxx-CO-x
            kwargs => If any of the kwargs is not provided, then it will be taken from the order details and sent to the oms
                limitPrice      : The limit price for the leg 1 order. This is applicable only if leg 1 was a limit order
                stopPrice       : The stop loss price of the stop loss order
    [RETURN]
        Success : [SUCCESS_C_1,successCode,"success message"]
        Failure : [CONST_function/oms_error,errorCode,"error message"]
    """
    funcName = "INTERNAL_modifyBracketOrder"
    try:
        orderID2 = orderID.split("-")
        orderID1 = orderID2[0]
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
        orderStatus = entireOrderDetails[9].lower()
        modifiedTrigPrice = entireOrderDetails[13]
        originalOrderQty = entireOrderDetails[10]
        trailingSlValue = entireOrderDetails[27]
        orderLegNumber = entireOrderDetails[29]
        slAbsTickValue = entireOrderDetails[30]
        prfAbsTickValue = entireOrderDetails[31]
        algoOrderNum = entireOrderDetails[32]
        orderOffOn = entireOrderDetails[33]

        # If orderStatus is already Cancelled, we will return from here itself
        if orderStatus == "cancelled" or orderStatus == "o-cancelled":
            return [ERROR_C_1, ERROR_C_OMS_ORDER_ALREADY_CANCELLED, ERROR_M_ORDER_ALREADY_CANCELLED]
        # If orderStatus is already filed, we will return from here itself
        elif orderStatus == "traded":
            return [ERROR_C_1, ERROR_C_OMS_ORDER_ALREADY_TRADED, ERROR_M_ORDER_ALREADY_TRADED]
        # If orderStatus is already rejected, we will return from here itself
        elif orderStatus == "rejected":
            return [ERROR_C_1, ERROR_C_OMS_ORDER_ALREADY_REJECTED, ERROR_M_ORDER_ALREADY_REJECTED]

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

        # If order leg is 1, then we can modify limit price and quantity
        if orderLegNumber == API_OMS_V_ORDER_LEG_VALUE_1:
            if "limitPrice" in kwargs:
                modifiedPrice = kwargs["limitPrice"]
            if "stopPrice" in kwargs:
                modifiedTrigPrice = kwargs["stopPrice"]
            if "qty" in kwargs:
                inputQty = kwargs["qty"]
                if inputQty != originalOrderQty:
                    modQtyRem = inputQty
            else:
                return [ERROR_C_1, ERROR_C_INV_ORDER_LMT_PRICE,ERROR_M_INV_ORDER_LMT_PRICE]

        # If order leg is 2, then we will try to modify the trigger price only. Nothing else
        elif orderLegNumber == API_OMS_V_ORDER_LEG_VALUE_2:
            if "stopPrice" in kwargs:
                modifiedTrigPrice = kwargs["stopPrice"]
            else:
                return [ERROR_C_1, ERROR_C_INV_ORDER_STP_PRICE, ERROR_M_INV_ORDER_STP_PRICE]

        # If order leg is 3, then we can only modify the limitPrice. Nothing else
        elif orderLegNumber == API_OMS_V_ORDER_LEG_VALUE_3:
            if "limitPrice" in kwargs:
                modifiedPrice = kwargs["limitPrice"]
            else:
                return [ERROR_C_1, ERROR_C_INV_ORDER_LMT_PRICE,ERROR_M_INV_ORDER_LMT_PRICE]

        # If some other leg number is given, then we will reject the request
        else:
            return [ERROR_C_1, ERROR_C_INV_ORDER_ID, ERROR_M_INV_ORDER_ID]

        try:
            orderType = entireOrderDetails[14].upper()
            if orderType == API_OMS_V_ORDER_TYPE_LMT_2:
                orderType = API_OMS_V_ORDER_TYPE_LMT_1
            elif orderType == API_OMS_V_ORDER_TYPE_MKT_2 or orderType == "SL-M":
                orderType = API_OMS_V_ORDER_TYPE_MKT_1
            elif orderType == "SL" or orderType == "SL-L":
                orderType = API_OMS_V_ORDER_TYPE_LMT_1
        except Exception as e:
            return [ERROR_C_1, ERROR_C_INV_ORDER_TYPE,ERROR_M_INV_ORDER_TYPE]

        try:
            modifiedProduct = entireOrderDetails[8].upper()
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

        # Check if modifiedTrigPrice which we got from the OMS is empty
        if modifiedTrigPrice == "":
            modifiedTrigPrice = 0
        
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
            "modquantity": str(modQtyRem),
            "inst_type": modInstrumentType,
            "buysell": transactionType,
            "modorder_serial_number": str(modOrderSerialNumber),
            API_OMS_K_REQ_SOURCE: source,
            "iLegValue": orderLegNumber,
            "user_id": OMSUserID,
            "client_id": OMSid,
            "modqty_remng": str(modQtyRem),
            "modprice": str(modifiedPrice),
            "exchange": modExchange,
            "fPBTikAbsValue": str(prfAbsTickValue),
            "fSLTikAbsValue": str(slAbsTickValue),
            "modorder_type": orderType,
            "mod_fTrailingSLValue": str(modTradedQty),
            "mod_algo_ord_number": str(algoOrderNum),
            "token_id": OMStoken,
            "marketProflag": API_OMS_V_DEFAULT_MARKET_PRO_FLAG,
            "marketProVal": API_OMS_V_DEFAULT_MARKET_PRO_VAL,
            "ParticipantType": "B",
            "settlor": "",
            "Gtcflag": API_OMS_V_DEFAULT_GTC_FLAG,
            "EncashFlag": API_OMS_V_DEFAULT_ENCASH_FLAG,
            API_OMS_K_PAN_1: pan
        }
        # Send request to the OMS
        urlForRequest = REQ_URL_OMS_MAIN_1 + API_OMS_REQ_PATH_BO_MODIFY
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
                            urlForRequest,fyId=OMSid, localMemory=localMemory,callingFuncName=callingFuncName,orderPlacement=True,userIp=userIp)
        return readOmsResponseFuncRet2

    except Exception as e:
        logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, e, ERROR_C_UNKNOWN, tokenHash)
        return [ERROR_C_1, ERROR_C_UNKNOWN, ""]


def main():
    None


if __name__ == "__main__":
    main()
