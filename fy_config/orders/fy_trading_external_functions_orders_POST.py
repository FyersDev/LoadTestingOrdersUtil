moduleName = "fy_trading_external_functions_orders_POST"
try:
	import sys
	import time
	import logging

	from fy_base_api_keys_values import API_K_STATUS, API_V_ERROR, API_K_CODE, \
	 API_K_DATA_1, API_V_SUCCESS, API_K_MSG, API_K_TOKENHASH
	from fy_base_success_error_codes import ERROR_C_UNKNOWN, \
	 ERROR_C_INV_ORDER_SHOW_NOTICE, ERROR_C_1, ERROR_C_OMS_1, \
	 ERROR_C_INVALID_TOKEN_6, ERROR_C_DEMO_USER
	from fy_base_success_error_messages import ERROR_M_INV_ORDER_TYPE, \
     ERROR_M_INV_ORDER_LMT_PRICE, ERROR_M_INV_ORDER_STOP_LOSS, \
	 ERROR_M_INV_ORDER_TARGET_VAL
	from fy_base_defines import LOG_STATUS_ERROR_1, LOG_STATUS_SUCCESS_1
	from fy_common_api_keys_values import API_K_USER_IP, API_K_FYSYMBOL, \
	 API_K_ORDER_QTY, API_K_ORDER_SIDE, API_K_ORDER_LMT_PRICE, \
	 API_K_ORDER_STP_PRICE, API_K_ORDER_PRODUCT, API_K_DISC_QTY, \
	 API_K_ORDER_VALIDITY, API_K_OFFLINE_FLAG, API_K_ORDER_TYPE, \
	 API_K_ORDER_ID, API_V_PRODTYPE_CO, API_K_ORDER_STOP_LOSS, \
	 API_V_PRODTYPE_BO, API_K_ORDER_TAKE_PROFIT	 
	from fy_trading_defines import API_K_DICT_ORDER_PLACE

	from fy_auth_functions import initial_validate_access_token
	from fy_base_functions import logEntryFunc2
	from fyers_logger import FyersLogger
	from orders.fy_trading_internal_functions_orders_POST import INTERNAL_placeCoverOrder, \
     INTERNAL_placeBracketOrder
	from fy_trading_common_functions import INTERNAL_placeOrder_withID

except Exception as e:
	print ("ERR : %s : %s : %s" % (moduleName, "Could not import module", e))
	sys.exit()

fy_logger = FyersLogger("ALB_LAMBDA", "DEBUG", logger_handler=logging.FileHandler("albEC2.log"))


def fy_placeOrder(kwargs):
	"""
		[FUNCTION]
			Place an order
		[PARAMS] => Key value arguments
			cookie  : This is the JWT string which has been saved in Fyers cookie
			....
		[RETURN]
			Success :
			Failure :
	"""
	funcName = "fy_placeOrder"
	try:
		for i in API_K_DICT_ORDER_PLACE.keys():
			if not i in kwargs:
				returnDict = {API_K_STATUS: API_V_ERROR,
							  # API_K_CODE: API_K_DICT_ORDER_PLACE[i][0],
							  API_K_CODE: ERROR_C_INV_ORDER_SHOW_NOTICE,
							  API_K_MSG: API_K_DICT_ORDER_PLACE[i][1]}
				return (returnDict)

		multi_orders = kwargs["multi_orders"]
        
		if not multi_orders:
			funcRet = initial_validate_access_token(kwargs, callingFuncName=funcName)
			if funcRet[API_K_STATUS] == API_V_ERROR:
				return funcRet

			tokenHash = funcRet[API_K_DATA_1][0]
			fyId = funcRet[API_K_DATA_1][1]

		else:
			tokenHash = kwargs[API_K_TOKENHASH]
			fyId = kwargs["fyId"]


		logEntryFunc2(LOG_STATUS_SUCCESS_1, moduleName, funcName,"",kwargs, fyId=fyId)

		userIp = ""
		if API_K_USER_IP in kwargs:
			userIp = kwargs[API_K_USER_IP]

		orderSymbol     = kwargs[API_K_FYSYMBOL]
		orderQty        = kwargs[API_K_ORDER_QTY]
		orderSide       = kwargs[API_K_ORDER_SIDE]
		orderPrice      = kwargs[API_K_ORDER_LMT_PRICE]
		orderStopPrice  = kwargs[API_K_ORDER_STP_PRICE]
		productType     = kwargs[API_K_ORDER_PRODUCT]
		errOrderId      = str(int(time.time()))
		disclosedQty    = kwargs[API_K_DISC_QTY]
		validity        = kwargs[API_K_ORDER_VALIDITY]
		offlineFlag     = str(kwargs[API_K_OFFLINE_FLAG])

		try:
			orderType = int(kwargs[API_K_ORDER_TYPE])
		except Exception as e:
			returnDict = {API_K_STATUS: API_V_ERROR, API_K_CODE: ERROR_C_INV_ORDER_SHOW_NOTICE,
						  API_K_MSG: ERROR_M_INV_ORDER_TYPE, API_K_ORDER_ID: errOrderId}
			return (returnDict)

		try:
			orderPrice = float(orderPrice)
		except Exception as e:
			returnDict = {API_K_STATUS: API_V_ERROR, API_K_CODE: ERROR_C_INV_ORDER_SHOW_NOTICE,API_K_MSG: ERROR_M_INV_ORDER_LMT_PRICE, API_K_ORDER_ID: errOrderId}
			return (returnDict)

		# If cover order
		if productType == API_V_PRODTYPE_CO:
			try:
				stopLoss = float(kwargs[API_K_ORDER_STOP_LOSS])
			except Exception as e:
				returnDict = {API_K_STATUS: API_V_ERROR, API_K_CODE: ERROR_C_INV_ORDER_SHOW_NOTICE,
							  API_K_MSG: ERROR_M_INV_ORDER_STOP_LOSS, API_K_ORDER_ID: errOrderId}
				return (returnDict)
			funcRetList = INTERNAL_placeCoverOrder(tokenHash, orderSymbol, orderSide, orderType, orderQty, orderPrice, stopLoss, callingFuncName=funcName,userIp=userIp)

		# If bracket order
		elif productType == API_V_PRODTYPE_BO:
			try:
				stopLossAbsVal = float(kwargs[API_K_ORDER_STOP_LOSS])
			except Exception as e:
				returnDict = {API_K_STATUS: API_V_ERROR, API_K_CODE: ERROR_C_INV_ORDER_SHOW_NOTICE,
							  API_K_MSG: ERROR_M_INV_ORDER_STOP_LOSS, API_K_ORDER_ID: errOrderId}
				return (returnDict)
			try:
				takeProfitAbsVal = float(kwargs[API_K_ORDER_TAKE_PROFIT])
			except Exception as e:
				returnDict = {API_K_STATUS: API_V_ERROR, API_K_CODE: ERROR_C_INV_ORDER_SHOW_NOTICE,
							  API_K_MSG: ERROR_M_INV_ORDER_TARGET_VAL, API_K_ORDER_ID: errOrderId}
				return (returnDict)
			funcRetList = INTERNAL_placeBracketOrder(tokenHash, symbol=orderSymbol, transType=orderSide, ordType=orderType, qty=orderQty, price=orderPrice,trigPrice=orderStopPrice,targetAbsVal=takeProfitAbsVal, stopLossAbsVal=stopLossAbsVal,prodList=productType,callingFuncName=funcName,userIp=userIp)

		# Any other product type
		else:
			funcRetList = INTERNAL_placeOrder_withID(tokenHash, orderSymbol, orderSide, orderType, orderQty,orderPrice, productType, trigPrice=orderStopPrice,callingFuncName=funcName,discQty=disclosedQty,valType=validity, offlineFlag=offlineFlag,userIp=userIp)

		if (funcRetList[0] == ERROR_C_1) or (funcRetList[0] == ERROR_C_OMS_1):
			# In case the order was rejected but the rejected order id is not there in the oms response, we will return unixtimestamp
			if len(funcRetList) < 4:
				funcRetList.append(errOrderId)
				if not (funcRetList[1] == ERROR_C_INVALID_TOKEN_6 or funcRetList[1] == ERROR_C_DEMO_USER):
					funcRetList[1] = ERROR_C_INV_ORDER_SHOW_NOTICE
			elif funcRetList[3] == "":
				funcRetList[3] = errOrderId
				funcRetList[1] = ERROR_C_INV_ORDER_SHOW_NOTICE

			returnDict = {API_K_STATUS: API_V_ERROR, API_K_CODE: funcRetList[1],
						  API_K_MSG: funcRetList[2], API_K_ORDER_ID: funcRetList[3]}
			return (returnDict)

		returnDict = {API_K_STATUS: API_V_SUCCESS, API_K_CODE: funcRetList[1], API_K_MSG: funcRetList[2],
					  API_K_ORDER_ID: funcRetList[3]}
		return (returnDict)

	except Exception as e:
		logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, "", e, ERROR_C_UNKNOWN, kwargs)
		returnDict = {API_K_STATUS: ERROR_C_1, API_K_CODE: ERROR_C_UNKNOWN, API_K_MSG: e}
		return (returnDict)


def main():
	pass  # Test here


if __name__ == "__main__":
	main()
