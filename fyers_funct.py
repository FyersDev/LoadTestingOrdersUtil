#!/usr/bin/env python
import sys, os, time, json
sys.path.append("./fy_config/")
import lambda_defines as ld
import TV_inp_defines as tvDef
import fy_base_api_keys_values as b_KV
import fy_common_api_keys_values as c_KV
import fyers_inp_validatn as fyValid
import fy_base_success_error_codes as base_SEC

class UserAuth(object):
	"""
	Authentication of the user accessing services from trading view

	"""
	def init(self, req):
		self.req = req
		self.isValid = False ## True is the user is validated successfully
		self.validateUser()

	def validateUser(self):
		authDict = self.req.getHeaderParm([tvDef.TV_HEADER_AUTHZATN])
		if tvDef.TV_HEADER_AUTHZATN not in authDict:
			authCode = authDict[tvDef.TV_HEADER_AUTHZATN]
			print( "authCode:", authCode)

def tvAuth():
	## Authenticate the user
	UserAuth()
	return {b_KV.API_K_STATUS : b_KV.API_V_SUCCESS, b_KV.API_K_CODE : 0, b_KV.API_K_MSG : ""}

	return {b_KV.API_K_STATUS : b_KV.API_V_ERROR, b_KV.API_K_CODE : -99, b_KV.API_K_MSG : "Something went wrong"}

def tvAuthorizePOST(req, resp):
	userName = "from form data"
	password = "from form data"
	respData = {
		b_KV.API_K_STATUS : b_KV.API_V_SUCCESS,
		c_KV.API_K_ERRMSG: "string",
		c_KV.API_K_DETAILS: {
			"access_token": "string",
			"expiration": 0
		},
		"f": "tvAuthorizePOST"
	}
	return respData

def tvConfigGET(req, resp):
	# {
	# 	"symbols_types": [
	# 		{"name": "All types", "value": ""},
	# 		{"name": "Stocks", "value": "Stock"},
	# 		{"name": "Futures", "value": "Futures"},
	# 		{"name": "Options", "value": "Options"},
	# 		{"name": "ETFs", "value": "ETF"},
	# 		{"name": "Indices", "value": "INDEX"}
	# 	],
	# 	"supports_group_request": False,
	# 	"symbolsTypes": [
	# 		{"name": "All types", "value": ""},
	# 		{"name": "Stocks", "value": "Stock"},
	# 		{"name": "Futures", "value": "Futures"},
	# 		{"name": "Options", "value": "Options"},
	# 		{"name": "ETFs", "value": "ETF"},
	# 		{"name": "Indices", "value": "INDEX"}
	# 	],
	# 	"supportedResolutions": ["1", "2", "3", "5", "10", "15", "20", "30", "60", "120", "240", "D", "W", "M", "12M"],
	# 	"supported_resolutions": ["1", "2", "3", "5", "10", "15", "20", "30", "60", "120", "240", "D", "W", "M", "12M"],
	# 	"supports_marks": true,
	# 	"supports_search": true,
	# 	"supports_timescale_marks": false,
	# 	"exchanges": [
	# 		{"name": "All Exchanges", "value": "", "desc": ""},
	# 		{"name": "NSE", "value": "NSE", "desc": "National Stock Exchange"},
	# 		{"name": "MCX", "value": "MCX", "desc": "Multi Commodity Exchange"}
	# 	],
	# 	"supports_time": true
	# }
	locale = "Input local"
	respData = {
		b_KV.API_K_STATUS : b_KV.API_V_SUCCESS,
		c_KV.API_K_ERRMSG: "string",
		c_KV.API_K_DETAILS: {
			"accountManager": [
				{
					"id": "string",
					"title": "string",
					"columns": [
						{
							"id": "string",
							"title": "string",
							"tooltip": "string",
							"fixedWidth": True,
							"sortable": True
						}
					]
				}
			],
			"durations": [
				{
					"id": "string",
					"title": "string",
					"hasDatePicker": True,
					"hasTimePicker": True
				}
			],
			"pullingInterval": {
				"history": 0,
				"quotes": 0,
				"orders": 0,
				"positions": 0,
				"accountManager": 0
			}
		},
		"f": "tvConfigGET"
	}
	return respData

def tvAccGET(req, resp):
	retAuth = tvAuth(req, resp)
	if retAuth[b_KV.API_K_STATUS] != b_KV.API_V_SUCCESS:
		return retAuth
	respData = {
		b_KV.API_K_STATUS : b_KV.API_V_SUCCESS,
		c_KV.API_K_ERRMSG: "string",
		c_KV.API_K_DETAILS: [
			{
				"id": "string",
				"name": "string",
				"currency": "Rs",
				"currencySign": "string",
				"config": {
					"showQuantityInsteadOfAmount": True,
					"supportDOM": True,
					"supportBrackets": True,
					"supportClosePosition": True,
					"supportEditAmount": True,
					"supportLevel2Data": True,
					"supportMultiposition": True,
					"supportPLUpdate": True,
					"supportReducePosition": True,
					"supportStopLimitOrders": True,
					"supportOrdersHistory": True,
					"supportExecutions": True
				}
			}
		],
		"f": "tvAccGET"
	}
	return respData

def tvAccStateGET(req, resp):
	"""
	Get account information.
	[INPUT] 	: 	accountId* :The account identifier
					string
					(path)

					locale* :Locale (language) id
					string
					(query)
	"""
	retAuth = tvAuth()
	if retAuth[b_KV.API_K_STATUS] != b_KV.API_V_SUCCESS:
		return retAuth
	pathList = req.getPathList()
	if pathList < 4:
		return { b_KV.API_K_STATUS : b_KV.API_V_ERROR, c_KV.API_K_ERRMSG: "Invalid request"}

	pathList = pathList[ld.TRADING_VIEW_ALB_PATH_LEN:]
	accountId = pathList[1]
	# print("pathList:", pathList, "accountId:", accountId)

	queryDict = req.getQueryParams([tvDef.TV_INP_LOCALE])
	if tvDef.TV_INP_LOCALE not in queryDict:
		return { b_KV.API_K_STATUS : b_KV.API_V_ERROR, c_KV.API_K_ERRMSG: "Invalid request parameter locale."}
	locale = queryDict[tvDef.TV_INP_LOCALE]
	print ("locale:", locale)

	respData = {
		b_KV.API_K_STATUS : b_KV.API_V_SUCCESS,
		c_KV.API_K_ERRMSG: "string",
		c_KV.API_K_DETAILS: {
			"balance": 0,
			"unrealizedPl": 0,
			"amData": [
				[
					[
						"string"
					]
				]
			]
		},
		"f": "tvAccStateGET"
	}
	return respData

def tvAccOrdersGET(req, resp):
	"""
	Get pending orders for an account.
	[INPUT] :	accountId*: The account identifier
				string
				(path)

	"""
	retAuth = tvAuth()
	if retAuth[b_KV.API_K_STATUS] != b_KV.API_V_SUCCESS:
		return retAuth
	pathList = req.getPathList()
	if pathList < 4:
		return { b_KV.API_K_STATUS : b_KV.API_V_ERROR, c_KV.API_K_ERRMSG: "Invalid request"}

	pathList 	= pathList[ld.TRADING_VIEW_ALB_PATH_LEN:]
	accountId 	= pathList[1]

	respData = {
		b_KV.API_K_STATUS : b_KV.API_V_SUCCESS,
		c_KV.API_K_ERRMSG: "string",
		c_KV.API_K_DETAILS: [
			{
				"id": "string",
				"instrument": "string",
				"qty": 0,
				"side": "buy",
				"type": "market",
				"filledQty": 0,
				"avgPrice": 0,
				"limitPrice": 0,
				"stopPrice": 0,
				"parentId": "string",
				"parentType": "order",
				"duration": {
					"type": "string",
					"datetime": 0
				},
			"status": "pending"
			}
		],
		'f': "tvAccOrdersGET"
	}
	return respData

def tvAccOrdersPOST(req, resp):
	"""
	Create a new order
	[INPUT]	:	accountId*: The account identifier
				string
				(path)

				instrument*: Instrument to open the order on
				string
				(formData)

				qty*: The number of units to open order for
				number
				(formData)

				side*: Side. Possible values - buy and sell.
				string
				(formData)

				type*: Type. Possible values - market, stop, limit, stoplimit.
				string
				(formData)

				limitPrice: Limit Price for Limit or StopLimit order
				number
				(formData)

				stopPrice: Stop Price for Stop or StopLimit order
				number
				(formData)

				durationType: Duration ID (if supported)
				string
				(formData)

				durationDateTime: Expiration datetime UNIX timestamp (if supported by duration type)
				number
				(formData)

				stopLoss: StopLoss price (if supported)
				number
				(formData)

				takeProfit: TakeProfit price (if supported)
				number
				(formData)

	"""
	retAuth = tvAuth()
	if retAuth[b_KV.API_K_STATUS] != b_KV.API_V_SUCCESS:
		return retAuth
	pathList 	= req.getPathList()
	if pathList < 4:
		return {b_KV.API_K_STATUS : b_KV.API_V_ERROR, c_KV.API_K_ERRMSG: "Invalid request path."}

	pathList 	= pathList[ld.TRADING_VIEW_ALB_PATH_LEN:]
	accountId 	= pathList[1]
	retBody 	= req.getBody()
	if not retBody:
		return {b_KV.API_K_STATUS : b_KV.API_V_ERROR, c_KV.API_K_ERRMSG: "Invalid request body."}

	if not isinstance(retBody, dict):
		try:
			retBody = json.loads(retBody)
		except Exception as e:
			return {b_KV.API_K_STATUS : b_KV.API_V_ERROR, c_KV.API_K_ERRMSG: "Invalid request body."}

	## Input validation
	## Required
	## Instrument
	if tvDef.TV_INP_ORDER_INSTR not in retBody:
		return {b_KV.API_K_STATUS : b_KV.API_V_ERROR, c_KV.API_K_ERRMSG: "Invalid request instrument."}
	inpInstr 		= retBody[tvDef.TV_INP_ORDER_INSTR]
	if inpInstr:
		## Validate instrument. May be validate ticker
		None
	## Quantity
	if tvDef.TV_INP_ORDER_QTY not in retBody:
		return {b_KV.API_K_STATUS : b_KV.API_V_ERROR, c_KV.API_K_ERRMSG: "Invalid request quantity."}
	inpQty 			= retBody[tvDef.TV_INP_ORDER_QTY]
	try:
		inpQty 		= int(inpQty)
	except Exception as e:
		return {b_KV.API_K_STATUS : b_KV.API_V_ERROR, c_KV.API_K_ERRMSG: "Invalid request quantity."}
	## Side
	if tvDef.TV_INP_ORDER_SIDE not in retBody:
		return {b_KV.API_K_STATUS : b_KV.API_V_ERROR, c_KV.API_K_ERRMSG: "Invalid request side."}
	inpSide 		= str(retBody[tvDef.TV_INP_ORDER_SIDE]).upper()
	if inpSide not in tvDef.TV_INP_ORDER_SIDE_VAL:
		return {b_KV.API_K_STATUS : b_KV.API_V_ERROR, c_KV.API_K_ERRMSG: "Invalid request side."}
	## Type
	if tvDef.TV_INP_ORDER_TYPE not in retBody:
		return {b_KV.API_K_STATUS : b_KV.API_V_ERROR, c_KV.API_K_ERRMSG: "Invalid request order type."}
	inpOrdType 		= str(retBody[tvDef.TV_INP_ORDER_TYPE]).upper()
	if inpOrdType not in tvDef.TV_INP_ORDER_TYPE_VAL:
		return {b_KV.API_K_STATUS : b_KV.API_V_ERROR, c_KV.API_K_ERRMSG: "Invalid request order type."}

	## Optional
	inpLimitPrice 	= None
	inpStopPrice 	= None
	inpDuratnType 	= None
	inpDuratnTime 	= None
	inpStopLoss 	= None
	inpTakeProfit 	= None
	if tvDef.TV_INP_ORDER_LIMIT_P in retBody:
		try:
			inpLimitPrice 	= float(retBody[tvDef.TV_INP_ORDER_LIMIT_P])
		except Exception as e:
			return {b_KV.API_K_STATUS : b_KV.API_V_ERROR, c_KV.API_K_ERRMSG: "Invalid request limit price."}
	if tvDef.TV_INP_ORDER_STOP_P in retBody:
		try:
			inpStopPrice 	= float(retBody[tvDef.TV_INP_ORDER_STOP_P])
		except Exception as e:
			return {b_KV.API_K_STATUS : b_KV.API_V_ERROR, c_KV.API_K_ERRMSG: "Invalid request stop price."}
	if tvDef.TV_INP_ORDER_DURATN_TY in retBody:
		## Dont know how to validate this
		inpDuratnType 	= retBody[tvDef.TV_INP_ORDER_DURATN_TY]
	if tvDef.TV_INP_ORDER_DYRATN_TI in retBody:
		try:
			inpDuratnTime 	= float(retBody[tvDef.TV_INP_ORDER_DYRATN_TI])
		except Exception as e:
			return {b_KV.API_K_STATUS : b_KV.API_V_ERROR, c_KV.API_K_ERRMSG: "Invalid request duration time."}
	if tvDef.TV_INP_ORDER_STOP_L in retBody:
		try:
			inpStopLoss 	= float(retBody[tvDef.TV_INP_ORDER_STOP_L])
		except Exception as e:
			return {b_KV.API_K_STATUS : b_KV.API_V_ERROR, c_KV.API_K_ERRMSG: "Invalid request stop loss."}
	if tvDef.TV_INP_ORDER_TAKE_PROF in retBody:
		try:
			inpTakeProfit 	= float(retBody[tvDef.TV_INP_ORDER_TAKE_PROF])
		except Exception as e:
			return {b_KV.API_K_STATUS : b_KV.API_V_ERROR, c_KV.API_K_ERRMSG: "Invalid request take profit."}

	## Write the code to place order before return
	respData = {
		b_KV.API_K_STATUS : b_KV.API_V_SUCCESS,
		c_KV.API_K_ERRMSG: "string",
		c_KV.API_K_DETAILS: {
			"orderId": "string"
		},
		'f': "tvAccOrdersPOST"
	}
	return respData

def tvAccOrdersHistGET(req, resp):
	"""
	Get order history for an account. It is expected that returned orders will have a final status (rejected, filled, canceled). This request is optional. If you dont support history of orders set AccountFlags::supportOrdersHistory to false.
	"""
	retAuth = tvAuth()
	if retAuth[b_KV.API_K_STATUS] != b_KV.API_V_SUCCESS:
		return retAuth
	pathList 	= req.getPathList()
	if pathList < 4:
		return {b_KV.API_K_STATUS : b_KV.API_V_ERROR, c_KV.API_K_ERRMSG: "Invalid request path."}

	pathList 	= pathList[ld.TRADING_VIEW_ALB_PATH_LEN:]
	accountId 	= pathList[1]

	queryDict = req.getQueryParams([tvDef.TV_INP_ORDER_HIST_MAX_CNT])
	maxCount = None
	if tvDef.TV_INP_ORDER_HIST_MAX_CNT in queryDict:
		try:
			maxCount = int(queryDict[tvDef.TV_INP_ORDER_HIST_MAX_CNT])
		except Exception as e:
			return {b_KV.API_K_STATUS : b_KV.API_V_ERROR, c_KV.API_K_ERRMSG: "Invalid request order history count."}

	maxCount = "input"
	respData = {
		b_KV.API_K_STATUS : b_KV.API_V_SUCCESS,
		c_KV.API_K_ERRMSG: "string",
		c_KV.API_K_DETAILS: [
			{
				"id": "string",
				"instrument": "string",
				"qty": 0,
				"side": "buy",
				"type": "market",
				"filledQty": 0,
				"avgPrice": 0,
				"limitPrice": 0,
				"stopPrice": 0,
				"parentId": "string",
				"parentType": "order",
				"duration": {
					"type": "string",
					"datetime": 0
				},
				"status": "pending"
			}
		],
		'f': "tvAccOrdersHistGET"
	}
	return respData

def tvAccOrderIdGET(req, resp):
	"""
	Get an order for an account. It can be an active or historical order.
	[INPUT]		:	accountId: The account identifier
					string
					(path)

					orderId: Order ID
					string
					(path)
	"""
	retAuth = tvAuth()
	if retAuth[b_KV.API_K_STATUS] != b_KV.API_V_SUCCESS:
		return retAuth
	pathList 	= req.getPathList()
	if pathList < 6:
		return {b_KV.API_K_STATUS : b_KV.API_V_ERROR, c_KV.API_K_ERRMSG: "Invalid request path."}
	pathList 	= pathList[ld.TRADING_VIEW_ALB_PATH_LEN:]
	accountId 	= pathList[1]
	orderId 	= pathList[3]
	## Validate order ID
	respData = {
		b_KV.API_K_STATUS : b_KV.API_V_SUCCESS,
		c_KV.API_K_ERRMSG: "string",
		c_KV.API_K_DETAILS: {
			"id": "string",
			"instrument": "string",
			"qty": 0,
			"side": "buy",
			"type": "market",
			"filledQty": 0,
			"avgPrice": 0,
			"limitPrice": 0,
			"stopPrice": 0,
			"parentId": "string",
			"parentType": "order",
			"duration": {
				"type": "string",
				"datetime": 0
			},
			"status": "pending"
		},
		'f': "tvAccOrderIdGET"
	}
	return respData

def tvAccOrderIdPUT(req, resp):
	"""
	Modify an existing order.
	[INPUT]		:	accountId : The account identifier
					string
					(path)

					orderId : Order ID
					string
					(path)

					qty : Number of units
					number
					(formData)

					limitPrice : Limit Price for Limit or StopLimit order
					number
					(formData)

					stopPrice : Stop Price for Stop or StopLimit order
					number
					(formData)

					stopLoss : StopLoss price (if supported)
					number
					(formData)

					takeProfit : TakeProfit price (if supported)
					number
					(formData)
	"""
	retAuth = tvAuth()
	if retAuth[b_KV.API_K_STATUS] != b_KV.API_V_SUCCESS:
		return retAuth
	pathList 	= req.getPathList()
	if pathList < 6:
		return {b_KV.API_K_STATUS : b_KV.API_V_ERROR, c_KV.API_K_ERRMSG: "Invalid request path."}
	pathList 	= pathList[ld.TRADING_VIEW_ALB_PATH_LEN:]
	accountId 	= pathList[1]
	orderId 	= pathList[3]

	## Quantity
	if tvDef.TV_INP_ORDER_QTY not in retBody:
		return {b_KV.API_K_STATUS : b_KV.API_V_ERROR, c_KV.API_K_ERRMSG: "Invalid request quantity."}
	inpQty 			= retBody[tvDef.TV_INP_ORDER_QTY]
	try:
		inpQty 		= int(inpQty)
	except Exception as e:
		return {b_KV.API_K_STATUS : b_KV.API_V_ERROR, c_KV.API_K_ERRMSG: "Invalid request quantity."}

	## Optional
	inpLimitPrice 	= None
	inpStopPrice 	= None
	inpStopLoss 	= None
	inpTakeProfit 	= None
	if tvDef.TV_INP_ORDER_LIMIT_P in retBody:
		try:
			inpLimitPrice 	= float(retBody[tvDef.TV_INP_ORDER_LIMIT_P])
		except Exception as e:
			return {b_KV.API_K_STATUS : b_KV.API_V_ERROR, c_KV.API_K_ERRMSG: "Invalid request limit price."}
	if tvDef.TV_INP_ORDER_STOP_P in retBody:
		try:
			inpStopPrice 	= float(retBody[tvDef.TV_INP_ORDER_STOP_P])
		except Exception as e:
			return {b_KV.API_K_STATUS : b_KV.API_V_ERROR, c_KV.API_K_ERRMSG: "Invalid request stop price."}
	if tvDef.TV_INP_ORDER_STOP_L in retBody:
		try:
			inpStopLoss 	= float(retBody[tvDef.TV_INP_ORDER_STOP_L])
		except Exception as e:
			return {b_KV.API_K_STATUS : b_KV.API_V_ERROR, c_KV.API_K_ERRMSG: "Invalid request stop loss."}
	if tvDef.TV_INP_ORDER_TAKE_PROF in retBody:
		try:
			inpTakeProfit 	= float(retBody[tvDef.TV_INP_ORDER_TAKE_PROF])
		except Exception as e:
			return {b_KV.API_K_STATUS : b_KV.API_V_ERROR, c_KV.API_K_ERRMSG: "Invalid request take profit."}

	respData = {
		b_KV.API_K_STATUS : b_KV.API_V_SUCCESS,
		c_KV.API_K_ERRMSG: "string",
		'f': "tvAccOrderIdPUT"
	}
	return respData

def tvAccOrderIdDEL(req, resp):
	"""
	Cancel an existing order
	[INPUT]		: 	accountId : The account identifier
					string
					(path)

					orderId : Order ID
					string
					(path)
	"""
	retAuth = tvAuth()
	if retAuth[b_KV.API_K_STATUS] != b_KV.API_V_SUCCESS:
		return retAuth
	pathList 	= req.getPathList()
	if pathList < 6:
		return {b_KV.API_K_STATUS : b_KV.API_V_ERROR, c_KV.API_K_ERRMSG: "Invalid request path."}
	pathList 	= pathList[ld.TRADING_VIEW_ALB_PATH_LEN:]
	accountId 	= pathList[1]
	orderId 	= pathList[3]

	respData = {
		b_KV.API_K_STATUS : b_KV.API_V_SUCCESS,
		c_KV.API_K_ERRMSG: "string",
		'f': "tvAccOrderIdDEL"
	}
	return respData

def tvAccPosnGET(req, resp):
	"""
	Get positions for an account
	[INPUT]		: 	accountId : The account identifier
					string
					(path)
	"""
	retAuth = tvAuth()
	if retAuth[b_KV.API_K_STATUS] != b_KV.API_V_SUCCESS:
		return retAuth
	pathList 	= req.getPathList()
	if pathList < 5:
		return {b_KV.API_K_STATUS : b_KV.API_V_ERROR, c_KV.API_K_ERRMSG: "Invalid request path."}
	pathList 	= pathList[ld.TRADING_VIEW_ALB_PATH_LEN:]
	accountId 	= pathList[1]

	respData = {
		b_KV.API_K_STATUS : b_KV.API_V_SUCCESS,
		c_KV.API_K_ERRMSG: "string",
		c_KV.API_K_DETAILS: [
			{
				"id": "string",
				"instrument": "string",
				"qty": 0,
				"side": "buy",
				"avgPrice": 0,
				"unrealizedPl": 0,
				"realizedPl": 0
			}
		],
		'f': "tvAccPosnGET"
	}
	return respData

def tvAccPosnIdGET(req, resp):
	"""
	Get a position for an account
	[INPUT]		:	accountId : The account identifier
					string
					(path)

					positionId : Position ID
					string
					(path)
	"""
	retAuth = tvAuth()
	if retAuth[b_KV.API_K_STATUS] != b_KV.API_V_SUCCESS:
		return retAuth
	pathList 	= req.getPathList()
	if pathList < 6:
		return {b_KV.API_K_STATUS : b_KV.API_V_ERROR, c_KV.API_K_ERRMSG: "Invalid request path."}
	pathList 	= pathList[ld.TRADING_VIEW_ALB_PATH_LEN:]
	accountId 	= pathList[1]
	positionId 	= pathList[3]

	respData = {
		b_KV.API_K_STATUS : b_KV.API_V_SUCCESS,
		c_KV.API_K_ERRMSG: "string",
		c_KV.API_K_DETAILS: {
			"id": "string",
			"instrument": "string",
			"qty": 0,
			"side": "buy",
			"avgPrice": 0,
			"unrealizedPl": 0,
			"realizedPl": 0
		},
		'f': "tvAccPosnIdGET"
	}
	return respData

def tvAccPosnIdPUT(req, resp):
	"""
	Modify an existing position stop loss or take profit or both
	[INPUT]		:	accountId : The account identifier
					string
					(path)

					positionId : Position ID
					string
					(path)

					stopLoss : StopLoss price
					number
					(formData)

					takeProfit : TakeProfit price
					number
					(formData)
	"""
	retAuth = tvAuth()
	if retAuth[b_KV.API_K_STATUS] != b_KV.API_V_SUCCESS:
		return retAuth
	pathList 	= req.getPathList()
	if pathList < 6:
		return {b_KV.API_K_STATUS : b_KV.API_V_ERROR, c_KV.API_K_ERRMSG: "Invalid request path."}
	pathList 	= pathList[ld.TRADING_VIEW_ALB_PATH_LEN:]
	accountId 	= pathList[1]
	positionId 	= pathList[3]
	retBody 	= req.getBody()

	## Optional
	inpStopLoss 	= None
	inpTakeProfit 	= None
	if tvDef.TV_INP_ORDER_STOP_L in retBody:
		try:
			inpStopLoss 	= float(retBody[tvDef.TV_INP_ORDER_STOP_L])
		except Exception as e:
			return {b_KV.API_K_STATUS : b_KV.API_V_ERROR, c_KV.API_K_ERRMSG: "Invalid request stop loss."}
	if tvDef.TV_INP_ORDER_TAKE_PROF in retBody:
		try:
			inpTakeProfit 	= float(retBody[tvDef.TV_INP_ORDER_TAKE_PROF])
		except Exception as e:
			return {b_KV.API_K_STATUS : b_KV.API_V_ERROR, c_KV.API_K_ERRMSG: "Invalid request take profit."}

	respData = {
		b_KV.API_K_STATUS : b_KV.API_V_SUCCESS,
		c_KV.API_K_ERRMSG: "string",
		"f": "tvAccPosnIdPUT"
	}
	return respData

def tvAccPosnIdDEL(req, resp):
	"""
	Close an existing position
	[INPUT]		:	accountId : The account identifier
					string
					(path)

					positionId : Position ID
					string
					(path)
	"""
	retAuth = tvAuth()
	if retAuth[b_KV.API_K_STATUS] != b_KV.API_V_SUCCESS:
		return retAuth
	pathList 	= req.getPathList()
	if pathList < 6:
		return {b_KV.API_K_STATUS : b_KV.API_V_ERROR, c_KV.API_K_ERRMSG: "Invalid request path."}
	pathList 	= pathList[ld.TRADING_VIEW_ALB_PATH_LEN:]
	accountId 	= pathList[1]
	positionId 	= pathList[3]

	respData = {
		b_KV.API_K_STATUS : b_KV.API_V_SUCCESS,
		c_KV.API_K_ERRMSG: "string",
		"f": "tvAccPosnIdDEL"
	}
	return respData

def tvAccExecGET(req, resp):
	"""
	Get a list of executions (i.e. fills or trades) for an account and an instrument. Executions are displayed on a chart
	[INPUT]		:	accountId : The account identifier
					string
					(path)

					instrument : Broker instrument name
					string
					(query)

					maxCount : Maximum count of executions to return
					number
					(query)
	"""
	retAuth = tvAuth()
	if retAuth[b_KV.API_K_STATUS] != b_KV.API_V_SUCCESS:
		return retAuth
	pathList 	= req.getPathList()
	if pathList < 5:
		return {b_KV.API_K_STATUS : b_KV.API_V_ERROR, c_KV.API_K_ERRMSG: "Invalid request path."}

	pathList 	= pathList[ld.TRADING_VIEW_ALB_PATH_LEN:]
	accountId 	= pathList[1]

	retBody 	= req.getBody()
	if not retBody:
		return {b_KV.API_K_STATUS : b_KV.API_V_ERROR, c_KV.API_K_ERRMSG: "Invalid request body."}

	if not isinstance(retBody, dict):
		try:
			retBody = json.loads(retBody)
		except Exception as e:
			return {b_KV.API_K_STATUS : b_KV.API_V_ERROR, c_KV.API_K_ERRMSG: "Invalid request body."}

	## Required
	if tvDef.TV_INP_ORDER_INSTR not in retBody:
		return {b_KV.API_K_STATUS : b_KV.API_V_ERROR, c_KV.API_K_ERRMSG: "Invalid request instrument."}
	inpInstr 		= retBody[tvDef.TV_INP_ORDER_INSTR]
	if inpInstr:
		## Validate instrument. May be validate ticker
		None

	## Optional
	maxCount = None
	if tvDef.TV_INP_MAX_COUNT in retBody:
		try:
			maxCount = int(retBody[tvDef.TV_INP_MAX_COUNT])
		except Exception as e:
			return {b_KV.API_K_STATUS : b_KV.API_V_ERROR, c_KV.API_K_ERRMSG: "Invalid max count."}

	respData = {
		b_KV.API_K_STATUS : b_KV.API_V_SUCCESS,
		c_KV.API_K_ERRMSG: "string",
		c_KV.API_K_DETAILS: [
			{
				"id": "string",
				"instrument": "string",
				"price": 0,
				"time": 0,
				"qty": 0,
				"side": "buy"
			}
		],
		"f": "tvAccExecGET"
	}
	return respData

def tvAccInstruGET(req, resp):
	"""
	Get a list of tradeable instruments that are available for trading with the account specified
	[INPUT]		:	accountId : The account identifier
					string
					(path)
	"""
	retAuth = tvAuth()
	if retAuth[b_KV.API_K_STATUS] != b_KV.API_V_SUCCESS:
		return retAuth
	pathList 	= req.getPathList()
	if pathList < 5:
		return {b_KV.API_K_STATUS : b_KV.API_V_ERROR, c_KV.API_K_ERRMSG: "Invalid request path."}

	pathList 	= pathList[ld.TRADING_VIEW_ALB_PATH_LEN:]
	accountId 	= pathList[1]

	respData = {
		b_KV.API_K_STATUS : b_KV.API_V_SUCCESS,
		c_KV.API_K_ERRMSG: "string",
		c_KV.API_K_DETAILS: [
			{
			"name": "string",
			"description": "string",
			"minQty": 0,
			"maxQty": 0,
			"qtyStep": 0,
			"pipSize": 0,
			"pipValue": 0,
			"minTick": 0
			}
		],
		"f": "tvAccInstruGET"
	}
	return respData

def tvMappingGET(req, resp):
	"""
	Return all broker instruments with corresponding TradingView instruments. It is required to add a Broker to TradingView.com. It is not required for Trading Terminal integration. This request works without authorization!
	"""
	respData = {
		"symbols": [
			{
				"f": [
					"string"
				],
				"s": "string"
			}
		],
		"fields": [
			"brokerSymbol"
		],
		"f": "tvMappingGET"
	}
	return respData

def tvSymInfoGET(req, resp):
	"""
	Get a list of all instruments
	"""
	retAuth = tvAuth()
	if retAuth[b_KV.API_K_STATUS] != b_KV.API_V_SUCCESS:
		return retAuth

	respData = {
		"symbol": [
			"string"
		],
		"description": [
			"string"
		],
		"exchange-listed": [
			"string"
		],
		"exchange-traded": [
			"string"
		],
		"minmovement": [
			0
		],
		"minmov2": [
			0
		],
		"fractional": [
			true
		],
		"pricescale": [
			0
		],
		"has-intraday": [
			true
		],
		"has-no-volume": [
			true
		],
		"type": [
			"string"
		],
		"ticker": [
			"string"
		],
		"timezone": [
			"string"
		],
		"session-regular": [
			"string"
		],
		"supported-resolutions": [
			[
				"string"
			]
		],
		"has-daily": [
			true
		],
		"intraday-multipliers": [
			[
				"string"
			]
		],
		"has-weekly-and-monthly": [
			true
		],
		"f": "tvSymInfoGET"
	}
	return respData

def tvHistGET(req, resp):
	symbol = "inp"
	resolution = "inp"
	histFrom = "inp"
	histTo = "inp"
	countback ="inp"
	respData = {
		b_KV.API_K_STATUS : b_KV.API_V_SUCCESS,
		c_KV.API_K_ERRMSG: "string",
		"nb": 0,
		"t": [ 0 ],
		"o": [ 0 ],
		"h": [ 0 ],
		"l": [ 0 ],
		"c": [ 0 ],
		"v": [ 0 ],
		"f": "tvHistGET"
	}
	return respData

def tvQuotesGET(req, resp):
	symbols = "inp"
	respData = {
		b_KV.API_K_STATUS : b_KV.API_V_SUCCESS,
		c_KV.API_K_ERRMSG: "string",
		c_KV.API_K_DETAILS: [
			{
			b_KV.API_K_STATUS : b_KV.API_V_SUCCESS,
			"n": "string",
			"v": {
				"ch": 0,
				"chp": 0,
				"lp": 0,
				"ask": 0,
				"bid": 0,
				"open_price": 0,
				"high_price": 0,
				"low_price": 0,
				"prev_close_price": 0,
				"volume": 0
				}
			}
		],
		"f":"tvQuotesGET"
	}
	return respData

def tvStreamingGET(req, resp):
	return "streamingGET"

## ******************* Fyers Internal *******************
# INP_REQUIRED_CHART_GET = ["token_id", "symbol", "resolution", "t"]
# INP_REQUIRED_CHART_POST = ["fyers_id", "secret_key", "exchange", "segment", "scrip_code", "resolution"]
# INP_REQUIRED_POPOUT_GET = ["symbol", "resolution"]
# INP_REQUIRED_ORDERS_POST = ["token_id", "side", "qty", "type", "symbol", "limitPrice", "stopPrice", "stopLoss", "takeProfit", "productType", "trailStopLoss", "validity", "disclosedQty", "offlineOrder"]
# INP_REQUIRED_ORDERS_PATCH = ["side", "qty", "type", "id", "symbol", "limitPrice", "stopPrice", "stopLoss", "productType"]
# INP_REQUIRED_ORDERS_DEL = ["id"]
# INP_REQUIRED_POSITN_POST = ["convertQty", "symbol", "positionSide", "convertFrom", "convertTo"]
# INP_REQUIRED_SAVELAYOUT_GET = ["client", "user", "chart"]
# INP_REQUIRED_SAVELAYOUT_POST = ["client", "user", "chart"]
# INP_REQUIRED_SAVELAYOUT_DEL = ["client", "user", "chart"]
# INP_REQUIRED_SAVETEMPLATE_GET = ["client", "user", "chart", "template"]
# INP_REQUIRED_SAVETEMPLATE_POST = ["client", "user", "chart"]
# INP_REQUIRED_SAVETEMPLATE_DEL = ["client", "user", "template"]

def fyChartGET(req, resp):
	# params = {
	# 	"funct"		: "mobileChartLoad",
	# 	"token_id"	: "$input.params('token_id')",
	# 	"symbol"	: "$input.params('symbol')",
	# 	"resolution": "$input.params('resolution')",
	# 	"t"			: "$input.params('t')"
	# }
	retParams = req.getQueryParams(["token_id", "symbol", "resolution", "t"])
	retParams["funct"] = "mobileChartLoad"
	from fy_config.fy_chartonly_functions import fy_mobileChartLoad
	return fy_mobileChartLoad(retParams)

def fyChartPOST(req, resp):
	# {
	# "funct": "mobileChartAuth",
	# "fyers_id": "$input.params('fyers_id')",
	# "secret_key": "$input.params('secret_key')",
	# "exchange": "$input.params('exchange')",
	# "segment": "$input.params('segment')",
	# "scrip_code": "$input.params('scrip_code')",
	# "resolution": "$input.params('resolution')"
	# }
	retParams = req.getQueryParams(["fyers_id", "secret_key", "exchange", "segment", "scrip_code", "resolution"])
	retParams["funct"] = "mobileChartAuth"
	from fy_config.fy_chartonly_functions import fy_mobileChartAuth
	return fy_mobileChartAuth(retParams)

def fyChartAuthPOST(req, resp):
	# {
	# "funct": "mobChartAuth",
	# "fyers_id": "$inputObj.fyers_id",
	# "secret_key": "$inputObj.secret_key",
	# "exchange": "$inputObj.exchange",
	# "segment": "$inputObj.segment",
	# "scrip_code": "$inputObj.scrip_code"
	# }
	# retParams = req.getQueryParams(["fyers_id", "secret_key", "exchange", "segment", "scrip_code", "resolution"])
	retParams = req.getBody()
	try:
		if not isinstance(retParams, dict):
			retParams = json.loads(retParams)
	except Exception as e:
		return "Invalid Input Format"
	retParams["funct"] = "mobChartAuth"
	from fy_config.mobile_chart import fy_mobChartAuth
	return fy_mobChartAuth(retParams)

def fyChartPopoutGET(req, resp):
	# {
	# "cookie" : "$util.escapeJavaScript($input.params('cookie'))",
	# "funct": "popOutChart",
	# "symbol": "$input.params('symbol')",
	# "resolution": "$input.params('resolution')"
	# }
	retParams = req.getQueryParams(["symbol", "resolution"])
	retParams["cookie"] = req.getCookies()
	retParams["funct"] = "popOutChart"
	from fy_config.fy_chartonly_functions import fy_popOutChart
	return fy_popOutChart(retParams)

def fyChartPopoutPOST(req, resp):
	#set ($inputObj = $input.path('$'))
	# {
	# "cookie" : "$util.escapeJavaScript($input.params('cookie'))",
	# "funct": "popOutChart",
	# "resolution": "$inputObj.resolution",
	# "symbol": "$inputObj.symbol"
	# }
	retParams = req.getQueryParams(["symbol", "resolution"])
	retParams["cookie"] = req.getCookies()
	retParams["funct"] = "popOutChart"
	from fy_config.fy_chartonly_functions import fy_popOutChart
	return fy_popOutChart(retParams)

def fyFundsGET(req, resp):
	# {
	# "funct": "funds",
	# "cookie":"$util.escapeJavaScript($input.params('cookie'))"
	# }
	retParams = {"funct": "funds"}
	# retParams["cookie"] = req.getCookies()
	retParams["cookie"] = req.getHeaderParm(["authorization"]).get("authorization","")
	retParams["token_id"] = ""
	getToken = req.getQueryParams(["token_id"])
	if "token_id" in getToken:
		retParams["token_id"] = getToken["token_id"]
	getHeader = req.getHeaderParm(["x-forwarded-for"])
	if "x-forwarded-for" in getHeader:
		retParams["user_ip"] = getHeader["x-forwarded-for"]
	from fy_config.funds.fy_trading_external_functions_funds import fy_getFundLimit
	return fy_getFundLimit(retParams)

def fyFundsDetailsGET(req, resp):
	# {
	# "funct": "limitDetails",
	# "cookie":"$util.escapeJavaScript($input.params('cookie'))"
	# }
	retParams = {"funct": "limitDetails"}
	# retParams["cookie"] = req.getCookies()
	retParams["cookie"] = req.getHeaderParm(["authorization"]).get("authorization","")
	retParams["token_id"] = ""
	getToken = req.getQueryParams(["token_id"])
	if "token_id" in getToken:
		retParams["token_id"] = getToken["token_id"]
	getHeader = req.getHeaderParm(["x-forwarded-for"])
	if "x-forwarded-for" in getHeader:
		retParams["user_ip"] = getHeader["x-forwarded-for"]
	# from fy_config.fy_trading_external_functions import fy_limitDetails
	from fy_config.funds.fy_trading_external_functions_funds_details import fy_limitDetails
	return fy_limitDetails(retParams)

def fyHoldingsGET(req, resp):
	# {
	# "funct": "holdings",
	# "cookie":"$util.escapeJavaScript($input.params('cookie'))"
	# }
	retParams = {"funct": "holdings"}
	# retParams["cookie"] = req.getCookies()
	retParams["cookie"] = req.getHeaderParm(["authorization"]).get("authorization","")
	retParams["token_id"] = ""
	getToken = req.getQueryParams(["token_id"])
	if "token_id" in getToken:
		retParams["token_id"] = getToken["token_id"]
	getHeader = req.getHeaderParm(["x-forwarded-for"])
	if "x-forwarded-for" in getHeader:
		retParams["user_ip"] = getHeader["x-forwarded-for"]
	from fy_config.holdings.fy_trading_external_functions_holdings import fy_getHoldings
	return fy_getHoldings(retParams)

def fyLogoutPost(req, resp):
	# {
	# "funct": "sessionLogout",
	# "cookie":"$util.escapeJavaScript($input.params('cookie'))"
	# }
	retParams = {"funct": "sessionLogout"}
	# retParams["cookie"] = req.getCookies()
	retParams["cookie"] = req.getHeaderParm(["authorization"]).get("authorization","")
	retParams["token_id"] = ""
	getToken = req.getQueryParams(["token_id"])
	if "token_id" in getToken:
		retParams["token_id"] = getToken["token_id"]
	getHeader = req.getHeaderParm(["x-forwarded-for"])
	if "x-forwarded-for" in getHeader:
		retParams["user_ip"] = getHeader["x-forwarded-for"]
	from fy_config.fy_login_functions import fy_logout
	return fy_logout(retParams)

def fyMinQtyGET(req, resp):
	# {
	# "cookie" : "$util.escapeJavaScript($input.params('cookie'))",
	# "funct": "minquantity"
	# }
	retParams = {"funct": "minquantity"}
	# retParams["cookie"] = req.getCookies()
	retParams["cookie"] = req.getHeaderParm(["authorization"]).get("authorization","")
	from fy_config.fy_trading_external_functions import fy_getAllSymMinQty2
	return fy_getAllSymMinQty2()

def fyOrdersGET(req, resp):
	# {
	# "cookie" : "$util.escapeJavaScript($input.params('cookie'))",
	# "funct": "orderbook"
	# }
	retParams = {"funct": "orderbook"}
	# retParams["cookie"] = req.getCookies()
	retParams["cookie"] = req.getHeaderParm(["authorization"]).get("authorization","")
	retParams["token_id"] = ""
	getToken = req.getQueryParams(["token_id"])
	if "token_id" in getToken:
		retParams["token_id"] = getToken["token_id"]
	getHeader = req.getHeaderParm(["x-forwarded-for"])
	if "x-forwarded-for" in getHeader:
		retParams["user_ip"] = getHeader["x-forwarded-for"]
	#from fy_config.fy_trading_external_functions import fy_getOrderBook
	from fy_config.orders.fy_trading_external_functions_orders_GET import fy_getOrderBook
	# print("fy_getOrderBook(retParams) : ",fy_getOrderBook(retParams))
	return fy_getOrderBook(retParams)

def fyOrdersPOST(req, resp):
	# {
	# "cookie" : "$util.escapeJavaScript($input.params('cookie'))",
	# "funct": "placeorder",
	# "token_id": "$inputObj.token_id",
	# "side": "$inputObj.side",
	# "qty": "$inputObj.qty",
	# "type": "$inputObj.type",
	# "symbol": "$inputObj.symbol",
	# "limitPrice": "$inputObj.limitPrice",
	# "stopPrice": "$inputObj.stopPrice",
	# "stopLoss": "$inputObj.stopLoss",
	# "takeProfit": "$inputObj.takeProfit",
	# "productType": "$inputObj.productType",
	# "trailStopLoss": "$inputObj.trailStopLoss",
	# "validity": "$inputObj.validity",
	# "disclosedQty": "$inputObj.disclosedQty",
	# "offlineOrder": "$inputObj.offlineOrder"
	# }
	getToken = req.getQueryParams(["token_id"])
	getHeader = req.getHeaderParm(["x-forwarded-for"])
	retParams = req.getBody()#["token_id", "side", "qty", "type", "symbol", "limitPrice", "stopPrice", "stopLoss", "takeProfit", "productType", "trailStopLoss", "validity", "disclosedQty", "offlineOrder"]
	if not isinstance(retParams, dict):
		retParams = json.loads(retParams)
	retParams["funct"] = "placeorder"
	# retParams["cookie"] = req.getCookies()
	retParams["cookie"] = req.getHeaderParm(["authorization"]).get("authorization","")
	retParams["token_id"] = ""
	if "token_id" in getToken:
		retParams["token_id"] = getToken["token_id"]
	if "x-forwarded-for" in getHeader:
		retParams["user_ip"] = getHeader["x-forwarded-for"]
	retParams["multi_orders"] = False
	#from fy_config.fy_trading_external_functions import fy_placeOrder
	from fy_config.orders.fy_trading_external_functions_orders_POST import fy_placeOrder
	return fy_placeOrder(retParams)

def fyOrdersPATCH(req, resp):
	# {
	# "cookie" : "$util.escapeJavaScript($input.params('cookie'))",
	# "funct": "modifyorder",
	# "side": "$inputObj.side",
	# "qty": "$inputObj.qty",
	# "type": "$inputObj.type",
	# "id": "$inputObj.id",
	# "symbol": "$inputObj.symbol",
	# "limitPrice": "$inputObj.limitPrice",
	# "stopPrice": "$inputObj.stopPrice",
	# "stopLoss": "$inputObj.stopLoss",
	# "productType": "$inputObj.productType"
	# }
	# retParams = req.getQueryParams(["side", "qty", "type", "id", "symbol", "limitPrice", "stopPrice", "stopLoss", "productType"])

	retParams = req.getBody()
	try:
		if not isinstance(retParams, dict):
			retParams = json.loads(retParams)
	except Exception as e:
		return "Invalid Input Format"
	retParams["funct"] = "modifyorder"
	# retParams["cookie"] = req.getCookies()
	retParams["cookie"] = req.getHeaderParm(["authorization"]).get("authorization","")
	retParams["token_id"] = ""
	getToken = req.getQueryParams(["token_id"])
	if "token_id" in getToken:
		retParams["token_id"] = getToken["token_id"]
	getHeader = req.getHeaderParm(["x-forwarded-for"])
	if "x-forwarded-for" in getHeader:
		retParams["user_ip"] = getHeader["x-forwarded-for"]
	#from fy_config.fy_trading_external_functions import fy_modifyOrder
	from fy_config.orders.fy_trading_external_functions_orders_PATCH import fy_modifyOrder
	return fy_modifyOrder(retParams)

def fyOrdersDELETE(req, resp):
	# {
	# "cookie" : "$util.escapeJavaScript($input.params('cookie'))",
	# "funct": "cancelorder",
	# "id":"$inputObj.id"
	# }
	# retParams = req.getQueryParams(["id"])

	retParams = req.getBody()
	try:
		if not isinstance(retParams, dict):
			retParams = json.loads(retParams)
	except Exception as e:
		return "Invalid Input Format"
	retParams["funct"] = "cancelorder"
	# retParams["cookie"] = req.getCookies()
	retParams["cookie"] = req.getHeaderParm(["authorization"]).get("authorization","")
	retParams["token_id"] = ""
	getToken = req.getQueryParams(["token_id"])
	if "token_id" in getToken:
		retParams["token_id"] = getToken["token_id"]
	getHeader = req.getHeaderParm(["x-forwarded-for"])
	if "x-forwarded-for" in getHeader:
		retParams["user_ip"] = getHeader["x-forwarded-for"]
	#from fy_config.fy_trading_external_functions import fy_cancelOrder
	from fy_config.orders.fy_trading_external_functions_orders_DELETE import fy_cancelOrder
	return fy_cancelOrder(retParams)

def fyOrderDetailsGET(req, resp):
	# {
	# "funct": "orderDetails",
	# "id": "$input.params('orderId')",
	# "segment": "$input.params('segment')",
	# "symbol": "$input.params('symbol')",
	# "cookie":"$util.escapeJavaScript($input.params('cookie'))"
	# }
	INP_REQUIRED_ORDERS_DETAILS_GET = ["segment", "symbol", "orderId","token_id"]
	retParams = req.getQueryParams(INP_REQUIRED_ORDERS_DETAILS_GET)
	if "orderId" in retParams: retParams["id"] = retParams["orderId"]
	retParams["funct"] = "orderDetails"
	# retParams["cookie"] = req.getCookies()
	retParams["cookie"] = req.getHeaderParm(["authorization"]).get("authorization","")
	getToken = req.getQueryParams(["token_id"])
	retParams["token_id"] = getToken.get("token_id","")
	# from fy_config.fy_trading_external_functions import fy_orderDetails
	from fy_config.orders.fy_trading_external_functions_orders_details_GET import fy_orderDetails
	return fy_orderDetails(retParams)

def fyPosGET(req, resp):
	# {
	# "funct": "positions",
	# "cookie":"$util.escapeJavaScript($input.params('cookie'))"
	# }
	retParams = {"funct": "positions"}
	# retParams["cookie"] = req.getCookies()
	retParams["cookie"] = req.getHeaderParm(["authorization"]).get("authorization","")
	retParams["token_id"] = ""
	getToken = req.getQueryParams(["token_id"])
	if "token_id" in getToken:
		retParams["token_id"] = getToken["token_id"]
	getHeader = req.getHeaderParm(["x-forwarded-for"])
	if "x-forwarded-for" in getHeader:
		retParams["user_ip"] = getHeader["x-forwarded-for"]
	from fy_config.positions.fy_trading_external_functions_positions_GET import fy_getNetPositions
	return fy_getNetPositions(retParams)

def fyPosPOST(req, resp):
	# {
	# "cookie" : "$util.escapeJavaScript($input.params('cookie'))",
	# "funct": "convertPosition",
	# "convertQty": "$inputObj.convertQty",
	# "symbol": "$inputObj.symbol",
	# "positionSide": "$inputObj.positionSide",
	# "convertFrom": "$inputObj.convertFrom",
	# "convertTo": "$inputObj.convertTo"
	# }
	# retParams = req.getQueryParams(["convertQty", "symbol", "positionSide", "convertFrom", "convertTo"])
	retParams = req.getBody()
	try:
		if not isinstance(retParams, dict):
			retParams = json.loads(retParams)
	except Exception as e:
		return "Invalid Input Format"
	retParams["funct"] = "convertPosition"
	# retParams["cookie"] = req.getCookies()
	retParams["cookie"] = req.getHeaderParm(["authorization"]).get("authorization","")
	retParams["token_id"] = ""
	getToken = req.getQueryParams(["token_id"])
	if "token_id" in getToken:
		retParams["token_id"] = getToken["token_id"]
	getHeader = req.getHeaderParm(["x-forwarded-for"])
	if "x-forwarded-for" in getHeader:
		retParams["user_ip"] = getHeader["x-forwarded-for"]
	#from fy_config.fy_trading_external_functions import fy_convertPosition
	from fy_config.positions.fy_trading_external_functions_positions_POST import fy_convertPosition
	return fy_convertPosition(retParams)

def fyExitPos(req, resp):
	getToken = req.getQueryParams(["token_id"])
	getHeader = req.getHeaderParm(["x-forwarded-for"])
	retParams = req.getBody()
	if not isinstance(retParams, dict):
		retParams = json.loads(retParams)
	retParams["funct"] = "exitpositions"
	# retParams["cookie"] = req.getCookies()
	retParams["cookie"] = req.getHeaderParm(["authorization"]).get("authorization","")
	retParams["token_id"] = ""
	if "token_id" in getToken:
		retParams["token_id"] = getToken["token_id"]
	if "x-forwarded-for" in getHeader:
		retParams["user_ip"] = getHeader["x-forwarded-for"]
	#from fy_config.fy_trading_external_functions import fy_exitPositions
	# print retParams
	from fy_config.positions.fy_trading_external_functions_exit_positions_POST import fy_exitPositions
	return fy_exitPositions(retParams)

def fySnapshotPOST(req, resp):
	# {
	# "funct": "snapshot",
	# "image": $input.json('$.images'),
	# "timezone": $input.params('timezone'),
	# "language": $input.params('language'),
	# "cookie":"$util.escapeJavaScript($input.params('cookie'))"
	# }
	retParams = {}
	retParams["params"] = req.getBody()
	retParams["funct"] = "snapshot"
	retParams["cookie"] = req.getCookies()
	token_val = req.getQueryParams(["token"])
	if token_val:
		retParams["token_id"] = token_val["token"]
	else:
		retParams["token_id"] = token_val
	# retParams["cookie"] = req.getHeaderParm(["authorization"]).get("authorization","")
	from fy_config.snapshot.fy_savechart_functions import snapShotFunction
	return snapShotFunction(retParams)

def fySymbolsGET(req, resp):
	# {
	# "funct": "symbolsinfo",
	# "cookie":"$util.escapeJavaScript($input.params('cookie'))"
	# }
	retParams = {"funct": "symbolsinfo"}
	retParams["cookie"] = req.getCookies()
	# from fy_config.fy_trading_external_functions import fy_getAllSymInfo
	from fy_config.symbols.fy_trading_external_functions_symbols_GET import fy_getAllSymInfo
	return fy_getAllSymInfo()

def fyTradebookGET(req, resp):
	# {
	# "funct": "tradebook",
	# "cookie":"$util.escapeJavaScript($input.params('cookie'))"
	# }
	retParams = {"funct": "tradebook"}
	# retParams["cookie"] = req.getCookies()
	retParams["cookie"] = req.getHeaderParm(["authorization"]).get("authorization","")
	getHeader = req.getHeaderParm(["x-forwarded-for"])
	if "x-forwarded-for" in getHeader:
		retParams["user_ip"] = getHeader["x-forwarded-for"]
	getToken = req.getQueryParams(["token_id"])
	retParams["token_id"] = getToken.get("token_id","")
	# from fy_config.fy_trading_external_functions import fy_getTradeBook
	from fy_config.tradebook.fy_trading_external_functions_tradebook import fy_getTradeBook
	return fy_getTradeBook(retParams)

def fyValidateGET(req, resp):
	# {
	# "funct": "validateSession",
	# "cookie":"$util.escapeJavaScript($input.params('cookie'))"
	# }
	retParams = req.getQueryParams(["token_id"])
	retParams["funct"] = "validateSession"
	retParams["cookie"] = req.getCookies()
	retParams["authorization"] = req.getHeaderParm(["authorization"]).get("authorization","")
	resp.setHeader("Content-Type", "application/json")
	from fy_config.fy_trading_external_functions import fy_validateSession
	return fy_validateSession(retParams)

def fyValidateDetailsGET(req, resp):
	# {
	# "funct": "validateRSdetails",
	# "cookie": "$util.escapeJavaScript($input.params('cookie'))",
	# "flag": "$input.params('flag')"
	# }
	retParams = req.getQueryParams(["flag"])
	retParams["funct"] = "validateRSdetails"
	# retParams["cookie"] = req.getCookies()
	retParams["cookie"] = req.getHeaderParm(["authorization"]).get("authorization","")
	from fy_config.fy_trading_external_functions import fy_getRSToken
	return fy_getRSToken(retParams)

def fyWlGET(req, resp):
	retParams = {"funct":"getWatchlist"}
	getToken = req.getQueryParams(["token_id"])
	retParams["token_id"] = getToken.get("token_id","")
	# retParams["cookie"] = req.getCookies()
	retParams["reqType"] = "M"
	retParams["cookie"] = req.getHeaderParm(["authorization"]).get("authorization","")
	# from fy_config.fy_watchlist_functions import fy_watchlist_get
	from fy_config.watchlists.fy_watchlist_functions_GET import fy_watchlist_get
	return fy_watchlist_get(retParams)

def fyWlPOST(req, resp):
	retParams = {"funct":"updateWatchlist"}
	getToken = req.getQueryParams(["token_id"])
	retParams["token_id"] = getToken.get("token_id","")
	# retParams["cookie"] = req.getCookies()
	retParams["cookie"] = req.getHeaderParm(["authorization"]).get("authorization","")
	retParams["params"] = req.getBody()
	# from fy_config.fy_watchlist_functions import fy_watchlist_update
	from fy_config.watchlists.fy_watchlist_functions_POST import fy_watchlist_update
	return fy_watchlist_update(retParams)

def fyWlDELETE(req, resp):
	retParams = {"funct":"delWatchlist"}
	getToken = req.getQueryParams(["token_id"])
	retParams["token_id"] = getToken.get("token_id","")
	# retParams["cookie"] = req.getCookies()
	retParams["cookie"] = req.getHeaderParm(["authorization"]).get("authorization","")
	retParams["params"] = req.getBody()
	# from fy_config.fy_watchlist_functions import fy_watchlist_delete
	from fy_config.watchlists.fy_watchlist_functions_DELETE import fy_watchlist_delete
	return fy_watchlist_delete(retParams)

# Watchlist PUT request added - 20200130 - Khyati
def fyWlPUT(req, resp):
	retParams = {"funct":"modifyWatchlist"}
	getToken = req.getQueryParams(["token_id"])
	retParams["token_id"] = getToken.get("token_id","")
	# retParams["cookie"] = req.getCookies()
	retParams["cookie"] = req.getHeaderParm(["authorization"]).get("authorization","")
	retParams["params"] = req.getBody()
	# from fy_config.fy_watchlist_functions import fy_watchlist_modify
	from fy_config.watchlists.fy_watchlist_functions_PUT import fy_watchlist_modify
	return fy_watchlist_modify(retParams)

def fyWlGETWeb(req, resp):
	retParams = {"funct" : "getWatchlist"}
	getToken = req.getQueryParams(["token_id"])
	retParams["token_id"] = getToken.get("token_id","")
	# retParams["cookie"] = req.getCookies()
	retParams["cookie"] = req.getHeaderParm(["authorization"]).get("authorization","")
	retParams["reqType"] = "W"
	# from fy_config.watchlists.fy_watchlist_functions import fy_watchlist_get  # Vikram file structure change
	from fy_config.watchlists.fy_watchlist_functions_GET import fy_watchlist_get
	return fy_watchlist_get(retParams)

def fyWlPOSTWeb(req, resp):
	retParams = {"funct":"updateWatchlist"}
	getToken = req.getQueryParams(["token_id"])
	retParams["token_id"] = getToken.get("token_id","")
	retParams["params"] = req.getBody()
	# retParams["cookie"] = req.getCookies()
	retParams["cookie"] = req.getHeaderParm(["authorization"]).get("authorization","")
	retParams["reqType"] = "W"
	# from fy_config.fy_watchlist_functions import fy_watchlist_update
	from fy_config.watchlists.fy_watchlist_functions_POST import fy_watchlist_update
	return fy_watchlist_update(retParams)

def fyWlDELETEWeb(req, resp):
	retParams = {"funct" : "delWatchlist"}
	getToken = req.getQueryParams(["token_id"])
	retParams["token_id"] = getToken.get("token_id","")
	retParams["params"] = req.getBody()
	# retParams["cookie"] = req.getCookies()
	retParams["cookie"] = req.getHeaderParm(["authorization"]).get("authorization","")
	retParams["reqType"] = "W"
	# from fy_config.fy_watchlist_functions import fy_watchlist_delete
	from fy_config.watchlists.fy_watchlist_functions_DELETE import fy_watchlist_delete
	return fy_watchlist_delete(retParams)	

def fySnapShotGalleryGET(req, res):
	retParams = req.getQueryParams(["token_id"])
	if not isinstance(retParams, dict):
		retParams = json.loads(retParams)
	retParams["funct"] = "getSnapshotGallery"
	retParams["method_type"] = "1"
	retParams["cookie"] = req.getHeaderParm(["authorization"]).get("authorization","")
	from fy_config.fy_data_external_functions import fy_snapshotGallery
	return fy_snapshotGallery(retParams)

def fySnapShotGalleryDELETE(req, res):
	retParams = req.getBody()
	try:
		if not isinstance(retParams, dict):
			retParams = json.loads(retParams)
	except Exception as e:
		return "Invalid Input Format"
	# getToken = req.getQueryParams(["token_id"]) # token_id is passed in the body
	# retParams["token_id"] = getToken.get("token_id", "")
	retParams["funct"] = "getSnapshotGallery"
	retParams["method_type"] = "2"
	retParams["cookie"] = req.getHeaderParm(["authorization"]).get("authorization","")
	from fy_config.fy_data_external_functions import fy_snapshotGallery
	return fy_snapshotGallery(retParams)

## Login API 20190717 Palash
def fyLoginAuthPOST(req, res):
	retParams = req.getBody()
	if not isinstance(retParams, dict):
		retParams = json.loads(retParams)
	retParams["funct"] = "auth"
	retParams["typeFlag"] = "4"
	getHeader = req.getHeaderParm(["x-forwarded-for"])
	if "x-forwarded-for" in getHeader:
		retParams["user_ip"] = getHeader["x-forwarded-for"]
	from fy_config.fy_login_API import loginPage
	return loginPage(retParams)

def fyChangePwdPOST(req, res):
	retParams = req.getBody()
	if not isinstance(retParams, dict):
		retParams = json.loads(retParams)
	retParams["funct"] = "auth"
	retParams["typeFlag"] = "3"
	getHeader = req.getHeaderParm(["x-forwarded-for"])
	if "x-forwarded-for" in getHeader:
		retParams["user_ip"] = getHeader["x-forwarded-for"]
	from fy_config.fy_login_API import loginPage
	return loginPage(retParams)

def fyForgotPwdPOST(req, res):
	retParams = req.getBody()
	if not isinstance(retParams, dict):
		retParams = json.loads(retParams)
	retParams["funct"] = "auth"
	retParams["typeFlag"] = "2"
	getHeader = req.getHeaderParm(["x-forwarded-for"])
	if "x-forwarded-for" in getHeader:
		retParams["user_ip"] = getHeader["x-forwarded-for"]
	from fy_config.fy_login_API import loginPage
	return loginPage(retParams)

def fyResetPwdPOST(req, res):
	retParams = req.getBody()
	if not isinstance(retParams, dict):
		retParams = json.loads(retParams)
	retParams["funct"] = "auth"
	retParams["typeFlag"] = "5"
	getHeader = req.getHeaderParm(["x-forwarded-for"])
	if "x-forwarded-for" in getHeader:
		retParams["user_ip"] = getHeader["x-forwarded-for"]
	from fy_config.fy_login_API import loginPage
	return loginPage(retParams)

def fyUnlockPOST(req, res):
	retParams = req.getBody()
	if not isinstance(retParams, dict):
		retParams = json.loads(retParams)
	retParams["funct"] = "auth"
	retParams["typeFlag"] = "1"
	getHeader = req.getHeaderParm(["x-forwarded-for"])
	if "x-forwarded-for" in getHeader:
		retParams["user_ip"] = getHeader["x-forwarded-for"]
	from fy_config.fy_login_API import loginPage
	return loginPage(retParams)

## Fundtransfer Ajay 2019-08-05
def fundTxView(req, res):
	"""
	{
		"funct": "fy_fundTransfer_API",
		"typeFlag":"5",
		"cookie":"$util.escapeJavaScript($input.params('cookie'))"
	}
	"""

	retParams = {"funct":"fy_fundTransfer_API"}
	# retParams["cookie"] = req.getCookies()
	retParams["cookie"] = req.getHeaderParm(["authorization"]).get("authorization","")
	retParams["token_id"] = ""
	retParams1 = req.getQueryParams(["token_id"])
	if "token_id" in retParams1:
		retParams["token_id"] = retParams1["token_id"]
	retParams["typeFlag"] = "5"
	getHeader = req.getHeaderParm(["x-forwarded-for"])
	if "x-forwarded-for" in getHeader:
		retParams["user_ip"] = getHeader["x-forwarded-for"]
	from fy_config.fy_fundTransfer_API import fundTxAPI
	retFun = fundTxAPI(retParams)
	# print "retParams : ", retParams
	# print retFun
	return retFun

def fundTxAddFunds(req, res):
	"""
	{
		"funct": "fy_fundTransfer_API",
		"typeFlag":"6",
		"cookie":"$util.escapeJavaScript($input.params('cookie'))",
		"bank_account": "$inputObj.bank_account",
		"transfer_amount": "$inputObj.transfer_amount"
	}
	"""
	retParams = req.getBody()
	try:

		if not isinstance(retParams, dict):
			retParams = json.loads(retParams)
	except Exception as e:
		return "Invalid Input Format"

	retParams["funct"] = "fy_fundTransfer_API"
	# retParams["cookie"] = req.getCookies()
	retParams["cookie"] = req.getHeaderParm(["authorization"]).get("authorization","")
	retParams["token_id"] = ""
	retParams1 = req.getQueryParams(["token_id"])
	if "token_id" in retParams1:
		retParams["token_id"] = retParams1["token_id"]
	retParams["typeFlag"] = "6"
	getHeader = req.getHeaderParm(["x-forwarded-for"])
	if "x-forwarded-for" in getHeader:
		retParams["user_ip"] = getHeader["x-forwarded-for"]
	from fy_config.fy_fundTransfer_API import fundTxAPI
	return fundTxAPI(retParams)

def fundTxAddFundsv2(req, res):
	retParams = req.getBody()
	try:
		if not isinstance(retParams, dict):
			retParams = json.loads(retParams)
	except Exception as e:
		return "Invalid Input Format"

	retParams["funct"] = "fy_fundTransfer_API"
	# retParams["cookie"] = req.getCookies()
	retParams["cookie"] = req.getHeaderParm(["authorization"]).get("authorization","")
	retParams["token_id"] = ""
	retParams1 = req.getQueryParams(["token_id"])
	if "token_id" in retParams1:
		retParams["token_id"] = retParams1["token_id"]
	retParams["typeFlag"] = "6"
	# Razorpay Mobile App SDK integration
	retParams["razorpayFlagV2"] = True
	getHeader = req.getHeaderParm(["x-forwarded-for"])
	if "x-forwarded-for" in getHeader:
		retParams["user_ip"] = getHeader["x-forwarded-for"]
	from fy_config.fy_fundTransfer_API import fundTxAPI
	return fundTxAPI(retParams)

def fundTxBankDetails(req, res):
	"""
	{
		"funct": "fy_fundTransfer_API",
		"typeFlag":"2",
		"cookie":"$util.escapeJavaScript($input.params('cookie'))",
		"t": "$inputObj.t"
	}
	"""
	retParams = req.getBody()
	try:
		if not isinstance(retParams, dict):
			retParams = json.loads(retParams)
	except Exception as e:
		return "Invalid Input Format"
	retParams["funct"] = "fy_fundTransfer_API"
	# retParams["cookie"] = req.getCookies()
	retParams["cookie"] = req.getHeaderParm(["authorization"]).get("authorization","")
	retParams["token_id"] = ""
	retParams1 = req.getQueryParams(["token_id"])
	if "token_id" in retParams1:
		retParams["token_id"] = retParams1["token_id"]
	retParams["typeFlag"] = "2"
	getHeader = req.getHeaderParm(["x-forwarded-for"])
	if "x-forwarded-for" in getHeader:
		retParams["user_ip"] = getHeader["x-forwarded-for"]
	from fy_config.fy_fundTransfer_API import fundTxAPI
	return fundTxAPI(retParams)

def fundTxMarginUtil(req, res):
	"""
	{
		"funct": "fy_margin_API",
		"cookie":"$util.escapeJavaScript($input.params('cookie'))"
	}
	"""
	retParams = {"funct": "fy_fundTransfer_API"}
	# retParams["cookie"] = req.getCookies()
	retParams["cookie"] = req.getHeaderParm(["authorization"]).get("authorization","")
	retParams["token_id"] = ""
	retParams1 = req.getQueryParams(["token_id"])
	if "token_id" in retParams1:
		retParams["token_id"] = retParams1["token_id"]
	from fy_config.fy_fundTransfer_API import getMargin
	return getMargin(retParams)

def fundTxWithdraw(req, res):
	"""
	{
		"funct": "fy_fundTransfer_API",
		"typeFlag":"7",
		"cookie":"$util.escapeJavaScript($input.params('cookie'))",
		"bank_account": "$inputObj.bank_account",
		"transfer_amount": "$inputObj.transfer_amount"
	}
	"""
	retParams = req.getBody()
	try:
		if not isinstance(retParams, dict):
			retParams = json.loads(retParams)
	except Exception as e:
		return "Invalid Input Format"
	retParams["funct"] = "fy_fundTransfer_API"
	# retParams["cookie"] = req.getCookies()
	retParams["cookie"] = req.getHeaderParm(["authorization"]).get("authorization","")
	retParams["token_id"] = ""
	retParams1 = req.getQueryParams(["token_id"])
	if "token_id" in retParams1:
		retParams["token_id"] = retParams1["token_id"]
	retParams["typeFlag"] = "7"
	getHeader = req.getHeaderParm(["x-forwarded-for"])
	if "x-forwarded-for" in getHeader:
		retParams["user_ip"] = getHeader["x-forwarded-for"]
	from fy_config.fy_fundTransfer_API import fundTxAPI
	return fundTxAPI(retParams)

## BO Validation session ID
def BOAuth(req, res):
	retParams = {"funct" : "validateSession"}
	retParams["cookie"] = req.getCookies()
	res.setHeader("Content-Type", "text/html")
	retQueryParam = req.getQueryParams(["sessionid"])
	if "sessionid" in retQueryParam:
		from fy_config.fy_auth_functions import INTERNAL_verifyTokenHash
		retValidate = INTERNAL_verifyTokenHash(retQueryParam["sessionid"], callingFuncName="BOAuth")
		if retValidate[0] == base_SEC.SUCCESS_C_1:
			return "AUTHENTICATION SUCCESS"
	return "AUTHENTICATION FAILED"

def MobileLogin(req, res):
	try:
		retParams = req.getBody()
		if not isinstance(retParams, dict):
			retParams = json.loads(retParams)
	except Exception as e:
		return "Invalid Input Format"
	from fy_config.fy_mobile_login_functions import fy_mobileLogin
	return fy_mobileLogin(retParams)

#Mobile APIs
def fyMobileAuthId(req,res):
	retParams = req.getBody()
	if not isinstance(retParams, dict):
		retParams = json.loads(retParams)
	retParams["funct"] = "fyMobileAuthId"
	getHeader = req.getHeaderParm(["x-forwarded-for"])
	if "x-forwarded-for" in getHeader:
		retParams["user_ip"] = getHeader["x-forwarded-for"]
	from fy_config.fy_mobile_login_functions import fy_authenticate_fyId
	return fy_authenticate_fyId(retParams)

def fyMobileLogin(req,res):
	retParams = req.getBody()
	if not isinstance(retParams, dict):
		retParams = json.loads(retParams)
	retParams["funct"] = "fyMobileLogin"
	getHeader = req.getHeaderParm(["x-forwarded-for"])
	if "x-forwarded-for" in getHeader:
		retParams["user_ip"] = getHeader["x-forwarded-for"]
	from fy_config.fy_mobile_login_functions import fy_mobile_login
	return fy_mobile_login(retParams)

def fySimplifiedRegister(req,res):
	retParams = req.getQueryParams(["token_id"])
	retParams["funct"] = "fySimplifiedRegister"
	retParams["params"] = req.getBody()
	getHeader = req.getHeaderParm(["x-forwarded-for"])
	if "x-forwarded-for" in getHeader:
		retParams["user_ip"] = getHeader["x-forwarded-for"]
	from fy_config.fy_mobile_login_functions import fy_simplified_register
	return fy_simplified_register(retParams)

def fyAddAppVersion(req,res):
	retParams = {"funct" : "fyAddAppVersion"}
	getToken = req.getQueryParams(["token_id"])
	retParams["token_id"] = getToken.get("token_id","")
	retParams["params"] = req.getBody()
	retParams["cookie"] = req.getHeaderParm(["authorization"]).get("authorization","")
	from fy_config.fy_mobile_login_functions import fy_add_app_version
	return fy_add_app_version(retParams)


# Mobile App Notification Registration
def fyNotiRegister(req, res):
	try:
		retParams = req.getBody()
		if not isinstance(retParams, dict):
			retParams = json.loads(retParams)
	except Exception as e:
		return "Invalid Input Format"
	retParams["funct"] = "fyNotiRegister"
	from fy_config.fy_push_notification_functions import fy_register
	return fy_register(retParams)

def fyGetProfile(req, res):
	retParams = req.getQueryParams(["token_id"])
	retParams["cookie"] = req.getHeaderParm(["authorization"]).get("authorization","")
	retParams["funct"] = "fyGetProfile"
	from fy_config.fy_mobile_login_functions import fy_get_profile
	return fy_get_profile(retParams)

def fyGuestRegister(req, res):
	retParams = {"funct" : "fyGuestRegister"}
	getHeader = req.getHeaderParm(["x-forwarded-for","authorization"])
	retParams["authorization"] = getHeader.get("authorization","")
	retParams["params"] = req.getBody()
	from fy_config.fy_mobile_login_functions import guest_register
	return guest_register(retParams)

def fyGuestValidate(req, res):
	retParams = {"funct" : "fyGuestValidate"}
	retParams["params"] = req.getBody()
	from fy_config.fy_mobile_login_functions import guest_verify
	return guest_verify(retParams)

def fyGetTimestamp(req, res):
	from fy_config.fy_watchlist_functions import getUnixTimeStamp
	return getUnixTimeStamp()

def fyUserRatingApp(req, res):
	retParams= {"funct":"fyUserRatingApp"}
	retParams["params"] = req.getBody()
	from fy_config.fy_mobile_login_functions import fy_rating_app
	return fy_rating_app(retParams)

def marginTxView(req, res):
	retParams = req.getBody()
	try:
		if not isinstance(retParams, dict):
			retParams = json.loads(retParams)
	except Exception as e:
		return "Invalid Input Format"
	retParams["funct"] = "marginTxView"
	# retParams["cookie"] = req.getCookies()
	retParams["cookie"] = req.getHeaderParm(["authorization"]).get("authorization","")
	getToken = req.getQueryParams(["token_id"])
	retParams["token_id"] = getToken.get("token_id","")
	#from fy_config.fy_margincalc_external_functions import fy_marginCalc
	from fy_config.margin.fy_margincalc_external_functions import fy_marginCalc
	return fy_marginCalc(retParams)

def fyGetBaskets(req, res):
	retParams = {}
	getToken = req.getQueryParams(["token_id"])
	retParams["token_id"] = getToken.get("token_id","")
	# retParams["cookie"] = req.getCookies()
	retParams["cookie"] = req.getHeaderParm(["authorization"]).get("authorization","")
	# from fy_config.fy_baskets_external_functions import get_baskets
	from fy_config.baskets.fy_baskets_external_functions import get_baskets
	return get_baskets(retParams)

def fyCreateBasket(req, res):
	retParams = {}
	getToken = req.getQueryParams(["token_id"])
	retParams["token_id"] = getToken.get("token_id","")
	# retParams["cookie"] = req.getCookies()
	retParams["cookie"] = req.getHeaderParm(["authorization"]).get("authorization","")
	retParams["typeFlag"] = 1
	retParams["body"] = req.getBody()
	# from fy_config.fy_baskets_external_functions import fy_basket
	from fy_config.baskets.fy_baskets_external_functions import fy_basket
	return fy_basket(retParams)

def fyModifyBasket(req, res):
	retParams = {}
	getToken = req.getQueryParams(["token_id"])
	retParams["token_id"] = getToken.get("token_id","")
	# retParams["cookie"] = req.getCookies()
	retParams["cookie"] = req.getHeaderParm(["authorization"]).get("authorization","")
	retParams["typeFlag"] = 2
	retParams["body"] = req.getBody()
	# from fy_config.fy_baskets_external_functions import fy_basket
	from fy_config.baskets.fy_baskets_external_functions import fy_basket
	return fy_basket(retParams)

def fyDeleteBasket(req, res):
	retParams = {}
	getToken = req.getQueryParams(["token_id"])
	retParams["token_id"] = getToken.get("token_id","")
	# retParams["cookie"] = req.getCookies()
	retParams["cookie"] = req.getHeaderParm(["authorization"]).get("authorization","")
	retParams["typeFlag"] = 3
	retParams["body"] = req.getBody()
	# from fy_config.fy_baskets_external_functions import fy_basket
	from fy_config.baskets.fy_baskets_external_functions import fy_basket
	return fy_basket(retParams)

def fyAddItemToBasket(req, res):
	retParams = {}
	getToken = req.getQueryParams(["token_id"])
	retParams["token_id"] = getToken.get("token_id","")
	# retParams["cookie"] = req.getCookies()
	retParams["cookie"] = req.getHeaderParm(["authorization"]).get("authorization","")
	retParams["typeFlag"] = 1
	retParams["body"] = req.getBody()
	# from fy_config.fy_baskets_external_functions import fy_basket_item
	from fy_config.baskets.fy_baskets_external_functions import fy_basket_item
	return fy_basket_item(retParams)

def fyModifyItemsInBasket(req, res):
	retParams = {}
	getToken = req.getQueryParams(["token_id"])
	retParams["token_id"] = getToken.get("token_id","")
	# retParams["cookie"] = req.getCookies()
	retParams["cookie"] = req.getHeaderParm(["authorization"]).get("authorization","")
	retParams["typeFlag"] = 2
	retParams["body"] = req.getBody()
	# from fy_config.fy_baskets_external_functions import fy_basket_item
	from fy_config.baskets.fy_baskets_external_functions import fy_basket_item
	return fy_basket_item(retParams)

def fyDeleteItemFromBasket(req, res):
	retParams = {}
	getToken = req.getQueryParams(["token_id"])
	retParams["token_id"] = getToken.get("token_id","")
	# retParams["cookie"] = req.getCookies()
	retParams["cookie"] = req.getHeaderParm(["authorization"]).get("authorization","")
	retParams["typeFlag"] = 3
	retParams["body"] = req.getBody()
	# from fy_config.fy_baskets_external_functions import fy_basket_item
	from fy_config.baskets.fy_baskets_external_functions import fy_basket_item
	return fy_basket_item(retParams)

def fyExecuteBasket(req, resp):
	retParams = {}
	getToken = req.getQueryParams(["token_id"])
	retParams["token_id"] = getToken.get("token_id","")
	# retParams["cookie"] = req.getCookies()
	retParams["cookie"] = req.getHeaderParm(["authorization"]).get("authorization","")
	retParams["body"] = req.getBody()
	retParams["funct"] = "placemultipleorders"
	retParams["multi_orders"] = True
	# from fy_config.fy_baskets_external_functions import fy_execute_basket
	from fy_config.baskets.fy_baskets_external_functions import fy_execute_basket
	return fy_execute_basket(retParams)

def fyResetBasket(req, res):
	retParams = {}
	getToken = req.getQueryParams(["token_id"])
	retParams["token_id"] = getToken.get("token_id","")
	# retParams["cookie"] = req.getCookies()
	retParams["cookie"] = req.getHeaderParm(["authorization"]).get("authorization","")
	retParams["body"] = req.getBody()
	# from fy_config.fy_baskets_external_functions import fy_reset_basket
	from fy_config.baskets.fy_baskets_external_functions import fy_reset_basket
	return fy_reset_basket(retParams)

def fyTechAdminOrderbook(req, res):
	retParams = req.getQueryParams(["fyId","checkSum"])
	retParams["typeFlag"] = 1
	from fy_config.fy_admin_trading_external_functions import fy_TechAdmin_GetDetails
	return fy_TechAdmin_GetDetails(retParams)

def fyTechAdminPositions(req, res):
	retParams = req.getQueryParams(["fyId","checkSum"])
	retParams["typeFlag"] = 2
	from fy_config.fy_admin_trading_external_functions import fy_TechAdmin_GetDetails
	return fy_TechAdmin_GetDetails(retParams)

def fyTechAdminHoldings(req, res):
	retParams = req.getQueryParams(["fyId","checkSum"])
	retParams["typeFlag"] = 3
	from fy_config.fy_admin_trading_external_functions import fy_TechAdmin_GetDetails
	return fy_TechAdmin_GetDetails(retParams)

def fyTechAdminFunds(req, res):
	retParams = req.getQueryParams(["fyId","checkSum"])
	retParams["typeFlag"] = 4
	from fy_config.fy_admin_trading_external_functions import fy_TechAdmin_GetDetails
	return fy_TechAdmin_GetDetails(retParams)

def fyTechAdminTrades(req, res):
	retParams = req.getQueryParams(["fyId","checkSum"])
	retParams["typeFlag"] = 5
	from fy_config.fy_admin_trading_external_functions import fy_TechAdmin_GetDetails
	return fy_TechAdmin_GetDetails(retParams)

def fyGetLoggedUsers(req, res):
	retParams = req.getBody()
	from fy_config.fy_admin_trading_external_functions import getAllUsers
	return getAllUsers(retParams)

# EDIS
def fyEdisBoTpinGenPOST(req, res):
	retParams = req.getQueryParams(["token_id"])
	retParams["funct"] = "edisBoTpinGen"
	from fy_config.fy_edis_external_functions import fy_edis_external_boTpin_generation
	return fy_edis_external_boTpin_generation(retParams)
	
def fyEdisIndexPOST(req, res):
	retParams = {}
	retParams["body"] = req.getBody()
	try:
		# if not isinstance(retParams, dict):
		# 	retParams = json.loads(retParams)
		retParamsToken = req.getQueryParams(["token_id"])
		retParams["token_id"] = retParamsToken["token_id"]
	except Exception as e:
		return "Invalid Input Format : " + str(e)
	retParams["funct"] = "edisIndex"
	from fy_config.fy_edis_external_functions import fy_edis_external_transaction_req
	return fy_edis_external_transaction_req(retParams)

def fyEdisDetailsPOST(req, res):
	retParams = req.getQueryParams(["token_id"])
	retParams["funct"] = "edisInquiry"
	from fy_config.fy_edis_external_functions import fy_edis_external_details
	return fy_edis_external_details(retParams)

def fyEdisInquiryPOST(req, res):
	retParams = {}
	retParams["body"] = req.getBody()
	try:
		# if not isinstance(retParams, dict):
		# 	retParams = json.loads(retParams)
		retParamsToken = req.getQueryParams(["token_id"])
		retParams["token_id"] = retParamsToken["token_id"]
	except Exception as e:
		return "Invalid Input Format : " + str(e)
	retParams["funct"] = "edisInquiry"
	from fy_config.fy_edis_external_functions import fy_edis_external_inquiry
	return fy_edis_external_inquiry(retParams)


def marginBasketPost(req, resp):
	getToken = req.getQueryParams(["token_id"])
	getHeader = req.getHeaderParm(["x-forwarded-for"])
	retParams = req.getBody()
	if not isinstance(retParams, dict):
		retParams = json.loads(retParams)
	retParams["funct"] = "margin_basket_post"
	# retParams["cookie"] = req.getCookies()
	retParams["cookie"] = req.getHeaderParm(["authorization"]).get("authorization","")
	retParams["token_id"] = ""
	if "token_id" in getToken:
		retParams["token_id"] = getToken["token_id"]
	if "x-forwarded-for" in getHeader:
		retParams["user_ip"] = getHeader["x-forwarded-for"]

	# from fy_config.fy_baskets_external_functions import fy_margin_basket
	from fy_config.baskets.fy_baskets_external_functions import fy_margin_basket
	return fy_margin_basket(retParams)
	
def main():
	None

if __name__ == "__main__":
	main()
