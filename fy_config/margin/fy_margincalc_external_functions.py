moduleName = "fy_margincalc_external_functions"
try:
	import sys
	import json
	import fy_trading_defines as tradeDef
	import fy_base_defines as fyBaseDef
	import fy_base_functions as fyBaseFunc
	import fy_base_api_keys_values as fyBaseKV
	import margin.fy_margincalc_internal_functions as margcalcIntr
	import fy_base_success_error_codes as baseCodes
	import fy_base_success_error_messages as baseMsg
	import fy_auth_functions as authFunc
	import requests
	
except Exception as e:
	print("ERR : %s : %s : %s" % (moduleName, "Could not import module", e))
	sys.exit()

def fy_marginCalc(kwargs):
	"""
		[FUNCTION]
			margin calculator
		[PARAMS] => Key value arguments
			tokenHash  : This is a hash of (fyId + AppId)
			securityId : exchange token
			productId  : 
			seg  : 
			exc  : NSE/BSE/MCX
			qty  : 
			price  : float value
			side  : B/S (buy/sell)
			triggerPrice  : float value
		[RETURN]
			Success :
			Failure :
	"""
	funcName = "fy_marginCalc"
	returnDict = {}
	try:
		if len(kwargs[tradeDef.API_K_COOKIE]) > 0:
			token = kwargs[tradeDef.API_K_COOKIE]
		elif len(kwargs[tradeDef.API_K_TOKENHASH]) > 0:
			token = kwargs[tradeDef.API_K_TOKENHASH]
		else:
			return {fyBaseKV.API_K_STATUS: fyBaseKV.API_V_ERROR, fyBaseKV.API_K_CODE: baseCodes.ERROR_C_INV_INP, fyBaseKV.API_K_MSG: baseMsg.ERROR_M_INV_INPUT_1}

		validateCookie = authFunc.INTERNAL_validateCookie(token, callingFuncName=funcName)
		if validateCookie[0] == baseCodes.ERROR_C_1:
			return {fyBaseKV.API_K_STATUS: fyBaseKV.API_V_ERROR, fyBaseKV.API_K_CODE: validateCookie[1], fyBaseKV.API_K_MSG: validateCookie[2]}
		tokenHash = validateCookie[1][authFunc.JWT_CLAIMS_K_TOKEN_HASH]
		fyId = validateCookie[1]["fy_id"]

		try:
			qty = kwargs[tradeDef.API_K_ORDER_QTY]
			qty = int(qty)
		except Exception as e:
			return {fyBaseKV.API_K_STATUS: fyBaseKV.API_V_ERROR, fyBaseKV.API_K_CODE: baseCodes.ERROR_C_INV_ORDER_QTY, fyBaseKV.API_K_MSG: baseMsg.ERROR_M_INV_ORDER_QTY}

		try:
			symbol = kwargs[tradeDef.API_K_FYSYMBOL]
		except Exception as e:
			return {fyBaseKV.API_K_STATUS: fyBaseKV.API_V_ERROR, fyBaseKV.API_K_CODE: baseCodes.ERROR_C_INV_FYSYMBOL, fyBaseKV.API_K_MSG: baseMsg.ERROR_M_INV_FYSYMBOL}

		try:
			prodList = kwargs[tradeDef.API_K_ORDER_PRODUCT]
			prodList = prodList.upper()
		except Exception as e:
			return {fyBaseKV.API_K_STATUS: fyBaseKV.API_V_ERROR, fyBaseKV.API_K_CODE: baseCodes.ERROR_C_INV_ORDER_PRODUCT, fyBaseKV.API_K_MSG: baseMsg.ERROR_M_INV_ORDER_PRODUCT}

		try:
			ordType = kwargs[tradeDef.API_K_ORDER_TYPE]
			ordType = int(ordType)
		except Exception as e:
			ordType = 2

		try:
			transType = kwargs[tradeDef.API_K_ORDER_SIDE]
			transType = int(transType)
		except Exception as e:
			return {fyBaseKV.API_K_STATUS: fyBaseKV.API_V_ERROR, fyBaseKV.API_K_CODE: baseCodes.ERROR_C_INV_ORDER_SIDE, fyBaseKV.API_K_MSG: baseMsg.ERROR_M_INV_ORDER_SIDE}

		try:
			price = kwargs[tradeDef.API_K_ORDER_LMT_PRICE]
			price = float(price)
		except Exception as e:
			if kwargs[tradeDef.API_K_ORDER_LMT_PRICE] == "":
				price = 0.0

		try:
			stopLoss=float(kwargs[tradeDef.API_K_ORDER_STOP_LOSS])
		except Exception as e:
			##Added because in some cases mobile app is sending blank string - considering 0 in such cases - ideally this should not happen
			if kwargs[tradeDef.API_K_ORDER_STOP_LOSS] == "":
				stopLoss = 0.0

		marginCalcRes = margcalcIntr.INTERNAL_fy_marginCalc(tokenHash, symbol, qty, ordType, transType, prodList, price, stopLoss)

		if marginCalcRes[0] == baseCodes.ERROR_C_1 or marginCalcRes[0] == baseCodes.ERROR_C_OMS_1:
			
			returnDict = {fyBaseKV.API_K_STATUS: fyBaseKV.API_V_ERROR,
						  fyBaseKV.API_K_CODE: marginCalcRes[1],
						  fyBaseKV.API_K_MSG: marginCalcRes[2]}
			return returnDict

		returnDict = {fyBaseKV.API_K_STATUS: fyBaseKV.API_V_SUCCESS,
					  fyBaseKV.API_K_CODE: baseCodes.SUCCESS_C_2,
					  fyBaseKV.API_K_DATA_1: marginCalcRes[1],
					  fyBaseKV.API_K_MSG: marginCalcRes[2]
			   }
		return returnDict

	except Exception as e:
		fyBaseFunc.logEntryFunc2(fyBaseDef.LOG_STATUS_ERROR_1, moduleName, funcName, "", e, baseCodes.ERROR_C_UNKNOWN, kwargs)
		return {fyBaseKV.API_K_STATUS: fyBaseKV.API_V_ERROR, fyBaseKV.API_K_CODE: baseCodes.ERROR_C_UNKNOWN, fyBaseKV.API_K_MSG: baseMsg.ERROR_M_UNKNOWN_1}

def fy_marginCalc_noAuth(kwargs, tokenHash):
	"""
		[FUNCTION]
			margin calculator
		[PARAMS] => Key value arguments
			tokenHash  : This is a hash of (fyId + AppId)
			securityId : exchange token
			productId  : 
			seg  : 
			exc  : NSE/BSE/MCX
			qty  : 
			price  : float value
			side  : B/S (buy/sell)
			triggerPrice  : float value
		[RETURN]
			Success :
			Failure :
	"""
	funcName = "fy_marginCalc"
	returnDict = {}
	try:
		try:
			qty = kwargs[tradeDef.API_K_ORDER_QTY]
			qty = int(qty)
		except Exception as e:
			# return [baseCodes.ERROR_C_1,baseCodes.ERROR_C_INV_ORDER_QTY,baseMsg.ERROR_M_INV_ORDER_QTY]
			return {fyBaseKV.API_K_STATUS: fyBaseKV.API_V_ERROR, fyBaseKV.API_K_CODE: baseCodes.ERROR_C_INV_ORDER_QTY, fyBaseKV.API_K_MSG: baseMsg.ERROR_M_INV_ORDER_QTY}

		try:
			symbol = kwargs[tradeDef.API_K_FYSYMBOL]
		except Exception as e:
			# return [baseCodes.ERROR_C_1,baseCodes.ERROR_C_INV_SYMBOL,baseMsg.ERROR_M_INV_FYSYMBOL]
			return {fyBaseKV.API_K_STATUS: fyBaseKV.API_V_ERROR, fyBaseKV.API_K_CODE: baseCodes.ERROR_C_INV_FYSYMBOL, fyBaseKV.API_K_MSG: baseMsg.ERROR_M_INV_FYSYMBOL}

		# try:
		# 	discQty = kwargs[tradeDef.API_K_DISC_QTY]
		# 	discQty = int(discQty)
		# except Exception as e:
		# 	# return [baseCodes.ERROR_C_1, baseCodes.ERROR_C_INV_ORDER_DISC_QTY, baseMsg.ERROR_M_INV_ORDER_DISC_QTY]
		# 	return {fyBaseKV.API_K_STATUS: fyBaseKV.API_V_ERROR, fyBaseKV.API_K_CODE: baseCodes.ERROR_C_INV_ORDER_DISC_QTY, fyBaseKV.API_K_MSG: baseMsg.ERROR_M_INV_ORDER_DISC_QTY}

		try:
			prodList = kwargs[tradeDef.API_K_ORDER_PRODUCT]
			prodList = prodList.upper()
		except Exception as e:
			# return [baseCodes.ERROR_C_1, baseCodes.ERROR_M_INV_PRODUCT_ID, baseMsg.ERROR_M_INV_ORDER_PRODUCT]
			return {fyBaseKV.API_K_STATUS: fyBaseKV.API_V_ERROR, fyBaseKV.API_K_CODE: baseCodes.ERROR_C_INV_ORDER_PRODUCT, fyBaseKV.API_K_MSG: baseMsg.ERROR_M_INV_ORDER_PRODUCT}

		try:
			ordType = kwargs[tradeDef.API_K_ORDER_TYPE]
			ordType = int(ordType)
		except Exception as e:
			ordType = 2
			# return [baseCodes.ERROR_C_1, baseCodes.ERROR_C_INV_ORDER_TYPE, baseMsg.ERROR_M_INV_ORDER_TYPE]
			# return {fyBaseKV.API_K_STATUS: fyBaseKV.API_V_ERROR, fyBaseKV.API_K_CODE: baseCodes.ERROR_C_INV_ORDER_TYPE, fyBaseKV.API_K_MSG: baseMsg.ERROR_M_INV_ORDER_TYPE}

		try:
			transType = kwargs[tradeDef.API_K_ORDER_SIDE]
			transType = int(transType)
		except Exception as e:
			# return [baseCodes.ERROR_C_1, baseCodes.ERROR_C_MF_INV_BUY_SELL_TYPE, baseMsg.ERROR_M_INV_ORDER_SIDE]
			return {fyBaseKV.API_K_STATUS: fyBaseKV.API_V_ERROR, fyBaseKV.API_K_CODE: baseCodes.ERROR_C_INV_ORDER_SIDE, fyBaseKV.API_K_MSG: baseMsg.ERROR_M_INV_ORDER_SIDE}

		try:
			price = kwargs[tradeDef.API_K_ORDER_LMT_PRICE]
			price = float(price)
		except Exception as e:
			if kwargs[tradeDef.API_K_ORDER_LMT_PRICE] == "":
				price = 0.0
			# return [baseCodes.ERROR_C_1, baseCodes.ERROR_C_INV_ORDER_LMT_PRICE, baseMsg.ERROR_M_INV_ORDER_LMT_PRICE]
			# return {fyBaseKV.API_K_STATUS: fyBaseKV.API_V_ERROR, fyBaseKV.API_K_CODE: baseCodes.ERROR_C_INV_ORDER_LMT_PRICE, fyBaseKV.API_K_MSG: baseMsg.ERROR_M_INV_ORDER_LMT_PRICE}

		try:
			stopLoss=float(kwargs[tradeDef.API_K_ORDER_STOP_LOSS])
		except Exception as e:
			##Added because in some cases mobile app is sending blank string - considering 0 in such cases - ideally this should not happen
			if kwargs[tradeDef.API_K_ORDER_STOP_LOSS] == "":
				stopLoss = 0.0
			# return {fyBaseKV.API_K_STATUS: fyBaseKV.API_V_ERROR, fyBaseKV.API_K_CODE: baseCodes.ERROR_C_INV_ORDER_STOP_LOSS, fyBaseKV.API_K_MSG: baseMsg.ERROR_M_INV_ORDER_STOP_LOSS}

		marginCalcRes = margcalcIntr.INTERNAL_fy_marginCalc(tokenHash, symbol, qty, ordType, transType, prodList, price, stopLoss)

		# print("marginCalcRes",marginCalcRes)
		if marginCalcRes[0] == baseCodes.ERROR_C_1 or marginCalcRes[0] == baseCodes.ERROR_C_OMS_1:

			returnDict = {fyBaseKV.API_K_STATUS: fyBaseKV.API_V_ERROR,
						  fyBaseKV.API_K_CODE: marginCalcRes[1],
						  fyBaseKV.API_K_MSG: marginCalcRes[2]}
			return returnDict

		returnDict = {fyBaseKV.API_K_STATUS: fyBaseKV.API_V_SUCCESS,
					  fyBaseKV.API_K_CODE: baseCodes.SUCCESS_C_2,
					  fyBaseKV.API_K_DATA_1: marginCalcRes[1],
					  fyBaseKV.API_K_MSG: marginCalcRes[2]
			   }
		return returnDict

	except Exception as e:
		fyBaseFunc.logEntryFunc2(fyBaseDef.LOG_STATUS_ERROR_1, moduleName, funcName, "", e, baseCodes.ERROR_C_UNKNOWN, kwargs)
		# returnDict[fyBaseKV.API_K_MSG] = e
		# return json.dumps(returnDict)
		return {fyBaseKV.API_K_STATUS: fyBaseKV.API_V_ERROR, fyBaseKV.API_K_CODE: baseCodes.ERROR_C_UNKNOWN, fyBaseKV.API_K_MSG: baseMsg.ERROR_M_UNKNOWN_1}



def get_spancalc_payload(kwargs, id, sym_info, instrument_type, count):
	segment = "D"
	if kwargs["exchange"] == "MCX":
		segment = "M"
	elif sym_info["fyToken"].startswith("1012"):
		segment = "C"
	return {
		"client_id": str(id),
		"exch_id": kwargs["exchange"],
		"segment": segment,
		"scrip_code": str(sym_info["exToken"]),
		"underlying_scrip": str(sym_info["underFyTok"])[10:],
		"buy_sell":"B" if int(kwargs["side"]) == 1 else "S",
		"quantity": str(kwargs["qty"]),
		"instrument": instrument_type,
		"strike_price": str(int(sym_info["strikePrice"])) if sym_info["strikePrice"] != -1 else 0,
		"row_no": str(count)
	}


def fy_spanCalc(kwargs, redis, count, id):
	symbol_info = redis.hget("symbol_master", kwargs["symbol"])
	if symbol_info:
		symbol_info = json.loads(symbol_info.decode("utf-8"))
	
	if symbol_info["fyToken"][:4] == "1120":
		payload = get_spancalc_payload(kwargs, id, symbol_info, "FUTCOM", count)
	elif symbol_info["fyToken"][:4] == "1012":
		if symbol_info["symTicker"].strip().endswith("FUT"):
			payload = get_spancalc_payload(kwargs, id, symbol_info, "FUTCUR", count)
		else:
			payload = get_spancalc_payload(kwargs, id, symbol_info, "OPTCUR", count)
	elif symbol_info["optType"] in ["CE", "PE"]:
		payload = get_spancalc_payload(kwargs, id, symbol_info, "OPTIDX", count)
	else:
		payload = get_spancalc_payload(kwargs, id, symbol_info, "FUTIDX", count)
	
	response = requests.post("https://tradeonline-pub.fyers.in/RupeeSeedWS/CalMargin/index", json=payload)
	if response.status_code == 200:
		resp = response.json()
		if "marginTotal" in resp:
			return {
				"totalMargin": resp["marginTotal"]["T_TOTAL_MARGIN"],
				"marginBenefit": resp["marginTotal"]["T_SPREAD_BENEFIT"]
			}, resp["marginList"][0]["CLIENT_ID"]			

	fyBaseFunc.logEntryFunc2(fyBaseDef.LOG_STATUS_ERROR_1, moduleName, "fySpanCalc", "", baseCodes.ERROR_C_UNKNOWN, kwargs, span_calc_request=payload, span_calc_response=response.status_code, span_calc_content=response.content )
	return {
		"totalMargin": 0,
		"marginBenefit": 0
	}, "-1"


def reset_spancalc(client_id):
	payload = {"client_id": client_id}
	response = requests.post("https://tradeonline-pub.fyers.in/RupeeSeedWS/CalMargin/reset", json=payload)
	if response.status_code != 200 or response.json()["MESSAGE"] != "Client Data Deleted Success":
		fyBaseFunc.logEntryFunc2(fyBaseDef.LOG_STATUS_ERROR_1, moduleName, "fySpanCalc", "", baseCodes.ERROR_C_UNKNOWN, client_id, span_calc_response=response.status_code, span_calc_content=response.content )
