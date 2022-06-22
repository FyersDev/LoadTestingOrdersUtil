moduleName = "fy_trading_internal_functions_orders_DELETE"
try:
    import sys

    from fy_base_defines import LOG_STATUS_ERROR_1
    from fy_base_success_error_codes import ERROR_C_1, \
     ERROR_C_UNKNOWN, \
     ERROR_C_INV_SEGMENT, ERROR_C_INV_ORDER_PRODUCT, \
     ERROR_C_INV_ORDER_SIDE, \
     ERROR_C_OMS_1, \
     ERROR_C_OMS_ORDER_ALREADY_CANCELLED, ERROR_C_OMS_ORDER_ALREADY_TRADED, \
     ERROR_C_OMS_ORDER_ALREADY_REJECTED, ERROR_C_INV_ORDER_TYPE
    from fy_base_success_error_messages import \
     ERROR_M_INV_SEGMENT, \
     ERROR_M_INV_ORDER_PRODUCT, \
     ERROR_M_INV_ORDER_SIDE, ERROR_M_INV_ORDER_TYPE, \
     ERROR_M_ORDER_ALREADY_CANCELLED, \
     ERROR_M_ORDER_ALREADY_TRADED, ERROR_M_ORDER_ALREADY_REJECTED
    from fy_trading_defines import API_OMS_K_REQ_SOURCE, \
     API_OMS_V_SEG_CD_1, \
     API_OMS_V_DEFAULT_ORDER_OFFLINE_FLAG_2, API_OMS_V_SEG_CM_2, \
     API_OMS_V_SEG_FO_2, API_OMS_V_SEG_COM_1, API_OMS_V_ORDER_SIDE_BUY_1, \
     API_OMS_V_ORDER_SIDE_SELL_1, API_OMS_V_DEFAULT_MARKET_PRO_FLAG, \
     API_OMS_V_DEFAULT_MARKET_PRO_VAL, API_OMS_V_DEFAULT_GTC_FLAG, \
     API_OMS_V_DEFAULT_ENCASH_FLAG, API_OMS_K_PAN_1, REQ_URL_OMS_MAIN_1, \
     API_OMS_V_SEG_CM_1, API_OMS_V_SEG_FO_1, API_OMS_V_ORDER_PROD_CNC_2, \
     API_OMS_V_ORDER_PROD_CNC_1, API_OMS_V_ORDER_PROD_MARGIN_2, \
     API_OMS_V_ORDER_PROD_MARGIN_1, API_OMS_V_ORDER_PROD_INTRADAY_2, \
     API_OMS_V_ORDER_PROD_INTRADAY_1, API_OMS_V_ORDER_TYPE_LMT_2, API_OMS_V_ORDER_TYPE_LMT_1, \
     API_OMS_V_ORDER_TYPE_MKT_2, API_OMS_V_ORDER_TYPE_MKT_1, API_OMS_REQ_PATH_ORDER_CANCEL

    from fy_connections import connectRedis
    from fy_base_functions import logEntryFunc2
    from fy_trading_common_functions import INTERNAL_fy_getNecessaryOMSData_withID, \
     INTERNAL_getOrderStatus_withID2
    from fy_trading_internal_functions import INTERNAL_createAndSendOmsRequest, \
     INTERNAL_decryptOmsResponse, INTERNAL_readOmsDecryptedResponse

except Exception as e:
    print("ERR : %s : %s : %s" % (moduleName, "Could not import module", e))
    sys.exit()


def INTERNAL_cancelOrder_withID(tokenHash, orderID,callingFuncName="",userIp=""):
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
    funcName = "INTERNAL_cancelOrder_withID"
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

        # Get order details
        entireOrderDetails1 = INTERNAL_getOrderStatus_withID2(tokenHash, orderID,localMemory=localMemory, callingFuncName=callingFuncName,userIp=userIp)
        if (entireOrderDetails1[0] == ERROR_C_1) or (entireOrderDetails1[0] == ERROR_C_OMS_1):
            return entireOrderDetails1
        entireOrderDetails = entireOrderDetails1[1]

        modOrderSerialNumber = entireOrderDetails[16]
        modSecurityId = entireOrderDetails[17]
        modTradedQty = entireOrderDetails[23]
        modQtyRem = entireOrderDetails[11]
        modInstrumentType = entireOrderDetails[5]

        try:
            modInstrumentType = modInstrumentType.upper()
        except Exception as e:
            return [ERROR_C_1, ERROR_C_INV_SEGMENT, ERROR_M_INV_SEGMENT]

        if modInstrumentType == API_OMS_V_SEG_CM_1:
            modInstrumentType = API_OMS_V_SEG_CM_2
        elif modInstrumentType == API_OMS_V_SEG_FO_1:
            modInstrumentType = API_OMS_V_SEG_FO_2
        elif modInstrumentType == API_OMS_V_SEG_CD_1:
            None
        elif modInstrumentType == API_OMS_V_SEG_COM_1:
            None
        else:
            return [ERROR_C_1, ERROR_C_INV_SEGMENT, ERROR_M_INV_SEGMENT]
        modExchange = entireOrderDetails[3]
        modScripName = entireOrderDetails[7]
        transactionType = entireOrderDetails[4]
        orderType = entireOrderDetails[14]
        modifiedQty = entireOrderDetails[11]
        modifiedPrice = entireOrderDetails[12]
        modifiedTrigPrice = entireOrderDetails[13]
        modifiedProduct = entireOrderDetails[8]
        orderStatus = entireOrderDetails[9].lower()

        # If orderStatus is already Cancelled, we will return from here itself
        if orderStatus == "cancelled" or orderStatus == "o-cancelled":
            return [ERROR_C_1,ERROR_C_OMS_ORDER_ALREADY_CANCELLED,ERROR_M_ORDER_ALREADY_CANCELLED]
        # If orderStatus is already filed, we will return from here itself
        elif orderStatus == "traded":
            return [ERROR_C_1,ERROR_C_OMS_ORDER_ALREADY_TRADED,ERROR_M_ORDER_ALREADY_TRADED]
        # If orderStatus is already rejected, we will return from here itself
        elif orderStatus == "rejected":
            return [ERROR_C_1,ERROR_C_OMS_ORDER_ALREADY_REJECTED,ERROR_M_ORDER_ALREADY_REJECTED]

        try:
            modifiedProduct = modifiedProduct.upper()
        except Exception as e:
            return [ERROR_C_1, ERROR_C_INV_ORDER_PRODUCT, ERROR_M_INV_ORDER_PRODUCT]

        if modifiedProduct == API_OMS_V_ORDER_PROD_CNC_2:
            modifiedProduct = API_OMS_V_ORDER_PROD_CNC_1
        elif modifiedProduct == API_OMS_V_ORDER_PROD_MARGIN_2:
            modifiedProduct = API_OMS_V_ORDER_PROD_MARGIN_1
        elif modifiedProduct == API_OMS_V_ORDER_PROD_INTRADAY_2:
            modifiedProduct = API_OMS_V_ORDER_PROD_INTRADAY_1
        else:
            return [ERROR_C_1, ERROR_C_INV_ORDER_PRODUCT, ERROR_M_INV_ORDER_PRODUCT]

        modifiedValidity = entireOrderDetails[18]
        modifiedDiscQty = entireOrderDetails[15]
        offlineFlag = API_OMS_V_DEFAULT_ORDER_OFFLINE_FLAG_2

        # If its an offline order, we should change the offline flag to true
        if "o-" in orderStatus:
            offlineFlag = "true"

        try:
            transactionType = transactionType.lower()
        except Exception as e:
            return [ERROR_C_1, ERROR_C_INV_ORDER_SIDE, ERROR_M_INV_ORDER_SIDE]

        # TransactionType needs to be changed
        if transactionType ==  "buy":
            transactionType = API_OMS_V_ORDER_SIDE_BUY_1
        elif transactionType ==  "sell":
            transactionType = API_OMS_V_ORDER_SIDE_SELL_1
        else:
            return [ERROR_C_1, ERROR_C_INV_ORDER_SIDE, ERROR_M_INV_ORDER_SIDE]

        try:
            orderType = orderType.upper()
        except Exception as e:
            return [ERROR_C_1, ERROR_C_INV_ORDER_TYPE, ERROR_M_INV_ORDER_TYPE]

        # Ordertype needs to be changed
        if (orderType == API_OMS_V_ORDER_TYPE_LMT_2):
            orderType = API_OMS_V_ORDER_TYPE_LMT_1
        elif (orderType == API_OMS_V_ORDER_TYPE_MKT_2):
            orderType = API_OMS_V_ORDER_TYPE_MKT_1

        # Create a paramsdict to send to the OMS
        paramsPayload = {
            "token_id": OMStoken,
            "client_id": OMSid,
            API_OMS_K_REQ_SOURCE: source,
            "client_type": OMSClientType,
            "exch_client_id": OMSExchClientId,
            "user_id": OMSUserID,
            "user_type": OMSUserType,
            "modinst_type": modInstrumentType,
            "modexchange": modExchange,
            "modorder_serial_number": str(modOrderSerialNumber),
            "modorder_number": str(orderID),
            "modscripname": "",
            "modbuysell": transactionType,
            "modquantitytype": orderType,
            "modquantity": modifiedQty,
            "modprice": modifiedPrice,
            "modtriggerprice": str(modifiedTrigPrice),
            "moddisclosequantity": str(modifiedDiscQty),
            "modproductlist": modifiedProduct,
            "modOrderType": modifiedValidity,
            "modsecurityid": str(modSecurityId),
            "modqty_remng": str(modQtyRem),
            "offline_flag": offlineFlag,
            "modtraded_qty": str(modTradedQty),
            "marketProflag": API_OMS_V_DEFAULT_MARKET_PRO_FLAG,
            "marketProVal": API_OMS_V_DEFAULT_MARKET_PRO_VAL,
            "ParticipantType": "",
            "settlor": "",
            "Gtcflag": API_OMS_V_DEFAULT_GTC_FLAG,
            "EncashFlag": API_OMS_V_DEFAULT_ENCASH_FLAG,
            API_OMS_K_PAN_1: pan
        }
        # Send request to the OMS
        urlForRequest = REQ_URL_OMS_MAIN_1 + API_OMS_REQ_PATH_ORDER_CANCEL

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
        readOmsResponseFuncRet2 = INTERNAL_readOmsDecryptedResponse(userInfoList,tokenHash, paramsPayload,urlForRequest,fyId=OMSid,localMemory=localMemory,callingFuncName=callingFuncName, userIp=userIp)
        return readOmsResponseFuncRet2

    except Exception as e:
        logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName,callingFuncName, e, ERROR_C_UNKNOWN, tokenHash)
        return [ERROR_C_1, ERROR_C_UNKNOWN, e]


def main():
    None


if __name__ == "__main__":
    main()
