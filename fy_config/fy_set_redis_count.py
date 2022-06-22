moduleName = "fy_set_redis_count"

import datetime
import json
import time
import pytz
import os

from fy_base_defines import LOG_STATUS_ERROR_1
from fy_base_success_error_codes import ERROR_C_1, ERROR_C_UNKNOWN, \
 SUCCESS_C_1

import fy_auth_functions as auth_func
from fy_base_functions import logEntryFunc2
from fy_connections import connectRedis


AWS_LAMBDA_FUNCTION_NAME = os.environ.get("AWS_LAMBDA_FUNCTION_NAME")

def incr_redis_field(route,reqMethod):

	funcName = "incr_redis_field"
	try:
		localMemory = connectRedis(callingFuncName=funcName)
		route = "/".join(route)
		redisKeyField = route.lower()+"-"+reqMethod.lower()

		key = f"Lambda-Load-{AWS_LAMBDA_FUNCTION_NAME}"
		localMemory.hincrby(key,redisKeyField)
		localMemory.hincrby(key,"total")

		todaydate = datetime.datetime.now(pytz.timezone("Asia/Calcutta")).date()
		todaydate2 = int(time.mktime(todaydate.timetuple())) + 66600
		localMemory.expireat(key,todaydate2)

	except Exception as e:
		logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, "", e,ERROR_C_UNKNOWN,route,reqMethod)
		return [ERROR_C_1, ERROR_C_UNKNOWN, ""]

def set_fyid_count(functionName,fyId=None,tokenHash=None,localMemory=None):
	funcName = "set_fyid_count"
	try:
		if localMemory == None:
			localMemory = connectRedis(callingFuncName=funcName)

		if AWS_LAMBDA_FUNCTION_NAME == "fy-mobile-prod-v2":
			key1 = "Fy-Lambda-Load-Mobile-v2"
			key2 = "-mobile-limit-v2"
		elif AWS_LAMBDA_FUNCTION_NAME == "Fyers-ALB-fy-v2":
			key1 = "Fy-Lambda-Load-Web-v2"
			key2 = "-web-limit-v2"
		elif AWS_LAMBDA_FUNCTION_NAME == "Fyers-ALB-dev-v1":
			key1 = "Fy-Lambda-Load-dev-v1"
			key2 = "-webmobile-limit"
		else:
			key1 = "Fy-Lambda-Load-Other-v2"
			key2 = "-other-limit-v2"

		key1 = f"FyId-Lambda-Load-{AWS_LAMBDA_FUNCTION_NAME}"

		if fyId == None:
			tokenList = auth_func.INTERNAL_splitTokenHash(tokenHash,callingFuncName=funcName)
			if tokenList[0] == ERROR_C_1:
				localMemory.hincrby(key1,"Invalid")
				return tokenList

			fyId, appId, token, inputTokenHash = tokenList[1]

		redisKeyField = fyId
		localMemory.hincrby(key1,redisKeyField)
		localMemory.hincrby(key1,"total")

		todaydate = datetime.datetime.now(pytz.timezone("Asia/Calcutta")).date()
		todaydate2 = int(time.mktime(todaydate.timetuple())) + 66600
		localMemory.expireat(key1,todaydate2)

		rateLimitKey1 = fyId + key2

		todaydate3 = todaydate2 - int(time.time())

		funcRet = rate_limiter(rateLimitKey1,localMemory,functionName,todaydate3,fyId)
		if funcRet[0] == ERROR_C_1:
			return funcRet
		return [SUCCESS_C_1,fyId,""]

	except Exception as e:
		logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, "", e,ERROR_C_UNKNOWN,tokenHash,functionName)
		return [ERROR_C_1, ERROR_C_UNKNOWN, ""]

def rate_limiter(key,localMemory,functionName,expiry,fyId):
	funcName = "rate_limiter"
	try:
		
		###Rate Limit Per Day

		internal_limit_day = 30000

		if localMemory.exists(key) != 0:
			count = int(localMemory.get(key))
			
			if count >= internal_limit_day:
				ttl = localMemory.ttl(key)
				if ttl == None or ttl > expiry or ttl == -1:
					localMemory.set(key, 1, expiry)
					count = 1
			if count < internal_limit_day:
				localMemory.incr(key)
				return [SUCCESS_C_1, "", ""]
			else:
				logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, functionName, ERROR_C_1,429,"rate limit exceed",key,fyId)
				localMemory.set(key, 1, expiry)
				exceedRateLimit = []
				redisget = localMemory.get("ratelimitexceeded")
				if redisget != None:
					exceedRateLimit = json.loads(redisget)
				exceedRateLimit.append(key)
				localMemory.set("ratelimitexceeded", json.dumps(exceedRateLimit))
				return [SUCCESS_C_1, "", ""]
		else:
			localMemory.set(key,1,expiry)
			return [SUCCESS_C_1, "", ""]

	except Exception as e:
		logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, "", e,ERROR_C_UNKNOWN,key,functionName,fyId)
		return [ERROR_C_1, ERROR_C_UNKNOWN, ""]


