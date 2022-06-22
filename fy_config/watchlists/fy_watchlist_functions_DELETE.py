moduleName = "fy_watchlist_functions"
try:
	import sys
	import boto3
	import json

	from fy_base_api_keys_values import API_K_STATUS, API_V_ERROR, API_K_CODE, \
	 API_K_DATA_1, API_V_SUCCESS, API_K_MSG
	from fy_connections_defines import AWS_SERVICE_S3
	from fy_base_success_error_codes import ERROR_C_1, SUCCESS_C_1, \
     ERROR_C_UNKNOWN, ERROR_C_DEMO_USER, ERROR_C_INV_WATCHLIST, ERROR_C_INV_INP, \
	 SUCCESS_C_WATCHLIST_DELETE, ERROR_C_DB_DATA_NOT_FOUND
	from fy_base_success_error_messages import ERROR_M_DEMO_USER, \
	 ERROR_M_INV_WATCHLIST, ERROR_M_INV_INPUT_1, ERROR_M_INV_WATCHLIST_NO_DATA, \
	 ERROR_M_WATCHLIST_INV_KEY, SUCCESS_M_WATCHLIST_DELETE
	from fy_base_defines import LOG_STATUS_ERROR_1
	from fy_data_and_trade_defines import GUEST_CLIENT_ID
	from fy_common_api_keys_values import API_K_PARAMS_1, API_K_WATCHLIST, \
	 API_K_WATCHLIST_NAME

	from fy_auth_functions import initial_validate_access_token
	from fy_base_functions import logEntryFunc2
	from fy_config.watchlists.fy_watchlist_common_functions import getUserAllWatchList, \
     insertUpdateWatchList

except Exception as e:
	print("ERR : %s : %s : %s" % (moduleName, "Could not import module", e))
	sys.exit()


def fy_watchlist_delete(args):
	funcName = "fy_watchlist_delete"
	try:
		funcRet = initial_validate_access_token(args, callingFuncName=funcName)
		if funcRet[API_K_STATUS] == API_V_ERROR:
			return funcRet
		tokenHash = funcRet[API_K_DATA_1][0]
		fyId = funcRet[API_K_DATA_1][1]

		try:
			if not isinstance(args[API_K_PARAMS_1], dict):
				args[API_K_PARAMS_1] = json.loads(args[API_K_PARAMS_1])
		except Exception as e:
			return {API_K_STATUS: API_V_ERROR, API_K_CODE: ERROR_C_INV_INP, API_K_MSG: ERROR_M_INV_INPUT_1}

		reqType = args.get("reqType")
		if reqType == "W":
			watchListDict = args[API_K_PARAMS_1][API_K_WATCHLIST]
		else:
			watchListDict = args[API_K_PARAMS_1][API_K_WATCHLIST_NAME]

		deleteWlFuncRet = INTERNAL_deleteWatchlist(fyId, watchListDict)
		returnDict = {API_K_STATUS: API_V_ERROR, API_K_CODE: deleteWlFuncRet[1],API_K_MSG: deleteWlFuncRet[2]}
		if deleteWlFuncRet[0] == SUCCESS_C_1:
			returnDict[API_K_STATUS] = API_V_SUCCESS
		return returnDict
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, "", e, ERROR_C_UNKNOWN, args,"Line Number: %s"%str(exc_tb.tb_lineno))
		returnDict = {API_K_STATUS: API_V_ERROR, API_K_CODE: ERROR_C_UNKNOWN, API_K_MSG: str(e)}
		return (returnDict)


def INTERNAL_deleteWatchlist(fyId, watchListDict):
	funcName = "INTERNAL_deleteWatchlist"
	try:
		if fyId in GUEST_CLIENT_ID:
			return [ERROR_C_1, ERROR_C_DEMO_USER, ERROR_M_DEMO_USER]
			
		if len(watchListDict) <= 0:
			return [ERROR_C_1, ERROR_C_INV_WATCHLIST, ERROR_M_INV_WATCHLIST]
		else:
			watchlistKey = watchListDict.strip()
			if not watchlistKey.startswith('_'):
				watchlistKey = '_'+watchlistKey
		s3client = boto3.client(AWS_SERVICE_S3)
		getuserWlFuncRet = getUserAllWatchList(fyId,s3client=s3client, callingFuncName = funcName)
		if getuserWlFuncRet[0] == ERROR_C_1:
			return [ERROR_C_1, ERROR_C_INV_WATCHLIST, ERROR_M_INV_WATCHLIST_NO_DATA]
		userWatchListDict = getuserWlFuncRet[1]
		if watchlistKey in userWatchListDict:
			del userWatchListDict[watchlistKey]
		else:
			return [ERROR_C_1, ERROR_C_UNKNOWN, ERROR_M_WATCHLIST_INV_KEY]
		updateUserWatchList = insertUpdateWatchList(fyId, userWatchListDict,s3client=s3client)
		if updateUserWatchList[0] == SUCCESS_C_1:
			return [SUCCESS_C_1, SUCCESS_C_WATCHLIST_DELETE, SUCCESS_M_WATCHLIST_DELETE]
		else:
			return [ERROR_C_1, ERROR_C_DB_DATA_NOT_FOUND, ERROR_M_INV_WATCHLIST]
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, funcName, e, ERROR_C_UNKNOWN,"Line Number: %s"%str(exc_tb.tb_lineno))
		return [ERROR_C_1, ERROR_C_UNKNOWN, ""]
