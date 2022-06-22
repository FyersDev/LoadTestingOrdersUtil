moduleName = "fy_watchlist_functions"

try:
	import sys
	import csv
	import boto3
	import time
	import functools
	import operator
	import string
	import random
	import json

	from fy_base_api_keys_values import API_K_STATUS, API_V_ERROR, API_K_CODE, \
	 API_K_DATA_1, API_V_SUCCESS, API_K_MSG
	from fy_connections_defines import AWS_SERVICE_S3, AWS_S3_FOLDER_PATH_USER_WATCHLIST, \
	 FILE_USER_WATCHLIST_SUFFIX, AWS_S3_FOLDER_PATH_WATCHLIST_INDICES
	from fy_base_success_error_codes import ERROR_C_1, SUCCESS_C_1, \
     ERROR_C_UNKNOWN, SUCCESS_C_2, ERROR_C_S3_GET_FAILED, ERROR_C_DEMO_USER, \
	 ERROR_C_INV_WATCHLIST_NAME, ERROR_C_INV_FYSYMBOLS, ERROR_C_INV_WATCHLIST
	from fy_base_success_error_messages import ERROR_M_S3_GET_FAILED, ERROR_M_DEMO_USER, \
	 ERROR_M_INV_WATCHLIST, ERROR_M_INV_FYSYMBOLS, ERROR_M_INV_WATCHLIST_MAX_SYMBOL, \
	 ERROR_M_INV_WATCHLIST_NO_DATA, ERROR_M_INV_WATCHLIST_MAX_NO, ERROR_M_INV_WATCHLIST_MAX_SIZE, \
	 ERROR_M_S3_UPDATE_FAILED
	from fy_base_defines import LOG_STATUS_ERROR_1
	from fy_connections_defines import AWS_S3_FOLDER_PATH_PREDEF_WATCHLIST, \
	 AWS_S3_BUCKET_USER_DATA, AWS_BOTO3_S3_CONNECTION
	from fy_data_and_trade_defines import CACHE_WATCHLIST_EXPIRY, GUEST_CLIENT_ID, \
	 EXCHANGE_CODE_NSE, EXCHANGE_CODE_MCX, SYM_SEGMENT_CD, SYM_SEGMENT_COM, \
	 SYM_INSTTYPE_FUTCUR, SYM_INSTTYPE_FUTCOM, SYM_INSTTYPE_FUTIDX, CACHE_K_WL_CURRFUT, \
	 CACHE_K_WL_MCXFUT, CACHE_K_WL_NIFTYFUT, CACHE_K_WL_BANKNIFTYFUT, \
	 SYM_INSTTYPE_FUTSTK, CACHE_K_WATCHLIST_PREDEFINED_FNO
	from fy_common_api_keys_values import API_K_WATCHLIST, API_K_WATCHLIST_MAX_SIZE, \
	 API_K_CUSTOM_WATCHLIST, API_K_PREDEFINED_WATCHLIST, API_K_WATCHLIST_NAME, \
	 API_K_FYSYMBOLS, API_K_ID_1, API_K_WATCHLIST_SOURCE, API_V_WATCHLIST_SOURCE_DEF, \
	 API_K_LAST_UPDATED_TIME
	from fy_watchlist_defines import WATCHLIST_MAXIMUM_NUMBER_SYMBOLS, WATCHLIST_NEW_PREDEFINED_LIST, \
	 WATCHLIST_PREDEFINED_ID_STARTSWITH, WATCHLIST_PREDEFINED_NAME_STARTSWITH, \
	 CACHE_K_WL_NIFTYINDICES, WATCHLIST_PREDEFINED_NAME_NIFTYINDICES, \
	 WATCHLIST_PREDEFINED_NAME_CURFUT, WATCHLIST_PREDEFINED_NAME_MCXFUTCOM, \
	 CACHE_K_WL_NIFTY50, CACHE_K_WL_NIFTYBANK, WATCHLIST_PREDEFINED_NAME_NIFTYFUT, \
	 WATCHLIST_PREDEFINED_NAME_BANKNIFTYFUT, WATCHLIST_PREDEFINED_FNO_UNDERLYING_FYTOKENS, \
	 WATCHLIST_MAX_SIZE, WATCHLIST_PREDEFINED_SYMBOLS_NIFTY50, \
	 WATCHLIST_PREDEFINED_SYMBOLS_NIFTYBANK

	from fy_auth_functions import initial_validate_access_token
	from fy_base_functions import logEntryFunc2
	from fy_connections import connectRedis
	from fy_common_internal_functions import getSymbolsFromSymbolMasterCache, \
	 internal_getExpiryForUnderlying
	from fy_data_internal_functions import INTERNAL_getL1PricesForFyTokenDict_1, \
	 INTERNAL_updateQuoteDetails
	from fy_config.watchlists.fy_watchlist_common_functions import getUserAllWatchList, \
     INTERNAL_createWatchlistSymbolDict2

except Exception as e:
	print("ERR : %s : %s : %s" % (moduleName, "Could not import module", e))
	sys.exit()


def fy_watchlist_get(args):
	funcName = "fy_watchlist_get"
	try:
		start = time.time()
		funcRet = initial_validate_access_token(args, callingFuncName=funcName)
		if funcRet[API_K_STATUS] == API_V_ERROR:
			return funcRet
		tokenHash = funcRet[API_K_DATA_1][0]
		fyId = funcRet[API_K_DATA_1][1]
		start2 = time.time()
		localMemory = connectRedis()
		start3 = time.time()

		reqType = args.get("reqType")

		getWLFuncRet = INTERNAL_getWatchlist(fyId, localMemory=localMemory, source = reqType)

		end = time.time() - start
		if end >= 2:
			logEntryFunc2("DEBUG", moduleName, funcName, "",
						  "WATCHLIST Time Log - Delay - More than 2 Secs",
						  f"Total: {time.time()-start}",
						  f"Auth Validation: {start2-start}",
						  f"connect to Redis: {start3-start2}",
						  f"Internal Get Function: {time.time()-start3}",
						  fyId=fyId
						  )
		else:
			logEntryFunc2("DEBUG", moduleName, funcName, "",
						  "WATCHLIST Time Log",
						  f"Total: {time.time()-start}",
						  f"Auth Validation: {start2-start}",
						  f"connect to Redis: {start3-start2}",
						  f"Internal Get Function: {time.time()-start3}",
						  fyId=fyId
						  )
		if getWLFuncRet[0] == ERROR_C_1:
			logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, "WATCHLIST ERROR", getWLFuncRet, fyId=fyId)
			returnDict = {API_K_STATUS: API_V_ERROR, API_K_CODE: getWLFuncRet[1], API_K_MSG: getWLFuncRet[2]}
			return returnDict
		retUserwatchList = getWLFuncRet[1][0]
		watchlistMaxSize = getWLFuncRet[1][1]

		if reqType == "W":
			returnDict = {API_K_STATUS:API_V_SUCCESS, API_K_WATCHLIST:retUserwatchList, API_K_WATCHLIST_MAX_SIZE: watchlistMaxSize,API_K_CODE:SUCCESS_C_2}
		else:
			returnDict = {API_K_STATUS:API_V_SUCCESS, API_K_WATCHLIST_MAX_SIZE:watchlistMaxSize, API_K_DATA_1:{API_K_CUSTOM_WATCHLIST:retUserwatchList[API_K_CUSTOM_WATCHLIST],API_K_PREDEFINED_WATCHLIST:retUserwatchList[API_K_PREDEFINED_WATCHLIST]},API_K_CODE:SUCCESS_C_2}
		return returnDict
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, "", e,ERROR_C_UNKNOWN, args,"Line Number: %s"%str(exc_tb.tb_lineno))
		returnDict = {API_K_STATUS: API_V_ERROR, API_K_CODE: ERROR_C_UNKNOWN, API_K_MSG: str(e)}
		return (returnDict)


def INTERNAL_getWatchlist(fyId, localMemory=None, s3client = None, source = None):
	funcName = "INTERNAL_getWatchlist"
	try:
		db, cursor = None, None

		if source == None:
			source = "M"

		if localMemory == None:
			localMemory = connectRedis(callingFuncName=funcName)
		
		if s3client is None:
			s3client = AWS_BOTO3_S3_CONNECTION
		
		userWlFuncRet = getUserAllWatchList(fyId,s3client=s3client,callingFuncName = funcName)
		if userWlFuncRet[0] != SUCCESS_C_1:
			logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, "WATCHLIST ERROR", "userWlFuncRet",userWlFuncRet, fyId=fyId)
			return userWlFuncRet
		
		retUserwatchList = {}
		watchlistMaxSize = WATCHLIST_MAXIMUM_NUMBER_SYMBOLS
		userWlFuncRet = userWlFuncRet[1]
		if len(userWlFuncRet) > 0:
			if source == "M":
				watchlistret = userWlFuncRet
				retUserwatchList[API_K_CUSTOM_WATCHLIST] =list(map(INTERNAL_watchlistRemoveUnderscore,watchlistret.items()))
				allSymbolsList1 = list(map(operator.itemgetter("symbols"), retUserwatchList[API_K_CUSTOM_WATCHLIST]))
				allSymbolsList = functools.reduce(operator.iconcat, allSymbolsList1, [])				
				allSymbolsList = list(set(allSymbolsList)) ##removed duplicates
				if allSymbolsList != []:
					symDict = {}
					invalidSymbols = []
					validSymbolsRet = getSymbolsFromSymbolMasterCache(allSymbolsList,localMemory=localMemory,callingFuncName=funcName)
					if validSymbolsRet[0] == SUCCESS_C_1:
						symDict = validSymbolsRet[1][1]
						invalidSymbols = list(set(allSymbolsList)-set(validSymbolsRet[1][0]))
						if len(invalidSymbols) > 0:
							logEntryFunc2("WATCHLIST", moduleName, "Invalid Symbols", invalidSymbols, fyId=fyId)
					else:
						logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, "getSymbolsFromSymbolMasterCache" ,funcName, validSymbolsRet, fyId=fyId)

					retUserwatchList[API_K_CUSTOM_WATCHLIST] = list(map(functools.partial(INTERNAL_createWatchlistSymbolDict2,symbolDict1=symDict),retUserwatchList[API_K_CUSTOM_WATCHLIST]))

					retUserwatchList[API_K_CUSTOM_WATCHLIST] = list(map(functools.partial(INTERNAL_createWatchlistSymbolDict3,invalidSymbols=invalidSymbols),retUserwatchList[API_K_CUSTOM_WATCHLIST]))

			elif source == "W":
				watchlistret = userWlFuncRet
				allSymbolsList = []

				for key in watchlistret:
					if watchlistret[key][API_K_WATCHLIST_NAME][:1] == '_':
						watchlistret[key][API_K_WATCHLIST_NAME] = ' '+watchlistret[key][API_K_WATCHLIST_NAME][1:]
					if key[:1] == '_':
						newKey = ' '+key[1:]
						retUserwatchList[newKey] = watchlistret[key]
					else:
						retUserwatchList[key] = watchlistret[key]
					allSymbolsList.extend(watchlistret[key]["symbols"])

				allSymbolsList = list(set(allSymbolsList))
				invalidSymbols = []
				validSymbolsRet = getSymbolsFromSymbolMasterCache(allSymbolsList,localMemory=localMemory,callingFuncName=funcName)
				if validSymbolsRet[0] == SUCCESS_C_1:
					invalidSymbols = list(set(allSymbolsList)-set(validSymbolsRet[1][0]))
					if len(invalidSymbols) > 0:
						logEntryFunc2("WATCHLIST", moduleName, "Invalid Symbols", invalidSymbols, fyId=fyId)

					for key in watchlistret:
						for i in invalidSymbols:
							if i in watchlistret[key]["symbols"]:
								watchlistret[key]["symbols"].remove(i)

		else:
			if source == "M":
				# Create a watchlist if user has no saved watchlists
				watchlistDict = {"symbols":[],"title":"Watchlist 1", "old_title":"", "slNo":0}

				updateWLFuncRet = INTERNAL_updateWatchlist(watchlistDict, fyId,s3client=s3client, userCustomWL=userWlFuncRet)
				if updateWLFuncRet[0] == ERROR_C_1:
					logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, "WATCHLIST ERROR", "updateWLFuncRet",updateWLFuncRet, fyId=fyId)
					return updateWLFuncRet
				watchlistDict1 = {}
				watchlistDict1[watchlistDict["title"]] = watchlistDict
				watchlistret = watchlistDict1
				retUserwatchList[API_K_CUSTOM_WATCHLIST] =list(map(INTERNAL_watchlistRemoveUnderscore,watchlistret.items()))

			elif source == "W":
				logEntryFunc2("DEBUG", moduleName, funcName, "", "WATCHLIST",source,"No custom_watchlists",retUserwatchList,fyId=fyId)

		##GET ALL PREDEFINED WATCHLISTS
		if source == "M":
			retUserwatchList[API_K_PREDEFINED_WATCHLIST] =list(map(functools.partial(INTERNAL_predefinedWatchlists,localMemory=localMemory,s3client=s3client),WATCHLIST_NEW_PREDEFINED_LIST))

		elif source == "W":
			# Get the default Watchlists from s3
			for i in WATCHLIST_NEW_PREDEFINED_LIST:
				# WATCHLIST_NEW_PREDEFINED_LIST: WL name, csv file name, cachekey, index
				watchlistIdEnd = (i[0].replace(" ","")).lower()
				watchlistId = "%s%s" %(WATCHLIST_PREDEFINED_ID_STARTSWITH,watchlistIdEnd)

				# Get the Symbols
				getFuncRet = getPredefinedWatchlists(i[1], i[2], i[3], localMemory = localMemory,s3client=s3client)

				if getFuncRet[0] != ERROR_C_1:
					retUserwatchList[watchlistId] = {
						API_K_WATCHLIST_NAME: "%s%s" %(WATCHLIST_PREDEFINED_NAME_STARTSWITH,i[0]),
						API_K_FYSYMBOLS: getFuncRet[1],
						API_K_ID_1: watchlistId,
						API_K_WATCHLIST_SOURCE: API_V_WATCHLIST_SOURCE_DEF,
					}

		# Get Nifty Indices List
		indicesRet = getNiftyIndices(CACHE_K_WL_NIFTYINDICES, localMemory = localMemory,s3client=s3client)
		if indicesRet[0] != ERROR_C_1:
			watchlistIdEnd = (WATCHLIST_PREDEFINED_NAME_NIFTYINDICES.replace(" ","")).lower()
			watchlistId = "%s%s" %(WATCHLIST_PREDEFINED_ID_STARTSWITH,watchlistIdEnd)
			if source == "M":
				retPredefinedDict = {
					API_K_WATCHLIST_NAME: "%s%s" %(WATCHLIST_PREDEFINED_NAME_STARTSWITH,WATCHLIST_PREDEFINED_NAME_NIFTYINDICES),
					API_K_FYSYMBOLS: indicesRet[1],
					API_K_ID_1: watchlistId,
					API_K_WATCHLIST_SOURCE: API_V_WATCHLIST_SOURCE_DEF,
				}

				retUserwatchList[API_K_PREDEFINED_WATCHLIST].append(retPredefinedDict)

			elif source == "W":
				retUserwatchList[watchlistId] = {
						API_K_WATCHLIST_NAME: "%s%s" %(WATCHLIST_PREDEFINED_NAME_STARTSWITH,WATCHLIST_PREDEFINED_NAME_NIFTYINDICES),
						API_K_FYSYMBOLS: indicesRet[1],
						API_K_ID_1: watchlistId,
						API_K_WATCHLIST_SOURCE: API_V_WATCHLIST_SOURCE_DEF,
					}

		predefinedWlRet = INTERNAL_predefined_WL_all([EXCHANGE_CODE_NSE,EXCHANGE_CODE_MCX],[SYM_SEGMENT_CD,SYM_SEGMENT_COM],[SYM_INSTTYPE_FUTCUR,SYM_INSTTYPE_FUTCOM,SYM_INSTTYPE_FUTIDX], [CACHE_K_WL_CURRFUT,CACHE_K_WL_MCXFUT],db=db, cursor=cursor, localMemory=localMemory,callingFuncName=funcName)	##SYM_INSTTYPE_FUTIDX added for mcx indices

		if predefinedWlRet[0] != ERROR_C_1:
			if predefinedWlRet[1][0] != []:
				cdWatchListSuffix = WATCHLIST_PREDEFINED_NAME_CURFUT.replace(" ", "").lower()
				cdWlId = "%s%s"%(WATCHLIST_PREDEFINED_ID_STARTSWITH, cdWatchListSuffix)
				if source == "M":
					retPredefinedDict = {
						API_K_WATCHLIST_NAME: "%s%s" %(WATCHLIST_PREDEFINED_NAME_STARTSWITH,WATCHLIST_PREDEFINED_NAME_CURFUT),
						API_K_FYSYMBOLS: predefinedWlRet[1][0],
						API_K_ID_1: cdWlId,
						API_K_WATCHLIST_SOURCE: API_V_WATCHLIST_SOURCE_DEF,
					}
					retUserwatchList[API_K_PREDEFINED_WATCHLIST].append(retPredefinedDict)

				elif source == "W":
					retUserwatchList[cdWlId] = {
								API_K_WATCHLIST_NAME: "%s%s" %(WATCHLIST_PREDEFINED_NAME_STARTSWITH,WATCHLIST_PREDEFINED_NAME_CURFUT),
								API_K_FYSYMBOLS: predefinedWlRet[1][0],
								API_K_ID_1: cdWlId,
								API_K_WATCHLIST_SOURCE: API_V_WATCHLIST_SOURCE_DEF,
							}

			if predefinedWlRet[1][1] != []:
				watchListSuffix = WATCHLIST_PREDEFINED_NAME_MCXFUTCOM.replace(" ", "").lower()
				wlId = "%s%s"%(WATCHLIST_PREDEFINED_ID_STARTSWITH, watchListSuffix)
				if source == "M":
					retPredefinedDict = {
						API_K_WATCHLIST_NAME: "%s%s" %(WATCHLIST_PREDEFINED_NAME_STARTSWITH,WATCHLIST_PREDEFINED_NAME_MCXFUTCOM),
						API_K_FYSYMBOLS: predefinedWlRet[1][1],
						API_K_ID_1: wlId,
						API_K_WATCHLIST_SOURCE: API_V_WATCHLIST_SOURCE_DEF,
					}
					retUserwatchList[API_K_PREDEFINED_WATCHLIST].append(retPredefinedDict)

				elif source == "W":
					retUserwatchList[wlId] = {
								API_K_WATCHLIST_NAME: "%s%s" %(WATCHLIST_PREDEFINED_NAME_STARTSWITH,WATCHLIST_PREDEFINED_NAME_MCXFUTCOM),
								API_K_FYSYMBOLS: predefinedWlRet[1][1],
								API_K_ID_1: wlId,
								API_K_WATCHLIST_SOURCE: API_V_WATCHLIST_SOURCE_DEF,
							}

		## Nifty Futures predefined list
		cacheKeyList = [CACHE_K_WL_NIFTYFUT,CACHE_K_WL_BANKNIFTYFUT]
		cacheKeyList2 = [CACHE_K_WL_NIFTY50,CACHE_K_WL_NIFTYBANK]
		futContRet = list(map(functools.partial(INTERNAL_futuresContracts_all,db=db,cursor=cursor,localMemory=localMemory,callingFuncName=funcName),cacheKeyList,cacheKeyList2))

		if futContRet[0][CACHE_K_WL_NIFTYFUT] != []:
			nifWatchListSuffix = WATCHLIST_PREDEFINED_NAME_NIFTYFUT.replace(" ", "").lower()
			nifWlId = "%s%s"%(WATCHLIST_PREDEFINED_ID_STARTSWITH, nifWatchListSuffix)
			if source == "M":
				retPredefinedDict = {
					API_K_WATCHLIST_NAME: "%s%s" %(WATCHLIST_PREDEFINED_NAME_STARTSWITH,WATCHLIST_PREDEFINED_NAME_NIFTYFUT),
					API_K_FYSYMBOLS: futContRet[0][CACHE_K_WL_NIFTYFUT],
					API_K_ID_1: nifWlId,
					API_K_WATCHLIST_SOURCE: API_V_WATCHLIST_SOURCE_DEF,
				}
				retUserwatchList[API_K_PREDEFINED_WATCHLIST].append(retPredefinedDict)

			elif source == "W":
				retUserwatchList[nifWlId] = {
												API_K_WATCHLIST_NAME: "%s%s" %(WATCHLIST_PREDEFINED_NAME_STARTSWITH,WATCHLIST_PREDEFINED_NAME_NIFTYFUT),
												API_K_FYSYMBOLS: futContRet[0][CACHE_K_WL_NIFTYFUT],
												API_K_ID_1: nifWlId,
												API_K_WATCHLIST_SOURCE: API_V_WATCHLIST_SOURCE_DEF,
											}

		if futContRet[1][CACHE_K_WL_BANKNIFTYFUT] != []:
			banknifWatchListSuffix = WATCHLIST_PREDEFINED_NAME_BANKNIFTYFUT.replace(" ", "").lower()
			banknifWlId = "%s%s"%(WATCHLIST_PREDEFINED_ID_STARTSWITH, banknifWatchListSuffix)
			if source == "M":
				retPredefinedDict = {
					API_K_WATCHLIST_NAME: "%s%s" %(WATCHLIST_PREDEFINED_NAME_STARTSWITH,WATCHLIST_PREDEFINED_NAME_BANKNIFTYFUT),
					API_K_FYSYMBOLS: futContRet[1][CACHE_K_WL_BANKNIFTYFUT],
					API_K_ID_1: banknifWlId,
					API_K_WATCHLIST_SOURCE: API_V_WATCHLIST_SOURCE_DEF,
				}
				retUserwatchList[API_K_PREDEFINED_WATCHLIST].append(retPredefinedDict)

			elif source == "W":
				retUserwatchList[banknifWlId] = {
													API_K_WATCHLIST_NAME: "%s%s" %(WATCHLIST_PREDEFINED_NAME_STARTSWITH,WATCHLIST_PREDEFINED_NAME_BANKNIFTYFUT),
													API_K_FYSYMBOLS: futContRet[1][CACHE_K_WL_BANKNIFTYFUT],
													API_K_ID_1: banknifWlId,
													API_K_WATCHLIST_SOURCE: API_V_WATCHLIST_SOURCE_DEF,
												}

		fnoResult = list(map(functools.partial(getFnoWl,db=db,cursor=cursor,localMemory=localMemory),WATCHLIST_PREDEFINED_FNO_UNDERLYING_FYTOKENS))

		if source == "M":
			for i in range(len(fnoResult)):
				if len(fnoResult[i]["symbols"]) > 0:
					retUserwatchList[API_K_PREDEFINED_WATCHLIST].append(fnoResult[i])

		elif source == "W":
			for i in fnoResult:
				retUserwatchList[i[API_K_ID_1]] = i

		return [SUCCESS_C_1, [retUserwatchList, watchlistMaxSize], ""]
	
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, "", e, ERROR_C_UNKNOWN,"Line Number: %s"%str(exc_tb.tb_lineno))
		return [ERROR_C_1, ERROR_C_UNKNOWN, ""]
	finally:
		if "db" in locals():
			if db is not None and db != "":
				db.close()


# ##watchlist shift from db to s3 -  - Khyati - 20200120
# def getUserAllWatchList(fyId, s3client= None,callingFuncName=""):
# 	funcName = "getUserAllWatchList"
# 	userWlData = {}
# 	try:
# 		if s3client == None:
# 			s3client = boto3.client(AWS_SERVICE_S3)

# 		key = AWS_S3_FOLDER_PATH_USER_WATCHLIST + fyId + FILE_USER_WATCHLIST_SUFFIX
# 		s3object = s3client.get_object(Bucket = AWS_S3_BUCKET_USER_DATA, Key = key)

# 		if s3object['ResponseMetadata']['HTTPStatusCode'] != 200:
# 			return [ERROR_C_1, ERROR_C_S3_GET_FAILED, ERROR_M_S3_GET_FAILED]
# 		if s3object['ContentLength'] == 0:
# 			return [ERROR_C_1, ERROR_C_S3_GET_FAILED, ERROR_M_S3_GET_FAILED]

# 		s3_data = s3object['Body'].read()
# 		userWlData = json.loads(s3_data)

# 		# print ("getUserAllWatchList s3: ", userWlData)
# 		list1 = [wL for wL in userWlData]
# 		list2 = [userWlData[wL].get("slNo",0) for wL in list1]
# 		zipped_pairs = zip(list2, list1)
# 		list3 = [x for _, x in sorted(zipped_pairs)]
# 		userWlData1 = OrderedDict()
# 		for wl in list3:
# 			if not "slNo" in userWlData[wl]:
# 				userWlData[wl]["slNo"] = 0
# 			userWlData1[wl] = userWlData[wl]
# 		return [SUCCESS_C_1, userWlData1, ""]

# 	except ClientError as e:
# 		if e.response["Error"]["Code"] == "NoSuchKey":      #if never saved watchlists
# 			return [SUCCESS_C_1, userWlData, ""]
# 		else:
# 			exc_type, exc_obj, exc_tb = sys.exc_info()
# 			logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, e, ERROR_C_UNKNOWN,"Line Number: %s"%str(exc_tb.tb_lineno))
# 			return [ERROR_C_1, ERROR_C_UNKNOWN, str(e)]


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
			s3client = AWS_BOTO3_S3_CONNECTION
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


def INTERNAL_watchlistRemoveUnderscore(watchlist):
	if watchlist[1][API_K_WATCHLIST_NAME][:1] == '_':
		watchlist[1][API_K_WATCHLIST_NAME] = ' '+watchlist[1][API_K_WATCHLIST_NAME][1:]
	return watchlist[1]


# def INTERNAL_createWatchlistSymbolDict2(symbolDict2,symbolDict1):
# 	for i in range(0,len(symbolDict2['symbols'])):
# 		try:
# 			symbolDict = {}
# 			symbolDict["ex_sym"]                = symbolDict1[symbolDict2['symbols'][i]]["underSym"]
# 			symbolDict[API_K_EXCH]              = symbolDict1[symbolDict2['symbols'][i]]["exchangeName"]
# 			symbolDict[API_K_SYMDESCRIPTION]    = symbolDict1[symbolDict2['symbols'][i]]["symbolDesc"]
# 			symbolDict["expired"]               = True if symbolDict1[symbolDict2['symbols'][i]]["tradeStatus"] == 0 else False
# 			symbolDict[API_K_FY_TOKEN]          = symbolDict1[symbolDict2['symbols'][i]]["fyToken"]
# 			symbolDict["symbol"]                = symbolDict2['symbols'][i]
# 			symbolDict[API_K_DATA_PRICE_CHANGE] = 0.0
# 			symbolDict[API_K_DATA_PERC_CHANGE]  = 0.0
# 			symbolDict[API_K_DATA_LTP]          = 0.0
# 			symbolDict2["symbols"][i]           = symbolDict
# 		except Exception as e:
# 			exc_type, exc_obj, exc_tb = sys.exc_info()
# 			logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, "INTERNAL_createWatchlistSymbolDict2", "", e, ERROR_C_UNKNOWN,"Line Number: %s"%str(exc_tb.tb_lineno))
# 			symbolDict = {}
# 			symbolDict["ex_sym"]                = symbolDict2['symbols'][i]
# 			symbolDict[API_K_EXCH]              = ""
# 			symbolDict[API_K_SYMDESCRIPTION]    = ""
# 			symbolDict["expired"]               = True
# 			symbolDict[API_K_FY_TOKEN]          = ""
# 			symbolDict["symbol"]                = symbolDict2['symbols'][i]
# 			symbolDict[API_K_DATA_PRICE_CHANGE] = 0.0
# 			symbolDict[API_K_DATA_PERC_CHANGE]  = 0.0
# 			symbolDict[API_K_DATA_LTP]          = 0.0
# 			symbolDict2["symbols"][i]           = symbolDict
# 	return symbolDict2


def INTERNAL_createWatchlistSymbolDict3(symbolDict,invalidSymbols):
	# Remove expired symbols from the watchlists
	returnsymbolDict = {}
	returnsymbolDict["symbols"] = []
	returnsymbolDict["slNo"] = symbolDict["slNo"]
	returnsymbolDict["lut"] = symbolDict["lut"]
	returnsymbolDict["id"] = symbolDict["id"]
	returnsymbolDict["title"] = symbolDict["title"]
	for i in range(0,len(symbolDict['symbols'])):
		if symbolDict['symbols'][i]["symbol"] not in invalidSymbols:
			returnsymbolDict["symbols"].append(symbolDict['symbols'][i])
	return returnsymbolDict


def INTERNAL_predefinedWatchlists(predefList,localMemory,s3client):
	funcName = "INTERNAL_predefinedWatchlists"
	watchlistIdEnd = (predefList[0].replace(" ","")).lower()
	watchlistId = "%s%s" %(WATCHLIST_PREDEFINED_ID_STARTSWITH,watchlistIdEnd)

	getFuncRet = getPredefinedWatchlists(predefList[1], predefList[2], predefList[3], localMemory = localMemory, s3client=s3client)

	retPredefinedDict = {}

	if getFuncRet[0] != ERROR_C_1:
		retPredefinedDict = {
			API_K_WATCHLIST_NAME: "%s%s" %(WATCHLIST_PREDEFINED_NAME_STARTSWITH,predefList[0]),
			API_K_FYSYMBOLS: getFuncRet[1],
			API_K_ID_1: watchlistId,
			API_K_WATCHLIST_SOURCE: API_V_WATCHLIST_SOURCE_DEF,
		}
	else:
		retPredefinedDict = {
			API_K_WATCHLIST_NAME: "%s%s" %(WATCHLIST_PREDEFINED_NAME_STARTSWITH,predefList[0]),
			API_K_FYSYMBOLS: [],
			API_K_ID_1: watchlistId,
			API_K_WATCHLIST_SOURCE: API_V_WATCHLIST_SOURCE_DEF,
		}
	return retPredefinedDict


## To get Nifty predefined watchlists from Cache or S3 - 20191107 - Khyati
def getPredefinedWatchlists(s3file, cacheKey, index, localMemory=None,s3client=None, callingFuncName=''):
	funcName = "getPredefinedWatchlists"
	try:
		if localMemory == None:
			localMemory = connectRedis(callingFuncName=callingFuncName)
		predefinedCacheWL = localMemory.get(cacheKey)
		if predefinedCacheWL is not None:
			predefinedCacheWL = json.loads(predefinedCacheWL)
			return [SUCCESS_C_1, predefinedCacheWL, ""]
		predefinedList = []
		predefinedList.append(index)
		try:
			if s3client == None:
				s3client = AWS_BOTO3_S3_CONNECTION
			key = AWS_S3_FOLDER_PATH_PREDEF_WATCHLIST + s3file
			s3_object = s3client.get_object(Bucket = AWS_S3_BUCKET_USER_DATA, Key = key)
			if s3_object['ResponseMetadata']['HTTPStatusCode'] != 200:
				return [ERROR_C_1, ERROR_C_S3_GET_FAILED, ERROR_M_S3_GET_FAILED]
			if s3_object['ContentLength'] == 0:
				return [ERROR_C_1, ERROR_C_S3_GET_FAILED, ERROR_M_S3_GET_FAILED]
			s3_data = s3_object['Body'].read()
			s3_data = s3_data.decode("utf-8").splitlines(True)
			reader = csv.reader(s3_data)
			next(reader)

			for i in reader:
				symbol = "NSE:"+i[2]+"-"+i[3]
				predefinedList.append(symbol)

			localMemory.set(cacheKey, json.dumps(predefinedList), CACHE_WATCHLIST_EXPIRY)
			return [SUCCESS_C_1, predefinedList, ""]
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, e, ERROR_C_UNKNOWN,"Line Number: %s"%str(exc_tb.tb_lineno))
			return [ERROR_C_1, ERROR_C_UNKNOWN, ""]

	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, e, ERROR_C_UNKNOWN,"Line Number: %s"%str(exc_tb.tb_lineno))
		return [ERROR_C_1, ERROR_C_UNKNOWN, ""]


##Shift from db to s3 - 20200120 - Khyati -
def insertUpdateWatchList(fyId, userWatchListDict, s3client=None, callingFuncName=""):
	funcName = "insertUpdateWatchList"
	try:
		userwatchlistJson = json.dumps(userWatchListDict)
		if s3client == None:
			s3client = AWS_BOTO3_S3_CONNECTION
		
		key = AWS_S3_FOLDER_PATH_USER_WATCHLIST + fyId + FILE_USER_WATCHLIST_SUFFIX
		s3client.put_object(Body = userwatchlistJson, Bucket = AWS_S3_BUCKET_USER_DATA, Key = key)

		return [SUCCESS_C_1, "",""]
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, e, ERROR_C_UNKNOWN,"Line Number: %s"%str(exc_tb.tb_lineno))
		return [ERROR_C_1, ERROR_C_S3_GET_FAILED, ERROR_M_S3_UPDATE_FAILED]


def getNiftyIndices(cacheKey, localMemory = None,s3client=None, callingFuncName=''):
	funcName = "getNiftyIndices"
	try:
		if localMemory == None:
			localMemory = connectRedis(callingFuncName=callingFuncName)
		IndicesListCache = localMemory.get(cacheKey)
		if IndicesListCache is not None:
			IndicesListCache = json.loads(IndicesListCache)
			return [SUCCESS_C_1, IndicesListCache, ""]

		if s3client == None:
			s3client = AWS_BOTO3_S3_CONNECTION
		s3object = s3client.get_object(Bucket = AWS_S3_BUCKET_USER_DATA, Key = AWS_S3_FOLDER_PATH_WATCHLIST_INDICES)

		if s3object['ResponseMetadata']['HTTPStatusCode'] != 200:
			return [ERROR_C_1, ERROR_C_S3_GET_FAILED, ERROR_M_S3_GET_FAILED]
		if s3object['ContentLength'] == 0:
			return [ERROR_C_1, ERROR_C_S3_GET_FAILED, ERROR_M_S3_GET_FAILED]

		IndicesListJson = s3object['Body'].read()
		IndicesList = json.loads(IndicesListJson)

		localMemory.set(cacheKey, IndicesListJson, CACHE_WATCHLIST_EXPIRY)

		return [SUCCESS_C_1, IndicesList, ""]
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, e, ERROR_C_UNKNOWN,"Line Number: %s"%str(exc_tb.tb_lineno))
		return [ERROR_C_1, ERROR_C_UNKNOWN, ""]


def INTERNAL_predefined_WL_all(exchangeCode, segmentCode, instType, cacheKeyList, db=None, cursor=None, localMemory=None, callingFuncName=''):
	funcName = "INTERNAL_predefined_WL"
	try:
		if localMemory == None:
			localMemory = connectRedis(callingFuncName=callingFuncName)
		## Cache changes from push to set as list as duplicate values which creates error on predefined WL 20190925 Palash
		predefinedCacheWL = localMemory.mget(cacheKeyList)

		predefinedListMcx = []
		predefinedListNse = []

		if predefinedCacheWL[0] is not None:
			predefinedListNse = json.loads(predefinedCacheWL[0])
		if predefinedCacheWL[1] is not None:
			predefinedListMcx = json.loads(predefinedCacheWL[1])
		if predefinedListMcx == [] or predefinedListNse == []:
			logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName,exchangeCode, segmentCode, instType, cacheKeyList,predefinedListNse,predefinedListMcx,"watchlist not found in redis")
		return[SUCCESS_C_1, [predefinedListNse,predefinedListMcx], ""]
		##Not fetching the list of symbols from db if not present in redis - 20210817

	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, e, ERROR_C_UNKNOWN,"Line Number: %s"%str(exc_tb.tb_lineno))
		return [ERROR_C_1, ERROR_C_UNKNOWN, ""]


def INTERNAL_futuresContracts_all(cacheKey,cacheKey2,db=None, cursor=None, localMemory=None, callingFuncName=''):
	funcName = "INTERNAL_FOContracts"
	try:
		if cacheKey == CACHE_K_WL_NIFTYFUT:
			symList = WATCHLIST_PREDEFINED_SYMBOLS_NIFTY50
		elif cacheKey == CACHE_K_WL_BANKNIFTYFUT:
			symList = WATCHLIST_PREDEFINED_SYMBOLS_NIFTYBANK
		else:
			return [ERROR_C_1, ERROR_C_UNKNOWN, ""]

		instTypeSTK, instTypeIDX = SYM_INSTTYPE_FUTSTK, SYM_INSTTYPE_FUTIDX

		if localMemory == None:
			localMemory = connectRedis(callingFuncName=funcName)

		## Cache changes from push to set as list as duplicate values which creates error on predefined WL 20190925 Palash
		predefinedDict = {cacheKey:[]}
		predefinedCacheWL = localMemory.get(cacheKey)
		if predefinedCacheWL is not None:
			predefinedCacheWL = json.loads(predefinedCacheWL)
			predefinedDict[cacheKey] = predefinedCacheWL

		if predefinedDict[cacheKey] == []:
			logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName,cacheKey,"watchlist not found in redis")
		return predefinedDict
		##Not fetching the list of symbols from db if not present in redis - 20210817

	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, e, ERROR_C_UNKNOWN,"Line Number: %s"%str(exc_tb.tb_lineno))
		return [ERROR_C_1, ERROR_C_UNKNOWN, ""]


def getFnoWl(fnoWatchlist,db,cursor,localMemory):
	# Get the required expiry as per the defines
	funcName = "getFnoWl"
	watchlistIdFO = "%s%s" % (WATCHLIST_PREDEFINED_ID_STARTSWITH, fnoWatchlist[3].replace(" ","").lower())
	returnDict = {
					API_K_WATCHLIST_NAME: "%s%s" %(WATCHLIST_PREDEFINED_NAME_STARTSWITH,fnoWatchlist[3]),
					API_K_FYSYMBOLS: [],
					API_K_ID_1: watchlistIdFO,
					API_K_WATCHLIST_SOURCE: API_V_WATCHLIST_SOURCE_DEF,
				}
	funcRet2 = internal_getExpiryForUnderlying(fnoWatchlist[0],fnoWatchlist[1],fnoWatchlist[2],db=db,cursor=cursor, localMemory=localMemory,callingFuncName=funcName)
	if funcRet2[0] != ERROR_C_1:
		# For the particular expiry, create the watchlist
		funcRet3 = internal_watchlist_createFnoContracts(fnoWatchlist[0],funcRet2[1],db=db,cursor=cursor,localMemory=localMemory,callingFuncName=funcName,underlyingSymbol=fnoWatchlist[4])
		if funcRet3[0] != ERROR_C_1:
			returnDict[API_K_FYSYMBOLS] = funcRet3[1]
	return returnDict


def internal_watchlist_createFnoContracts(underlyingFyToken, expiryDate, db=None, cursor=None, localMemory=None,callingFuncName="",underlyingSymbol=None):
	funcName = "internal_watchlist_createFnoContracts"
	try:
		# Check if the predefined watchlist already exists in the cache itself
		if localMemory == None:
			localMemory = connectRedis(callingFuncName=callingFuncName)
		watchlistSymbolsCacheKey = "%s_%s_%s" % (underlyingFyToken, expiryDate, CACHE_K_WATCHLIST_PREDEFINED_FNO)
		## Cache changes from push to set as list as duplicate values which creates error on predefined WL 20190925 Palash
		predefinedWatchlistGet = localMemory.get(watchlistSymbolsCacheKey)
		if predefinedWatchlistGet is not None:
			predefinedWatchlistGet = json.loads(predefinedWatchlistGet)
			return [SUCCESS_C_1,predefinedWatchlistGet,""]
		else:
			return [ERROR_C_1,"",""]
		##Not fetching the list of symbols from db if not present in redis - 20210817

	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, e, ERROR_C_UNKNOWN,"Line Number: %s"%str(exc_tb.tb_lineno))
		return [ERROR_C_1, ERROR_C_UNKNOWN, ""]