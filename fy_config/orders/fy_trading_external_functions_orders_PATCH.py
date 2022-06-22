moduleName = "fy_trading_external_functions_orders_PATCH"
try:
	import sys
	import logging

	from fy_base_api_keys_values import API_K_STATUS, API_V_ERROR, API_K_CODE, \
	 API_K_DATA_1, API_V_SUCCESS, API_K_MSG
	from fy_base_success_error_codes import ERROR_C_UNKNOWN, \
	 ERROR_C_1, ERROR_C_OMS_1
	from fy_base_success_error_messages import SUCCESS_M_ORDER_MODIFIED_1
	from fy_base_defines import LOG_STATUS_ERROR_1, LOG_STATUS_SUCCESS_1
	from fy_common_api_keys_values import API_K_USER_IP, API_K_ORDER_ID
	from fy_trading_defines import API_K_DICT_ORDER_MODIFY, \
     API_OMS_V_ORDER_PROD_CO_2, API_OMS_V_ORDER_PROD_BO_2

	from fy_auth_functions import initial_validate_access_token
	from fy_base_functions import logEntryFunc2
	from fyers_logger import FyersLogger
	from orders.fy_trading_internal_functions_orders_PATCH import INTERNAL_modifyCoverOrder, \
     INTERNAL_modifyBracketOrder, INTERNAL_modifyOrder_withID

except Exception as e:
	print ("ERR : %s : %s : %s" % (moduleName, "Could not import module", e))
	sys.exit()

fy_logger = FyersLogger("ALB_LAMBDA", "DEBUG", logger_handler=logging.FileHandler("albEC2.log"))


def fy_modifyOrder(kwargs):
	"""
		[FUNCTION]
			Modify the order based on the type of the order
		[PARAMS] => Key value arguments
			cookie  : This is the JWT string which has been saved in Fyers cookie
			....
		[RETURN]
			Success :
			Failure :
	"""
	funcName = "fy_modifyOrder"
	try:
		for i in API_K_DICT_ORDER_MODIFY.keys():
			if not i in kwargs:
				returnDict = {API_K_STATUS: API_V_ERROR, API_K_CODE: API_K_DICT_ORDER_MODIFY[i][0],
							  API_K_MSG: API_K_DICT_ORDER_MODIFY[i][1]}
				return (returnDict)

		funcRet = initial_validate_access_token(kwargs, callingFuncName=funcName)
		if funcRet[API_K_STATUS] == API_V_ERROR:
			return funcRet

		tokenHash = funcRet[API_K_DATA_1][0]
		fyId = funcRet[API_K_DATA_1][1]
		fy_logger.set_fyId(fyId)

		orderNumber = kwargs[API_K_ORDER_ID]

		logEntryFunc2(LOG_STATUS_SUCCESS_1, moduleName, funcName,"",kwargs, fyId=fyId)

		userIp = ""
		if API_K_USER_IP in kwargs:
			userIp = kwargs[API_K_USER_IP]

		# If it is a cover order
		if API_OMS_V_ORDER_PROD_CO_2 in orderNumber:
			funcRetList = INTERNAL_modifyCoverOrder(tokenHash,orderNumber,kwargs,callingFuncName=funcName,userIp=userIp)
		# If bracket order
		elif API_OMS_V_ORDER_PROD_BO_2 in orderNumber:
			funcRetList = INTERNAL_modifyBracketOrder(tokenHash, orderNumber, kwargs, callingFuncName=funcName,userIp=userIp)
		else:
			funcRetList = INTERNAL_modifyOrder_withID(tokenHash, orderNumber, kwargs,callingFuncName=funcName,userIp=userIp)

		if (funcRetList[0] == ERROR_C_1) or (funcRetList[0] == ERROR_C_OMS_1):
			returnDict = {API_K_STATUS: API_V_ERROR, API_K_CODE: funcRetList[1],
						  API_K_MSG: funcRetList[2], API_K_ORDER_ID: orderNumber}
			return (returnDict)

		returnDict = {API_K_STATUS: API_V_SUCCESS, API_K_CODE: funcRetList[1],
					  API_K_MSG: SUCCESS_M_ORDER_MODIFIED_1, API_K_ORDER_ID: orderNumber}
		return (returnDict)

	except Exception as e:
		logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, "", e, ERROR_C_UNKNOWN, kwargs)
		returnDict = {API_K_STATUS: ERROR_C_1, API_K_CODE: ERROR_C_UNKNOWN, API_K_MSG: e}
		return (returnDict)


def main():
	pass  # Test here


if __name__ == "__main__":
	main()
