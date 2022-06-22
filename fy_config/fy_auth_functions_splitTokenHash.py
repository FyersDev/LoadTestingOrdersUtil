moduleName = "fy_auth_functions_splitTokenHash"
try:
    import sys
    import json

    from fy_base_defines import LOG_STATUS_ERROR_1, CACHE_T_4
    from fy_base_success_error_codes import ERROR_C_1, ERROR_C_INVALID_TOKEN_2, \
     ERROR_C_INVALID_TOKEN_3, SUCCESS_C_1, ERROR_C_DB_1, ERROR_C_INVALID_TOKEN_4, \
     ERROR_C_INVALID_TOKEN_5, ERROR_C_INVALID_TOKEN_6, ERROR_C_UNKNOWN
    from fy_base_success_error_messages import ERROR_M_INV_TOKEN_AUTH_FAIL
    from fy_connections_defines import FY_ENCRYPT_DB_AESKEY_1, TBL_OMS_AUTH_V2

    from fy_base_functions import logEntryFunc2
    from fy_connections import connectRedis, dbConnect
    from vagator_auth_check import INTERNAL_splitTokenHash

except Exception as e:
    print("ERR : %s : %s : %s" % (moduleName, "Could not import module", e))


def INTERNAL_verifyTokenHash(inputTokenHash, db=None, cursor=None, localMemory=None, callingFuncName="", **kwargs):
    """
        [FUNCTION]
            INTERNAL_verifyTokenHash : Verify whether the tokenHash exists in the db or not
            It the db and cursor are passed to the function there may be requirement tot write to DB.
            [PARAMS]
            tokenHash    :
            [RETURN]
                Success : [SUCCESS_C_1,[fyId,appId,randomKey],""]
                Failure : [ERROR_C_1,errorCode,errorMessage]
    """
    funcName = "INTERNAL_verifyTokenHash"
    try:
        if localMemory is None:
            localMemory = connectRedis(callingFuncName=callingFuncName)

        cacheFlag = 0
        if localMemory is not None:
            cacheFlag = 1

        if ("appId" in kwargs) and ("dbTokenHash" in kwargs):
            appId = kwargs["appId"]
            dbTokenHash = json.loads(kwargs["dbTokenHash"])
            try:
                tokenList = INTERNAL_splitTokenHash(dbTokenHash[appId],callingFuncName=callingFuncName)
                if tokenList[0] == ERROR_C_1:
                    return tokenList
                fyId, appId, token, inputTokenHash = tokenList[1]

            except KeyError:
                return [ERROR_C_1, ERROR_C_INVALID_TOKEN_2, ERROR_M_INV_TOKEN_AUTH_FAIL]

            except Exception as e:
                logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName,
                              e, ERROR_C_INVALID_TOKEN_3,inputTokenHash)
                return [ERROR_C_1, ERROR_C_INVALID_TOKEN_3, ERROR_M_INV_TOKEN_AUTH_FAIL]

        else:
            tokenList = INTERNAL_splitTokenHash(inputTokenHash,callingFuncName=callingFuncName)
            if tokenList[0] == ERROR_C_1:
                return tokenList
            fyId, appId, token, inputTokenHash = tokenList[1]

            if cacheFlag == 1:
                dbTokenHash = localMemory.get("tokenHash-%s-%s" % (fyId, appId))
                if dbTokenHash is not None and dbTokenHash == inputTokenHash:
                    # TODO: Token verification needs to be changed here
                    return [SUCCESS_C_1, tokenList[1], ""]

            if db is None or cursor is None:
                db, cursor = dbConnect(dbType=3, readOnly=1,callingFuncName=callingFuncName)
                if db is None or cursor is None:
                    return [ERROR_C_1, ERROR_C_DB_1, ERROR_M_INV_TOKEN_AUTH_FAIL]
            getTokenSql = """SELECT cast(AES_DECRYPT(TOKEN_HASH,'%s') as char) FROM `%s` WHERE FY_ID = '%s';""" % (FY_ENCRYPT_DB_AESKEY_1,TBL_OMS_AUTH_V2, fyId)
            cursor.execute(getTokenSql)
            sqlFetchAll = cursor.fetchall()

            if sqlFetchAll == ():
                # if db is not None and cursor is not None:
                    # Below function not used
                    # INTERNAL_incrementLoginFails(db, cursor, fyId,callingFuncName=callingFuncName)
                return [ERROR_C_1, ERROR_C_INVALID_TOKEN_4, ERROR_M_INV_TOKEN_AUTH_FAIL]
            else:
                ((dbTokenHash,),) = sqlFetchAll
                dbTokenHash = json.loads(dbTokenHash)

        if not str(appId) in dbTokenHash:
            # if db is not None and cursor is not None:
                # INTERNAL_incrementLoginFails(db, cursor, fyId,callingFuncName=callingFuncName)
            return [ERROR_C_1, ERROR_C_INVALID_TOKEN_5, ERROR_M_INV_TOKEN_AUTH_FAIL]

        if dbTokenHash[str(appId)] == inputTokenHash:
            if cacheFlag == 1:
                localMemory.set("tokenHash-%s-%s" % (fyId, appId), inputTokenHash, CACHE_T_4)
            return [SUCCESS_C_1, tokenList[1], ""]

        return [ERROR_C_1, ERROR_C_INVALID_TOKEN_6, ERROR_M_INV_TOKEN_AUTH_FAIL]

    except Exception as e:
        logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName,
                      e, ERROR_C_UNKNOWN, inputTokenHash)
        return [ERROR_C_1, ERROR_C_UNKNOWN, ERROR_M_INV_TOKEN_AUTH_FAIL] 