moduleName = "fy_trading_internal_functions_orders_details_GET"
try:
    import sys

    from fy_base_defines import LOG_STATUS_ERROR_1
    from fy_base_success_error_codes import ERROR_C_1, SUCCESS_C_1, \
     ERROR_C_UNKNOWN, ERROR_C_OMS_1, ERROR_C_OMS_ORDERBOOK_EMPTY
    from fy_base_success_error_messages import ERROR_M_INV_ORDER_ID
    from fy_trading_defines import API_OMS_K_TOKEN_ID_2, API_OMS_K_CLIENT_ID_1, \
     API_OMS_K_REQ_SOURCE, API_OMS_ORDER_DETAIL_SEG, REQ_URL_OMS_MAIN_1, \
     API_OMS_REQ_PATH_ORDER_DETAILS

    from fy_connections import connectRedis
    from fy_base_functions import logEntryFunc2
    from fy_trading_internal_functions import INTERNAL_getToken_checkStatus, \
     INTERNAL_createAndSendOmsRequest, INTERNAL_decryptOmsResponse, \
     INTERNAL_readOmsDecryptedResponse

except Exception as e:
    print("ERR : %s : %s : %s" % (moduleName, "Could not import module", e))
    sys.exit()


def INTERNAL_getOrderAdditionalDetails_withId(tokenHash, orderID, segment, symbol, db=None,cursor=None,localMemory=None,callingFuncName="",userIp=""):
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
    funcName = "INTERNAL_getOrderAdditionalDetails_withId"
    try:
        orderID = str(orderID)
        tokenHash = str(tokenHash)
        if localMemory == None:
            localMemory = connectRedis(callingFuncName=callingFuncName)

        fyTokenList = INTERNAL_getToken_checkStatus(tokenHash,localMemory=localMemory,callingFuncName=callingFuncName,userIp=userIp)
        if fyTokenList[0] == ERROR_C_1:
            return fyTokenList
        fyId = fyTokenList[1][0]
        omsTokenId = fyTokenList[1][1]
        aesKey = fyTokenList[1][2]
        appId       = fyTokenList[2]
        source      = fyTokenList[3]

        # Send the request to the OMS
        paramsForEncryption = {API_OMS_K_TOKEN_ID_2: omsTokenId, API_OMS_K_CLIENT_ID_1: fyId, API_OMS_K_REQ_SOURCE: source,
                               "ord_no":orderID, API_OMS_ORDER_DETAIL_SEG: segment}
        urlForRequest = REQ_URL_OMS_MAIN_1 + API_OMS_REQ_PATH_ORDER_DETAILS
        sendReqFuncRet = INTERNAL_createAndSendOmsRequest(fyId, omsTokenId, aesKey,paramsForEncryption, urlForRequest, callingFuncName=callingFuncName,userIp=userIp)
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
                                                urlForRequest,fyId=fyId, localMemory=localMemory,callingFuncName=callingFuncName, userIp=userIp)
        if (readOmsResponseFuncRet2[0] == ERROR_C_1) or (readOmsResponseFuncRet2[0] == ERROR_C_OMS_1):
            return readOmsResponseFuncRet2
        userInfoList = readOmsResponseFuncRet2[1]

        # If we have received data for orderbook
        if (len(userInfoList) != 0):
            for i in range(0,len(userInfoList)):
                userInfoList[i]["SEM_SYMBOL"] = symbol
            return [SUCCESS_C_1, userInfoList, ""]
        else:
            return [ERROR_C_1, ERROR_C_OMS_ORDERBOOK_EMPTY, ERROR_M_INV_ORDER_ID]

    except Exception as e:
        logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName,callingFuncName, tokenHash, err_msg=e, code=ERROR_C_UNKNOWN, fyId=fyId)
        return [ERROR_C_1, ERROR_C_UNKNOWN, funcName]


def main():
    None


if __name__ == "__main__":
    main()
