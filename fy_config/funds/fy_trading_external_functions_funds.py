moduleName = "fy_trading_external_functions_funds"
try:
	import sys
	import logging

	from fy_base_api_keys_values import API_K_STATUS, API_V_ERROR, API_K_CODE, \
	 API_K_DATA_1, API_V_SUCCESS, API_K_MSG
	from fy_base_success_error_codes import SUCCESS_C_1, SUCCESS_C_2, \
	 ERROR_C_UNKNOWN
	from fy_base_defines import LOG_STATUS_ERROR_1
	from fy_common_api_keys_values import API_K_FUND_LIMIT, API_K_USER_IP

	from fy_config.funds.fy_trading_internal_functions_funds import INTERNAL_getFundLimit4
	from fy_auth_functions import initial_validate_access_token
	from fy_base_functions import logEntryFunc2
	from fyers_logger import FyersLogger

except Exception as e:
	print("ERR : %s : %s : %s" % (moduleName, "Could not import module", e))
	sys.exit()

fy_logger = FyersLogger("ALB_LAMBDA", "DEBUG", logger_handler=logging.FileHandler("albEC2.log"))


def fy_getFundLimit(kwargs):
	"""
		[FUNCTION]
			Get the user's fund limit
		[PARAMS] => Key value arguments
			cookie  : This is the JWT string which has been saved in Fyers cookie
		[RETURN]
			Success    : [1,Dict]     = The second element is a dictionary of entire fund limit status
								= Dict[limitType] => "CAPITAL/COMMODITY"
									{"limitSod":#,
									"limitAdhoc":#,
									"limitRecv":#,
									"limitBankHld":#,
									"limitCollaterals":#,
									"limitRealizedPnl":#,
									"limitUtilized":#,
									"limitClearBal":#,
									"limitSum":#,
									"limitAvailBal":#}

			Failure :
	"""
	funcName = "fy_getFundLimit"
	try:
		funcRet = initial_validate_access_token(kwargs, callingFuncName=funcName)
		if funcRet[API_K_STATUS] == API_V_ERROR:
			return funcRet

		# tokenHash = "gAAAAABiZiFUfreFD1v5qp-1TkCRiRIO4xwwfpUwcbDpBpvytLPFiZhKDwFSVK3h0u6dpch3PjefZR1WnHE_K9ewJ-vnHIi33SYZGk2NjUy3FFUIiXK1vwU="
		# fyId = "XV01179"
		tokenHash = funcRet[API_K_DATA_1][0]
		fyId = funcRet[API_K_DATA_1][1]
		fy_logger.set_fyId(fyId)


		userIp = ""
		if API_K_USER_IP in kwargs:
			userIp = kwargs[API_K_USER_IP]

		funcRetList = INTERNAL_getFundLimit4(tokenHash, callingFuncName=funcName, userIp=userIp)
		if funcRetList[0] == SUCCESS_C_1:
			retDict = {API_K_STATUS: API_V_SUCCESS, API_K_MSG: "", API_K_FUND_LIMIT: funcRetList[1],API_K_CODE:SUCCESS_C_2}
			return retDict

		# If nothing else gets triggered this will get triggered
		returnDict = {API_K_STATUS: API_V_ERROR, API_K_CODE: funcRetList[1], API_K_MSG: funcRetList[2]}
		return returnDict

	except Exception as e:
		logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, "", e,ERROR_C_UNKNOWN, kwargs)
		returnDict = {API_K_STATUS: API_V_ERROR, API_K_CODE: ERROR_C_UNKNOWN, API_K_MSG: e}
		return returnDict


def main():
	pass  # Do testing here


if __name__ == "__main__":
	main()
