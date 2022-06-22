moduleName = "fy_auth_functions"
try:
	import sys

except Exception as e:
	print("ERR : %s : %s : %s" % (moduleName, "Could not import module", e))

try:
	from fy_auth_defines import JWT_DEFAULT_AUDIENCE_APPID, \
     COOKIE_NAME_MAIN_1, JWT_CLAIMS_K_TOKEN_HASH
	from fy_base_api_keys_values import API_K_COOKIE, API_K_TOKENHASH, \
	 API_K_STATUS, API_V_ERROR, API_K_CODE, API_K_MSG, API_V_SUCCESS, \
	 API_K_DATA_1
	from fy_base_success_error_codes import ERROR_C_1, SUCCESS_C_1, \
	 ERROR_C_UNKNOWN, ERROR_C_INV_COOKIE, \
	 ERROR_C_INV_INP, ERROR_C_COOKIE_INV_LENGTH, \
	 ERROR_C_INVALID_TOKEN_6
	from fy_base_defines import LOG_STATUS_ERROR_1
	from fy_base_success_error_messages import ERROR_M_INV_COOKIE, \
	 ERROR_M_COOKIE_INV_1

	import vagator_auth_check
	from fy_base_functions import get_logger, logEntryFunc2


except Exception as e:
	print("ERR : %s : %s : %s" % (moduleName, "Could not import module", e))
	sys.exit()


def initial_validate_access_token(kwargs, callingFuncName="", snapshot_flag=False):
	funcName = "initial_validate_access_token"
	try:
		if API_K_COOKIE not in kwargs and API_K_TOKENHASH not in kwargs:
			returnDict = {API_K_STATUS: API_V_ERROR, API_K_CODE: ERROR_C_INV_COOKIE, API_K_MSG: ERROR_M_INV_COOKIE}
			return returnDict

		if len(kwargs[API_K_COOKIE]) > 0:
			token = kwargs[API_K_COOKIE]
			if snapshot_flag:
				# Added the chek for cookie/token
				extractFyersCookie=True

		elif len(kwargs[API_K_TOKENHASH]) > 0:
			token = kwargs[API_K_TOKENHASH]
			if snapshot_flag:
				# Added the chek for cookie/token
				extractFyersCookie=False

		else:
			returnDict = {API_K_STATUS: API_V_ERROR, API_K_CODE: ERROR_C_INV_INP, API_K_MSG: ERROR_M_INV_COOKIE}
			return returnDict
			
		#import pdb; pdb.set_trace()

		if snapshot_flag:
			validateCookie = INTERNAL_validateCookie(token, callingFuncName=callingFuncName, extractFyersCookie=extractFyersCookie)
		else:
			validateCookie = INTERNAL_validateCookie(token, callingFuncName=callingFuncName)

		if validateCookie[0] == ERROR_C_1:
			returnDict = {API_K_STATUS: API_V_ERROR, API_K_CODE: validateCookie[1],API_K_MSG: validateCookie[2]}
			return returnDict
		tokenHash = validateCookie[1][JWT_CLAIMS_K_TOKEN_HASH].strip()
		fyId = validateCookie[1]["fy_id"].strip()
		get_logger().set_fyId(fyId)
		# funcResult = redis_func.set_fyid_count(callingFuncName, fyId=fyId)
		# if funcResult[1] == 429:
		# 	returnDict = {API_K_STATUS: API_V_ERROR, API_K_CODE: funcResult[1], API_K_MSG: funcResult[2]}
		# 	return returnDict

		return {API_K_STATUS: API_V_SUCCESS, API_K_DATA_1: [tokenHash, fyId]}

	except Exception as e:
		logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, "", e, ERROR_C_UNKNOWN, kwargs)
		returnDict = {API_K_STATUS: API_V_ERROR, API_K_CODE: ERROR_C_UNKNOWN,
					  API_K_MSG: str(e)}
		return returnDict


def INTERNAL_validateCookie(cookieString, appAudience=JWT_DEFAULT_AUDIENCE_APPID, callingFuncName="", extractFyersCookie=False):
	funcName = "INTERNAL_validateCookie"
	try:
		#import pdb; pdb.set_trace()
		if extractFyersCookie:
			if len(cookieString) <= 0:
				return [ERROR_C_1, ERROR_C_COOKIE_INV_LENGTH, ERROR_M_COOKIE_INV_1]
			cookieString = cookieString.strip()
			cookiesList = cookieString.split(";")
			fyersCookie = ""
			for i in cookiesList:
				i = i.strip()
				i = i.replace(' ','')
				if i.startswith("%s=" % COOKIE_NAME_MAIN_1):
					fyersCookie = i[len("%s=" % COOKIE_NAME_MAIN_1):]
					break

			res = vagator_auth_check.INTERNAL_validate_access_token(fyersCookie)

		else:
			res = vagator_auth_check.INTERNAL_validate_access_token(cookieString)

		if res[0] == SUCCESS_C_1 and res[4]["user_loggedin"]:
			return [SUCCESS_C_1, res[4]["decoded_access"], ""]
		
		return [ERROR_C_1, ERROR_C_INVALID_TOKEN_6, ERROR_M_COOKIE_INV_1]

	except Exception as e:
		logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName,
					  callingFuncName, e, ERROR_C_UNKNOWN,
					  cookieString)
		return [ERROR_C_1, ERROR_C_INVALID_TOKEN_6, ERROR_M_COOKIE_INV_1]


def main():
	pass  # test here


if __name__ == "__main__":
	main()
