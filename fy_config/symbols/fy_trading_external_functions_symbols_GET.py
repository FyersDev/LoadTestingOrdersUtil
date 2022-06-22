moduleName = "fy_trading_external_functions_symbols_GET"
try:
	import sys
	import logging

	from fy_base_api_keys_values import API_K_STATUS, API_V_ERROR, API_K_CODE, \
	 API_V_SUCCESS
	from fy_base_success_error_codes import SUCCESS_C_1, \
	 ERROR_C_UNKNOWN
	from fy_base_defines import LOG_STATUS_ERROR_1
	from fy_common_api_keys_values import API_K_SYM_INFO_DICT, API_K_ERRMSG

	from fy_base_functions import logEntryFunc2
	from fyers_logger import FyersLogger
	from symbols.fy_trading_internal_functions_symbols_GET import INTERNAL_getAllSymInfo

except Exception as e:
	print ("ERR : %s : %s : %s" % (moduleName, "Could not import module", e))
	sys.exit()

fy_logger = FyersLogger("ALB_LAMBDA", "DEBUG", logger_handler=logging.FileHandler("albEC2.log"))


def fy_getAllSymInfo():
	"""
		[FUNCTION]
			Get the symbol info for each contract
		[PARAMS]

		[RETURN]
			Success : json output({})
			Failure :
	"""
	funcName = "fy_getAllSymInfo"
	try:
		funcRetList = INTERNAL_getAllSymInfo(exchange=0,callingFuncName=funcName)
		if funcRetList[0] == SUCCESS_C_1:
			returnDict = {API_K_STATUS: API_V_SUCCESS, API_K_SYM_INFO_DICT: funcRetList[1]}
			return returnDict

		returnDict = {API_K_STATUS: API_V_ERROR, API_K_CODE: funcRetList[1],API_K_ERRMSG: funcRetList[2]}
		return returnDict

	except Exception as e:
		logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, "", e, ERROR_C_UNKNOWN)
		returnDict = {API_K_STATUS: API_V_ERROR, API_K_CODE: ERROR_C_UNKNOWN,API_K_ERRMSG: ""}
		return returnDict


def main():
	pass  # test here


if __name__ == "__main__":
	main()
