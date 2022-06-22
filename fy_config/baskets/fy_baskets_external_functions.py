moduleName = "fy_baskets_external_functions"

try:
	import sys
	import json
	# import boto3
	import copy
	import time

	import fy_base_functions as baseFunc
	import fy_base_defines as baseDef
	import fy_base_success_error_codes as baseCodes
	import fy_base_success_error_messages as baseMsg
	import fy_base_api_keys_values as baseKV
	import fy_auth_functions as authFunc
	import fy_auth_defines as authDef
	# import fy_baskets_internal_functions as intFunc
	# import fy_trading_external_functions as tradeExtFunc
	import fy_data_and_trade_defines as dataTradeDef

	from orders.fy_trading_external_functions_orders_POST import fy_placeOrder
	from fy_config.baskets import fy_baskets_internal_functions as intFunc

	from fy_config.fy_base_api_keys_values import API_K_CODE, API_K_DATA_1, API_K_STATUS, API_V_SUCCESS
	from fy_config.fy_base_success_error_codes import ERROR_C_1
	from fy_config.fy_common_api_keys_values import API_K_AVAIL_MARGIN, API_K_TOT_MARGIN, API_V_ORDER_SIDE_BUY_1
	from fy_config.fy_common_internal_functions import INTERNAL_checkSymbolNameOrToken
	from fy_config.fy_connections import connectRedis
	from fy_config.margin.fy_margincalc_external_functions import reset_spancalc, fy_spanCalc, fy_marginCalc_noAuth
	from fy_config.fy_trading_defines import API_OMS_K_MESSAGE_1

except Exception as e:
	print("ERR : %s : %s : %s" % (moduleName, "Could not import module", e))
	sys.exit()


def get_baskets(kwargs):
	"""
		Authenticate the user and return the user's baskets.
		Inputs => token_id/cookie
		If token_id is present, verify the token_id, else validate the cookie and then verify the token_id
	"""
	funcName = "get_baskets"
	try:
		funcRet = authFunc.initial_validate_access_token(kwargs, callingFuncName=funcName)
		if funcRet[baseKV.API_K_STATUS] == baseKV.API_V_ERROR:
			return funcRet
		tokenHash = funcRet[baseKV.API_K_DATA_1][0]
		fyId = funcRet[baseKV.API_K_DATA_1][1]

		funcRet = intFunc.INTERNAL_getUserBasketsFromS3(fyId, callingFuncName=funcName)
		if funcRet[0] == baseCodes.ERROR_C_1:
			return {baseKV.API_K_STATUS: baseKV.API_V_ERROR, baseKV.API_K_CODE: funcRet[1], baseKV.API_K_MSG: funcRet[2]}

		return {baseKV.API_K_STATUS: baseKV.API_V_SUCCESS, baseKV.API_K_CODE: baseCodes.SUCCESS_C_2, baseKV.API_K_MSG: "", baseKV.API_K_DATA_1: funcRet[1]}

	except Exception as e:
		baseFunc.logEntryFunc2(baseDef.LOG_STATUS_ERROR_1, moduleName, funcName, "", err_msg=e)
		return {baseKV.API_K_STATUS: baseKV.API_V_ERROR, baseKV.API_K_CODE: baseCodes.ERROR_C_UNKNOWN, baseKV.API_K_MSG: baseMsg.ERROR_M_UNKNOWN_1}


def fy_basket(kwargs):
	"""
		Key value arguments => typeFlag, token_id/cookie, body
			typeFlag = 1 : Create a new basket
				name 	:	Name of the basket to be created (Required)
				items 	: 	Items to add in the basket

			typeFlag = 2 : Modify an existing basket
				basketid	:	id of the basket to be modified (Required)
				name 		:	New name of the basket
				items 		: 	Updated items to add in the basket

			typeFlag = 3 : Delete an existing basket
				basketid 	:	id of the basket to be deleted (Required)
	"""
	funcName = "fy_basket"
	try:
		typeFlag = kwargs[baseKV.API_K_TYPE_FLAG]
		if not isinstance(typeFlag, int):
			return {baseKV.API_K_STATUS: baseKV.API_V_ERROR, baseKV.API_K_CODE: baseCodes.ERROR_C_UNKNOWN, baseKV.API_K_MSG: baseMsg.ERROR_M_UNKNOWN_1}

		funcRet = authFunc.initial_validate_access_token(kwargs, callingFuncName=funcName)
		if funcRet[baseKV.API_K_STATUS] == baseKV.API_V_ERROR:
			return funcRet
		tokenHash = funcRet[baseKV.API_K_DATA_1][0]
		fyId = funcRet[baseKV.API_K_DATA_1][1]

		if fyId in dataTradeDef.GUEST_CLIENT_ID:
			return {baseKV.API_K_STATUS: baseKV.API_V_ERROR, baseKV.API_K_CODE: baseCodes.ERROR_C_DEMO_USER, baseKV.API_K_MSG: baseMsg.ERROR_M_DEMO_USER}

		inputBody = kwargs["body"]
		if not isinstance(inputBody, dict):
			inputBody = json.loads(inputBody)

		if typeFlag == 1:
			basketName = inputBody["name"]
			basketItems = inputBody.get("items")
			funcRet = intFunc.INTERNAL_createBasket(fyId, basketName, basketItems, callingFuncName=funcName)

		elif typeFlag == 2:
			basketId = inputBody["basketid"]
			basketName = inputBody.get("name")
			basketItems = inputBody.get("items")
			funcRet = intFunc.INTERNAL_modifyBasket(fyId, basketId, basketName, basketItems, callingFuncName=funcName)

		elif typeFlag == 3:
			basketId = inputBody["basketid"]
			funcRet = intFunc.INTERNAL_deleteBasket(fyId, basketId, callingFuncName=funcName)

		else:
			return {baseKV.API_K_STATUS: baseKV.API_V_ERROR, baseKV.API_K_CODE: baseCodes.ERROR_C_UNKNOWN, baseKV.API_K_MSG: baseMsg.ERROR_M_UNKNOWN_1}

		if funcRet[0] == baseCodes.ERROR_C_1:
			return {baseKV.API_K_STATUS: baseKV.API_V_ERROR, baseKV.API_K_CODE: funcRet[1], baseKV.API_K_MSG: funcRet[2]}

		return {baseKV.API_K_STATUS: baseKV.API_V_SUCCESS, baseKV.API_K_CODE: baseCodes.SUCCESS_C_2, baseKV.API_K_MSG: "", baseKV.API_K_DATA_1: funcRet[1]}

	except KeyError as e:
		baseFunc.logEntryFunc2(baseDef.LOG_STATUS_ERROR_1, moduleName, funcName, "", err_msg=e)
		return {baseKV.API_K_STATUS: baseKV.API_V_ERROR, baseKV.API_K_CODE: baseCodes.ERROR_C_INV_INP, baseKV.API_K_MSG: baseMsg.ERROR_M_INV_INPUT_1}

	except Exception as e:
		baseFunc.logEntryFunc2(baseDef.LOG_STATUS_ERROR_1, moduleName, funcName, "", err_msg=e)
		return {baseKV.API_K_STATUS: baseKV.API_V_ERROR, baseKV.API_K_CODE: baseCodes.ERROR_C_UNKNOWN, baseKV.API_K_MSG: baseMsg.ERROR_M_UNKNOWN_1}


def fy_basket_item(kwargs):
	"""
		Key value arguments => typeFlag, token_id/cookie, body
			typeFlag = 1 : Add a new item to an existing basket
				basketid 	:	id of the basket to add the item to (Required)
				params 		:	Order details of the item to add (Required)

			typeFlag = 2 : Modify an existing item in a basket
				basketid	:	id of the basket in which the item to modify belongs (Required)
				itemid 		:	id of the item to be modified (Required)
				params 		: 	Updated Order details of the item to change (Required)

			typeFlag = 3 : Delete an existing item in a basket
				basketid	:	id of the basket in which the item to delete belongs (Required)
				itemid 		:	id of the item to be deleted (Required)

	"""
	funcName = "fy_basket_item"
	try:
		typeFlag = kwargs[baseKV.API_K_TYPE_FLAG]
		if not isinstance(typeFlag, int):
			return {baseKV.API_K_STATUS: baseKV.API_V_ERROR, baseKV.API_K_CODE: baseCodes.ERROR_C_UNKNOWN, baseKV.API_K_MSG: baseMsg.ERROR_M_UNKNOWN_1}

		funcRet = authFunc.initial_validate_access_token(kwargs, callingFuncName=funcName)
		if funcRet[baseKV.API_K_STATUS] == baseKV.API_V_ERROR:
			return funcRet
		tokenHash = funcRet[baseKV.API_K_DATA_1][0]
		fyId = funcRet[baseKV.API_K_DATA_1][1]

		if fyId in dataTradeDef.GUEST_CLIENT_ID:
			return {baseKV.API_K_STATUS: baseKV.API_V_ERROR, baseKV.API_K_CODE: baseCodes.ERROR_C_DEMO_USER, baseKV.API_K_MSG: baseMsg.ERROR_M_DEMO_USER}

		inputBody = kwargs["body"]
		if not isinstance(inputBody, dict):
			inputBody = json.loads(inputBody)

		if typeFlag == 1:
			itemParams = inputBody["params"]
			basketId = inputBody["basketid"]
			funcRet = intFunc.INTERNAL_addItem(fyId, itemParams, basketId, callingFuncName=funcName)

		elif typeFlag == 2:
			itemParams = inputBody["params"]
			basketId = inputBody["basketid"]
			itemId = inputBody["itemid"]
			funcRet = intFunc.INTERNAL_modifyItem(fyId, itemParams, itemId, basketId, callingFuncName=funcName)

		elif typeFlag == 3:
			basketId = inputBody["basketid"]
			itemId = inputBody["itemid"]
			funcRet = intFunc.INTERNAL_deleteItem(fyId, itemId, basketId, callingFuncName=funcName)

		else:
			return {baseKV.API_K_STATUS: baseKV.API_V_ERROR, baseKV.API_K_CODE: baseCodes.ERROR_C_UNKNOWN, baseKV.API_K_MSG: baseMsg.ERROR_M_UNKNOWN_1}

		if funcRet[0] == baseCodes.ERROR_C_1:
			return {baseKV.API_K_STATUS: baseKV.API_V_ERROR, baseKV.API_K_CODE: funcRet[1], baseKV.API_K_MSG: funcRet[2]}

		return {baseKV.API_K_STATUS: baseKV.API_V_SUCCESS, baseKV.API_K_CODE: baseCodes.SUCCESS_C_2, baseKV.API_K_MSG: "", baseKV.API_K_DATA_1: funcRet[1]}

	except KeyError as e:
		baseFunc.logEntryFunc2(baseDef.LOG_STATUS_ERROR_1, moduleName, funcName, "", err_msg=e)
		return {baseKV.API_K_STATUS: baseKV.API_V_ERROR, baseKV.API_K_CODE: baseCodes.ERROR_C_INV_INP, baseKV.API_K_MSG: baseMsg.ERROR_M_INV_INPUT_1}

	except Exception as e:
		baseFunc.logEntryFunc2(baseDef.LOG_STATUS_ERROR_1, moduleName, funcName, "", err_msg=e)
		return {baseKV.API_K_STATUS: baseKV.API_V_ERROR, baseKV.API_K_CODE: baseCodes.ERROR_C_UNKNOWN, baseKV.API_K_MSG: baseMsg.ERROR_M_UNKNOWN_1}


def fy_execute_basket(kwargs):
	funcName = "fy_execute_basket"
	try:
		funcRet = authFunc.initial_validate_access_token(kwargs, callingFuncName=funcName)
		if funcRet[baseKV.API_K_STATUS] == baseKV.API_V_ERROR:
			return funcRet
		tokenHash = funcRet[baseKV.API_K_DATA_1][0]
		fyId = funcRet[baseKV.API_K_DATA_1][1]

		if fyId in dataTradeDef.GUEST_CLIENT_ID:
			return {baseKV.API_K_STATUS: baseKV.API_V_ERROR, baseKV.API_K_CODE: baseCodes.ERROR_C_DEMO_USER, baseKV.API_K_MSG: baseMsg.ERROR_M_DEMO_USER}

		baseFunc.logEntryFunc2(baseDef.LOG_STATUS_SUCCESS_1, moduleName, funcName, "",kwargs["body"], fyId=fyId)

		inputBody = kwargs["body"]
		if not isinstance(inputBody, dict):
			inputBody = json.loads(inputBody)
		if "basketid" not in inputBody:
			return {baseKV.API_K_STATUS: baseKV.API_V_ERROR, baseKV.API_K_CODE: baseCodes.ERROR_C_INV_INP, baseKV.API_K_MSG: baseMsg.ERROR_M_INV_INPUT_1}
		basketId = inputBody["basketid"]

		## Check if the basket exists and get the order details of all items
		# s3client = boto3.client(intFunc.connDef.AWS_SERVICE_S3)
		s3client = intFunc.connDef.AWS_BOTO3_S3_CONNECTION
		funcRet = intFunc.INTERNAL_getBasketOrderDetails(fyId, basketId, s3client=s3client, callingFuncName=funcName)
		if funcRet[0] == baseCodes.ERROR_C_1:
			return {baseKV.API_K_STATUS: baseKV.API_V_ERROR, baseKV.API_K_CODE: funcRet[1], baseKV.API_K_MSG: funcRet[2]}
		basketItemsList = funcRet[1]

		baseFunc.logEntryFunc2(baseDef.LOG_STATUS_SUCCESS_1, moduleName, funcName, "", inputBody, fyId=fyId)

		returnList = []
		for itemDict in basketItemsList:
			orderDict = copy.copy(itemDict["params"])
			orderDict["multi_orders"] = True
			orderDict[baseKV.API_K_TOKENHASH] = tokenHash
			orderDict["fyId"] = fyId
			orderDict[baseKV.API_K_COOKIE] = ""
			# orderFuncRet = tradeExtFunc.fy_placeOrder(orderDict)
			orderFuncRet = fy_placeOrder(orderDict)
			returnList.append(orderFuncRet)
			time.sleep(0.1) ##100ms wait after each order is placed
			if itemDict["params"]["productType"] in ["INTRADAY", "MARGIN"]:
				time.sleep(0.1)


		## Add the order placement status to basket
		funcRet = intFunc.INTERNAL_updateOrderDetailsToBasket(fyId, returnList, funcRet[2], funcRet[3], s3client=s3client, callingFuncName=funcName)

		return {baseKV.API_K_STATUS: baseKV.API_V_SUCCESS, baseKV.API_K_CODE: baseCodes.SUCCESS_C_2, baseKV.API_K_MSG: "Basket Order Executed Successfully", baseKV.API_K_DATA_1: funcRet[1]}

	except Exception as e:
		baseFunc.logEntryFunc2(baseDef.LOG_STATUS_ERROR_1, moduleName, funcName, "",kwargs, err_msg=e)
		return {baseKV.API_K_STATUS: baseKV.API_V_ERROR, baseKV.API_K_CODE: baseCodes.ERROR_C_UNKNOWN, baseKV.API_K_MSG: baseMsg.ERROR_M_UNKNOWN_1}


def bifurcate_scrips_by_underlying(futdata, redis):
	underlying_dict = {}
	for data in futdata:
		symbol_info = redis.hget("symbol_master", data["symbol"])
		if symbol_info:
			symbol_info = json.loads(symbol_info.decode("utf-8"))
			underlying = symbol_info["underFyTok"][10:]
			if underlying not in underlying_dict:
				pass

		

def fy_margin_basket(kwargs):
	funcName = "fy_margin_basket"
	try:
		funcRet = authFunc.initial_validate_access_token(kwargs, callingFuncName=funcName)
		if funcRet[baseKV.API_K_STATUS] == baseKV.API_V_ERROR:
			return funcRet
		tokenHash = funcRet[baseKV.API_K_DATA_1][0]
		fyId = funcRet[baseKV.API_K_DATA_1][1]

		if fyId in dataTradeDef.GUEST_CLIENT_ID:
			return {baseKV.API_K_STATUS: baseKV.API_V_ERROR, baseKV.API_K_CODE: baseCodes.ERROR_C_DEMO_USER, baseKV.API_K_MSG: baseMsg.ERROR_M_DEMO_USER}

		baseFunc.logEntryFunc2(baseDef.LOG_STATUS_SUCCESS_1, moduleName, funcName, "",kwargs, fyId=fyId)

		inputBody = kwargs
		if not isinstance(inputBody, dict):
			inputBody = json.loads(inputBody)
		if "basketid" not in inputBody:
			return {baseKV.API_K_STATUS: baseKV.API_V_ERROR, baseKV.API_K_CODE: baseCodes.ERROR_C_INV_INP, baseKV.API_K_MSG: baseMsg.ERROR_M_INV_INPUT_1}
		basketId = inputBody["basketid"]

		##Check if the basket exists and get the order details of all items
		# s3client = boto3.client(intFunc.connDef.AWS_SERVICE_S3)
		s3client = intFunc.connDef.AWS_BOTO3_S3_CONNECTION
		funcRet = intFunc.INTERNAL_getBasketOrderDetails(fyId, basketId, s3client=s3client, callingFuncName=funcName)
		if funcRet[0] == baseCodes.ERROR_C_1:
			return {baseKV.API_K_STATUS: baseKV.API_V_ERROR, baseKV.API_K_CODE: funcRet[1], baseKV.API_K_MSG: funcRet[2]}
		basketItemsList = funcRet[1]

		baseFunc.logEntryFunc2(baseDef.LOG_STATUS_SUCCESS_1, moduleName, funcName, "", inputBody, fyId=fyId)

		margin_sum = 0
		localMemory = connectRedis()
		futdata = []
		avail_margin = 0
		defaultItemDict = {
			'symbol': 'NSE:SBIN-EQ', 
			'qty': 1, 
			'side': 1,
			'limitPrice': 0.0, 
			'stopPrice': 0.0, 
			'productType': 'INTRADAY', 
			'type': 2,
			'disclosedQty': 0,
			'validity': 'DAY',
			'offlineOrder': False,
			'stopLoss': 0.0,
			'takeProfit': 0.0, 
			'ex_sym': 'SBIN',
			'description': 'STATE BANK OF INDIA',
			'sym_token': '10100000003045', 
			'exchange': 'NSE', 
			'segment': 10,
			'source': 'M'
		}
		avail_margin_updated = False
		basketItemsList = [item for item in basketItemsList if INTERNAL_checkSymbolNameOrToken(item["params"]["symbol"],localMemory=localMemory,callingFuncName=funcName)[0] != ERROR_C_1]
		basketItemsList = combine_qty_fno(basketItemsList)
		for itemDict in basketItemsList:
			itemDict = itemDict["params"]
			if (itemDict["sym_token"][:4] in ["1010", "1210"]):
				itemDict["cookie"] = kwargs["cookie"]
				margin_response = fy_marginCalc_noAuth(itemDict, tokenHash)
				if margin_response["s"] == "ok":
					avail_margin_updated = True
					margin_sum += margin_response[API_K_DATA_1][API_K_TOT_MARGIN]
					avail_margin = margin_response[API_K_DATA_1][API_K_AVAIL_MARGIN]
				else:
					baseFunc.logEntryFunc2(baseDef.LOG_STATUS_ERROR_1, moduleName, funcName, "",itemDict, margin_response=margin_response, message="Check Margin API failed")
			else:
				if (int(itemDict["side"]) == API_V_ORDER_SIDE_BUY_1 and not itemDict["symbol"].strip().endswith("FUT")):
					itemDict["cookie"] = kwargs["cookie"]
					margin_response = fy_marginCalc_noAuth(itemDict, tokenHash)
					if margin_response["s"] == "ok":
						avail_margin_updated = True
						margin_sum += margin_response[API_K_DATA_1][API_K_TOT_MARGIN]
						avail_margin = margin_response[API_K_DATA_1][API_K_AVAIL_MARGIN]
					else:
						baseFunc.logEntryFunc2(baseDef.LOG_STATUS_ERROR_1, moduleName, funcName, "",itemDict, margin_response=margin_response, message="Check Margin API failed")
				
				futdata.append(itemDict)

		if not avail_margin_updated:
			margin_response = fy_marginCalc_noAuth(defaultItemDict, tokenHash)
			if margin_response["s"] == "ok":
				avail_margin = margin_response[API_K_DATA_1][API_K_AVAIL_MARGIN]

		client_id = "-1"
		span_sum = 0
		for idx, item in enumerate(futdata):
			item["cookie"] = kwargs["cookie"]
			resp, client_id = fy_spanCalc(item, localMemory, idx + 1, client_id)
			span_sum = resp["totalMargin"]
		margin_sum += span_sum

		reset_spancalc(client_id)
		return {
			API_K_STATUS: API_V_SUCCESS,
			API_K_CODE: 200,
			API_K_DATA_1: {
				API_K_TOT_MARGIN: round(margin_sum, 2),
				API_K_AVAIL_MARGIN: round(avail_margin, 2),
			},
			API_OMS_K_MESSAGE_1: ""
		}

	except Exception as e:
		baseFunc.logEntryFunc2(baseDef.LOG_STATUS_ERROR_1, moduleName, funcName, "",kwargs, err_msg=e)
		return {baseKV.API_K_STATUS: baseKV.API_V_ERROR, baseKV.API_K_CODE: baseCodes.ERROR_C_UNKNOWN, baseKV.API_K_MSG: baseMsg.ERROR_M_UNKNOWN_1}


def combine_qty_fno(basket_orders_list):
	index_data = {}
	index_to_remove = []
	for idx, itemDict in enumerate(basket_orders_list):
		print(itemDict)
		itemDict = itemDict["params"]
		if itemDict["sym_token"][:4] not in ["1010", "1210"]:
			symbol = itemDict["symbol"]
			qty = int(itemDict["qty"])
			side = str(itemDict["side"])
			key = f"{symbol}-{side}"
			if key not in index_data:
				index_data[key] = idx
			else:
				basket_orders_list[index_data[key]]["params"]["qty"] += qty
				index_to_remove.append(idx)

	basket_orders_list = [item for idx, item in enumerate(basket_orders_list) if idx not in index_to_remove]
	return basket_orders_list
				

def fy_reset_basket(kwargs):
	funcName = "fy_reset_basket"
	try:
		funcRet = authFunc.initial_validate_access_token(kwargs, callingFuncName=funcName)
		if funcRet[baseKV.API_K_STATUS] == baseKV.API_V_ERROR:
			return funcRet
		tokenHash = funcRet[baseKV.API_K_DATA_1][0]
		fyId = funcRet[baseKV.API_K_DATA_1][1]

		if fyId in dataTradeDef.GUEST_CLIENT_ID:
			return {baseKV.API_K_STATUS: baseKV.API_V_ERROR, baseKV.API_K_CODE: baseCodes.ERROR_C_DEMO_USER, baseKV.API_K_MSG: baseMsg.ERROR_M_DEMO_USER}
			
		baseFunc.logEntryFunc2(baseDef.LOG_STATUS_SUCCESS_1, moduleName, funcName, "",kwargs["body"], fyId=fyId)

		inputBody = kwargs["body"]
		if not isinstance(inputBody, dict):
			inputBody = json.loads(inputBody)
		if "basketid" not in inputBody:
			return {baseKV.API_K_STATUS: baseKV.API_V_ERROR, baseKV.API_K_CODE: baseCodes.ERROR_C_INV_INP, baseKV.API_K_MSG: baseMsg.ERROR_M_INV_INPUT_1}
		basketId = inputBody["basketid"]

		funcRet = intFunc.INTERNAL_resetBasket(fyId, basketId, callingFuncName=funcName)
		if funcRet[0] == baseCodes.ERROR_C_1:
			return {baseKV.API_K_STATUS: baseKV.API_V_ERROR, baseKV.API_K_CODE: funcRet[1], baseKV.API_K_MSG: funcRet[2]}

		return {baseKV.API_K_STATUS: baseKV.API_V_SUCCESS, baseKV.API_K_CODE: baseCodes.SUCCESS_C_2, baseKV.API_K_MSG: "", baseKV.API_K_DATA_1: funcRet[1]}

	except Exception as e:
		baseFunc.logEntryFunc2(baseDef.LOG_STATUS_ERROR_1, moduleName, funcName, "",kwargs, err_msg=e)
		return {baseKV.API_K_STATUS: baseKV.API_V_ERROR, baseKV.API_K_CODE: baseCodes.ERROR_C_UNKNOWN, baseKV.API_K_MSG: baseMsg.ERROR_M_UNKNOWN_1}

