moduleName = "fy_watchlist_functions"
try:
	import sys
	import boto3
	import time
	import functools
	import string
	import random
	import json

	from fy_base_api_keys_values import API_K_STATUS, API_V_ERROR, API_K_CODE, \
	 API_K_DATA_1, API_V_SUCCESS, API_K_MSG
	from fy_connections_defines import AWS_SERVICE_S3
	from fy_base_success_error_codes import ERROR_C_1, SUCCESS_C_1, \
     ERROR_C_UNKNOWN, SUCCESS_C_2, ERROR_C_DEMO_USER, \
	 ERROR_C_INV_WATCHLIST_NAME, ERROR_C_INV_FYSYMBOLS, ERROR_C_INV_WATCHLIST, \
	 ERROR_C_INV_LUT, ERROR_C_INV_INP
	from fy_base_success_error_messages import ERROR_M_DEMO_USER, \
	 ERROR_M_INV_WATCHLIST, ERROR_M_INV_FYSYMBOLS, ERROR_M_INV_WATCHLIST_MAX_SYMBOL, \
	 ERROR_M_INV_WATCHLIST_NO_DATA, ERROR_M_INV_WATCHLIST_MAX_NO, ERROR_M_INV_WATCHLIST_MAX_SIZE, \
	 ERROR_M_INV_WATCHLIST_ID, ERROR_M_INV_LAST_UPDATED_TIME, \
	 ERROR_M_INV_INPUT_2, ERROR_M_INV_INPUT_1
	from fy_base_defines import LOG_STATUS_ERROR_1
	from fy_data_and_trade_defines import GUEST_CLIENT_ID
	from fy_common_api_keys_values import API_K_PARAMS_1, API_K_WATCHLIST, \
	 API_K_WATCHLIST_NAME, API_K_FYSYMBOLS, API_K_LAST_UPDATED_TIME, API_K_ID_1, \
	 API_K_WATCHLIST_SOURCE, API_V_WATCHLIST_SOURCE_WEB
	from fy_watchlist_defines import WATCHLIST_MAXIMUM_NUMBER_SYMBOLS, WATCHLIST_MAX_SIZE, \
	 WATCHLIST_MAX_INPUT_SIZE

	from fy_auth_functions import initial_validate_access_token
	from fy_base_functions import logEntryFunc2
	from fy_connections import connectRedis
	from fy_common_internal_functions import getSymbolsFromSymbolMasterCache
	from fy_data_internal_functions import INTERNAL_getL1PricesForFyTokenDict_1, \
	 INTERNAL_updateQuoteDetails
	from fy_config.watchlists.fy_watchlist_common_functions import getUserAllWatchList, \
     INTERNAL_createWatchlistSymbolDict2, insertUpdateWatchList

except Exception as e:
	print("ERR : %s : %s : %s" % (moduleName, "Could not import module", e))
	sys.exit()


def fy_watchlist_update(args):
	funcName = "fy_watchlist_update"
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
			updateWLFuncRet = INTERNAL_updateWatchlist_web(args[API_K_PARAMS_1][API_K_WATCHLIST], fyId)
		else:
			updateWLFuncRet = INTERNAL_updateWatchlist(args[API_K_PARAMS_1], fyId)
		if updateWLFuncRet[0] == ERROR_C_1:
			logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, "WATCHLIST ERROR", updateWLFuncRet, fyId=fyId)
			returnDict = {API_K_STATUS: API_V_ERROR, API_K_CODE: updateWLFuncRet[1], API_K_MSG: updateWLFuncRet[2]}
			return (returnDict)
		returnDict = {API_K_STATUS:API_V_SUCCESS, API_K_DATA_1:updateWLFuncRet[1],API_K_CODE:SUCCESS_C_2}
		return returnDict
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, "", e, ERROR_C_UNKNOWN, args,"Line Number: %s"%str(exc_tb.tb_lineno))
		returnDict = {API_K_STATUS: API_V_ERROR, API_K_CODE: ERROR_C_UNKNOWN, API_K_MSG: str(e)}
		return (returnDict)


def INTERNAL_updateWatchlist(watchlistDict, fyId, s3client=None, userCustomWL=None):
	funcName = "INTERNAL_updateWatchlist"
	try:
		if fyId in GUEST_CLIENT_ID:
			return [ERROR_C_1, ERROR_C_DEMO_USER, ERROR_M_DEMO_USER]
		renameTitle = ""
		if 'old_title' in watchlistDict:
			if watchlistDict['old_title'] != "":
				renameTitle = watchlistDict['old_title'].strip()
				if not renameTitle.startswith('_'):
					renameTitle = '_'+renameTitle
			del watchlistDict['old_title']

		lastUpdateTime = int(time.time())

		updatedWatchList = {}
		if not isinstance(watchlistDict, dict):
			jsonDict = json.loads(watchlistDict)
		else:
			jsonDict = watchlistDict

		if API_K_WATCHLIST_NAME in jsonDict:
			if jsonDict[API_K_WATCHLIST_NAME] == '':
				return [ERROR_C_1, ERROR_C_INV_WATCHLIST_NAME, ERROR_M_INV_WATCHLIST]
			elif jsonDict[API_K_WATCHLIST_NAME] == renameTitle:
				return [ERROR_C_1, ERROR_C_INV_WATCHLIST_NAME, ERROR_M_INV_WATCHLIST]
			else:
				titleKey = jsonDict[API_K_WATCHLIST_NAME].strip()
				if not titleKey.startswith('_'):
					titleKey = '_'+titleKey
				jsonDict[API_K_WATCHLIST_NAME] = '_'+jsonDict[API_K_WATCHLIST_NAME].strip()
		else:
			return [ERROR_C_1, ERROR_C_INV_WATCHLIST_NAME, ERROR_M_INV_WATCHLIST]

		if API_K_FYSYMBOLS in jsonDict:
			if jsonDict[API_K_FYSYMBOLS] == '':
				return [ERROR_C_1, ERROR_C_INV_FYSYMBOLS, ERROR_M_INV_FYSYMBOLS]
			if len(jsonDict[API_K_FYSYMBOLS]) > WATCHLIST_MAXIMUM_NUMBER_SYMBOLS:
				return [ERROR_C_1, ERROR_C_INV_WATCHLIST, ERROR_M_INV_WATCHLIST_MAX_SYMBOL]
		else:
			return [ERROR_C_1, ERROR_C_INV_FYSYMBOLS, ERROR_M_INV_FYSYMBOLS]

		symbols = [x.replace(' ','') for x in jsonDict[API_K_FYSYMBOLS]]
		jsonDict[API_K_FYSYMBOLS] = symbols
		jsonDict[API_K_LAST_UPDATED_TIME] = lastUpdateTime
		chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
		jsonDict["id"] = ''.join(random.choice(chars) for _ in range(12))

		# Get watchlist data for the user
		if s3client == None:
			s3client = boto3.client(AWS_SERVICE_S3)
		if userCustomWL is None:
			getuserWlFuncRet = getUserAllWatchList(fyId,s3client=s3client, callingFuncName = funcName)
			if getuserWlFuncRet[0] == ERROR_C_1:
				return [ERROR_C_1, ERROR_C_INV_WATCHLIST, ERROR_M_INV_WATCHLIST_NO_DATA]

			userCustomWL = getuserWlFuncRet[1]
		getuserWlFuncRet = userCustomWL
		# If there is no data for the user
		if len(getuserWlFuncRet) == 0:
			watchlistData = {}
			updatedWatchList[titleKey] = jsonDict
			watchlistData = updatedWatchList

			watchlistData[titleKey]["slNo"] = 0

		# If the user already has data, then we will append to it
		else:
			watchlistData = getuserWlFuncRet
			if len(watchlistData) > WATCHLIST_MAX_SIZE:
				return [ERROR_C_1, ERROR_C_INV_WATCHLIST, ERROR_M_INV_WATCHLIST_MAX_NO]

			list1 = [wL for wL in watchlistData]
			list2 = [watchlistData[wL].get("slNo",0) for wL in list1]
			list2.sort()

			# Check if watchlist id already exists
			if renameTitle in watchlistData:
				if "slNo" not in jsonDict:
					jsonDict["slNo"] = watchlistData[renameTitle].get("slNo",0)
				del watchlistData[renameTitle]

			if "slNo" not in jsonDict:
				if titleKey in watchlistData:
					jsonDict["slNo"] = watchlistData[titleKey].get("slNo",0)
				else:
					jsonDict["slNo"] = list2[-1] + 1
					list2.append(jsonDict["slNo"])
			updatedWatchList[titleKey] = jsonDict
			watchlistData[titleKey] = updatedWatchList[titleKey]

		# Check if new watchlist is greater than the permissable size
		if len(watchlistData) > WATCHLIST_MAX_SIZE:
			return [ERROR_C_1, ERROR_C_INV_WATCHLIST, ERROR_M_INV_WATCHLIST_MAX_SIZE]

		localMemory = connectRedis()
		symDict = {}
		invalidSymbols = []
		validSymbolsRet = getSymbolsFromSymbolMasterCache(updatedWatchList[titleKey][API_K_FYSYMBOLS], localMemory=localMemory, callingFuncName=funcName)
		if validSymbolsRet[0] == SUCCESS_C_1:
			symDict = validSymbolsRet[1][1]
			invalidSymbols = list(set(updatedWatchList[titleKey][API_K_FYSYMBOLS])-set(validSymbolsRet[1][0]))
		else:
			logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, "getSymbolsFromSymbolMasterCache" ,funcName, validSymbolsRet, fyId)

		insertUpdateRet = insertUpdateWatchList(fyId, watchlistData,s3client=s3client)
		if insertUpdateRet[0] != SUCCESS_C_1:
			return [ERROR_C_1, ERROR_C_INV_WATCHLIST, ERROR_M_INV_WATCHLIST]

		updatedWatchList[titleKey] = INTERNAL_createWatchlistSymbolDict2(updatedWatchList[titleKey],symDict)
		fyTokenDict = {}
		for i in validSymbolsRet[1][0]:
			fyTokenDict[i] = validSymbolsRet[1][1][i]["fyToken"]
		l2DictRetList = INTERNAL_getL1PricesForFyTokenDict_1(fyTokenDict, localMemory=localMemory,callingFuncName=funcName)
		if l2DictRetList[0] != ERROR_C_1:
			l2Dict = l2DictRetList[1]
			list(map(functools.partial(INTERNAL_updateQuoteDetails,l2Dict=l2Dict),updatedWatchList[titleKey]["symbols"]))

		updatedWatchList[titleKey][API_K_WATCHLIST_NAME] = updatedWatchList[titleKey][API_K_WATCHLIST_NAME][1:]

		return [SUCCESS_C_1, updatedWatchList[titleKey], ""]
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, funcName, e, ERROR_C_UNKNOWN, fyId,"Line Number: %s"%str(exc_tb.tb_lineno))
		return [ERROR_C_1, ERROR_C_UNKNOWN, ""]


def INTERNAL_updateWatchlist_web(watchlistDict, fyId,s3client=None):
	funcName = "INTERNAL_updateWatchlist_web"
	try:
		renameTitle = watchlistDict['old_title'].strip()
		if not renameTitle.startswith('_'):
			renameTitle = '_'+renameTitle
		del watchlistDict['old_title']

		if len(watchlistDict) > WATCHLIST_MAX_INPUT_SIZE:
			return [ERROR_C_1, ERROR_C_INV_WATCHLIST, ERROR_M_INV_INPUT_2]
		else:
			updatedWatchList = {}
			for token in watchlistDict:
				try:
					titleKey = token.strip()
					if not titleKey.startswith('_'):
						titleKey = '_'+titleKey
				except Exception as e:
					return [ERROR_C_1, ERROR_C_UNKNOWN, ""]

				if isinstance(watchlistDict[token], str):
					jsonDict = json.loads(watchlistDict[token])
				else:
					jsonDict = watchlistDict[token]

				if API_K_ID_1 in jsonDict:
					if jsonDict[API_K_ID_1] == '':
						return [ERROR_C_1, ERROR_C_INV_WATCHLIST, ERROR_M_INV_WATCHLIST_ID]
				else:
					return [ERROR_C_1, ERROR_C_INV_WATCHLIST, ERROR_M_INV_WATCHLIST_ID]

				if API_K_LAST_UPDATED_TIME in jsonDict:
					if jsonDict[API_K_LAST_UPDATED_TIME] == '':
						return [ERROR_C_1, ERROR_C_INV_LUT, ERROR_M_INV_LAST_UPDATED_TIME]
				else:
					return [ERROR_C_1, ERROR_C_INV_LUT, ERROR_M_INV_LAST_UPDATED_TIME]

				if API_K_WATCHLIST_NAME in jsonDict:
					if jsonDict[API_K_WATCHLIST_NAME] == '':
						return [ERROR_C_1, ERROR_C_INV_WATCHLIST_NAME, ERROR_M_INV_WATCHLIST]
					elif jsonDict[API_K_WATCHLIST_NAME] == renameTitle:
						return [ERROR_C_1, ERROR_C_INV_WATCHLIST_NAME, ERROR_M_INV_WATCHLIST]
					else:
						jsonDict[API_K_WATCHLIST_NAME] = '_'+jsonDict[API_K_WATCHLIST_NAME].strip()
				else:
					return [ERROR_C_1, ERROR_C_INV_WATCHLIST_NAME, ERROR_M_INV_WATCHLIST]

				if API_K_FYSYMBOLS in jsonDict:
					if jsonDict[API_K_FYSYMBOLS] == '':
						return [ERROR_C_1, ERROR_C_INV_FYSYMBOLS, ERROR_M_INV_FYSYMBOLS]
					if len(jsonDict[API_K_FYSYMBOLS]) > WATCHLIST_MAXIMUM_NUMBER_SYMBOLS:
						return [ERROR_C_1, ERROR_C_INV_WATCHLIST, ERROR_M_INV_WATCHLIST_MAX_SYMBOL]
				else:
					return [ERROR_C_1, ERROR_C_INV_FYSYMBOLS, ERROR_M_INV_FYSYMBOLS]

				symbols = [x.replace(' ','') for x in jsonDict[API_K_FYSYMBOLS]]
				jsonDict[API_K_FYSYMBOLS] = symbols
				jsonDict[API_K_WATCHLIST_SOURCE] = API_V_WATCHLIST_SOURCE_WEB
				updatedWatchList[titleKey] = jsonDict
			# END: Validation

			# Get watchlist data for the user
			if s3client == None:
				s3client = boto3.client(AWS_SERVICE_S3)
			getuserWlFuncRet = getUserAllWatchList(fyId,s3client=s3client, callingFuncName = funcName)
			if getuserWlFuncRet[0] == ERROR_C_1:
				return [ERROR_C_1, ERROR_C_INV_WATCHLIST, ERROR_M_INV_WATCHLIST_NO_DATA]

			getuserWlFuncRet = getuserWlFuncRet[1]
			# If there is no data for the user
			if len(getuserWlFuncRet) == 0:
				watchlistData = {}
				watchlistData = updatedWatchList
				watchlistData[titleKey]["slNo"] = 0

			# If the user already has data, then we will append to it
			else:
				watchlistData = getuserWlFuncRet
				if len(watchlistData) > WATCHLIST_MAX_SIZE:
					return [ERROR_C_1, ERROR_C_INV_WATCHLIST, ERROR_M_INV_WATCHLIST_MAX_NO]

				list1 = [wL for wL in watchlistData]
				list2 = [watchlistData[wL].get("slNo",0) for wL in list1]
				list2.sort()

				# Check if watchlist id already exists
				for wLid in updatedWatchList:
					if renameTitle in watchlistData:
						slno = watchlistData[renameTitle].get("slNo",0)
						del watchlistData[renameTitle]
					elif wLid in watchlistData:
						slno = watchlistData[wLid].get("slNo",0)
					else:
						slno = list2[-1] + 1
					updatedWatchList[wLid]["slNo"] = slno
					watchlistData[wLid] = updatedWatchList[wLid]
			# Check if new watchlist is greater than the permissable size
			if len(watchlistData) > WATCHLIST_MAX_SIZE:
				return [ERROR_C_1, ERROR_C_INV_WATCHLIST, ERROR_M_INV_WATCHLIST_MAX_SIZE]

			insertUpdateRet = insertUpdateWatchList(fyId, watchlistData,s3client=s3client)
			if insertUpdateRet[0] == SUCCESS_C_1:
				return [SUCCESS_C_1, updatedWatchList, ""]
			else:
				return [ERROR_C_1, ERROR_C_INV_WATCHLIST, ERROR_M_INV_WATCHLIST]
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, funcName,watchlistDict,"Line Number: %s"%str(exc_tb.tb_lineno),err_msg= e, code=ERROR_C_UNKNOWN,fyId=fyId)
		return [ERROR_C_1, ERROR_C_UNKNOWN, ""]


# ##Shift from db to s3 - 20200120 - Khyati -
# def insertUpdateWatchList(fyId, userWatchListDict, s3client=None, callingFuncName=""):
# 	funcName = "insertUpdateWatchList"
# 	try:
# 		userwatchlistJson = json.dumps(userWatchListDict)
# 		if s3client == None:
# 			s3client = boto3.client(AWS_SERVICE_S3)
		
# 		key = AWS_S3_FOLDER_PATH_USER_WATCHLIST + fyId + FILE_USER_WATCHLIST_SUFFIX
# 		s3client.put_object(Body = userwatchlistJson, Bucket = AWS_S3_BUCKET_USER_DATA, Key = key)

# 		return [SUCCESS_C_1, "",""]
# 	except Exception as e:
# 		exc_type, exc_obj, exc_tb = sys.exc_info()
# 		logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, e, ERROR_C_UNKNOWN,"Line Number: %s"%str(exc_tb.tb_lineno))
# 		return [ERROR_C_1, ERROR_C_S3_GET_FAILED, ERROR_M_S3_UPDATE_FAILED]
