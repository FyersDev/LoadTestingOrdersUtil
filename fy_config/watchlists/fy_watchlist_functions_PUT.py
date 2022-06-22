moduleName = "fy_watchlist_functions"
try:
	import sys
	import boto3
	import time
	import json

	from fy_base_api_keys_values import API_K_STATUS, API_V_ERROR, API_K_CODE, \
	 API_K_DATA_1, API_V_SUCCESS, API_K_MSG
	from fy_connections_defines import AWS_SERVICE_S3
	from fy_base_success_error_codes import ERROR_C_1, SUCCESS_C_1, \
     ERROR_C_UNKNOWN, SUCCESS_C_2, ERROR_C_DEMO_USER, \
	 ERROR_C_INV_WATCHLIST_NAME, ERROR_C_INV_WATCHLIST, ERROR_C_INV_INP
	from fy_base_success_error_messages import ERROR_M_DEMO_USER, \
	 ERROR_M_INV_WATCHLIST, ERROR_M_INV_WATCHLIST_MAX_SYMBOL, \
	 ERROR_M_INV_WATCHLIST_NO_DATA, ERROR_M_INV_WATCHLIST_MAX_NO, ERROR_M_INV_WATCHLIST_MAX_SIZE, \
	 ERROR_M_INV_WATCHLIST_SYMBOL_EXISTS, ERROR_M_INV_WATCHLIST_SYMBOL_NOT_EXIST, \
	 ERROR_M_INV_INPUT_1
	from fy_base_defines import LOG_STATUS_ERROR_1
	from fy_data_and_trade_defines import GUEST_CLIENT_ID
	from fy_common_api_keys_values import API_K_WATCHLIST_NAME, \
	 API_K_FYSYMBOLS, API_K_LAST_UPDATED_TIME, API_K_PARAMS_1
	from fy_watchlist_defines import WATCHLIST_MAXIMUM_NUMBER_SYMBOLS, \
	 WATCHLIST_MAX_SIZE

	from fy_auth_functions import initial_validate_access_token
	from fy_base_functions import logEntryFunc2
	from fy_connections import connectRedis
	from fy_common_internal_functions import getSymbolsFromSymbolMasterCache
	from fy_config.watchlists.fy_watchlist_common_functions import getUserAllWatchList, \
     INTERNAL_createWatchlistSymbolDict2, insertUpdateWatchList

except Exception as e:
	print("ERR : %s : %s : %s" % (moduleName, "Could not import module", e))
	sys.exit()


# watchlist PUT request for modifying an existing list - 20200130 - Khyati
def fy_watchlist_modify(args):
	funcName = "fy_watchlist_modify"
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

		lastUpdateTime = int(time.time())

		watchlistDict = args[API_K_PARAMS_1]

		updateWLFuncRet = INTERNAL_modifyWatchlist(watchlistDict, fyId, lastUpdateTime,callingFuncName=funcName)
		if updateWLFuncRet[0] == ERROR_C_1:
			returnDict = {API_K_STATUS: API_V_ERROR, API_K_CODE: updateWLFuncRet[1], API_K_MSG: updateWLFuncRet[2]}
			return (returnDict)
		updatedWatchList = updateWLFuncRet[1]
		returnDict = {API_K_STATUS:API_V_SUCCESS, API_K_DATA_1:updatedWatchList,API_K_CODE:SUCCESS_C_2}
		return returnDict
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, "", e, ERROR_C_UNKNOWN, args,"Line Number: %s"%str(exc_tb.tb_lineno))
		returnDict = {API_K_STATUS: API_V_ERROR, API_K_CODE: ERROR_C_UNKNOWN, API_K_MSG: str(e)}
		return (returnDict)


def INTERNAL_modifyWatchlist(watchlistDict, fyId, lastUpdateTime,s3client = None,callingFuncName=""):
	funcName = "INTERNAL_modifyWatchlist"
	try:
		if fyId in GUEST_CLIENT_ID:
			return [ERROR_C_1, ERROR_C_DEMO_USER, ERROR_M_DEMO_USER]

		if not isinstance(watchlistDict, dict):
			watchlistDict = json.loads(watchlistDict)

		# Check for watchlist title
		if API_K_WATCHLIST_NAME not in watchlistDict or watchlistDict[API_K_WATCHLIST_NAME] == '':
			return [ERROR_C_1, ERROR_C_INV_WATCHLIST_NAME, ERROR_M_INV_WATCHLIST]
		watchlistDict[API_K_WATCHLIST_NAME] = watchlistDict[API_K_WATCHLIST_NAME].strip()
		if not watchlistDict[API_K_WATCHLIST_NAME].startswith('_'):
			watchlistDict[API_K_WATCHLIST_NAME] = '_'+watchlistDict[API_K_WATCHLIST_NAME]
		wltitle = watchlistDict[API_K_WATCHLIST_NAME]

		if ("add_symbols" not in watchlistDict or len(watchlistDict["add_symbols"])<=0) and ("del_symbols" not in watchlistDict or len(watchlistDict["del_symbols"])<=0) and ("old_title" not in watchlistDict or len(watchlistDict["old_title"])<=0) and ("slNo" not in watchlistDict):
			return [ERROR_C_1, ERROR_C_INV_INP, ERROR_M_INV_INPUT_1]

		# Get existing watchlist data for the user
		if s3client == None:
			s3client = boto3.client(AWS_SERVICE_S3)
		getuserWlFuncRet = getUserAllWatchList(fyId,s3client=s3client, callingFuncName = funcName)
		if getuserWlFuncRet[0] == ERROR_C_1:
			return [ERROR_C_1, ERROR_C_INV_WATCHLIST, ERROR_M_INV_WATCHLIST_NO_DATA]
		# If there is no data for the user
		if len(getuserWlFuncRet[1]) == 0:
			return [ERROR_C_1, ERROR_C_INV_WATCHLIST, ERROR_M_INV_WATCHLIST_NO_DATA]

		watchlistData = getuserWlFuncRet[1]
		if len(watchlistData) > WATCHLIST_MAX_SIZE:
			return [ERROR_C_1, ERROR_C_INV_WATCHLIST, ERROR_M_INV_WATCHLIST_MAX_NO]

		# Rename the watchlist
		if "old_title" in watchlistDict and watchlistDict["old_title"] != "":
			renameTitle = watchlistDict['old_title'].strip()
			if not renameTitle.startswith('_'):
				renameTitle = '_'+renameTitle
			if wltitle == renameTitle:
				return [ERROR_C_1, ERROR_C_INV_WATCHLIST_NAME, ERROR_M_INV_WATCHLIST]
			if not renameTitle in watchlistData:
				return [ERROR_C_1, ERROR_C_INV_WATCHLIST_NAME, ERROR_M_INV_WATCHLIST]
			watchlistData[wltitle] = watchlistData[renameTitle]
			del watchlistData[renameTitle]
			watchlistData[wltitle][API_K_WATCHLIST_NAME] = wltitle
			watchlistData[wltitle][API_K_LAST_UPDATED_TIME] = lastUpdateTime

		elif wltitle not in watchlistData:
			return [ERROR_C_1, ERROR_C_INV_WATCHLIST_NAME, ERROR_M_INV_WATCHLIST]

		# Update the symbols in the existing watchlist
		if "add_symbols" in watchlistDict and watchlistDict["add_symbols"] != []:
			symbolList = watchlistDict["add_symbols"]
			for symbol in symbolList:
				if symbol in watchlistData[wltitle][API_K_FYSYMBOLS]:
					return [ERROR_C_1, ERROR_C_INV_INP, ERROR_M_INV_WATCHLIST_SYMBOL_EXISTS]
				watchlistData[wltitle][API_K_FYSYMBOLS].append(symbol)
			watchlistData[wltitle][API_K_LAST_UPDATED_TIME] = lastUpdateTime
		if "del_symbols" in  watchlistDict and watchlistDict["del_symbols"] != []:
			delSymbolList = watchlistDict["del_symbols"]
			for symbol in delSymbolList:
				if not symbol in watchlistData[wltitle][API_K_FYSYMBOLS]:
					return [ERROR_C_1, ERROR_C_INV_INP, ERROR_M_INV_WATCHLIST_SYMBOL_NOT_EXIST]
				watchlistData[wltitle][API_K_FYSYMBOLS].remove(symbol)
			watchlistData[wltitle][API_K_LAST_UPDATED_TIME] = lastUpdateTime

		if "slNo" in watchlistDict:
			watchlistData[wltitle]["slNo"] = watchlistDict["slNo"]

		# Check if new watchlist is greater than the permissable size
		if len(watchlistData) > WATCHLIST_MAX_SIZE:
			return [ERROR_C_1, ERROR_C_INV_WATCHLIST, ERROR_M_INV_WATCHLIST_MAX_SIZE]

		if len(watchlistData[wltitle][API_K_FYSYMBOLS]) > WATCHLIST_MAXIMUM_NUMBER_SYMBOLS:
			return [ERROR_C_1, ERROR_C_INV_WATCHLIST, ERROR_M_INV_WATCHLIST_MAX_SYMBOL]

		localMemory = connectRedis(callingFuncName= funcName)

		symDict = {}
		invalidSymbols = []
		validSymbolsRet = getSymbolsFromSymbolMasterCache(watchlistData[wltitle][API_K_FYSYMBOLS], localMemory=localMemory, callingFuncName=funcName)
		if validSymbolsRet[0] == SUCCESS_C_1:
			symDict = validSymbolsRet[1][1]
			invalidSymbols = list(set(watchlistData[wltitle][API_K_FYSYMBOLS])-set(validSymbolsRet[1][0]))
		else:
			logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, "getSymbolsFromSymbolMasterCache" ,funcName, validSymbolsRet, fyId)

		watchlistData[wltitle][API_K_FYSYMBOLS] = [symbol for symbol in watchlistData[wltitle][API_K_FYSYMBOLS] if symbol not in invalidSymbols]

		# Update the watchlists data for the user
		insertUpdateRet = insertUpdateWatchList(fyId, watchlistData,s3client=s3client,callingFuncName=funcName)
		if insertUpdateRet[0] != SUCCESS_C_1:
			return [ERROR_C_1, ERROR_C_INV_WATCHLIST, ERROR_M_INV_WATCHLIST]

		watchlistData[wltitle] = INTERNAL_createWatchlistSymbolDict2(watchlistData[wltitle],symDict)

		watchlistData[wltitle][API_K_WATCHLIST_NAME] = watchlistData[wltitle][API_K_WATCHLIST_NAME][1:]
		return [SUCCESS_C_1, watchlistData[wltitle], ""]
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, e, ERROR_C_UNKNOWN,"Line Number: %s"%str(exc_tb.tb_lineno))
		return [ERROR_C_1, ERROR_C_UNKNOWN, ""]
