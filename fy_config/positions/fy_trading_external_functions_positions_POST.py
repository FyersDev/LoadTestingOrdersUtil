moduleName = "fy_trading_external_functions_positions_POST"
try:
	import sys
	import logging

	from fy_base_api_keys_values import API_K_STATUS, API_V_ERROR, API_K_CODE, \
	 API_K_DATA_1, API_V_SUCCESS, API_K_MSG, API_K_COOKIE, API_K_TOKENHASH
	from fy_base_success_error_codes import SUCCESS_C_2, \
	 ERROR_C_UNKNOWN, ERROR_C_INV_COOKIE, ERROR_C_INV_INP, ERROR_C_1, ERROR_C_OMS_1
	from fy_base_success_error_messages import ERROR_M_INV_COOKIE, ERROR_M_INV_FYSYMBOL, \
     ERROR_M_INV_POSITION_SIDE, ERROR_M_INV_CONVERT_QTY, ERROR_M_INV_ORDER_PRODUCT
	from fy_base_defines import LOG_STATUS_ERROR_1
	from fy_common_api_keys_values import API_K_USER_IP, API_K_CONVERT_POSITION_DETAILS, \
	 API_K_ORDER_PROD_CONVERT_FROM, API_K_ORDER_PROD_CONVERT_TO, API_K_FYSYMBOL, \
	 API_K_POSITION_SIDE, API_K_CONVERT_QTY

	from fy_auth_functions import initial_validate_access_token
	from fy_base_functions import logEntryFunc2
	from fyers_logger import FyersLogger
	from fy_config.positions.fy_trading_internal_functions_positions_POST import INTERNAL_omsConvertPosition

except Exception as e:
	print ("ERR : %s : %s : %s" % (moduleName, "Could not import module", e))
	sys.exit()

fy_logger = FyersLogger("ALB_LAMBDA", "DEBUG", logger_handler=logging.FileHandler("albEC2.log"))


def fy_convertPosition(kwargs):
	funcName = "fy_convertPosition"
	try:
		# Validation for tokenhash added - Khyati
		if API_K_COOKIE not in kwargs and API_K_TOKENHASH not in kwargs:
			return {API_K_STATUS: API_V_ERROR, API_K_CODE: ERROR_C_INV_COOKIE, API_K_MSG: ERROR_M_INV_COOKIE}

		if API_K_FYSYMBOL not in kwargs:
			return {API_K_STATUS: API_V_ERROR, API_K_CODE: ERROR_M_INV_FYSYMBOL, API_K_MSG: ERROR_M_INV_FYSYMBOL}

		if API_K_POSITION_SIDE not in kwargs:
			return {API_K_STATUS: API_V_ERROR, API_K_CODE: ERROR_C_INV_INP, API_K_MSG: ERROR_M_INV_POSITION_SIDE}

		if API_K_CONVERT_QTY not in kwargs:
			return {API_K_STATUS: API_V_ERROR, API_K_CODE: ERROR_C_INV_INP, API_K_MSG: ERROR_M_INV_CONVERT_QTY}

		if API_K_ORDER_PROD_CONVERT_FROM not in kwargs:
			return {API_K_STATUS: API_V_ERROR, API_K_CODE: ERROR_C_INV_INP, API_K_MSG: ERROR_M_INV_ORDER_PRODUCT}

		if API_K_ORDER_PROD_CONVERT_TO not in kwargs:
			return {API_K_STATUS: API_V_ERROR, API_K_CODE: ERROR_C_INV_INP, API_K_MSG: ERROR_M_INV_ORDER_PRODUCT}

		userIp = ""
		if API_K_USER_IP in kwargs:
			userIp = kwargs[API_K_USER_IP]

		funcRet = initial_validate_access_token(kwargs, callingFuncName=funcName)
		if funcRet[API_K_STATUS] == API_V_ERROR:
			return funcRet

		tokenHash = funcRet[API_K_DATA_1][0]
		fyId = funcRet[API_K_DATA_1][1]
		fy_logger.set_fyId(fyId)

		funcRet = INTERNAL_omsConvertPosition(tokenHash, kwargs[API_K_FYSYMBOL], kwargs[API_K_POSITION_SIDE], kwargs[API_K_CONVERT_QTY], kwargs[API_K_ORDER_PROD_CONVERT_FROM], kwargs[API_K_ORDER_PROD_CONVERT_TO], funcName,userIp=userIp)
		if funcRet[0] == ERROR_C_1 or funcRet[0] == ERROR_C_OMS_1:
			return {API_K_STATUS: API_V_ERROR, API_K_CODE: funcRet[1], API_K_MSG: funcRet[2]}
		return {API_K_STATUS: API_V_SUCCESS, API_K_CONVERT_POSITION_DETAILS: funcRet[1], API_K_MSG: funcRet[2],API_K_CODE:SUCCESS_C_2}
	except Exception as e:
		logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, "", e, ERROR_C_UNKNOWN, kwargs)
		returnDict = {API_K_STATUS: API_V_ERROR, API_K_CODE: ERROR_C_UNKNOWN, API_K_MSG: e}
		return (returnDict)


def main():
	pass  # Test here	


if __name__ == "__main__":
	main()
