moduleName = "fy_trading_external_functions_orders_DELETE"
try:
	import sys
	import logging

	from fy_base_api_keys_values import API_K_STATUS, API_V_ERROR, API_K_CODE, \
	 API_K_DATA_1, API_V_SUCCESS, API_K_MSG
	from fy_base_success_error_codes import ERROR_C_UNKNOWN, \
	 ERROR_C_1, ERROR_C_OMS_1
	from fy_base_success_error_messages import SUCCESS_M_ORDER_CANCELLED_1
	from fy_base_defines import LOG_STATUS_ERROR_1, LOG_STATUS_SUCCESS_1
	from fy_common_api_keys_values import API_K_USER_IP, API_K_ORDER_ID 
	from fy_trading_defines import API_K_DICT_ORDER_CANCEL, API_OMS_V_ORDER_PROD_CO_2, \
     API_OMS_V_ORDER_PROD_BO_2

	from fy_auth_functions import initial_validate_access_token
	from fy_base_functions import logEntryFunc2
	from fyers_logger import FyersLogger
	from positions.fy_trading_internal_functions_exit_positions_POST import INTERNAL_exitCoverOrder, \
	 INTERNAL_exitBracketOrder
	from orders.fy_trading_internal_functions_orders_DELETE import INTERNAL_cancelOrder_withID

except Exception as e:
	print ("ERR : %s : %s : %s" % (moduleName, "Could not import module", e))
	sys.exit()

fy_logger = FyersLogger("ALB_LAMBDA", "DEBUG", logger_handler=logging.FileHandler("albEC2.log"))


def fy_cancelOrder(kwargs):
	"""
		[FUNCTION]
			Cancel the order based on the type of the order.
		[PARAMS] => Key value arguments
			cookie  : This is the JWT string which has been saved in Fyers cookie
			orderID
		[RETURN]
			Success :
			Failure :
	"""
	funcName = "fy_cancelOrder"
	try:
		for i in API_K_DICT_ORDER_CANCEL.keys():
			if not i in kwargs:
				returnDict = {API_K_STATUS: API_V_ERROR, API_K_CODE: API_K_DICT_ORDER_CANCEL[i][0],
							  API_K_MSG: API_K_DICT_ORDER_CANCEL[i][1]}
				return (returnDict)

		funcRet = initial_validate_access_token(kwargs, callingFuncName=funcName)
		if funcRet[API_K_STATUS] == API_V_ERROR:
			return funcRet

		tokenHash = funcRet[API_K_DATA_1][0]
		fyId = funcRet[API_K_DATA_1][1]
		fy_logger.set_fyId(fyId)
		
		orderNumber = kwargs[API_K_ORDER_ID]

		logEntryFunc2(LOG_STATUS_SUCCESS_1, moduleName, funcName,"",orderNumber, fyId=fyId)

		userIp = ""
		if API_K_USER_IP in kwargs:
			userIp = kwargs[API_K_USER_IP]

		# Check if cover order
		if API_OMS_V_ORDER_PROD_CO_2 in orderNumber:
			funcRetList = INTERNAL_exitCoverOrder(tokenHash,orderNumber,callingFuncName=funcName,userIp=userIp)
		# Bracket order
		elif API_OMS_V_ORDER_PROD_BO_2 in orderNumber:
			funcRetList = INTERNAL_exitBracketOrder(tokenHash,orderNumber,callingFuncName=funcName,userIp=userIp)
		else:
			funcRetList = INTERNAL_cancelOrder_withID(tokenHash, orderNumber,callingFuncName=funcName,userIp=userIp)

		if (funcRetList[0] == ERROR_C_1) or (funcRetList[0] == ERROR_C_OMS_1):
			returnDict = {API_K_STATUS: API_V_ERROR, API_K_CODE: funcRetList[1],
						  API_K_MSG: funcRetList[2], API_K_ORDER_ID: (orderNumber)}
			return (returnDict)

		returnDict = {API_K_STATUS: API_V_SUCCESS, API_K_CODE: funcRetList[1], API_K_MSG: SUCCESS_M_ORDER_CANCELLED_1,
					  API_K_ORDER_ID: str(orderNumber)}
		return (returnDict)

	except Exception as e:
		logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, "", e, ERROR_C_UNKNOWN, kwargs)
		returnDict = {API_K_STATUS: ERROR_C_1, API_K_CODE: ERROR_C_UNKNOWN, API_K_MSG: e}
		return (returnDict)


def main():
	pass  # Test here


if __name__ == "__main__":
	main()
