moduleName = "fy_watchlist_common_functions"

try:
	import sys
	import boto3
	from botocore.exceptions import ClientError
	from collections import OrderedDict
	import json

	from fy_connections_defines import AWS_SERVICE_S3, AWS_S3_FOLDER_PATH_USER_WATCHLIST, \
	 FILE_USER_WATCHLIST_SUFFIX, AWS_BOTO3_S3_CONNECTION
	from fy_base_success_error_codes import ERROR_C_1, SUCCESS_C_1, \
     ERROR_C_UNKNOWN, ERROR_C_S3_GET_FAILED
	from fy_base_success_error_messages import ERROR_M_S3_GET_FAILED, \
	 ERROR_M_S3_UPDATE_FAILED
	from fy_base_defines import LOG_STATUS_ERROR_1
	from fy_connections_defines import AWS_S3_BUCKET_USER_DATA
	from fy_common_api_keys_values import API_K_SYMDESCRIPTION, \
	 API_K_FY_TOKEN, API_K_DATA_PRICE_CHANGE, API_K_DATA_PERC_CHANGE, \
	 API_K_DATA_LTP, API_K_EXCH
	from fy_data_and_trade_defines import CUSTOM_WATCHLISTS_KEY
	from helper import getSecondsToNextDayTillSix

	from fy_base_functions import logEntryFunc2
	from fy_connections import connectRedis

except Exception as e:
	print("ERR : %s : %s : %s" % (moduleName, "Could not import module", e))
	sys.exit()

# watchlist shift from db to s3 -  - Khyati - 20200120
def getUserAllWatchList(fyId, s3client= None,callingFuncName=""):
	funcName = "getUserAllWatchList"
	userWlData = {}
	try:
		localMemory = connectRedis(callingFuncName=funcName)
		
		# Check if we are able to get custom watchlists from redis
		redis_watchlist_key = CUSTOM_WATCHLISTS_KEY + '-' + fyId
		s3_data = localMemory.get(redis_watchlist_key)
		if s3_data is None: 
			if s3client == None:
				s3client = AWS_BOTO3_S3_CONNECTION

			key = AWS_S3_FOLDER_PATH_USER_WATCHLIST + fyId + FILE_USER_WATCHLIST_SUFFIX
			s3object = s3client.get_object(Bucket = AWS_S3_BUCKET_USER_DATA, Key = key)

			if s3object['ResponseMetadata']['HTTPStatusCode'] != 200:
				return [ERROR_C_1, ERROR_C_S3_GET_FAILED, ERROR_M_S3_GET_FAILED]
			if s3object['ContentLength'] == 0:
				return [ERROR_C_1, ERROR_C_S3_GET_FAILED, ERROR_M_S3_GET_FAILED]

			s3_data = s3object['Body'].read()

			# Get seconds till next day 6:00 AM
			expiry_time_resp = getSecondsToNextDayTillSix(callingFuncName=funcName)
			if expiry_time_resp[0] != SUCCESS_C_1:
				return expiry_time_resp
			expiry_time = expiry_time_resp[1]

			# Set custom watchlist data in redis
			localMemory.set(redis_watchlist_key, s3_data, expiry_time)

		userWlData = json.loads(s3_data)

		# print ("getUserAllWatchList s3: ", userWlData)
		list1 = [wL for wL in userWlData]
		list2 = [userWlData[wL].get("slNo",0) for wL in list1]
		zipped_pairs = zip(list2, list1)
		list3 = [x for _, x in sorted(zipped_pairs)]
		userWlData1 = OrderedDict()
		for wl in list3:
			if not "slNo" in userWlData[wl]:
				userWlData[wl]["slNo"] = 0
			userWlData1[wl] = userWlData[wl]
		return [SUCCESS_C_1, userWlData1, ""]

	except ClientError as e:
		if e.response["Error"]["Code"] == "NoSuchKey":      #if never saved watchlists
			return [SUCCESS_C_1, userWlData, ""]
		else:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, e, ERROR_C_UNKNOWN,"Line Number: %s"%str(exc_tb.tb_lineno))
			return [ERROR_C_1, ERROR_C_UNKNOWN, str(e)]


def INTERNAL_createWatchlistSymbolDict2(symbolDict2,symbolDict1):
	for i in range(0,len(symbolDict2['symbols'])):
		try:
			symbolDict = {}
			symbolDict["ex_sym"]                = symbolDict1[symbolDict2['symbols'][i]]["underSym"]
			symbolDict[API_K_EXCH]              = symbolDict1[symbolDict2['symbols'][i]]["exchangeName"]
			symbolDict[API_K_SYMDESCRIPTION]    = symbolDict1[symbolDict2['symbols'][i]]["symbolDesc"]
			symbolDict["expired"]               = True if symbolDict1[symbolDict2['symbols'][i]]["tradeStatus"] == 0 else False
			symbolDict[API_K_FY_TOKEN]          = symbolDict1[symbolDict2['symbols'][i]]["fyToken"]
			symbolDict["symbol"]                = symbolDict2['symbols'][i]
			symbolDict[API_K_DATA_PRICE_CHANGE] = 0.0
			symbolDict[API_K_DATA_PERC_CHANGE]  = 0.0
			symbolDict[API_K_DATA_LTP]          = 0.0
			symbolDict2["symbols"][i]           = symbolDict
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, "INTERNAL_createWatchlistSymbolDict2", "", e, ERROR_C_UNKNOWN,"Line Number: %s"%str(exc_tb.tb_lineno))
			symbolDict = {}
			symbolDict["ex_sym"]                = symbolDict2['symbols'][i]
			symbolDict[API_K_EXCH]              = ""
			symbolDict[API_K_SYMDESCRIPTION]    = ""
			symbolDict["expired"]               = True
			symbolDict[API_K_FY_TOKEN]          = ""
			symbolDict["symbol"]                = symbolDict2['symbols'][i]
			symbolDict[API_K_DATA_PRICE_CHANGE] = 0.0
			symbolDict[API_K_DATA_PERC_CHANGE]  = 0.0
			symbolDict[API_K_DATA_LTP]          = 0.0
			symbolDict2["symbols"][i]           = symbolDict
	return symbolDict2


def insertUpdateWatchList(fyId, userWatchListDict, s3client=None, callingFuncName=""):
	funcName = "insertUpdateWatchList"
	try:
		localMemory = connectRedis(callingFuncName=funcName)
		redis_watchlist_key = CUSTOM_WATCHLISTS_KEY + '-' + fyId

		userwatchlistJson = json.dumps(userWatchListDict)
		if s3client == None:
			s3client = AWS_BOTO3_S3_CONNECTION
		
		key = AWS_S3_FOLDER_PATH_USER_WATCHLIST + fyId + FILE_USER_WATCHLIST_SUFFIX
		s3client.put_object(Body = userwatchlistJson, Bucket = AWS_S3_BUCKET_USER_DATA, Key = key)

		# Get seconds till next day 6:00 AM
		expiry_time_resp = getSecondsToNextDayTillSix(callingFuncName=funcName)
		if expiry_time_resp[0] != SUCCESS_C_1:
			return expiry_time_resp
		expiry_time = expiry_time_resp[1]
		
		# Store updated custom watchlists in redis
		localMemory.set(redis_watchlist_key, userwatchlistJson, expiry_time)

		return [SUCCESS_C_1, "",""]
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, e, ERROR_C_UNKNOWN,"Line Number: %s"%str(exc_tb.tb_lineno))
		return [ERROR_C_1, ERROR_C_S3_GET_FAILED, ERROR_M_S3_UPDATE_FAILED]