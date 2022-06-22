moduleName = "fy_trading_external_functions_exit_positions_POST"
try:
	import sys
	import logging

	from fy_base_defines import LOG_STATUS_SUCCESS_1
	from fy_base_api_keys_values import API_K_STATUS, API_V_ERROR, API_K_CODE, \
	 API_K_DATA_1, API_V_SUCCESS, API_K_MSG
	from fy_base_success_error_codes import \
	 ERROR_C_UNKNOWN, ERROR_C_INV_INP, ERROR_C_1, ERROR_C_OMS_1, \
	 ERROR_C_DEMO_USER, ERROR_C_INV_ORDER_SIDE, ERROR_C_INV_SEGMENT, ERROR_C_INV_ORDER_PRODUCT
	from fy_base_success_error_messages import ERROR_M_INV_ORDER_PRODUCT, \
	 ERROR_M_DEMO_USER, ERROR_M_INV_ORDER_SIDE, ERROR_M_INV_SEGMENT, ERROR_M_INV_INPUT_1
	from fy_base_defines import LOG_STATUS_ERROR_1
	from fy_common_api_keys_values import API_K_USER_IP, \
     API_V_ORDER_SIDE_BUY_1, API_V_ORDER_SIDE_SELL_1
	from fy_data_and_trade_defines import GUEST_CLIENT_ID, SYM_SEGMENT_CM, SYM_SEGMENT_FO, \
	 SYM_SEGMENT_CD, SYM_SEGMENT_COM
	from fy_trading_defines import API_OMS_V_ORDER_PROD_CNC_2, API_OMS_V_ORDER_PROD_MARGIN_2, \
     API_OMS_V_ORDER_PROD_INTRADAY_2, API_OMS_V_ORDER_PROD_CO_2, API_OMS_V_ORDER_PROD_BO_2
	from fy_config.positions.fy_trading_internal_functions_exit_positions_POST import INTERNAL_exitPositions, \
	 INTERNAL_exitAllPositions

	from fy_auth_functions import initial_validate_access_token
	from fy_base_functions import logEntryFunc2
	from fyers_logger import FyersLogger


except Exception as e:
	print ("ERR : %s : %s : %s" % (moduleName, "Could not import module", e))
	sys.exit()

fy_logger = FyersLogger("ALB_LAMBDA", "DEBUG", logger_handler=logging.FileHandler("albLambda.log"))


# Exit positions added - 20200117 - Khyati
def fy_exitPositions(kwargs):
	funcName = "fy_exitPositions"
	try:
		funcRet = initial_validate_access_token(kwargs, callingFuncName=funcName)
		if funcRet[API_K_STATUS] == API_V_ERROR:
			return funcRet

		tokenHash = funcRet[API_K_DATA_1][0]
		fyId = funcRet[API_K_DATA_1][1]
		fy_logger.set_fyId(fyId)
			
		if fyId in GUEST_CLIENT_ID:
			returnDict = {API_K_STATUS: API_V_ERROR, API_K_CODE: ERROR_C_DEMO_USER, API_K_MSG: ERROR_M_DEMO_USER}
			return returnDict

		logEntryFunc2(LOG_STATUS_SUCCESS_1, moduleName, funcName,"exit_positions_1",kwargs, fyId=fyId)

		userIp = ""
		if API_K_USER_IP in kwargs:
			userIp = kwargs[API_K_USER_IP]

		positionsIds = kwargs.get("id")

		if positionsIds:
			if not isinstance(positionsIds,list):
				positionsIds = [positionsIds]
			funcRet = INTERNAL_exitPositions(tokenHash,positionsIds,callingFuncName=funcName,userIp=userIp, fyId=fyId)
		else:
			try:
				exitAll = 0
				if "exit_all" in kwargs:
					exitAll = kwargs["exit_all"]

				if exitAll:
					funcRet = INTERNAL_exitAllPositions(tokenHash,exitAll=True,callingFuncName=funcName,userIp=userIp, fyId=fyId)

				elif positionsIds == "" or positionsIds == None:
					if "side" not in kwargs and "segment" not in kwargs and "productType" not in kwargs:
						funcRet = INTERNAL_exitAllPositions(tokenHash,exitAll=True,callingFuncName=funcName,userIp=userIp, fyId=fyId)
					elif "side" in kwargs and "segment" in kwargs and "productType" in kwargs:
						inputside = kwargs["side"]
						inputsegment = kwargs["segment"]
						inputproductType = kwargs["productType"]

						if not set(inputside).issubset(set([0,API_V_ORDER_SIDE_BUY_1,API_V_ORDER_SIDE_SELL_1])):
							return {API_K_STATUS: API_V_ERROR, API_K_CODE: ERROR_C_INV_ORDER_SIDE, API_K_MSG: ERROR_M_INV_ORDER_SIDE}
						if not set(inputsegment).issubset(set([SYM_SEGMENT_CM, SYM_SEGMENT_FO, SYM_SEGMENT_CD, SYM_SEGMENT_COM,0])):
							return {API_K_STATUS: API_V_ERROR, API_K_CODE: ERROR_C_INV_SEGMENT, API_K_MSG: ERROR_M_INV_SEGMENT}
						if not set(inputproductType).issubset(set([API_OMS_V_ORDER_PROD_CNC_2,API_OMS_V_ORDER_PROD_MARGIN_2,API_OMS_V_ORDER_PROD_INTRADAY_2,API_OMS_V_ORDER_PROD_CO_2,API_OMS_V_ORDER_PROD_BO_2,"ALL"])):
							return {API_K_STATUS: API_V_ERROR, API_K_CODE: ERROR_C_INV_ORDER_PRODUCT, API_K_MSG: ERROR_M_INV_ORDER_PRODUCT}

						if 0 in inputside:
							inputside.remove(0)
						if 0 in inputsegment:
							inputsegment.remove(0)
						if "ALL" in inputproductType:
							inputproductType.remove("ALL")

						if len(inputside) == 0 or len(inputsegment) == 0 or len(inputproductType) == 0:
							return {API_K_STATUS: API_V_ERROR, API_K_CODE: ERROR_C_INV_INP, API_K_MSG: ERROR_M_INV_INPUT_1}

						funcRet = INTERNAL_exitAllPositions(tokenHash,inputside=inputside,inputsegment=inputsegment,inputproductType=inputproductType,callingFuncName=funcName,userIp=userIp, fyId=fyId)

					else:
						return {API_K_STATUS: API_V_ERROR, API_K_CODE: ERROR_C_INV_INP, API_K_MSG: ERROR_M_INV_INPUT_1}
				else:
					return {API_K_STATUS: API_V_ERROR, API_K_CODE: ERROR_C_INV_INP, API_K_MSG: ERROR_M_INV_INPUT_1}

			except Exception as e:
				return {API_K_STATUS: API_V_ERROR, API_K_CODE: ERROR_C_INV_INP, API_K_MSG: ERROR_M_INV_INPUT_1}

		if (funcRet[0] == ERROR_C_1) or (funcRet[0] == ERROR_C_OMS_1):
			returnDict = {API_K_STATUS: API_V_ERROR, API_K_CODE: funcRet[1], API_K_MSG: funcRet[2]}
			return (returnDict)

		returnDict = {API_K_STATUS: API_V_SUCCESS, API_K_CODE: funcRet[1], API_K_MSG: funcRet[2]}
		return (returnDict)

	except Exception as e:
		logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, "", e, ERROR_C_UNKNOWN, kwargs)
		returnDict = {API_K_STATUS: API_V_ERROR, API_K_CODE: ERROR_C_UNKNOWN, API_K_MSG: ""}
		return (returnDict)


def main():
	pass  # Test here


if __name__ == "__main__":
	main()
