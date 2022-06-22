moduleName = "fy_trading_external_functions_orders_details_GET"
try:
	import sys
	import logging

	from fy_base_api_keys_values import API_K_STATUS, API_V_ERROR, API_K_CODE, \
	 API_K_DATA_1, API_V_SUCCESS, API_K_MSG, API_K_COOKIE
	from fy_base_success_error_codes import ERROR_C_INV_COOKIE, ERROR_C_INV_ORDER_ID, \
	 ERROR_C_UNKNOWN, ERROR_C_INV_SEGMENT, ERROR_C_INV_FYSYMBOL, ERROR_C_1
	from fy_base_success_error_messages import ERROR_M_INV_COOKIE, ERROR_M_INV_ORDER_ID, \
      ERROR_M_INV_SEGMENT, ERROR_M_INV_FYSYMBOL
	from fy_base_defines import LOG_STATUS_ERROR_1
	from fy_common_api_keys_values import API_K_USER_IP, API_K_ORDER_ID, \
      API_K_FYSYMBOL, API_K_ORDER_DETAILS
	from fy_data_and_trade_defines import SEGMENT_NAME_CM, SEGMENT_NAME_CD, \
	  SEGMENT_NAME_FO, SEGMENT_NAME_COM
	from fy_trading_defines import API_OMS_ORDER_DETAIL_SEG, API_OMS_V_SEG_CM_1, \
	  API_OMS_V_SEG_CD_1, API_OMS_V_SEG_FO_1, API_OMS_V_SEG_COM_1
	from vagator_auth_check import API_K_TOKENHASH

	from fy_auth_functions import initial_validate_access_token
	from fy_base_functions import logEntryFunc2
	from fyers_logger import FyersLogger
	from orders.fy_trading_internal_functions_orders_details_GET import INTERNAL_getOrderAdditionalDetails_withId


except Exception as e:
	print ("ERR : %s : %s : %s" % (moduleName, "Could not import module", e))
	sys.exit()

fy_logger = FyersLogger("ALB_LAMBDA", "DEBUG", logger_handler=logging.FileHandler("albEC2.log"))


def fy_orderDetails(kwargs):
	funcName = "fy_orderDetails"
	try:		
		# Validation for tokenhash added - Khyati
		if API_K_COOKIE not in kwargs and API_K_TOKENHASH not in kwargs:
			return {API_K_STATUS:API_V_ERROR, API_K_CODE:ERROR_C_INV_COOKIE, API_K_MSG:ERROR_M_INV_COOKIE}

		if API_K_ORDER_ID not in kwargs:
			return {API_K_STATUS:API_V_ERROR, API_K_CODE: ERROR_C_INV_ORDER_ID, API_K_MSG: ERROR_M_INV_ORDER_ID}

		if API_OMS_ORDER_DETAIL_SEG not in kwargs:
			return {API_K_STATUS:API_V_ERROR, API_K_CODE: ERROR_C_INV_SEGMENT, API_K_MSG: ERROR_M_INV_SEGMENT}

		if API_K_FYSYMBOL not in kwargs:
			return {API_K_STATUS:API_V_ERROR, API_K_CODE: ERROR_C_INV_FYSYMBOL, API_K_MSG: ERROR_M_INV_FYSYMBOL}

		userIp = ""
		if API_K_USER_IP in kwargs:
			userIp = kwargs[API_K_USER_IP]

		funcRet = initial_validate_access_token(kwargs, callingFuncName=funcName)
		if funcRet[API_K_STATUS] == API_V_ERROR:
			return funcRet

		tokenHash = funcRet[API_K_DATA_1][0]
		fyId = funcRet[API_K_DATA_1][1]

		fy_logger.set_fyId(fyId)
		
		segment = kwargs[API_OMS_ORDER_DETAIL_SEG]
		segParam = ''
		if segment == SEGMENT_NAME_CM:
			segParam = API_OMS_V_SEG_CM_1
		elif segment == SEGMENT_NAME_CD:
			segParam = API_OMS_V_SEG_CD_1
		elif segment == SEGMENT_NAME_FO:
			segParam = API_OMS_V_SEG_FO_1
		elif segment == SEGMENT_NAME_COM:
			segParam = API_OMS_V_SEG_COM_1
		else:
			return {API_K_STATUS:API_V_ERROR, API_K_CODE: ERROR_C_INV_SEGMENT, API_K_MSG: ERROR_M_INV_SEGMENT}

		orderNumber = kwargs[API_K_ORDER_ID]
		funcRet = INTERNAL_getOrderAdditionalDetails_withId(tokenHash, orderNumber, segParam, kwargs[API_K_FYSYMBOL],userIp=userIp)
		if funcRet[0] == ERROR_C_1:
			return {API_K_STATUS:API_V_ERROR, API_K_CODE: funcRet[1], API_K_MSG: funcRet[2]}
		return {API_K_STATUS: API_V_SUCCESS, API_K_MSG: "", API_K_ORDER_DETAILS: funcRet[1]}
	except Exception as e:
		logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, "", e, ERROR_C_UNKNOWN, kwargs)
		returnDict = {API_K_STATUS: ERROR_C_1, API_K_CODE: ERROR_C_UNKNOWN, API_K_MSG: e}
		return (returnDict)


def main():
	pass  # Test here


if __name__ == "__main__":
	main()
