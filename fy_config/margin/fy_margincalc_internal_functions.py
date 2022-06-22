moduleName = "fy_margincalc_internal_functions"

try:
	import sys
	import fy_trading_defines as tradeDef
	import fy_data_and_trade_defines as dataTradeDef
	from fy_base_defines import LOG_STATUS_ERROR_1
	from fy_base_success_error_codes import ERROR_C_1, ERROR_C_INVALID_TOKEN_6, \
	 ERROR_C_OMS_UNKNOWN, ERROR_C_INV_EXCHANGE, ERROR_C_INV_ORDER_TRIG_PRICE, \
	 ERROR_C_INV_SEGMENT, ERROR_C_INV_ORDER_TYPE, ERROR_C_OMS_1, \
	 SUCCESS_C_1, ERROR_C_UNKNOWN
	from fy_base_success_error_messages import ERROR_M_MF_INV_TOKEN_ID, \
	 ERROR_M_INV_EXCHANGE, ERROR_M_INV_ORDER_TRIG_PRICE, ERROR_M_INV_SEGMENT, \
	 ERROR_M_INV_ORDER_TYPE
	from fy_common_api_keys_values import API_K_TOT_MARGIN, API_K_AVAIL_MARGIN

	import fy_base_functions as fyBaseFunc
	import fy_trading_internal_functions as fyTradeInt
	from fy_common_internal_functions import INTERNAL_checkSymbolNameOrToken, \
     INTERNAL_getSymExAndSegment

except Exception as e:
	print("ERR : %s : %s : %s" % (moduleName, "Could not import module", e))
	sys.exit()


def INTERNAL_fy_marginCalc(tokenHash, symbol, qty, ordType, transType, prodList, price, stopLoss, localMemory = None, callingFuncName=""):
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
	funcName = "INTERNAL_fy_marginCalc"
	try:
		tokenHash = str(tokenHash)		
		fyTokenList = fyTradeInt.INTERNAL_getToken_checkStatus(tokenHash, callingFuncName=funcName)
		if fyTokenList[0] == ERROR_C_1:
			if (fyTokenList[1] == ERROR_C_INVALID_TOKEN_6) or (fyTokenList[1] == ERROR_C_OMS_UNKNOWN) :		
				fyTokenList[2] = ERROR_M_MF_INV_TOKEN_ID
				return fyTokenList
			return fyTokenList

		fyId = fyTokenList[1][0]
		omsTokenId = fyTokenList[1][1]
		aesKey = fyTokenList[1][2]

		# Converting symbol name to token
		checkSymbolList = INTERNAL_checkSymbolNameOrToken(symbol,localMemory=localMemory,callingFuncName=callingFuncName)
		if checkSymbolList[0] == ERROR_C_1:
			fyBaseFunc.logEntryFunc2(LOG_STATUS_ERROR_1,moduleName,funcName,callingFuncName,fyId,checkSymbolList)
			return checkSymbolList

		# Splitting the token to get the exchange, segment and scripCode
		symbolList = INTERNAL_getSymExAndSegment(checkSymbolList[1][0],callingFuncName=callingFuncName)
		
		if symbolList[0] == ERROR_C_1:
			fyBaseFunc.logEntryFunc2(LOG_STATUS_ERROR_1,moduleName,funcName,callingFuncName,fyId,symbolList)
			return symbolList

		if symbolList[1][0] == str(dataTradeDef.EXCHANGE_CODE_NSE):
			symExcg = dataTradeDef.EXCHANGE_NAME_NSE
		elif symbolList[1][0] == str(dataTradeDef.EXCHANGE_CODE_MCX):
			symExcg = dataTradeDef.EXCHANGE_NAME_MCX_1
		elif symbolList[1][0] == str(dataTradeDef.EXCHANGE_CODE_BSE):
			symExcg = dataTradeDef.EXCHANGE_NAME_BSE
		else:
			return [ERROR_C_1, ERROR_C_INV_EXCHANGE, ERROR_M_INV_EXCHANGE]

		try:
			stopLoss = float(stopLoss)
			if prodList == "BO":
				triggerPrice = stopLoss
			elif prodList == "CO":
				triggerPrice = stopLoss
			else:
				triggerPrice = 0
		except Exception as e:
			return [ERROR_C_1, ERROR_C_INV_ORDER_TRIG_PRICE, ERROR_M_INV_ORDER_TRIG_PRICE]

		rsFormatRet = fyTradeInt.changeToRSFormat(segment=symbolList[1][1], productType=prodList, orderType=ordType, price=price, transType=transType, funcType="marginCalc")
		if rsFormatRet[0] == ERROR_C_1:
			fyBaseFunc.logEntryFunc2(LOG_STATUS_ERROR_1,moduleName,funcName,callingFuncName,fyId,rsFormatRet)
			return rsFormatRet

		symType = rsFormatRet[1][fyTradeInt.API_K_SYM_SEGMENT]
		prodList = rsFormatRet[1][fyTradeInt.API_K_ORDER_PRODUCT]
		ordType = rsFormatRet[1][fyTradeInt.API_K_ORDER_TYPE_RS]
		transType = rsFormatRet[1][fyTradeInt.API_K_TRANS_TYPE]
		
		# Rupeeseed has different codes for each segment
		if symbolList[1][1] == str(dataTradeDef.SYM_SEGMENT_CM):
			symType = fyTradeInt.API_OMS_V_SEG_CM_1
		elif symbolList[1][1] == str(dataTradeDef.SYM_SEGMENT_FO):
			symType = fyTradeInt.API_OMS_V_SEG_FO_1
		elif symbolList[1][1] == str(dataTradeDef.SYM_SEGMENT_CD):
			symType = fyTradeInt.API_OMS_V_SEG_CD_1
		elif symbolList[1][1] == str(dataTradeDef.SYM_SEGMENT_COM):
			symType = fyTradeInt.API_OMS_V_SEG_COM_1
		else:
			return [ERROR_C_1, ERROR_C_INV_SEGMENT, ERROR_M_INV_SEGMENT]

		# Based on order type, we will update the price to the paramsdict
		if (ordType == fyTradeInt.API_V_ORDER_TYPE_LMT_2):
			price = str(price)
		elif (ordType == fyTradeInt.API_V_ORDER_TYPE_MKT_2):
			price = str(0)
		else:
			return [ERROR_C_1, ERROR_C_INV_ORDER_TYPE, ERROR_M_INV_ORDER_TYPE]	

		secId = symbolList[1][2]
		qty = str(qty)
		price = str(price)
		triggerPrice = str(triggerPrice)

		paramsForEncryption = {
			tradeDef.API_OMS_K_CLIENT_ID_2: fyId,
			tradeDef.API_OMS_K_SECURITY_ID: secId,
			tradeDef.API_OMS_K_PRODUCT_ID: prodList,
			tradeDef.API_OMS_ORDER_DETAIL_SEG: symType,
			tradeDef.API_OMS_K_EXCHANE: symExcg,
			tradeDef.API_OMS_K_TOTAL_REDEEM_QTY: qty,
			tradeDef.API_OMS_K_PRICE: price,
			tradeDef.API_OMS_K_BUYSELL : transType, 							
			tradeDef.API_OMS_K_TRIGGER_PRICE: triggerPrice,
		}

		urlForRequest = tradeDef.REQ_URL_OMS_MAIN_3 + tradeDef.API_OMS_REQ_PATH_MARGIN_CALC
		
		sendReqFuncRet = fyTradeInt.INTERNAL_createAndSendOmsRequest(fyId, omsTokenId, aesKey,paramsForEncryption, urlForRequest, callingFuncName=funcName)
	
		if(sendReqFuncRet[0] == ERROR_C_1):
			return sendReqFuncRet

		omsResponse = sendReqFuncRet[1]

		# Decrypt the response received from the OMS
		readOmsResponseFuncRet = fyTradeInt.INTERNAL_decryptOmsResponse(omsResponse, aesKey, callingFuncName=funcName)
		if readOmsResponseFuncRet[0] == ERROR_C_1:
			return readOmsResponseFuncRet
		userInfoList = readOmsResponseFuncRet[1]

		# Check for user invalidation. If yes, re-send the request
		readOmsResponseFuncRet2 = fyTradeInt.INTERNAL_readOmsDecryptedResponse(userInfoList,tokenHash, paramsForEncryption, urlForRequest,localMemory=localMemory,callingFuncName=funcName)
		if (readOmsResponseFuncRet2[0] == ERROR_C_1) or (readOmsResponseFuncRet2[0] == ERROR_C_OMS_1):
			return readOmsResponseFuncRet2
		marginList = readOmsResponseFuncRet2[2]
		marginDetailsList = []
		
		# If we have received data for margin
		if (len(marginList) != 0):
			totMargin = marginList["TOTMARGIN"]
			availBal = marginList["AVAILBALANCE"]

			marginDict = {API_K_TOT_MARGIN:totMargin,API_K_AVAIL_MARGIN:availBal}
			return [SUCCESS_C_1,marginDict,""]
			
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fyBaseFunc.logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, e, ERROR_C_UNKNOWN,"Line Number: %s"%str(exc_tb.tb_lineno))
		return [ERROR_C_1 , ERROR_C_UNKNOWN, funcName]

