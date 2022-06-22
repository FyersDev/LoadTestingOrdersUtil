moduleName = "fy_trading_internal_functions_symbols_GET"
try:
    import sys
    import json

    from fy_base_defines import LOG_STATUS_ERROR_1, CACHE_T_2
    from fy_base_success_error_codes import ERROR_C_1, \
     ERROR_C_UNKNOWN, SUCCESS_C_1, ERROR_C_DB_1
    from fy_common_api_keys_values import API_K_LOT_SIZE, API_K_MIN_TICK_SIZE
    from fy_connections_defines import TBL_SYM_MASTER
    from fy_data_and_trade_defines import EXCHANGE_CODE_NSE, \
     EXCHANGE_CODE_BSE, SYM_SEGMENT_CM, SYM_SEGMENT_FO, SYM_SEGMENT_CD, \
     EXCHANGE_CODE_MCX, SYM_SEGMENT_COM, EXCHANGE_NAME_NSE, EXCHANGE_NAME_MCX_1, \
     EXCHANGE_NAME_BSE, CACHE_K_SYM_INFO_DICT_2, SYM_INSTTYPE_FUTIDX, \
     SYM_INSTTYPE_FUTIVX, SYM_INSTTYPE_FUTSTK, SYM_INSTTYPE_FUTCUR, SYM_INSTTYPE_FUTIRT, \
     SYM_INSTTYPE_FUTIRC, SYM_INSTTYPE_FUTCOM, SYM_INSTTYPE_OPTIDX, SYM_INSTTYPE_OPTSTK, \
     SYM_INSTTYPE_OPTCUR, SYM_INSTTYPE_FUTOPT

    from fy_connections import connectRedis, dbConnect
    from fy_base_functions import logEntryFunc2, INTERNAL_convertTimestampToDateString

except Exception as e:
    print("ERR : %s : %s : %s" % (moduleName, "Could not import module", e))
    sys.exit()


def INTERNAL_getAllSymInfo(exchange=0, callingFuncName=""):
    """
        [FUNCTION]
        [PARAMS]

        [RETURN]
            Success :   [SUCCESS_C_1,{..},errorMessage]
            Failure :   [ERROR_C_1,errorCode,errorMessage]
    """
    funcName = "INTERNAL_getAllSymInfo"
    try:
        localMemory = connectRedis(callingFuncName=callingFuncName)
        symInfoDictFromCache = localMemory.get("%s-%s%s" % (funcName, exchange, CACHE_K_SYM_INFO_DICT_2))
        if symInfoDictFromCache != None:
            # None
            return [SUCCESS_C_1, json.loads(symInfoDictFromCache), ""]

        # If it is not there in the cache, we will have to get the entire data from the db
        db, cursor = dbConnect(dbType=3, readOnly=1)
        if db == None or cursor == None:
            return [ERROR_C_1, ERROR_C_DB_1, ""]

        sqlQuery = """SELECT EX,EX_SYMBOL,MIN_LOT_SIZE,EXPIRY_DATE,TICK_SIZE,EX_SEGMENT,EX_INST_TYPE FROM `%s` WHERE TRADE_STATUS = 1 AND (EX_SEGMENT = %s OR EX_SEGMENT = %s OR EX_SEGMENT = %s OR EX_SEGMENT = %s) GROUP BY EX, EX_SYMBOL, EXPIRY_DATE, EX_INST_TYPE;""" % \
                   (TBL_SYM_MASTER, SYM_SEGMENT_CM, SYM_SEGMENT_FO, SYM_SEGMENT_CD, SYM_SEGMENT_COM)
        cursor.execute(sqlQuery)
        symInfoAll = cursor.fetchall()

        # Main dictionary which will be returned
        symInfoDict = {}
        for i in symInfoAll:
            # Check the exchange code and get the exchange name
            if i[0] == EXCHANGE_CODE_NSE:
                if i[5] == SYM_SEGMENT_CM:
                    exName = "%s_%s" %(EXCHANGE_NAME_NSE, "CM")
                else:
                    exName = EXCHANGE_NAME_NSE
            elif i[0] == EXCHANGE_CODE_MCX:
                exName = EXCHANGE_NAME_MCX_1
            elif i[0] == EXCHANGE_CODE_BSE:
                if i[5] == SYM_SEGMENT_CM:
                    exName = "%s_%s" %(EXCHANGE_NAME_BSE, "CM")
                else:
                    exName = EXCHANGE_NAME_BSE
            else:
                continue

            if i[6] in [SYM_INSTTYPE_FUTIDX, SYM_INSTTYPE_FUTIVX, SYM_INSTTYPE_FUTSTK, SYM_INSTTYPE_FUTCUR, SYM_INSTTYPE_FUTIRT, SYM_INSTTYPE_FUTIRC, SYM_INSTTYPE_FUTCOM]:
                inst_type = "FUT"
            elif i[6] in [SYM_INSTTYPE_OPTIDX, SYM_INSTTYPE_OPTSTK, SYM_INSTTYPE_OPTCUR, SYM_INSTTYPE_FUTOPT]:
                inst_type = "OPT"
            else:
                inst_type = "OTHER"

            # Within the main dict, we will create a dict for each exchange
            if not exName in symInfoDict:
                symInfoDict[exName] = {}

            # Add the capital market symbols into the dictionary
            if i[5] == SYM_SEGMENT_CM:
                symInfoDict[exName][i[1]] = {API_K_LOT_SIZE: i[2], API_K_MIN_TICK_SIZE: i[4]}
                continue

            # Converting the expiry timestamp into year and month
            try:
                expYearFuncRet = INTERNAL_convertTimestampToDateString(i[3], "%y", callingFuncName=callingFuncName)
                if expYearFuncRet[0] == ERROR_C_1:
                    logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, "Expiry year",
                                  expYearFuncRet[1], expYearFuncRet[2])
                    continue
                expYear = expYearFuncRet[1]
                expMonthFuncRet = INTERNAL_convertTimestampToDateString(i[3], "%b", callingFuncName=callingFuncName)
                if expMonthFuncRet[0] == ERROR_C_1:
                    logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, "Expiry month",
                                  expMonthFuncRet[1], expMonthFuncRet[2])
                    continue
                expMonth = expMonthFuncRet[1]
            except Exception as e:
                continue

            # Within the exchange dict, we will create seperate dict for each symbol
            if not i[1] in symInfoDict[exName]:
                symInfoDict[exName][i[1]] = {}

            # Within the symbol dict, we will create seperate dict for each year
            if not expYear in symInfoDict[exName][i[1]]:
                symInfoDict[exName][i[1]][expYear] = {}

            # Within the year dict, we will create separate dict for each month
            if not expMonth.upper() in symInfoDict[exName][i[1]][expYear]:
                symInfoDict[exName][i[1]][expYear][expMonth.upper()] = {}

            # Within the symbol dict, we will create separate dict for inst_type
            if not inst_type in symInfoDict[exName][i[1]][expYear]:
                symInfoDict[exName][i[1]][expYear][expMonth.upper()][inst_type] = {API_K_LOT_SIZE: i[2], API_K_MIN_TICK_SIZE: i[4]}

        # Set the minQtyDict to cache so that the next user will not have to connect to the db
        localMemory.set("%s-%s%s" % (funcName, exchange, CACHE_K_SYM_INFO_DICT_2), json.dumps(symInfoDict),
                        CACHE_T_2)
        return [SUCCESS_C_1, symInfoDict, ""]

    except Exception as e:
        logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, e, ERROR_C_UNKNOWN)
        return [ERROR_C_1, ERROR_C_UNKNOWN, str(e)]


def main():
    None


if __name__ == "__main__":
    main()
