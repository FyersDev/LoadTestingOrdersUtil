moduleName = "fy_trading_internal_functions_positions_POST"
try:    
    import sys

    from fy_base_defines import LOG_STATUS_ERROR_1
    from fy_base_success_error_codes import ERROR_C_1, ERROR_C_INV_EXCHANGE, \
     ERROR_C_INV_SEGMENT, ERROR_C_INV_ORDER_PRODUCT, ERROR_C_INV_ORDER_SIDE, \
     ERROR_C_UNKNOWN
    from fy_base_success_error_messages import ERROR_M_INV_EXCHANGE, \
     ERROR_M_INV_SEGMENT, ERROR_M_INV_ORDER_PRODUCT, \
     ERROR_M_INV_ORDER_SIDE
    from fy_data_and_trade_defines import EXCHANGE_CODE_NSE, EXCHANGE_NAME_NSE, \
     EXCHANGE_CODE_MCX, EXCHANGE_NAME_MCX_1, EXCHANGE_CODE_BSE, EXCHANGE_NAME_BSE, \
     SYM_SEGMENT_CM, SYM_SEGMENT_FO, SYM_SEGMENT_CD, SYM_SEGMENT_COM
    from fy_trading_defines import API_OMS_V_SEG_CM_1, API_OMS_V_SEG_FO_1, \
     API_OMS_V_SEG_CD_1, API_OMS_V_SEG_COM_1, API_OMS_V_ORDER_PROD_CNC_2, \
     API_OMS_V_ORDER_PROD_CNC_1, API_OMS_V_ORDER_PROD_MARGIN_2, \
     API_OMS_V_ORDER_PROD_MARGIN_1, API_OMS_V_ORDER_PROD_INTRADAY_2, \
     API_OMS_V_ORDER_PROD_INTRADAY_1, API_V_ORDER_SIDE_BUY_1, API_V_ORDER_SIDE_SELL_1, \
     API_OMS_V_ORDER_SIDE_BUY_1, API_OMS_V_ORDER_SIDE_SELL_1, API_OMS_K_REQ_SOURCE, \
     REQ_URL_OMS_MAIN_1, API_OMS_REQ_PATH_CONVERT_POSITION
     
    from fy_common_internal_functions import INTERNAL_checkSymbolNameOrToken, \
     INTERNAL_getSymExAndSegment
    from fy_connections import connectRedis
    from fy_base_functions import logEntryFunc2
    from fy_trading_internal_functions import INTERNAL_createAndSendOmsRequest, \
     INTERNAL_decryptOmsResponse, INTERNAL_readOmsDecryptedResponse
    from fy_trading_common_functions import INTERNAL_fy_getNecessaryOMSData_withID

except Exception as e:
    print("ERR : %s : %s : %s" % (moduleName, "Could not import module", e))
    sys.exit()


def INTERNAL_omsConvertPosition(tokenHash,symbol,positionSide,convertQuantity,convertFrom,convertTo,callingFuncName="",userIp=""):
    funcName = "INTERNAL_omsConvertPosition"
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
        appId = fyTokenList[2]
        source = fyTokenList[3]

        # Based in symbol input we can derive the necessary details
        # Converting symbol name to token
        checkSymbolList = INTERNAL_checkSymbolNameOrToken(symbol, localMemory=localMemory,callingFuncName=callingFuncName)
        if checkSymbolList[0] == ERROR_C_1:
            return checkSymbolList
        # Splitting the token to get the exchange, segment and scripCode
        symbolList = INTERNAL_getSymExAndSegment(checkSymbolList[1][0],callingFuncName=callingFuncName)
        if symbolList[0] == ERROR_C_1:
            return symbolList

        if symbolList[1][0] == str(EXCHANGE_CODE_NSE):
            exchange = EXCHANGE_NAME_NSE
        elif symbolList[1][0] == str(EXCHANGE_CODE_MCX):
            exchange = EXCHANGE_NAME_MCX_1
        elif symbolList[1][0] == str(EXCHANGE_CODE_BSE):
            exchange = EXCHANGE_NAME_BSE
        else:
            return [ERROR_C_1, ERROR_C_INV_EXCHANGE, ERROR_M_INV_EXCHANGE]

        # Rupeeseed has different codes for each segment
        if symbolList[1][1] == str(SYM_SEGMENT_CM):
            symSegment = API_OMS_V_SEG_CM_1
        elif symbolList[1][1] == str(SYM_SEGMENT_FO):
            symSegment = API_OMS_V_SEG_FO_1
        elif symbolList[1][1] == str(SYM_SEGMENT_CD):
            symSegment = API_OMS_V_SEG_CD_1
        elif symbolList[1][1] == str(SYM_SEGMENT_COM):
            symSegment = API_OMS_V_SEG_COM_1
        else:
            return [ERROR_C_1, ERROR_C_INV_SEGMENT, ERROR_M_INV_SEGMENT]

        symInstType = symSegment

        try:
            convertFrom = convertFrom.upper()
            convertTo = convertTo.upper()
        except Exception as e:
            return [ERROR_C_1, ERROR_C_INV_ORDER_PRODUCT, ERROR_M_INV_ORDER_PRODUCT]

        # Rupeeseed has different codes for each product type
        if (convertFrom == API_OMS_V_ORDER_PROD_CNC_2) or (convertFrom == API_OMS_V_ORDER_PROD_CNC_1):
            convertFrom = API_OMS_V_ORDER_PROD_CNC_1
        elif (convertFrom == API_OMS_V_ORDER_PROD_MARGIN_2) or (convertFrom == API_OMS_V_ORDER_PROD_MARGIN_1):
            convertFrom = API_OMS_V_ORDER_PROD_MARGIN_1
        elif (convertFrom == API_OMS_V_ORDER_PROD_INTRADAY_2) or (
            convertFrom == API_OMS_V_ORDER_PROD_INTRADAY_1):
            convertFrom = API_OMS_V_ORDER_PROD_INTRADAY_1
        else:
            return [ERROR_C_1, ERROR_C_INV_ORDER_PRODUCT, ERROR_M_INV_ORDER_PRODUCT]

        # Rupeeseed has different codes for each product type
        if (convertTo == API_OMS_V_ORDER_PROD_CNC_2) or (
            convertTo == API_OMS_V_ORDER_PROD_CNC_1):
            convertTo = API_OMS_V_ORDER_PROD_CNC_1
        elif (convertTo == API_OMS_V_ORDER_PROD_MARGIN_2) or (
            convertTo == API_OMS_V_ORDER_PROD_MARGIN_1):
            convertTo = API_OMS_V_ORDER_PROD_MARGIN_1
        elif (convertTo == API_OMS_V_ORDER_PROD_INTRADAY_2) or (
                    convertTo == API_OMS_V_ORDER_PROD_INTRADAY_1):
            convertTo = API_OMS_V_ORDER_PROD_INTRADAY_1
        else:
            return [ERROR_C_1, ERROR_C_INV_ORDER_PRODUCT, ERROR_M_INV_ORDER_PRODUCT]

        # Check positionSide
        try:
            positionSide = int(positionSide)
        except Exception as e:
            if positionSide == 'Buy' or positionSide == 'BUY':
                positionSide = API_V_ORDER_SIDE_BUY_1
            elif positionSide == 'Sell' or positionSide == 'SELL':
                positionSide = API_V_ORDER_SIDE_SELL_1
            else:
                return [ERROR_C_1, ERROR_C_INV_ORDER_SIDE, ERROR_M_INV_ORDER_SIDE]
        # Rupeeseed has different codes for buy/sell like B/S
        if positionSide == API_V_ORDER_SIDE_BUY_1:
            positionSide = API_OMS_V_ORDER_SIDE_BUY_1
        elif positionSide == API_V_ORDER_SIDE_SELL_1:
            positionSide = API_OMS_V_ORDER_SIDE_SELL_1
        else:
            return [ERROR_C_1, ERROR_C_INV_ORDER_SIDE, ERROR_M_INV_ORDER_SIDE]

        paramsPayload = {
            "user_id":OMSUserID,
            "token_id":OMStoken,
            "client_type":OMSClientType,
            "user_type":OMSUserType,
            "exchange":exchange,
            API_OMS_K_REQ_SOURCE:source,
            "seg":symSegment,
            "securityid":symbolList[1][2],
            "client_id":OMSid,
            "exch_client_id":OMSExchClientId,
            "buysell":positionSide,
            "quantity":str(convertQuantity),
            "productfrom":convertFrom,
            "productto":convertTo,
            "inst_type":symInstType
        }

        # Send the request to the OMS
        urlForRequest = REQ_URL_OMS_MAIN_1 + API_OMS_REQ_PATH_CONVERT_POSITION
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
        readOmsResponseFuncRet2 = INTERNAL_readOmsDecryptedResponse(userInfoList,tokenHash, paramsPayload,urlForRequest,fyId=OMSid, localMemory=localMemory,callingFuncName=callingFuncName,userIp=userIp)
        return readOmsResponseFuncRet2

    except Exception as e:
        logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName,
                      callingFuncName, e, ERROR_C_UNKNOWN)
        return [ERROR_C_1, ERROR_C_UNKNOWN, ""]


def main():
    None


if __name__ == "__main__":
    main()
