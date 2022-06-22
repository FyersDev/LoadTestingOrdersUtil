from socket import timeout


moduleName = "fy_trading_internal_functions"
try:
    import base64
    import json
    import random
    import sys
    import string
    import time
    import urllib3
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.backends import default_backend

    from fy_auth_defines import APPID_TRADE_FYERS, APPID_MOBILE_FYERS
    from fy_base_success_error_codes import ERROR_C_1, SUCCESS_C_1, \
     ERROR_C_DEMO_USER, RUPEE_SEED_ERROR, ERROR_C_UNKNOWN, \
     ERROR_C_OMS_URL_STATUS_CODE, ERROR_C_OMS_URL_CONNECTION, \
     ERROR_C_OMS_URL_TIMEOUT, ERROR_C_OMS_URL_HTTP, ERROR_C_OMS_1, \
     ERROR_C_OMS_STATUS_ALREADY_UNLOCKED, ERROR_C_OMS_STATUS_MAX_ATTEMPTS, \
     ERROR_C_OMS_INV_REQUEST, ERROR_C_OMS_UNKNOWN, ERROR_C_OMS_INV_FYERSID_2, \
     ERROR_C_OMS_STATUS_LOCKED, ERROR_C_OMS_INV_PWD, ERROR_C_OMS_INV_PWD2, \
     ERROR_C_OMS_STATUS_NOT_SUBSCRIBED, ERROR_C_OMS_AUTHFAIL, \
     ERROR_C_OMS_INV_MANDATORY_MISSING, ERROR_C_OMS_STATUS_DISABLED, \
     ERROR_C_OMS_STATUS_SUSPENDED, ERROR_C_OMS_INV_DOB, ERROR_C_OMS_INV_PAN, \
     ERROR_C_OMS_STATUS_PWD_EXPIRED, ERROR_C_OMS_MARKET_OFFLINE, \
     ERROR_C_OMS_ORDER_FAIL_1, ERROR_C_OMS_ORDER_FAIL_LIMIT_NOT_AVAILABLE, \
     ERROR_C_OMS_ORDER_FAIL_INV_FYID_DATA, ERROR_C_OMS_ORDER_FAIL_INV_QTY_NOT_NUM, \
     ERROR_C_OMS_ORDER_FAIL_INV_TRG_PRICE, ERROR_C_OMS_ORDER_FAIL_INV_DISC_QTY, \
     ERROR_C_OMS_ORDER_FAIL_INV_EXCH, ERROR_C_OMS_ORDER_FAIL_INV_INST_TYPE, \
     ERROR_C_EDIS_INV_TXN_ID, ERROR_C_OMS_PASSWD_SAME_PREV_5, \
     ERROR_C_OMS_ORDER_MODIFY_FAILED, ERROR_C_OMS_INV_ALPHANUM_REQ, \
     ERROR_C_OMS_INV_PWD_NOT_MATCHING, ERROR_C_OMS_INV_PWD_TOO_SHORT, \
     ERROR_C_OMS_INV_EXIST_PWD, ERROR_C_OMS_INV_SAME_AS_EXIST_PWD, \
     ERROR_C_OMS_ORDER_NOT_CONNECTED, SUCCESS_C_OMS, SUCCESS_C_OMS_PWD_RESET, \
     SUCCESS_C_OMS_UNLOCK, SUCCESS_C_OMS_FT_OUTWARD, SUCCESS_C_OMS_ORDER_PLACE, \
     SUCCESS_C_OMS_PWD_CHANGE, SUCCESS_C_OMS_LOGOUT, SUCCESS_C_OMS_ORDER_MODIFY, \
     SUCCESS_C_OMS_ORDER_CANCEL, ERROR_C_INV_INST_TYPE, ERROR_C_INV_SEGMENT, \
     ERROR_C_INV_ORDER_PRODUCT, ERROR_C_INV_ORDER_STOP_LMT_PRICE, \
     ERROR_C_INV_ORDER_TYPE, ERROR_C_INV_ORDER_SIDE
    from fy_base_success_error_messages import ERROR_M_UNKNOWN_1, \
     ERROR_M_COULD_NOT_CONNECT_TRY_AGAIN, ERROR_M_INV_INST_TYPE, \
     ERROR_M_INV_SEGMENT, ERROR_M_INV_ORDER_PRODUCT, ERROR_M_INV_ORDER_STP_LMT_PRICE, \
     ERROR_M_INV_ORDER_TYPE, ERROR_M_INV_ORDER_SIDE
    from fy_base_defines import LOG_STATUS_ERROR_1, LOG_OMS_RESPONSE_1
    from fy_common_api_keys_values import API_K_SYM_SEGMENT, API_K_ORDER_PRODUCT, \
     API_K_ORDER_TYPE_RS, API_V_ORDER_TYPE_MKT_1, API_V_ORDER_TYPE_MKT_2, \
     API_K_DATA_PRICE_1, API_K_TRIG_PRICE, API_V_ORDER_TYPE_LMT_1, API_V_ORDER_TYPE_LMT_2, \
     API_V_ORDER_TYPE_STP_MKT, API_V_ORDER_TYPE_STP_LMT, API_K_TRANS_TYPE, \
     API_V_ORDER_SIDE_BUY_1, API_V_ORDER_SIDE_SELL_1
    from fy_data_and_trade_defines import GUEST_CLIENT_ID, BEWARE_CLIENTS_LIST, \
     SYM_SEGMENT_CM, SYM_SEGMENT_FO, SYM_SEGMENT_CD, SYM_SEGMENT_COM
    from fy_trading_defines import REQ_URL_OMS_MAIN_1, API_OMS_V_REQ_SOURCE_WEB, \
     API_OMS_V_REQ_SOURCE_MOBILE, API_OMS_V_DEFAULT_REQ_SOURCE, \
     API_OMS_K_TOKEN_ID_2, API_OMS_K_CLIENT_ID_1, API_OMS_K_REQ_SOURCE, \
     API_OMS_K_ROW_START, API_OMS_V_PAGINATION_START, API_OMS_K_ROW_END, \
     API_OMS_V_PAGINATION_END, REQ_URL_OMS_MAIN_2, API_OMS_REQ_PATH_FUNDS, \
     API_OMS_K_USER_ID, API_OMS_K_TOKEN_ID, API_OMS_K_IV_STRING, \
     API_OMS_K_DATA_1, API_OMS_REQ_TIMEOUT, API_OMS_K_STATUS_1, \
     API_OMS_V_ERROR_1, API_OMS_K_ERROR_CODE, API_OMS_K_CODE_1, \
     API_OMS_K_MESSAGE_1, API_OMS_V_SUCCESS_1, API_OMS_K_TOKEN_ID_3, \
     API_OMS_V_SEG_CM_1, API_OMS_V_SEG_CM_2, API_OMS_V_SEG_FO_1, \
     API_OMS_V_SEG_FO_2, API_OMS_V_SEG_CD_1, API_OMS_V_SEG_COM_1, API_OMS_V_ORDER_PROD_CNC_2, \
     API_OMS_V_ORDER_PROD_CNC_1, API_OMS_V_ORDER_PROD_MARGIN_2, API_OMS_V_ORDER_PROD_MARGIN_1, \
     API_OMS_V_ORDER_PROD_INTRADAY_2, API_OMS_V_ORDER_PROD_INTRADAY_1, \
     API_OMS_V_ORDER_PROD_CO_2, API_OMS_V_ORDER_PROD_CO_1, API_OMS_V_ORDER_PROD_BO_2, \
     API_OMS_V_ORDER_PROD_BO_1, API_OMS_V_ORDER_TYPE_LMT_1, \
     API_OMS_V_ORDER_TYPE_MKT_1, API_OMS_V_ORDER_TYPE_LMT_2, API_OMS_V_ORDER_TYPE_MKT_2, \
     API_OMS_V_ORDER_SIDE_BUY_2, API_OMS_V_ORDER_SIDE_BUY_1, API_OMS_V_ORDER_SIDE_SELL_1, \
     API_OMS_V_ORDER_SIDE_SELL_2

    from fy_base_functions import logEntryFunc2
    from fy_connections import connectRedis
    # from fy_auth_functions import INTERNAL_splitTokenHash
    from vagator_auth_check import INTERNAL_splitTokenHash

except Exception as e:
    print("ERR : %s : %s : %s" % (moduleName, "Could not import module", e))
    sys.exit()

# http_pool = urllib3.PoolManager()


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


def INTERNAL_getToken_checkStatus(tokenHash=None,db=None,cursor=None,localMemory=None,inputFyId=None,inputAppId=None,callingFuncName="",userIp=""):
    """
    [FUNCTION]
        Checks the return of INTERNAL_fy_getToken_withID, will do re authenticate if required and return the status
    [PARAMS]
        tokenHash    : This is a hash of (fyId + AppId)
    [RETURN]
        Success : [SUCCESS_C_1,OMSID,OMSTOKEN]
        Failure : [ERROR_C_1,errorCode,functionName]
    """
    funcName = "INTERNAL_getToken_checkStatus"

    try:
        if localMemory == None:
            localMemory = connectRedis(callingFuncName=callingFuncName)


        if inputFyId == None or inputFyId == "" or inputAppId == None or inputAppId == "":
            tokenList = INTERNAL_splitTokenHash(tokenHash,callingFuncName=funcName)
            # print(tokenList)
            if tokenList[0] == ERROR_C_1:
                return tokenList
            user_id = tokenList[1][0]
            app_id = tokenList[1][1]
        else:
            user_id = inputFyId
            app_id = inputAppId


        omsDetailsCache = localMemory.get(f"oms_data-{user_id}-7831|")
        if omsDetailsCache != None:
            omsDetailsCache = json.loads(omsDetailsCache)

        else:
            funcRet = INTERNAL_fy_reauth_withID(inputFyId=user_id, inputAppId=app_id)
            if funcRet[0] == SUCCESS_C_1:
                omsDetailsCache = funcRet[1]
            else:
                return funcRet

        if app_id == APPID_TRADE_FYERS:
            source = API_OMS_V_REQ_SOURCE_WEB
        elif app_id == APPID_MOBILE_FYERS:
            source = API_OMS_V_REQ_SOURCE_MOBILE
        else:
            logEntryFunc2("DEBUG", moduleName, funcName, callingFuncName, user_id, app_id, "App Id other than web or mobile")
            source = API_OMS_V_DEFAULT_REQ_SOURCE

        if omsDetailsCache != None:
            return [SUCCESS_C_1, [omsDetailsCache[0].strip(), omsDetailsCache[1].strip(), omsDetailsCache[2].strip(), omsDetailsCache[3].strip()], app_id, source]
        else:
            logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName,callingFuncName,tokenHash, inputFyId, "OMS details not found", code=ERROR_C_UNKNOWN, fyId=inputFyId)
            return [ERROR_C_1, ERROR_C_UNKNOWN, ERROR_M_UNKNOWN_1]

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName,callingFuncName,tokenHash, err_msg=e, code=ERROR_C_UNKNOWN, fyId=inputFyId)
        return [ERROR_C_1, ERROR_C_UNKNOWN, ERROR_M_UNKNOWN_1]


def INTERNAL_fy_reauth_withID(tokenHash=None,db=None,cursor=None,localMemory=None,inputFyId=None,inputAppId=None,callingFuncName="",userIp=""):
    """
        Re-validate user and inserts/updates the TBL_OMS_AUTH_V2 table & returns OMSTOKEN
        [PARAMS]
            tokenHash    : This is a hash of (fyId + AppId)
        [RETURN]
            Success : [SUCCESS_C_1,OMSID,OMSTOKEN] = Array that returns OMS ID and TOKEN
            Failure : [ERROR_C_1,ERROR_C_DB_NOT_FOUND,"errorMessage"] = Could not find tokenHash in db
                      [ERROR_C_1,ERROR_C_UNKNOWN,"error message"] = Unknown error
                      [#,#,""] = All other returns are from fy_omsAuth
    """
    funcName = "INTERNAL_fy_reauth_withID"
    try:
        API_OMS_K_USER_DETAILS              = "USER_DETAIL"
        API_OMS_K_USER_ID_2                 = "USERID" # NOT USED
        API_OMS_K_USER_ENTITY_ID            = "ENTITYID"
        API_OMS_K_USER_UM_TYPE              = "UM_USER_TYPE"
        API_OMS_K_USER_EM_NAME              = "EM_NAME"
        API_OMS_K_USER_PROFILE_ID           = "PROFILEID"
        API_OMS_K_USER_LOGIN_ID             = "LOGINID"
        API_OMS_K_AES_KEY                   = "AES_KEY"
        API_OMS_K_USER_PAN_1                = "PANNO"
        API_OMS_K_USER_STATUS_1             = "STATUS"
        API_OMS_K_USER_DOB_1                = "DOB"
        API_OMS_K_USER_TOKEN_ID             = "TOKENID"
        API_OMS_K_USER_LAST_LOGOFF_DATE     = "LOGOFF_DATE"
        API_OMS_K_USER_EM_EXCH_CLIENT_ID    = "EM_EXCH_CLIENT_ID"
        API_OMS_K_USER_EM_STATUS            = "EM_STATUS"
        API_OMS_K_USER_EMAIL_ID             = "EMAIL_ID"
        API_OMS_K_USER_LAST_LOGIN_TIME      = "LAST_LOGIN_TIME"
        API_OMS_K_USER_LAST_PWD_CHANGE      = "LAST_PWD_CHANGE_DATE"
        API_OMS_K_USER_AC_CODE              = "ACCCODE"
        API_OMS_K_USER_UM_EXCH_ALLOWED      = "UM_EXCH_ALLOWED"
        API_OMS_K_USER_UM_ENTITY_TYPE       = "UM_ENTITY_TYPE"
        API_OMS_K_USER_EM_ENTITY_MANAG_TYPE = "EM_ENTITY_MANAGER_TYPE"
        API_OMS_K_USER_BANK_DETAILS         = "bank_account_details"
        API_OMS_K_POA_FLAG                  = "POA_FLAG"

        FULL_SESSION_CREATE_API = REQ_URL_OMS_MAIN_1 + "SessionCreate"
        # def oms_rupeeseed_session_create(user_id, source, tokenHashJson, callingFuncName = ''):
        if inputFyId == None or inputFyId == "" or inputAppId == None or inputAppId == "":
            tokenList = INTERNAL_splitTokenHash(tokenHash,callingFuncName=funcName)
            if tokenList[0] == ERROR_C_1:
                return tokenList
            user_id = tokenList[1][0]
            app_id = tokenList[1][1]
        else:
            user_id = inputFyId
            app_id = inputAppId

        if user_id in GUEST_CLIENT_ID:
            return [ERROR_C_1, ERROR_C_DEMO_USER, ""]

        if app_id == APPID_TRADE_FYERS:
            source = API_OMS_V_REQ_SOURCE_WEB
        elif app_id == APPID_MOBILE_FYERS:
            source = API_OMS_V_REQ_SOURCE_MOBILE
        else:
            logEntryFunc2("DEBUG", moduleName, funcName, callingFuncName, user_id, app_id, "App Id other than web or mobile")
            source = API_OMS_V_DEFAULT_REQ_SOURCE

        funcName = "oms_rupeeseed_session_create"
        data = {
                "user_id" : str(user_id),
                "source" : str(source).upper()
                }
        data = json.dumps(data)

        #response = requests.request("POST", FULL_SESSION_CREATE_API, data=data)
        # Using urllib3
        http_pool = urllib3.PoolManager()
        http_obj = http_pool
        response = http_obj.request("POST", url=FULL_SESSION_CREATE_API, body=data)
        
        # if response.status_code != 200:
        if response.status != 200:
            return [ERROR_C_1, RUPEE_SEED_ERROR, "connection failed, please try again"]

        # userInfo            = response.json()
        userInfo = json.loads(response.data.decode("utf-8"))

        if API_OMS_K_USER_DETAILS in userInfo:
            userInfoDetails = userInfo[API_OMS_K_USER_DETAILS]
            userOmsTokenId      = userInfoDetails[API_OMS_K_USER_TOKEN_ID]
            exClientId          = userInfoDetails[API_OMS_K_USER_EM_EXCH_CLIENT_ID]
            userId              = userInfoDetails[API_OMS_K_USER_ID_2]
            userType            = userInfoDetails[API_OMS_K_USER_UM_TYPE]
            aesKeyRecv          = userInfoDetails[API_OMS_K_AES_KEY]
            userPanNo           = userInfoDetails[API_OMS_K_USER_PAN_1]
            poaFlag             = userInfoDetails[API_OMS_K_POA_FLAG]

            if localMemory == None:
                localMemory = connectRedis(callingFuncName=callingFuncName)

            omsdetails = [user_id.strip(), userOmsTokenId,aesKeyRecv,poaFlag]

            localMemory.set(f"oms_data-{user_id}-7831|", json.dumps(omsdetails))


            logEntryFunc2("REQUEST_REAUTH_2", moduleName, funcName, callingFuncName, inputFyId, fyId=inputFyId)
            return [SUCCESS_C_1, omsdetails, app_id, source]

        else:
            message = ERROR_M_UNKNOWN_1
            if "message" in userInfo:
                message = userInfo["message"]
            return [ERROR_C_1, ERROR_C_UNKNOWN, message]

    except Exception as e:
        logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName,callingFuncName, err_msg=e, code=ERROR_C_UNKNOWN, fyId=inputFyId)
        return [ERROR_C_1, ERROR_C_UNKNOWN, funcName]


def INTERNAL_createAndSendOmsRequest(fyId,omsTokenId,aesKeyForEncryption,paramsForEncryption,urlPath,callingFuncName="",userIp=""):
    """
    This function will create the entire paramateres with encryption to send to OMS
        :param callingFuncName: The function that is calling this function
        :param fyId: Fyers Client Id which needs to be sent to the OMS
        :param omsTokenId: The tokenId provided by the OMS for session validation
        :param aesKeyForEncryption: This is the aesKey which will be used for encryption
        :param paramsForEncryption: This is the params in dict which needs to be encrypted with AES before sending to OMS

        :return: Success => [SUCCESS_C_1,"string response from oms",""]
                 Error   => [ERROR_C_1,errorCode,errorMessage]
    """
    funcName = "INTERNAL_createAndSendOmsRequest"
    try:
        start = int(time.time())
        # First convert dict to json string before encryption
        paramsForEncryptionJson = json.dumps(paramsForEncryption)

        # Encrypt the paramsJson string in AES
        encryptAesFuncRet = INTERNAL_encryptInAes(paramsForEncryptionJson,aesKeyForEncryption,callingFuncName=callingFuncName)
        if encryptAesFuncRet[0] == ERROR_C_1:
            return encryptAesFuncRet
        sendEncryptedData = encryptAesFuncRet[1][0].decode('utf-8')
        sendIvString = encryptAesFuncRet[1][1].decode('utf-8')
        # Create final params which will be sent to the OMS
        paramsPayload = {API_OMS_K_USER_ID:fyId,API_OMS_K_TOKEN_ID:omsTokenId, API_OMS_K_IV_STRING:sendIvString,API_OMS_K_REQ_SOURCE:API_OMS_V_DEFAULT_REQ_SOURCE, API_OMS_K_DATA_1:sendEncryptedData}
        try:
            paramsPayload[API_OMS_K_REQ_SOURCE] = paramsForEncryption[API_OMS_K_REQ_SOURCE]
        except Exception as e:
            logEntryFunc2("DEBUG", moduleName, funcName, callingFuncName, urlPath, paramsForEncryption, "source missing in paramsForEncryption", fyId=fyId)
        paramsPayloadJson = json.dumps(paramsPayload)    # todo testing
        #paramsPayloadJson = urllib.parse.urlencode(paramsPayload)        
        
        
        headers = {'x-forwarded-for': userIp}
        # logEntryFunc2("REQUEST_1", moduleName, funcName, callingFuncName, fyId, omsTokenId, aesKeyForEncryption, paramsForEncryption, urlPath, paramsPayloadJson, fyId=fyId)
        #response = requests.post(urlPath, data=paramsPayloadJson,timeout = API_OMS_REQ_TIMEOUT, headers=headers) #Forward User IP-20200710-Khyati
        
        http_pool = urllib3.PoolManager()
        http_obj = http_pool
        response = http_obj.request("POST", url=urlPath, body=paramsPayloadJson, timeout=API_OMS_REQ_TIMEOUT, headers=headers)     
        
        
        if int(time.time()) - start >= 2:
            logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, "Response delay",urlPath,int(time.time()) - start, fyId=fyId)
        # if response.status_code != 200:
        if response.status != 200:
            logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, urlPath, response.status_code, response.content, fyId=fyId)
            return [ERROR_C_1,ERROR_C_OMS_URL_STATUS_CODE,ERROR_M_COULD_NOT_CONNECT_TRY_AGAIN]
        # return [SUCCESS_C_1,response.content,""]
        return [SUCCESS_C_1,response.data,""]


    # except requests.ConnectionError as e:
    #     logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, err_msg=e, code=ERROR_C_OMS_URL_CONNECTION, fyId=fyId)
    #     return [ERROR_C_1, ERROR_C_OMS_URL_CONNECTION, ERROR_M_COULD_NOT_CONNECT_TRY_AGAIN]
    # except requests.Timeout as e:
    #     logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, err_msg=e, code=ERROR_C_OMS_URL_TIMEOUT, fyId=fyId)
    #     return [ERROR_C_1, ERROR_C_OMS_URL_TIMEOUT, ERROR_M_COULD_NOT_CONNECT_TRY_AGAIN]
    # except requests.HTTPError as e:
    #     logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, err_msg=e, code=ERROR_C_OMS_URL_HTTP, fyId=fyId)
    #     return [ERROR_C_1, ERROR_C_OMS_URL_HTTP, ERROR_M_COULD_NOT_CONNECT_TRY_AGAIN]
    
    except Exception as e:
        logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, err_msg=e, code=ERROR_C_UNKNOWN, fyId=fyId)
        return [ERROR_C_1, ERROR_C_UNKNOWN, ""]


def INTERNAL_encryptInAes(message,keyInBase64,ivBlockSize=16,callingFuncName=""):
    """
    This function will create an AES object with the given key and then encrypt the message with the new AES object
        :param message: The string that is to be encrypted with the AES object
        :param key: The key/passphrase which is to be used at the time of creation of the AES object. In base64 format
        :param ivBlockSize: This is the length of the string that is to be created as an IV for AES encryption
        :param callingFuncName: This is used only for logging purpose

        :return: Error => [ERROR_C_1,erroCode,""]
                 Success => [SUCCESS_C_1,[encryptedString,ivUsedForEncryption],""]
                             Encrypted string and ivUsedForEncryption will be base64 encoded
    """
    funcName = "INTERNAL_encryptInAes"
    try:
        # Decode the key in base64 format
        key = base64.b64decode(keyInBase64)
        # Create a new ivString which will be used for encrypting the data in AES
        funcRet = INTERNAL_createRandomIv(lengthOfIv=ivBlockSize,callingFuncName=callingFuncName)
        if funcRet[0] == ERROR_C_1:
            return funcRet
        newIv = funcRet[1] # The ivString is in UTF-8 format

        # Pad the string before AES encryption
        paddedStringFuncRet = INTERNAL_aesPadding(message,ivBlockSize,callingFuncName)
        if paddedStringFuncRet[0] == ERROR_C_1:
            return paddedStringFuncRet
        paddedString = paddedStringFuncRet[1].encode('utf-8')

        # Create an AES key object using the key/passphrase provided and the newIv generated above
        # aes = AES.new(key, AES.MODE_CBC,newIv)
        # encrypted = aes.encrypt(paddedString)
        backend = default_backend()
        cipher = Cipher(algorithms.AES(key), modes.CBC(newIv), backend=backend)
        encryptor = cipher.encryptor()
        encrypted = encryptor.update(paddedString) + encryptor.finalize()

        # Encode both the return values in base64
        encryptedBase64 = base64.b64encode(encrypted)
        newIvToBeReturned = base64.b64encode(newIv)

        return [SUCCESS_C_1,[encryptedBase64,newIvToBeReturned],""]
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, e, ERROR_C_UNKNOWN,"Line Number: %s"%str(exc_tb.tb_lineno), message,keyInBase64)
        return [ERROR_C_1, ERROR_C_UNKNOWN, ""]


def INTERNAL_createRandomIv(lengthOfIv=16,callingFuncName=""):
    """
    This function will create a random string of lowercase letters a-z.
        :param lengthOfIv: The length of the random string that you want to create
        :return: Random string of the desired length returned in UTF-8 format
                Success => [SUCCESS_C_1,"ivString",""]
                Error => [ERROR_C_1, errorCode, "error message"]
    """
    funcName = "INTERNAL_createRandomIv"
    try:
        randomIv = ""
        choiceOfCharacters = string.ascii_lowercase

        for i in range(0,lengthOfIv):
            randomChar = random.choice(choiceOfCharacters)
            randomIv += randomChar

        return [SUCCESS_C_1,randomIv.encode("utf-8"),""]
    except Exception as e:
        logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, e, ERROR_C_UNKNOWN)
        return [ERROR_C_1, ERROR_C_UNKNOWN, ""]


def INTERNAL_aesPadding(stringToBePadded,blockSize=16,callingFuncName=""):
    """
    This function will pad a given string based on the blockSize. This is used for PKCS padding
        The lambda format of the function: aesPadding = lambda s: s + (16 - len(s) % 16) * chr(16 - len(s) % 16)
        :param stringToBePadded: The string that needs to be padded
        :param blockSize: This should be in multiple of 8
        :param callingFuncName: The function that is calling this function. This will be used for logs

        :return: Success => [SUCCESS_C_1,"padded string",""]
                Error => [ERROR_C_1,erroCode,"error message"]
    """
    funcName = "INTERNAL_aesPadding"
    try:
        paddedString = stringToBePadded + (blockSize - len(stringToBePadded) % blockSize) * chr(blockSize - len(stringToBePadded) % blockSize)
        return [SUCCESS_C_1,paddedString,""]
    except Exception as e:
        logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName,
                      callingFuncName, e, ERROR_C_UNKNOWN, stringToBePadded)
        return [ERROR_C_1, ERROR_C_UNKNOWN, ""]


def INTERNAL_decryptOmsResponse(omsResponseJsonString,aesKeyForDecryption,callingFuncName=""):
    """
    This function decrypt the response received from the oms
        :param callingFuncName: The function that is calling this function
        :param omsResponseJsonString: The string response received from the oms
        :param aesKeyForDecryption: This is the aesKey which will be used for decryption

        :return: Success => [SUCCESS_C_1,{}/[],""]
                 Error   => [ERROR_C_1,errorCode,errorMessage]
    """
    funcName = "INTERNAL_decryptOmsResponse"
    try:
        omsResponseDict = json.loads(omsResponseJsonString)
        # If oms status is error
        if omsResponseDict[API_OMS_K_STATUS_1] == API_OMS_V_ERROR_1:
            return [ERROR_C_OMS_1,omsResponseDict,""]
        # If the status is not an error (It is assumed to be success)
        ivStringRecv = omsResponseDict[API_OMS_K_IV_STRING]
        encryptedDataRecv = omsResponseDict[API_OMS_K_DATA_1]

        # Decrypt the data with AES Key and new ivString
        aesDecryptFuncRet = INTERNAL_decryptInAes(encryptedDataRecv, aesKeyForDecryption, ivStringRecv,
                                                  callingFuncName=callingFuncName)
        if aesDecryptFuncRet[0] == ERROR_C_1:
            return aesDecryptFuncRet

        # If decryption was successful, return the decrypted data
        decryptedOmsResponse = json.loads(aesDecryptFuncRet[1])
        return [SUCCESS_C_1,decryptedOmsResponse,""]

    except Exception as e:
        logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName,
                      callingFuncName, e, ERROR_C_UNKNOWN, omsResponseJsonString, aesKeyForDecryption)
        return [ERROR_C_1, ERROR_C_UNKNOWN, ""]


def INTERNAL_decryptInAes(encryptedMessageInBase64,keyInBase64,ivStringInBase64,callingFuncName=""):
    """
    This function will create an AES object with the given key and then decrypt the message with the new AES object
        :param message: The string that is to be decrypted with the AES object. This is in base64 format
        :param key: The key/passphrase which is to be used at the time of creation of the AES object. In base64 format
        :param ivStringInBase64: The ivstring that is to be used for decryption. In base64 format
        :param callingFuncName: This is used only for logging purpose

        :return: Error => [ERROR_C_1,erroCode,""]
                 Success => [SUCCESS_C_1,decryptedString,""]
    """
    funcName = "INTERNAL_decryptInAes"
    try:
        # Decode the input strings in base64
        key = base64.b64decode(keyInBase64)
        ivString = base64.b64decode(ivStringInBase64)
        encryptedMessage = base64.b64decode(encryptedMessageInBase64)

        # Create a AES Object with the key and ivString
        # aes = AES.new(key,AES.MODE_CBC,ivString)
        # decryptedMessage = aes.decrypt(encryptedMessage)
        backend = default_backend()
        cipher = Cipher(algorithms.AES(key), modes.CBC(ivString), backend=backend)
        decryptor = cipher.decryptor()
        decryptedMessage = decryptor.update(encryptedMessage) + decryptor.finalize()

        # Unpad the decrypted message
        unpadFuncRet = INTERNAL_aesUnpadding(decryptedMessage,callingFuncName=callingFuncName)
        if unpadFuncRet[0] == ERROR_C_1:
            logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, "INTERNAL_aesUnpadding", unpadFuncRet, decryptedMessage, type(decryptedMessage))
            return unpadFuncRet
        unpaddedDecryptedMessage = unpadFuncRet[1]

        return [SUCCESS_C_1,unpaddedDecryptedMessage,""]
    except Exception as e:
        logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, e, ERROR_C_UNKNOWN, encryptedMessageInBase64, keyInBase64)
        return [ERROR_C_1, ERROR_C_UNKNOWN, ""]


def INTERNAL_aesUnpadding(stringToBeUnpadded,callingFuncName=""):
    """
    This function will unpad a given string. This is used for PKCS padding
        The lambda format of the function: aesUnpadding = lambda s : s[0:-ord(s[-1])]
        :param stringToBeUnpadded: The string that is already padded
        :param callingFuncName: The function that is calling this function. This will be used for logs

        :return: Success => [SUCCESS_C_1,"padded string",""]
                Error => [ERROR_C_1,erroCode,"error message"]
    """
    funcName = "INTERNAL_aesUnpadding"
    try:
        try:
            stringToBeUnpadded = stringToBeUnpadded.decode("utf-8")
        except AttributeError:
            logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, "AttributeError", stringToBeUnpadded, type(stringToBeUnpadded))
        unpaddedString = stringToBeUnpadded[0:-ord(stringToBeUnpadded[-1])]
        return [SUCCESS_C_1,unpaddedString,""]
    except Exception as e:
        logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, e, ERROR_C_UNKNOWN, stringToBeUnpadded, type(stringToBeUnpadded))
        return [ERROR_C_1, ERROR_C_UNKNOWN, ""]


def INTERNAL_readOmsDecryptedResponse(decryptedOmsResponse,tokenHash,paramsForEncryption,urlPathForRequest, fyId= "",
                                  localMemory=None,returnReadOmsStatus=True,callingFuncName="",orderPlacement=False,userIp=""):
    """
    This function will read the decrypted oms response. Check if user validation fail error. Send another request if required
        :param callingFuncName: The function that is calling this function
        :param decryptedOmsResponse: The decrypted response from the oms.
        :param tokenHash: This is the user"s tokenHash which will be used to send the request again if required
        :param paramsForEncryption: This is the paramsDict which needs to be encrypted and sent again if required
        :param urlPathForRequest: This is the path which the request needs to be sent again if required
        :param returnReadOmsStatus: If this is True then in case of dictionary response, we will return INTERNAL_rs_readStatus()
                                    If this is False, then we will return the decryptedOmsResponse
        :param orderPlacement : If this is True, then we will try to search for the order number in the message
                                If this is False, then we will not search for the order number in the message

        :return: Success => [SUCCESS_C_1,{}/[]/code,""]
                 Error   => [ERROR_C_1,errorCode,errorMessage]
    """
    funcName = "INTERNAL_readOmsDecryptedResponse"

    try:
        # Check if the decrypted response is a dict
        if type(decryptedOmsResponse) == dict:
            # If the oms status is error, we will read the error code
            if decryptedOmsResponse[API_OMS_K_STATUS_1] == API_OMS_V_ERROR_1:
                omsResponse = INTERNAL_rs_readStatus(callingFuncName, decryptedOmsResponse, orderPlacement=orderPlacement,fyId=fyId)
                # If the error was user authentication failed, then we will re-auth the user
                if omsResponse[1] == ERROR_C_OMS_AUTHFAIL:
                    logEntryFunc2("REQUEST_REAUTH_1", moduleName, funcName, callingFuncName, urlPathForRequest, paramsForEncryption, decryptedOmsResponse, fyId=fyId)
                    fyTokenList = INTERNAL_reAuth_checkStatus(tokenHash, localMemory=localMemory, callingFuncName=funcName, userIp=userIp)
                    if (fyTokenList[0] == ERROR_C_1) or (fyTokenList[0] == ERROR_C_OMS_1) :
                        return fyTokenList
                    fyId = fyTokenList[1][0]
                    omsTokenId = fyTokenList[1][1]
                    aesKey = fyTokenList[1][2]

                    # Update the paramdict with new omstokenid and send the request again with the new aesKey
                    paramsForEncryption[API_OMS_K_TOKEN_ID_2] = omsTokenId
                    paramsForEncryption[API_OMS_K_TOKEN_ID_3] = omsTokenId
                    # Send the request again to the OMS with new OMS Token and aesKey
                    sendReqFuncRet = INTERNAL_createAndSendOmsRequest(fyId, omsTokenId, aesKey,paramsForEncryption,urlPathForRequest,callingFuncName=funcName, userIp=userIp)
                    if sendReqFuncRet[0] == ERROR_C_1:
                        return sendReqFuncRet
                    omsResponseJsonString = sendReqFuncRet[1]

                    # Send the omsResponseJsonString to read and decrypt function
                    readOmsResponseFuncRet = INTERNAL_decryptOmsResponse(omsResponseJsonString, aesKey, callingFuncName=funcName)
                    if readOmsResponseFuncRet[0] == ERROR_C_1:
                        return readOmsResponseFuncRet
                    decryptedOmsResponse = readOmsResponseFuncRet[1]

                # If any other error apart from user authentication failed, then return the error
                else:
                    return omsResponse

        # If the type of decryptedResponse is None or is an empty string, then return an error
        if (type(decryptedOmsResponse) == None) or (decryptedOmsResponse == ""):
            return [SUCCESS_C_1, decryptedOmsResponse, ""]

        # If the decryptedOmsResponse is a list, then return success
        elif type(decryptedOmsResponse) == list:
            return [SUCCESS_C_1, decryptedOmsResponse, ""]

        # If the decryptedOmsResponse is a dict, then we will check if the status is error
        elif type(decryptedOmsResponse) == dict:
            omsResponse = INTERNAL_rs_readStatus(callingFuncName, decryptedOmsResponse, fyId=fyId)

            # If the returnReadOmsStatus == True, then the calling function wants only the return of INTERNAL_rs_readStatus
            if returnReadOmsStatus == True:
                return omsResponse

            # In this case, the calling function wants the decryptedOmsResponseDict
            else:
                # If the oms status is error, we will read the error code
                if decryptedOmsResponse[API_OMS_K_STATUS_1] == API_OMS_V_ERROR_1:
                    omsResponse = INTERNAL_rs_readStatus(callingFuncName, decryptedOmsResponse,fyId=fyId)
                    return omsResponse
                else:
                    return [SUCCESS_C_1,decryptedOmsResponse,""]

        # If any other object type then return unknownError
        else:
            logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, decryptedOmsResponse, err_msg="unknownType", code=ERROR_C_UNKNOWN, fyId=fyId)
            return [ERROR_C_1,decryptedOmsResponse,""]

    except Exception as e:
        logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, decryptedOmsResponse, err_msg=e, code=ERROR_C_UNKNOWN, fyId=fyId)
        return [ERROR_C_1, ERROR_C_UNKNOWN, ""]


def INTERNAL_rs_readStatus(functionName, responseDict, orderPlacement=False,fyId=""):
    """
        [FUNCTION]
        Reads the status message and error codes returned by Rupeeseed

        [PARAMS]
        functionname  : The function from which this function is being called
        responseDict   : This is the dict of the response received from OMS
                        This dict will have the following keys: status, message, code, errorcode
        orderPlacement : This should be set to True to get the orderId which is returned from the OMS

        [RETURN]      :
                Success => [Status,Code,"errorMessage","orderId"]
                Error   => [Status,Code,"errorMessage","orderId"]
    """
    funcName = "INTERNAL_rs_readStatus"
    try:
        # Read the status, errorCode and rwsCode
        rwsStatus = responseDict[API_OMS_K_STATUS_1]
        rwsErrorCode = responseDict[API_OMS_K_ERROR_CODE]
        try:
            rwsCode = responseDict[API_OMS_K_CODE_1]
        except Exception as e:
            rwsCode = ""
        rwsMessage = responseDict[API_OMS_K_MESSAGE_1]
        orderIdString = ""
        if orderPlacement == True:
            orderIdString = INTERNAL_findOrderNumberInMessage(rwsMessage,functionName)

        # Log all the returns that we get from Rupeeseed into a seperate file
        logEntryFunc2(LOG_OMS_RESPONSE_1, moduleName, funcName,functionName, rwsStatus, rwsErrorCode,
                      rwsCode, rwsMessage,fyId=fyId)

        # If rwsStatus is an error
        if rwsStatus == API_OMS_V_ERROR_1:
            if rwsErrorCode == "RS-0000":

                if rwsCode == "AUT-001":
                    # User already unlocked
                    if rwsMessage == "User Already unlocked !!!":
                        return [ERROR_C_OMS_1, ERROR_C_OMS_STATUS_ALREADY_UNLOCKED, rwsMessage, orderIdString]

                    # If maximum number of attemps have been exceeded
                    elif rwsMessage == "Maximum number of attempts exceeded, please contact Helpdesk":
                        return [ERROR_C_OMS_1, ERROR_C_OMS_STATUS_MAX_ATTEMPTS, rwsMessage, orderIdString]

                    # If the request that has been sent to the oms is invalid
                    elif rwsMessage == "Invalid Request !!!":
                        return [ERROR_C_OMS_1,ERROR_C_OMS_INV_REQUEST,rwsMessage, orderIdString]

                    else:
                        return [ERROR_C_OMS_1,ERROR_C_OMS_UNKNOWN,rwsMessage, orderIdString]

                # If client does not exist
                elif rwsCode == "AUT-003":
                    return [ERROR_C_OMS_1, ERROR_C_OMS_INV_FYERSID_2, rwsMessage, orderIdString]

                # If user id is locked.
                elif (rwsCode == "AUT-004") or (rwsCode == "AUT-005") :
                    return [ERROR_C_OMS_1, ERROR_C_OMS_STATUS_LOCKED, rwsMessage, orderIdString]

                # If invalid password
                elif rwsCode == "AUT-006":
                    return [ERROR_C_OMS_1, ERROR_C_OMS_INV_PWD, rwsMessage, orderIdString]

                # If invalid PAN/DOB
                elif rwsCode == "AUT-007":
                    return [ERROR_C_OMS_1, ERROR_C_OMS_INV_PWD2, rwsMessage, orderIdString]

                # Client is not subscribed
                elif rwsCode == "AUT-017":
                    return [ERROR_C_OMS_1,ERROR_C_OMS_STATUS_NOT_SUBSCRIBED,rwsMessage, orderIdString]

                # Client id does not exist
                elif rwsCode == "AUT-023":
                    return [ERROR_C_OMS_1,ERROR_C_OMS_INV_FYERSID_2,rwsMessage, orderIdString]

                else:
                    # If none of the rwsCodes are known, then try to see if the error message is known
                    if rwsMessage.lower() == "invalid request !!!":
                        return [ERROR_C_OMS_1, ERROR_C_OMS_INV_REQUEST, rwsMessage, orderIdString]

                    # If none of the messages are also known, then return unknown error with rwsMessage
                    return [ERROR_C_OMS_1,ERROR_C_UNKNOWN,rwsMessage, orderIdString]

            elif rwsErrorCode == "RS-0002":

                # When the User Authentication has failed.
                if rwsCode == "":
                    return [ERROR_C_OMS_1, ERROR_C_OMS_AUTHFAIL, rwsMessage, orderIdString]

                # One of the mandatory fields are missing
                if rwsCode == "AUT-003":
                    return [ERROR_C_OMS_1, ERROR_C_OMS_INV_MANDATORY_MISSING, rwsMessage, orderIdString]

            elif rwsErrorCode == "RS-0003":

                # If User disabled
                if rwsCode == "AUT-008":
                    return [ERROR_C_OMS_1, ERROR_C_OMS_STATUS_DISABLED, rwsMessage, orderIdString]

                # If User suspended
                elif rwsCode == "AUT-009":
                    return [ERROR_C_OMS_1, ERROR_C_OMS_STATUS_SUSPENDED, rwsMessage, orderIdString]

            elif rwsErrorCode == "RS-0004":

                # When the User Authentication has failed.
                if rwsCode == "":
                    return [ERROR_C_OMS_1, ERROR_C_OMS_AUTHFAIL, rwsMessage, orderIdString]
                
                # Invalid dob
                if rwsCode == "AUT-005":
                    return [ERROR_C_OMS_1, ERROR_C_OMS_INV_DOB, rwsMessage, orderIdString]

            elif rwsErrorCode == "RS-0005":

                # Invalid PAN
                if rwsCode == "AUT-006":
                    return [ERROR_C_OMS_1, ERROR_C_OMS_INV_PAN, rwsMessage, orderIdString]

                # If User password has been reset and needs to be changed
                if rwsCode == "AUT-011":
                    return [ERROR_C_OMS_1, ERROR_C_OMS_STATUS_PWD_EXPIRED, rwsMessage, orderIdString]

                # Client id does not exist
                if rwsCode == "AUT-023":
                    return [ERROR_C_OMS_1,ERROR_C_OMS_INV_FYERSID_2,rwsMessage, orderIdString]

            elif rwsErrorCode == "RS-0006":
                # If user is locked
                if rwsCode == "AUT-005":
                    return [ERROR_C_OMS_1, ERROR_C_OMS_STATUS_LOCKED, rwsMessage, orderIdString]

                # If User password has been reset and needs to be changed
                if rwsCode == "AUT-012":
                    return [ERROR_C_OMS_1, ERROR_C_OMS_STATUS_PWD_EXPIRED, rwsMessage, orderIdString]

            elif rwsErrorCode == "RS-0008":
                # If user is disabled
                if rwsCode == "AUT-008":
                    return [ERROR_C_OMS_1, ERROR_C_OMS_STATUS_DISABLED, rwsMessage, orderIdString]

            elif rwsErrorCode == "RS-0009":
                # If user is suspended
                if rwsCode == "AUT-009":
                    return [ERROR_C_OMS_1, ERROR_C_OMS_STATUS_SUSPENDED, rwsMessage, orderIdString]

            elif rwsErrorCode == "RS-00010":
                # User invalidated
                if rwsCode == "":
                    return [ERROR_C_OMS_1,ERROR_C_OMS_AUTHFAIL,rwsMessage, orderIdString]

                elif rwsMessage.lower() == "data not in correct format":
                    return [ERROR_C_OMS_1,ERROR_C_OMS_INV_REQUEST,rwsMessage, orderIdString]

            elif rwsErrorCode == "RS-0013":
                # Invalid password
                if rwsCode == "AUT-006":
                    return [ERROR_C_OMS_1, ERROR_C_OMS_INV_PWD, rwsMessage, orderIdString]

            elif rwsErrorCode == "RS-0014":
                # If User password has been reset and needs to be changed
                if rwsCode == "AUT-012":
                    return [ERROR_C_OMS_1, ERROR_C_OMS_STATUS_PWD_EXPIRED, rwsMessage, orderIdString]

            elif rwsErrorCode == "RS-0016":
                # If User password has been reset and needs to be changed
                if rwsCode == "AUT-011":
                    return [ERROR_C_OMS_1, ERROR_C_OMS_STATUS_PWD_EXPIRED, rwsMessage, orderIdString]

            elif rwsErrorCode == "RS-0034":
                # If market is offline
                return [ERROR_C_OMS_1, ERROR_C_OMS_MARKET_OFFLINE, rwsMessage, orderIdString]

            elif rwsErrorCode == "RS-0065":
                # Order placement failed
                return [ERROR_C_OMS_1, ERROR_C_OMS_ORDER_FAIL_1, rwsMessage, orderIdString]

            elif rwsErrorCode == "RS-0065":
                # Order placement failed
                return [ERROR_C_OMS_1, ERROR_C_OMS_ORDER_FAIL_1, rwsMessage, orderIdString]

            elif rwsErrorCode == "RS-0066":
                # Client s limit is not available in the OMS limit table
                return [ERROR_C_OMS_1,ERROR_C_OMS_ORDER_FAIL_LIMIT_NOT_AVAILABLE,rwsMessage, orderIdString]

            elif rwsErrorCode == "RS-0072":
                return [ERROR_C_OMS_1, ERROR_C_OMS_ORDER_FAIL_INV_FYID_DATA, rwsMessage, orderIdString]

            elif rwsErrorCode == "RS-0075":
                # Invalid quantity
                return [ERROR_C_OMS_1, ERROR_C_OMS_ORDER_FAIL_INV_QTY_NOT_NUM, rwsMessage, orderIdString]

            elif rwsErrorCode == "RS-0077":
                # Invalid trigger price
                return [ERROR_C_OMS_1, ERROR_C_OMS_ORDER_FAIL_INV_TRG_PRICE, rwsMessage, orderIdString]

            elif rwsErrorCode == "RS-0078":
                # Invalid disclosed qty
                return [ERROR_C_OMS_1, ERROR_C_OMS_ORDER_FAIL_INV_DISC_QTY, rwsMessage, orderIdString]

            elif rwsErrorCode == "RS-0082":
                # Invalid exchange given at the time of order entry
                return [ERROR_C_OMS_1, ERROR_C_OMS_ORDER_FAIL_INV_EXCH, rwsMessage, orderIdString]

            elif rwsErrorCode == "RS-0083":
                # Invalid transaction type (buy/sell) given at the time of order entry
                return [ERROR_C_OMS_1, ERROR_C_OMS_ORDER_FAIL_INV_EXCH, rwsMessage, orderIdString]

            elif rwsErrorCode == "RS-0084":
                # Invalid instrument type given at the time of order entry
                return [ERROR_C_OMS_1, ERROR_C_OMS_ORDER_FAIL_INV_INST_TYPE, rwsMessage, orderIdString]

            elif rwsErrorCode == "RS-0085":
                # Invalid instrument type given at the time of order entry
                return [ERROR_C_OMS_1, ERROR_C_OMS_ORDER_FAIL_INV_INST_TYPE, rwsMessage, orderIdString]

            # EDIS
            elif rwsErrorCode == "RS-0088":
                return [ERROR_C_OMS_1, ERROR_C_EDIS_INV_TXN_ID, rwsMessage, orderIdString]

            # Pragya 20200117
            elif rwsErrorCode == "RS-0089":
                # Password entered as same as previous 5 passwords
                return [ERROR_C_OMS_1, ERROR_C_OMS_PASSWD_SAME_PREV_5, rwsMessage, orderIdString]

            elif rwsErrorCode == "RS-0100":
                # Order modification
                return [ERROR_C_OMS_1, ERROR_C_OMS_ORDER_MODIFY_FAILED, rwsMessage, orderIdString]

            elif rwsErrorCode == "0034":
                # Modification failed
                return [ERROR_C_OMS_1, ERROR_C_OMS_ORDER_MODIFY_FAILED, rwsMessage, orderIdString]

            # New password should contain alpha numeric
            elif rwsErrorCode == "4008":
                return [ERROR_C_OMS_1, ERROR_C_OMS_INV_ALPHANUM_REQ, rwsMessage, orderIdString]

            # New password and confirm new password does not match
            elif rwsErrorCode == "4006":
                return [ERROR_C_OMS_1, ERROR_C_OMS_INV_PWD_NOT_MATCHING, rwsMessage, orderIdString]

            # New password is too short
            elif rwsErrorCode == "4007":
                return [ERROR_C_OMS_1, ERROR_C_OMS_INV_PWD_TOO_SHORT, rwsMessage, orderIdString]

            # Old password provided is incorrect
            elif rwsErrorCode == "4004":
                return [ERROR_C_OMS_1, ERROR_C_OMS_INV_EXIST_PWD, rwsMessage, orderIdString]

            # Fyers Id is either invalid, disabled or suspended
            elif rwsErrorCode == "4010":
                return [ERROR_C_OMS_1, ERROR_C_OMS_INV_FYERSID_2, rwsMessage, orderIdString]

            # New password is same as old password
            elif rwsErrorCode == "4009":
                return [ERROR_C_OMS_1, ERROR_C_OMS_INV_SAME_AS_EXIST_PWD, rwsMessage, orderIdString]

            # Not connected to exchange
            elif rwsErrorCode == "110001":
                return [ERROR_C_OMS_1, ERROR_C_OMS_ORDER_NOT_CONNECTED, rwsMessage, orderIdString]
            else:
                return [ERROR_C_OMS_1, ERROR_C_OMS_UNKNOWN, rwsMessage, orderIdString]

        # If rwsStatus is a success
        elif rwsStatus.lower() == API_OMS_V_SUCCESS_1:

            if rwsErrorCode == "RS-0006":

                if rwsCode == "AUT-007":

                    if "password reset successfully" in rwsMessage.lower():
                        return [SUCCESS_C_OMS, SUCCESS_C_OMS_PWD_RESET, rwsMessage, orderIdString]

                    elif "user unlocked successfully" in rwsMessage.lower():
                        return [SUCCESS_C_OMS, SUCCESS_C_OMS_UNLOCK, rwsMessage, orderIdString]

            # Payout request was successful
            elif rwsErrorCode == "RS-00025":
                return [SUCCESS_C_OMS, SUCCESS_C_OMS_FT_OUTWARD, rwsMessage, orderIdString]

            # Cover order placement
            elif rwsErrorCode == "RS-0036":
                orderIdString = "".join(filter(str.isdigit, str(rwsMessage)))
                if orderIdString != "":
                    orderIdString = str(int(orderIdString))
                return [SUCCESS_C_OMS, SUCCESS_C_OMS_ORDER_PLACE, rwsMessage, orderIdString]

            # If password change was successful
            elif rwsErrorCode == "RS-00038":
                return [SUCCESS_C_OMS, SUCCESS_C_OMS_PWD_CHANGE, rwsMessage, orderIdString]

            # Order placement and watchlist successfully created
            elif rwsErrorCode == "RS-0067":

                if "order submitted" in rwsMessage.lower():
                    orderIdString = "".join(filter(str.isdigit, str(rwsMessage)))
                    if orderIdString != "":
                        orderIdString = str(int(orderIdString))
                    return [SUCCESS_C_OMS, SUCCESS_C_OMS_ORDER_PLACE, rwsMessage,orderIdString]

            elif rwsErrorCode == "RS-0075":
                # Password reset was successful
                return [SUCCESS_C_OMS, SUCCESS_C_OMS_PWD_RESET, rwsMessage, orderIdString]

            elif rwsErrorCode == "RS-0077":
                # Successfully signed out
                return [SUCCESS_C_OMS, SUCCESS_C_OMS_LOGOUT, rwsMessage, orderIdString]

            elif rwsErrorCode == "RS-00095":
                # Order cancellation
                return [SUCCESS_C_OMS,SUCCESS_C_OMS_ORDER_CANCEL,rwsMessage, orderIdString]

            elif rwsErrorCode == "RS-0100":
                # If payout request was successful
                if rwsCode == "":
                    return [SUCCESS_C_OMS, SUCCESS_C_OMS_FT_OUTWARD, rwsMessage, orderIdString]

            elif rwsErrorCode == "RS-0102":
                # Order modification
                return [SUCCESS_C_OMS,SUCCESS_C_OMS_ORDER_MODIFY,rwsMessage, orderIdString]

            elif rwsErrorCode == "RS-0150":

                if "user signout successfully" in rwsMessage.lower():
                    return [SUCCESS_C_OMS,SUCCESS_C_OMS_LOGOUT,"", orderIdString]

            # TODO : Increase the number of success responses
            return [SUCCESS_C_OMS, rwsErrorCode, rwsMessage, orderIdString]

        return [ERROR_C_OMS_1, ERROR_C_OMS_UNKNOWN, rwsMessage, orderIdString]
    except Exception as e:
        logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName,functionName, err_msg=e, code=ERROR_C_UNKNOWN, fyId=fyId)
        return [ERROR_C_1, ERROR_C_UNKNOWN, ""]


def INTERNAL_findOrderNumberInMessage(message, callingFuncName=""):
    """
    This function will find and return the number from the string
        :param message: This is the message which contains the order number
        :param callingFuncName: This is the function that is calling this function
    :return:
        Success => "...." A string of the order number
        Error   => "" If there is no order number of if there was an error, it will return an empty string
    """
    funcName = "INTERNAL_findOrderNumberInMessage"
    orderId = ""
    try:
        numbersList = message.split(":")
        if len(numbersList) > 2:
            orderId = numbersList[1]
        return orderId
    except Exception as e:
        logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName,callingFuncName, e, ERROR_C_UNKNOWN, message)
        return orderId


def INTERNAL_reAuth_checkStatus(tokenHash,db=None,cursor=None,localMemory=None,inputFyId=None, callingFuncName="",userIp=""):
    """
    [FUNCTION]
        Will re authenticate and then check the status
    [PARAMS]
        tokenHash    : This is a hash of (fyId + AppId)
    [RETURN]
            Success : [SUCCESS_C_1,OMSID,OMSTOKEN]
            Failure : [ERROR_C_1,errorCode,callingFuncName]
    """
    funcName = "INTERNAL_reAuth_checkStatus"
    try:
        if localMemory == None:
            localMemory = connectRedis(callingFuncName=callingFuncName)

        fyTokenList = INTERNAL_fy_reauth_withID(tokenHash=tokenHash,db=db,cursor=cursor,localMemory=localMemory,inputFyId=inputFyId,callingFuncName=funcName)
        return fyTokenList

    except Exception as e:
        logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName,callingFuncName, tokenHash, err_msg=e, code=ERROR_C_UNKNOWN)
        return [ERROR_C_1, ERROR_C_UNKNOWN, callingFuncName]


def changeToRSFormat(funcType = "", **kwargs):
    funcName = "changeToRSFormat"
    try:
        symType = prodList = ordType = transType = ""
        returnDict = {}
        # Rupeeseed has different codes for each segment
        if API_K_SYM_SEGMENT in kwargs:
            if kwargs[API_K_SYM_SEGMENT] == str(SYM_SEGMENT_CM) or kwargs[API_K_SYM_SEGMENT] == API_OMS_V_SEG_CM_1:
                if funcType == "convertPos":
                    symType = API_OMS_V_SEG_CM_1
                else:
                    symType = API_OMS_V_SEG_CM_2
            elif kwargs[API_K_SYM_SEGMENT] == str(SYM_SEGMENT_FO) or kwargs[API_K_SYM_SEGMENT] == API_OMS_V_SEG_FO_1:
                if funcType == "convertPos":
                    symType = API_OMS_V_SEG_FO_1
                else:
                    symType = API_OMS_V_SEG_FO_2
            elif kwargs[API_K_SYM_SEGMENT] == str(SYM_SEGMENT_CD) or kwargs[API_K_SYM_SEGMENT] == API_OMS_V_SEG_CD_1:
                if kwargs[API_K_SYM_SEGMENT] == API_OMS_V_SEG_CD_1 and funcType in ["modify", "cancel", "modifyCO", "modifyBO", "exitBO"]:
                    symType = kwargs[API_K_SYM_SEGMENT]
                else:
                    symType = API_OMS_V_SEG_CD_1
            elif kwargs[API_K_SYM_SEGMENT] == str(SYM_SEGMENT_COM) or kwargs[API_K_SYM_SEGMENT] == API_OMS_V_SEG_COM_1:
                if kwargs[API_K_SYM_SEGMENT] == API_OMS_V_SEG_COM_1 and funcType in ["modify", "cancel", "modifyCO", "modifyBO", "exitBO"]:
                    symType = kwargs[API_K_SYM_SEGMENT]
                else:
                    symType = API_OMS_V_SEG_COM_1
            else:
                if funcType == "modify":
                    return [ERROR_C_1, ERROR_C_INV_INST_TYPE, ERROR_M_INV_INST_TYPE]
                return [ERROR_C_1, ERROR_C_INV_SEGMENT, ERROR_M_INV_SEGMENT]
            returnDict[API_K_SYM_SEGMENT] = symType


        # Rupeeseed has different codes for each product type
        if API_K_ORDER_PRODUCT in kwargs:
            if (kwargs[API_K_ORDER_PRODUCT] == API_OMS_V_ORDER_PROD_CNC_2) or (kwargs[API_K_ORDER_PRODUCT] == API_OMS_V_ORDER_PROD_CNC_1):
                prodList = API_OMS_V_ORDER_PROD_CNC_1
            elif (kwargs[API_K_ORDER_PRODUCT] == API_OMS_V_ORDER_PROD_MARGIN_2) or (kwargs[API_K_ORDER_PRODUCT] == API_OMS_V_ORDER_PROD_MARGIN_1):
                prodList = API_OMS_V_ORDER_PROD_MARGIN_1
            elif (kwargs[API_K_ORDER_PRODUCT] == API_OMS_V_ORDER_PROD_INTRADAY_2) or (kwargs[API_K_ORDER_PRODUCT] == API_OMS_V_ORDER_PROD_INTRADAY_1):
                prodList = API_OMS_V_ORDER_PROD_INTRADAY_1
            elif (kwargs[API_K_ORDER_PRODUCT] == API_OMS_V_ORDER_PROD_CO_2) or (kwargs[API_K_ORDER_PRODUCT] == API_OMS_V_ORDER_PROD_CO_1):
                prodList = API_OMS_V_ORDER_PROD_CO_1
            elif (kwargs[API_K_ORDER_PRODUCT] == API_OMS_V_ORDER_PROD_BO_2) or (kwargs[API_K_ORDER_PRODUCT] == API_OMS_V_ORDER_PROD_BO_1):
                prodList = API_OMS_V_ORDER_PROD_BO_1
            else:
                return [ERROR_C_1, ERROR_C_INV_ORDER_PRODUCT, ERROR_M_INV_ORDER_PRODUCT]
            returnDict[API_K_ORDER_PRODUCT] = prodList

        # Rupeeseed has different codes for order type like LMT/MKT
        if API_K_ORDER_TYPE_RS in kwargs:
            if kwargs[API_K_ORDER_TYPE_RS] == API_V_ORDER_TYPE_MKT_1:
                ordType =API_V_ORDER_TYPE_MKT_2
                if funcType == "BO":
                    returnDict[API_K_DATA_PRICE_1] = 0
                    returnDict[API_K_TRIG_PRICE] = 0

            elif kwargs[API_K_ORDER_TYPE_RS] == API_V_ORDER_TYPE_LMT_1:
                ordType = API_V_ORDER_TYPE_LMT_2
                if funcType == "BO":
                    if API_K_DATA_PRICE_1 in returnDict:
                        del returnDict[API_K_DATA_PRICE_1]
                    returnDict[API_K_TRIG_PRICE] = 0

            elif kwargs[API_K_ORDER_TYPE_RS] == API_V_ORDER_TYPE_STP_MKT:
                if funcType == "BO":
                    ordType = API_V_ORDER_TYPE_MKT_2
                    if API_K_TRIG_PRICE in returnDict:
                        del returnDict[API_K_TRIG_PRICE]
                    returnDict[API_K_DATA_PRICE_1] = 0
                else:
                    # If order type is stop then we need to check price. If price is 0, then order is market and if price != 0 then order type is limit
                    if kwargs[API_K_DATA_PRICE_1] == 0:
                        ordType = API_V_ORDER_TYPE_MKT_2
                    else:
                        ordType = API_V_ORDER_TYPE_LMT_2

            elif kwargs[API_K_ORDER_TYPE_RS] == API_V_ORDER_TYPE_STP_LMT:
                if funcType == "modify":
                    # If order type is stoplimit then we need to check price. If price is 0, then order is market and if price != then order type is limit
                    if kwargs[API_K_DATA_PRICE_1] == 0:
                        ordType = API_V_ORDER_TYPE_MKT_2
                    else:
                        ordType = API_V_ORDER_TYPE_LMT_2
                elif funcType == "marginCalc":
                        ordType = API_V_ORDER_TYPE_LMT_2
                else:
                    # If order type is stoplimit then we need to check price. If price is 0, stopLimit order is invalid
                    if kwargs[API_K_DATA_PRICE_1] == 0:
                        return [ERROR_C_1, ERROR_C_INV_ORDER_STOP_LMT_PRICE, ERROR_M_INV_ORDER_STP_LMT_PRICE]
                    ordType = API_V_ORDER_TYPE_LMT_2
            elif (kwargs[API_K_ORDER_TYPE_RS] == API_OMS_V_ORDER_TYPE_LMT_2): ## FOR cancel order
                ordType = API_OMS_V_ORDER_TYPE_LMT_1
            elif (kwargs[API_K_ORDER_TYPE_RS] == API_OMS_V_ORDER_TYPE_MKT_2):
                ordType = API_OMS_V_ORDER_TYPE_MKT_1
            elif kwargs[API_K_ORDER_TYPE_RS] == "SL-M":
                if funcType != "cancel":
                    ordType = API_OMS_V_ORDER_TYPE_MKT_1
                else:
                    ordType = kwargs[API_K_ORDER_TYPE_RS]
            elif kwargs[API_K_ORDER_TYPE_RS] == "SL" or kwargs[API_K_ORDER_TYPE_RS] == "SL-L":
                if funcType != "cancel":
                    ordType = API_OMS_V_ORDER_TYPE_LMT_1
                else:
                    ordType = kwargs[API_K_ORDER_TYPE_RS]
            else:
                return [ERROR_C_1, ERROR_C_INV_ORDER_TYPE, ERROR_M_INV_ORDER_TYPE]
            returnDict[API_K_ORDER_TYPE_RS] = ordType

        # Rupeeseed has different codes for buy/sell like B/S
        if API_K_TRANS_TYPE in kwargs:

            if isinstance(kwargs[API_K_TRANS_TYPE], str) or isinstance(kwargs[API_K_TRANS_TYPE], str):
                if kwargs[API_K_TRANS_TYPE].upper() == API_OMS_V_ORDER_SIDE_BUY_2 or kwargs[API_K_TRANS_TYPE] == API_OMS_V_ORDER_SIDE_BUY_1:
                    transType = API_OMS_V_ORDER_SIDE_BUY_1
                elif kwargs[API_K_TRANS_TYPE].upper() == API_OMS_V_ORDER_SIDE_SELL_2 or kwargs[API_K_TRANS_TYPE] == API_OMS_V_ORDER_SIDE_SELL_1:
                    transType = API_OMS_V_ORDER_SIDE_SELL_1
            elif isinstance(kwargs[API_K_TRANS_TYPE], int):
                if kwargs[API_K_TRANS_TYPE] == API_V_ORDER_SIDE_BUY_1:
                    transType = API_OMS_V_ORDER_SIDE_BUY_1
                elif kwargs[API_K_TRANS_TYPE] == API_V_ORDER_SIDE_SELL_1:
                    transType = API_OMS_V_ORDER_SIDE_SELL_1
            else:
                return [ERROR_C_1, ERROR_C_INV_ORDER_SIDE, ERROR_M_INV_ORDER_SIDE]

            returnDict[API_K_TRANS_TYPE] = transType
        return [SUCCESS_C_1, returnDict, ""]
    except Exception as e:
        logEntryFunc2(LOG_STATUS_ERROR_1,moduleName,funcName,"",ERROR_C_UNKNOWN,e, funcType, kwargs)
        return [ERROR_C_1, ERROR_C_UNKNOWN, ""]


def main():
    pass  # Do testing here


if __name__ == "__main__":
    main()
