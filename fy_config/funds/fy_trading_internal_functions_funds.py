from socket import timeout


moduleName = "fy_trading_internal_functions_funds"
try:
    import sys

    from fy_base_success_error_codes import ERROR_C_1, SUCCESS_C_1, \
     ERROR_C_UNKNOWN, ERROR_C_OMS_1
    from fy_base_defines import LOG_STATUS_ERROR_1
    from fy_data_and_trade_defines import BEWARE_CLIENTS_LIST
    from fy_trading_defines import API_OMS_K_TOKEN_ID_2, API_OMS_K_CLIENT_ID_1, \
     API_OMS_K_REQ_SOURCE, API_OMS_K_ROW_START, API_OMS_V_PAGINATION_START, \
     API_OMS_K_ROW_END,API_OMS_V_PAGINATION_END, REQ_URL_OMS_MAIN_2, \
     API_OMS_REQ_PATH_FUNDS

    from fy_base_functions import logEntryFunc2
    from fy_connections import connectRedis
    from fy_trading_internal_functions import INTERNAL_getToken_checkStatus, \
     INTERNAL_createAndSendOmsRequest, INTERNAL_decryptOmsResponse, \
     INTERNAL_readOmsDecryptedResponse

except Exception as e:
    print("ERR : %s : %s : %s" % (moduleName, "Could not import module", e))
    sys.exit()


def INTERNAL_getFundLimit4(tokenHash,callingFuncName="",userIp="", fyId=""):
    """
    [FUNCTION]
        Get the user's fund limit
    [PARAMS]
            tokenHash   : This is a hash of (fyId + AppId)
    [RETURN]
        Success    : [1,Dict]     = The second element is a dictionary of entire fund limit status
                        Dict[limitType] => "CAPITAL/COMMODITY"
                            {"limitSod":#,
                            "limitAdhoc":#,
                            "limitRecv":#,
                            "limitBankHld":#,
                            "limitCollaterals":#,
                            "limitRealizedPnl":#,
                            "limitUtilized":#,
                            "limitClearBal":#,
                            "limitSum":#,
                            "limitAvailBal":#}
        Failure : [ERROR_C_1, errorCode,"error message"]
    """
    funcName = "INTERNAL_getFundLimit4"
    try:
        localMemory = connectRedis(callingFuncName=callingFuncName)

        tokenHash = str(tokenHash)
        limitAvailBalDict = {"id": 10, "title": "Available Balance", "equityAmount": 0, "commodityAmount": 0}
        limitSodDict = {"id": 9, "title": "Limit at start of the day", "equityAmount": 0, "commodityAmount": 0}
        limitAdhocDict = {"id": 8, "title": "Adhoc Limit", "equityAmount": 0, "commodityAmount": 0}
        limitRecvDict = {"id": 7, "title": "Receivables", "equityAmount": 0, "commodityAmount": 0}
        limitBankHldDict = {"id": 6, "title": "Fund Transfer", "equityAmount": 0, "commodityAmount": 0}
        limitCollateralsDict = {"id": 5, "title": "Collaterals", "equityAmount": 0, "commodityAmount": 0}
        limitRealizedPnlDict = {"id": 4, "title": "Realized Profit and Loss", "equityAmount": 0,
                                "commodityAmount": 0}
        limitClearBalDict = {"id": 3, "title": "Clear Balance", "equityAmount": 0, "commodityAmount": 0}
        limitUtilizedDict = {"id": 2, "title": "Utilized Amount", "equityAmount": 0, "commodityAmount": 0}
        limitSumDict = {"id": 1, "title": "Total Balance", "equityAmount": 0, "commodityAmount": 0}
        returnList2 = [limitSodDict, limitAdhocDict, limitRecvDict, limitBankHldDict,
                             limitCollateralsDict, limitRealizedPnlDict, limitUtilizedDict, limitClearBalDict,
                             limitSumDict, limitAvailBalDict]
        fyTokenList = INTERNAL_getToken_checkStatus(tokenHash,localMemory=localMemory,callingFuncName=callingFuncName, userIp=userIp)

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

        paramsForEncryption = {API_OMS_K_TOKEN_ID_2: omsTokenId, API_OMS_K_CLIENT_ID_1: fyId, API_OMS_K_REQ_SOURCE: source, API_OMS_K_ROW_START: API_OMS_V_PAGINATION_START,
                               API_OMS_K_ROW_END: API_OMS_V_PAGINATION_END}
        urlForRequest = REQ_URL_OMS_MAIN_2 + API_OMS_REQ_PATH_FUNDS

        sendReqFuncRet = INTERNAL_createAndSendOmsRequest(fyId, omsTokenId, aesKey,paramsForEncryption, urlForRequest,callingFuncName=callingFuncName, userIp=userIp)

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

        if (len(userInfoList) != 0):
            for i in userInfoList:
                limitType = i["LIMIT_TYPE"].lstrip()
                try:
                    limitSod             = float(i["LIMIT_SOD"])
                    limitAdhoc             = float(i["ADHOC_LIMIT"])
                    limitRecv             = float(i["RECEIVABLES"])
                    limitBankHld         = float(i["BANK_HOLDING"])
                    limitCollaterals     = float(i["COLLATERALS"])
                    limitRealizedPnl     = float(i["REALISED_PROFITS"])
                    limitUtilized         = float(i["AMOUNT_UTILIZED"])
                    limitClearBal         = float(i["CLEAR_BALANCE"])
                    limitSum             = float(i["SUM_OF_ALL"])
                    limitAvailBal         = float(i["AVAILABLE_BALANCE"])
                except AttributeError:
                    logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, i, err_msg="AttributeError", code=ERROR_C_OMS_STRING_CONVERSION_FAIL,fyId=fyId)
                    continue
                except Exception as e:
                    logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, i, err_msg=e, code=ERROR_C_OMS_STRING_CONVERSION_FAIL,fyId=fyId)
                    continue

                if limitType == "CAPITAL":
                    limitSodDict["equityAmount"] = limitSod
                    limitAdhocDict["equityAmount"] = limitAdhoc
                    limitRecvDict["equityAmount"] = limitRecv
                    limitBankHldDict["equityAmount"] = limitBankHld
                    limitCollateralsDict["equityAmount"] = limitCollaterals
                    limitRealizedPnlDict["equityAmount"] = limitRealizedPnl
                    limitUtilizedDict["equityAmount"] = limitUtilized
                    limitClearBalDict["equityAmount"] = limitClearBal
                    limitSumDict["equityAmount"] = limitSum
                    limitAvailBalDict["equityAmount"] = limitAvailBal
                elif limitType == "COMMODITY":
                    limitSodDict["commodityAmount"] = limitSod
                    limitAdhocDict["commodityAmount"] = limitAdhoc
                    limitRecvDict["commodityAmount"] = limitRecv
                    limitBankHldDict["commodityAmount"] = limitBankHld
                    limitCollateralsDict["commodityAmount"] = limitCollaterals
                    limitRealizedPnlDict["commodityAmount"] = limitRealizedPnl
                    limitUtilizedDict["commodityAmount"] = limitUtilized
                    limitClearBalDict["commodityAmount"] = limitClearBal
                    limitSumDict["commodityAmount"] = limitSum
                    limitAvailBalDict["commodityAmount"] = limitAvailBal
            # This will get returned
            returnList2 = [limitSodDict, limitAdhocDict, limitRecvDict, limitBankHldDict,
                           limitCollateralsDict, limitRealizedPnlDict, limitUtilizedDict, limitClearBalDict,
                           limitSumDict, limitAvailBalDict]
            return [SUCCESS_C_1, returnList2, userInfoList]
        else:
            # If nothing else gets triggered this will get triggered
            return [SUCCESS_C_1, returnList2, userInfoList]

    except Exception as e:
        logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName,callingFuncName, e, ERROR_C_UNKNOWN, tokenHash)
        return [ERROR_C_1, ERROR_C_UNKNOWN, ""]


def main():
    pass  # Do testing here


if __name__ == "__main__":
    main()
