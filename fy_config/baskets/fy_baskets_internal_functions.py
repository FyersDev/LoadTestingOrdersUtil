moduleName = "fy_baskets_internal_functions"

try:
	import sys
	# import boto3
	import time
	import json
	import string
	import random
	from botocore.exceptions import ClientError

	import fy_connections_defines as connDef
	import fy_data_and_trade_defines as dataTradeDef
	import fy_base_functions as baseFunc
	import fy_base_defines as baseDef
	import fy_base_success_error_codes as baseCodes
	import fy_base_success_error_messages as baseMsg
	import fy_common_api_keys_values as commonKV
	import fy_common_internal_functions as commonInt

except Exception as e:
	print ("ERR : %s : %s : %s" % (moduleName, "Could not import module", e))
	sys.exit()

def INTERNAL_getUserBasketsFromS3(fyId, s3client=None, callingFuncName=""):
	"""
		Fetch the particular user's baskets which are saved in S3 and return the result
		
		Inputs => fyId 	: Fyers Client Id : str
		Return => List of the baskets created by the user  : list
		
	"""
	funcName = "INTERNAL_getUserBasketsFromS3"
	try:
		userData = []
		if s3client == None:
			# s3client = boto3.client(connDef.AWS_SERVICE_S3)
			s3client = connDef.AWS_BOTO3_S3_CONNECTION
		key = connDef.AWS_S3_FOLDER_PATH_USER_BASKETS + fyId + connDef.FILE_USER_BASKETS_SUFFIX
		s3object = s3client.get_object(Bucket = connDef.AWS_S3_BUCKET_USER_DATA, Key = key)

		if s3object['ResponseMetadata']['HTTPStatusCode'] != 200:
			return [baseCodes.ERROR_C_1, baseCodes.ERROR_C_S3_GET_FAILED, baseMsg.ERROR_M_S3_GET_FAILED]
		if s3object['ContentLength'] == 0:
			return [baseCodes.ERROR_C_1, baseCodes.ERROR_C_S3_GET_FAILED, baseMsg.ERROR_M_S3_GET_FAILED]

		s3_data = s3object['Body'].read()
		userData = json.loads(s3_data)

		# print ("INTERNAL_getUserBasketsFromS3 s3: ", userData)
		return [baseCodes.SUCCESS_C_1, userData, ""]

	except ClientError as e:
		baseFunc.logEntryFunc2(baseDef.LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, key, err_msg=e, fyId=fyId)
		#if user never created baskets - no data fetched from s3 - return an empty list
		if e.response["Error"]["Code"] == "NoSuchKey":
			return [baseCodes.SUCCESS_C_1, userData, ""]
	except Exception as e:
		baseFunc.logEntryFunc2(baseDef.LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, err_msg=e, fyId=fyId)
		return [baseCodes.ERROR_C_1, baseCodes.ERROR_C_UNKNOWN, baseMsg.ERROR_M_UNKNOWN_1]

def INTERNAL_updateUserBasketsToS3(fyId, userData, s3client=None, callingFuncName=""):
	"""
		Save the particular user's baskets in S3
		
		Inputs => 	fyId 	: Fyers Client Id : str
					userData: Updated baskets of the user to be saved in S3 : list
	"""
	funcName = "INTERNAL_updateUserBasketsToS3"
	try:
		userDataJson = json.dumps(userData)
		key = connDef.AWS_S3_FOLDER_PATH_USER_BASKETS + fyId + connDef.FILE_USER_BASKETS_SUFFIX
		if s3client == None:
			# s3client = boto3.client(connDef.AWS_SERVICE_S3)
			s3client = connDef.AWS_BOTO3_S3_CONNECTION
		s3client.put_object(Body = userDataJson, Bucket = connDef.AWS_S3_BUCKET_USER_DATA, Key = key)
		return [baseCodes.SUCCESS_C_1, "",""]
	except Exception as e:
		baseFunc.logEntryFunc2(baseDef.LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, err_msg=e, fyId=fyId)
		return [baseCodes.ERROR_C_1, baseCodes.ERROR_C_UNKNOWN, baseMsg.ERROR_M_UNKNOWN_1]

def INTERNAL_createBasketId(callingFuncName=""):
	"""
		Create a unique id for basket id/ item id
		Return => idString : Random 10 digit string of digits and uppercase letters : str
	"""
	funcName = "INTERNAL_createBasketId"
	try:
		chars = string.ascii_uppercase + string.digits
		idString = "".join(random.choice(chars) for _ in range(10))
		return [baseCodes.SUCCESS_C_1, idString, ""]
	except Exception as e:
		baseFunc.logEntryFunc2(baseDef.LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, err_msg=e)
		return [baseCodes.ERROR_C_1, baseCodes.ERROR_C_UNKNOWN, baseMsg.ERROR_M_UNKNOWN_1]

def INTERNAL_validateItemParams(item, callingFuncName=""):
	"""
		Verify the order details and the structure of an item in a basket
		
		Return => item : Valid item param with the order details : dict
	"""
	funcName = "INTERNAL_validateItemParams"
	try:
		if not isinstance(item, dict):
			item = json.loads(item)

		if commonKV.API_K_FYSYMBOL not in item:
			return [baseCodes.ERROR_C_1,baseCodes.ERROR_C_INV_FYSYMBOL, baseMsg.ERROR_M_INV_FYSYMBOL]

		if item[commonKV.API_K_FYSYMBOL].endswith("INDEX"):
			return [baseCodes.ERROR_C_1,baseCodes.ERROR_C_INV_FYSYMBOL, baseMsg.ERROR_M_INV_FYSYMBOL]

		if commonKV.API_K_ORDER_QTY not in item:
			return [baseCodes.ERROR_C_1,baseCodes.ERROR_C_INV_ORDER_QTY, baseMsg.ERROR_M_INV_ORDER_QTY]

		if commonKV.API_K_ORDER_SIDE not in item:
			return [baseCodes.ERROR_C_1,baseCodes.ERROR_C_INV_ORDER_SIDE, baseMsg.ERROR_M_INV_ORDER_SIDE]

		if commonKV.API_K_ORDER_TYPE not in item:
			return [baseCodes.ERROR_C_1,baseCodes.ERROR_C_INV_ORDER_TYPE, baseMsg.ERROR_M_INV_ORDER_TYPE]

		if commonKV.API_K_ORDER_PRODUCT not in item:
			return [baseCodes.ERROR_C_1,baseCodes.ERROR_C_INV_ORDER_PRODUCT, baseMsg.ERROR_M_INV_ORDER_PRODUCT]

		if commonKV.API_K_ORDER_LMT_PRICE not in item:
			return [baseCodes.ERROR_C_1,baseCodes.ERROR_C_INV_ORDER_LMT_PRICE, baseMsg.ERROR_M_INV_ORDER_LMT_PRICE]

		if commonKV.API_K_ORDER_STP_PRICE not in item:
			return [baseCodes.ERROR_C_1,baseCodes.ERROR_C_INV_ORDER_STP_PRICE, baseMsg.ERROR_M_INV_ORDER_STP_PRICE]

		if commonKV.API_K_DISC_QTY not in item:
			return [baseCodes.ERROR_C_1,baseCodes.ERROR_C_INV_ORDER_DISC_QTY, baseMsg.ERROR_M_INV_ORDER_DISC_QTY]

		if commonKV.API_K_ORDER_VALIDITY not in item:
			return [baseCodes.ERROR_C_1,baseCodes.ERROR_C_INV_ORDER_VALIDITY, baseMsg.ERROR_M_INV_ORDER_VALIDITY]

		if commonKV.API_K_OFFLINE_FLAG not in item:
			return [baseCodes.ERROR_C_1,baseCodes.ERROR_C_INV_ORDER_OFFLINE_FLAG, baseMsg.ERROR_M_INV_ORDER_OFFLINE_FLAG]

		if item[commonKV.API_K_ORDER_PRODUCT] == commonKV.API_V_PRODTYPE_CO:
			if commonKV.API_K_ORDER_STOP_LOSS not in item:
				return [baseCodes.ERROR_C_1,baseCodes.ERROR_C_INV_ORDER_STOP_LOSS, baseMsg.ERROR_M_INV_ORDER_STOP_LOSS]

		if item[commonKV.API_K_ORDER_PRODUCT] == commonKV.API_V_PRODTYPE_BO:
			if commonKV.API_K_ORDER_STOP_LOSS not in item:
				return [baseCodes.ERROR_C_1,baseCodes.ERROR_C_INV_ORDER_STOP_LOSS, baseMsg.ERROR_M_INV_ORDER_STOP_LOSS]

			if commonKV.API_K_ORDER_TAKE_PROFIT not in item:
				return [baseCodes.ERROR_C_1,baseCodes.ERROR_C_INV_ORDER_TARGET_VAL, baseMsg.ERROR_M_INV_ORDER_TARGET_VAL]

		item[commonKV.API_K_ORDER_QTY] = int(item[commonKV.API_K_ORDER_QTY])
		item[commonKV.API_K_ORDER_SIDE] = int(item[commonKV.API_K_ORDER_SIDE])
		item[commonKV.API_K_ORDER_TYPE] = int(item[commonKV.API_K_ORDER_TYPE])
		item[commonKV.API_K_ORDER_LMT_PRICE] = float(item[commonKV.API_K_ORDER_LMT_PRICE])
		item[commonKV.API_K_ORDER_STP_PRICE] = float(item[commonKV.API_K_ORDER_STP_PRICE])
		item[commonKV.API_K_DISC_QTY] = int(item[commonKV.API_K_DISC_QTY])
		item[commonKV.API_K_ORDER_STOP_LOSS] = float(item[commonKV.API_K_ORDER_STOP_LOSS])
		item[commonKV.API_K_ORDER_TAKE_PROFIT] = float(item[commonKV.API_K_ORDER_TAKE_PROFIT])
		item[commonKV.API_K_OFFLINE_FLAG] = json.loads(str(item[commonKV.API_K_OFFLINE_FLAG]).lower())

		##If any of the symbol details are not present - fetch from redis and add in the item dict
		if "ex_sym" not in item or "description" not in item or "sym_token" not in item or "exchange" not in item or "segment" not in item:
			allSymbolsList = [item[commonKV.API_K_FYSYMBOL]]
			validSymbolsRet = commonInt.getSymbolsFromSymbolMasterCache(allSymbolsList,callingFuncName=funcName)
			# print("validSymbolsRet",validSymbolsRet)
			try:
				if validSymbolsRet[0] == baseCodes.SUCCESS_C_1:
					symDict = validSymbolsRet[1][1]
					item["ex_sym"] = symDict[item[commonKV.API_K_FYSYMBOL]]["underSym"]
					item["description"] = symDict[item[commonKV.API_K_FYSYMBOL]]["symbolDesc"]
					item["sym_token"] = symDict[item[commonKV.API_K_FYSYMBOL]]["fyToken"]
					item["exchange"] = symDict[item[commonKV.API_K_FYSYMBOL]]["exchangeName"]
					item["segment"] = symDict[item[commonKV.API_K_FYSYMBOL]]["segment"]
			except Exception as e:
				item["ex_sym"] = ""
				item["description"] = ""
				item["sym_token"] = ""
				item["exchange"] = ""
				item["segment"] = 0

		return [baseCodes.SUCCESS_C_1, item, ""]

	except ValueError as e:
		baseFunc.logEntryFunc2(baseDef.LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, err_msg=e)
		return [baseCodes.ERROR_C_1, baseCodes.ERROR_C_INV_INP, baseMsg.ERROR_M_INV_INPUT_1]

	except Exception as e:
		baseFunc.logEntryFunc2(baseDef.LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, err_msg=e)
		return [baseCodes.ERROR_C_1, baseCodes.ERROR_C_UNKNOWN, baseMsg.ERROR_M_UNKNOWN_1]

def INTERNAL_createBasket(fyId, basketName, basketItems, callingFuncName=""):
	"""
		Create a new empty basket for the particular user
		Inputs => 	fyId 		: Fyers Client Id : str
					basketName 	: Name of the basket to be created : str
					basketItems : Order details of the Items to add in the basket : list
		Return => 	userData 	: Updated list of all the baskets of the user  : list
	"""
	funcName = "INTERNAL_createBasket"
	try:
		# s3client = boto3.client(connDef.AWS_SERVICE_S3)
		s3client = connDef.AWS_BOTO3_S3_CONNECTION
		getUserData = INTERNAL_getUserBasketsFromS3(fyId, s3client=s3client, callingFuncName=funcName)
		if getUserData[0] == baseCodes.ERROR_C_1:
			return getUserData
		userData = getUserData[1]

		names = [basket["name"] for basket in userData]
		if basketName in names:
			return [baseCodes.ERROR_C_1, baseCodes.ERROR_C_INV_INP, "Basket with same name already exists"]

		if not len(basketName)>0:
			return [baseCodes.ERROR_C_1, baseCodes.ERROR_C_INV_INP, "Please provide a basket name"]

		idFuncRet = INTERNAL_createBasketId(callingFuncName=funcName)
		if idFuncRet[0] == baseCodes.ERROR_C_1:
			return idFuncRet
		basketId = idFuncRet[1]

		items = []
		time_now = int(time.time())

		if basketItems:
			for itemParams in basketItems:
				funcRet = INTERNAL_validateItemParams(itemParams, callingFuncName=funcName)
				if funcRet[0] != baseCodes.ERROR_C_1:
					idFuncRet = INTERNAL_createBasketId(callingFuncName=funcName)
					if idFuncRet[0] != baseCodes.ERROR_C_1:
						item = {"params":funcRet[1],
								"time_update":time_now,
								"time_create":time_now,
								"id":idFuncRet[1],
								"order_data":{"status":0,"order_id":"","message":""}}
						items.append(item)

		basketDict = {	"name": basketName,
						"time_create": time_now,
						"time_update": time_now,
						"time_execute": 0,
						"status_execute": 0,
						"items": items,
						"id": basketId	}

		# print(basketDict)

		userData.append(basketDict)

		if len(items) > dataTradeDef.MAX_NUMBER_BASKETS_ITEMS:
			return [baseCodes.ERROR_C_1, baseCodes.ERROR_C_INV_INP, "Maximum Items number limit reached."]

		if len(userData) > dataTradeDef.MAX_NUMBER_BASKETS:
			return [baseCodes.ERROR_C_1, baseCodes.ERROR_C_INV_INP, "Maximum Basket number limit reached."]

		updateFuncRet = INTERNAL_updateUserBasketsToS3(fyId, userData, s3client=s3client, callingFuncName=funcName)
		if updateFuncRet[0] == baseCodes.ERROR_C_1:
			return updateFuncRet

		return [baseCodes.SUCCESS_C_1, userData, ""]

	except Exception as e:
		baseFunc.logEntryFunc2(baseDef.LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, basketName,err_msg=e, fyId=fyId)
		return [baseCodes.ERROR_C_1, baseCodes.ERROR_C_UNKNOWN, baseMsg.ERROR_M_UNKNOWN_1]

def INTERNAL_modifyBasket(fyId, basketId, basketName, basketItems, callingFuncName=""):
	"""
		Modify an existing basket of the particular user
		Modify the name of the basket / Update the items in the basket (Will replace the items in the basket with the items provided in the input)
		Inputs => 	fyId 		: Fyers Client Id : str
					basketId 	: id of the basket to modify : str
					basketName 	: New name of the basket : str
					basketItems : Items in the basket : list
		Return => 	userData 	: Updated list of all the baskets of the user  : list
	"""
	funcName = "INTERNAL_modifyBasket"
	try:
		if basketName != None:
			if not len(basketName)>0:
				return [baseCodes.ERROR_C_1, baseCodes.ERROR_C_INV_INP, "Please provide a basket name"]

		if basketItems != None:
			for item in basketItems:
				funcRet = INTERNAL_validateItemParams(item["params"], callingFuncName=funcName)
				if funcRet[0] == baseCodes.ERROR_C_1:
					return funcRet
				item["params"] = funcRet[1]
				if "time_create" not in item:
					return [baseCodes.ERROR_C_1, baseCodes.ERROR_C_INV_INP, baseMsg.ERROR_M_INV_INPUT_1]
				if "time_update" not in item:
					return [baseCodes.ERROR_C_1, baseCodes.ERROR_C_INV_INP, baseMsg.ERROR_M_INV_INPUT_1]
				if "id" not in item:
					return [baseCodes.ERROR_C_1, baseCodes.ERROR_C_INV_INP, baseMsg.ERROR_M_INV_INPUT_1]
				if "order_data" not in item:
					item["order_data"] = {"status":0,"order_id":"","message":""}

		# s3client = boto3.client(connDef.AWS_SERVICE_S3)
		s3client = connDef.AWS_BOTO3_S3_CONNECTION
		getUserData = INTERNAL_getUserBasketsFromS3(fyId, s3client=s3client, callingFuncName=funcName)
		if getUserData[0] == baseCodes.ERROR_C_1:
			return getUserData
		userData = getUserData[1]

		ids = [data["id"] for data in userData]
		basketIndex = ids.index(basketId)

		if basketName != None:
			names = [basket["name"] for basket in userData]
			if basketName in names:
				return [baseCodes.ERROR_C_1, baseCodes.ERROR_C_INV_INP, "Basket with same name already exists"]
			userData[basketIndex]["name"] = basketName
		if basketItems != None:
			userData[basketIndex]["items"] = basketItems
		userData[basketIndex]["time_update"] = int(time.time())

		updateFuncRet = INTERNAL_updateUserBasketsToS3(fyId, userData, s3client=s3client, callingFuncName=funcName)
		if updateFuncRet[0] == baseCodes.ERROR_C_1:
			return updateFuncRet

		return [baseCodes.SUCCESS_C_1, userData, ""]

	except ValueError as e:
		baseFunc.logEntryFunc2(baseDef.LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, err_msg=e)
		return [baseCodes.ERROR_C_1, baseCodes.ERROR_C_INV_INP, baseMsg.ERROR_M_INV_BASKET_ID]

	except Exception as e:
		baseFunc.logEntryFunc2(baseDef.LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, basketId, basketName, basketItems,err_msg=e, fyId=fyId)
		return [baseCodes.ERROR_C_1, baseCodes.ERROR_C_UNKNOWN, baseMsg.ERROR_M_UNKNOWN_1]

def INTERNAL_deleteBasket(fyId, basketId, callingFuncName=""):
	"""
		Delete an existing basket of the particular user
		Inputs => 	fyId 		: Fyers Client Id : str
					basketId 	: id of the basket to delete : str
		Return => 	userData 	: Updated list of all the baskets of the user  : list
	"""
	funcName = "INTERNAL_deleteBasket"
	try:
		# s3client = boto3.client(connDef.AWS_SERVICE_S3)
		s3client = connDef.AWS_BOTO3_S3_CONNECTION
		getUserData = INTERNAL_getUserBasketsFromS3(fyId, s3client=s3client, callingFuncName=funcName)
		if getUserData[0] == baseCodes.ERROR_C_1:
			return getUserData
		userData = getUserData[1]

		ids = [data["id"] for data in userData]
		basketIndex = ids.index(basketId)
		del userData[basketIndex]

		updateFuncRet = INTERNAL_updateUserBasketsToS3(fyId, userData, s3client=s3client, callingFuncName=funcName)
		if updateFuncRet[0] == baseCodes.ERROR_C_1:
			return updateFuncRet

		return [baseCodes.SUCCESS_C_1, userData, ""]

	except ValueError as e:
		baseFunc.logEntryFunc2(baseDef.LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, basketId, err_msg=e, fyId=fyId)
		return [baseCodes.ERROR_C_1, baseCodes.ERROR_C_INV_INP, baseMsg.ERROR_M_INV_BASKET_ID]

	except Exception as e:
		baseFunc.logEntryFunc2(baseDef.LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, basketId,err_msg=e , fyId=fyId)
		return [baseCodes.ERROR_C_1, baseCodes.ERROR_C_UNKNOWN, baseMsg.ERROR_M_UNKNOWN_1]

def INTERNAL_addItem(fyId, itemParams, basketId, callingFuncName=""):
	"""
		Add a new item to an existing basket
		Inputs => 	fyId 		: Fyers Client Id : str
					basketId 	: id of the basket to add the item to : str
					itemParams 	: Order details of the item to add : dict
		Return => 	userData 	: Updated list of all the baskets of the user  : list
	"""
	funcName = "INTERNAL_addItem"
	try:
		funcRet = INTERNAL_validateItemParams(itemParams, callingFuncName=funcName)
		if funcRet[0] == baseCodes.ERROR_C_1:
			return funcRet
		itemParams = funcRet[1]

		# s3client = boto3.client(connDef.AWS_SERVICE_S3)
		s3client = connDef.AWS_BOTO3_S3_CONNECTION
		getUserData = INTERNAL_getUserBasketsFromS3(fyId, s3client=s3client, callingFuncName=funcName)
		if getUserData[0] == baseCodes.ERROR_C_1:
			return getUserData
		userData = getUserData[1]

		ids = [data["id"] for data in userData]
		basketIndex = ids.index(basketId)

		idFuncRet = INTERNAL_createBasketId(callingFuncName=funcName)
		if idFuncRet[0] == baseCodes.ERROR_C_1:
			return idFuncRet
		itemId = idFuncRet[1]

		time_now = int(time.time())

		item = {"params":itemParams,
				"time_update":time_now,
				"time_create":time_now,
				"id":itemId,
				"order_data":{"status":0,"order_id":"","message":""}}
		userData[basketIndex]["items"].append(item)
		userData[basketIndex]["time_update"] = time_now

		if len(userData) > dataTradeDef.MAX_NUMBER_BASKETS:
			return [baseCodes.ERROR_C_1, baseCodes.ERROR_C_INV_INP, "Maximum Basket number limit reached."]
		if len(userData[basketIndex]["items"]) > dataTradeDef.MAX_NUMBER_BASKETS_ITEMS:
			return [baseCodes.ERROR_C_1, baseCodes.ERROR_C_INV_INP, "Maximum Items number limit reached."]

		updateFuncRet = INTERNAL_updateUserBasketsToS3(fyId, userData, s3client=s3client, callingFuncName=funcName)
		if updateFuncRet[0] == baseCodes.ERROR_C_1:
			return updateFuncRet

		return [baseCodes.SUCCESS_C_1, userData, ""]

	except ValueError as e:
		baseFunc.logEntryFunc2(baseDef.LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, err_msg=e)
		return [baseCodes.ERROR_C_1, baseCodes.ERROR_C_INV_INP, baseMsg.ERROR_M_INV_BASKET_ID]

	except Exception as e:
		baseFunc.logEntryFunc2(baseDef.LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, itemParams, basketId,err_msg=e, fyId=fyId)
		return [baseCodes.ERROR_C_1, baseCodes.ERROR_C_UNKNOWN, baseMsg.ERROR_M_UNKNOWN_1]

def INTERNAL_modifyItem(fyId, itemParams, itemId, basketId, callingFuncName=""):
	"""
		Modify an existing item in an existing basket
		Inputs => 	fyId 		: Fyers Client Id : str
					itemParams 	: Updated Order details of the item to change : dict
					itemId 		: id of the item to be modified : str
					basketId 	: id of the basket of the particular item : str
		Return => 	userData 	: Updated list of all the baskets of the user  : list
	"""
	funcName = "INTERNAL_modifyItem"
	try:
		funcRet = INTERNAL_validateItemParams(itemParams, callingFuncName=funcName)
		if funcRet[0] == baseCodes.ERROR_C_1:
			return funcRet
		itemParams = funcRet[1]

		# s3client = boto3.client(connDef.AWS_SERVICE_S3)
		s3client = connDef.AWS_BOTO3_S3_CONNECTION
		getUserData = INTERNAL_getUserBasketsFromS3(fyId, s3client=s3client, callingFuncName=funcName)
		if getUserData[0] == baseCodes.ERROR_C_1:
			return getUserData
		userData = getUserData[1]

		time_now = int(time.time())

		ids = [data["id"] for data in userData]
		basketIndex = ids.index(basketId)

		items = userData[basketIndex]["items"]
		itemids = [data["id"] for data in items]
		itemIndex = itemids.index(itemId)

		item = items[itemIndex]
		if item["order_data"]["status"] != 0:
			return [baseCodes.ERROR_C_1, baseCodes.ERROR_C_INV_INP, "Reset this item to modify"]
		item["params"] = itemParams
		item["time_update"] = time_now

		userData[basketIndex]["time_update"] = time_now

		updateFuncRet = INTERNAL_updateUserBasketsToS3(fyId, userData, s3client=s3client, callingFuncName=funcName)
		if updateFuncRet[0] == baseCodes.ERROR_C_1:
			return updateFuncRet

		return [baseCodes.SUCCESS_C_1, userData, ""]

	except ValueError as e:
		baseFunc.logEntryFunc2(baseDef.LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, err_msg=e)
		return [baseCodes.ERROR_C_1, baseCodes.ERROR_C_INV_INP, baseMsg.ERROR_M_INV_BASKET_ID]

	except Exception as e:
		baseFunc.logEntryFunc2(baseDef.LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, itemParams, itemId, basketId,err_msg=e, fyId=fyId)
		return [baseCodes.ERROR_C_1, baseCodes.ERROR_C_UNKNOWN, baseMsg.ERROR_M_UNKNOWN_1]

def INTERNAL_deleteItem(fyId, itemId, basketId, callingFuncName=""):
	"""
		Delete an item in an existing basket
		Inputs => 	fyId 		: Fyers Client Id : str
					itemId 		: id of the item to be deleted : str
					basketId 	: id of the basket of the particular item : str
		Return => 	userData 	: Updated list of all the baskets of the user  : list
	"""
	funcName = "INTERNAL_deleteItem"
	try:
		# s3client = boto3.client(connDef.AWS_SERVICE_S3)
		s3client = connDef.AWS_BOTO3_S3_CONNECTION
		getUserData = INTERNAL_getUserBasketsFromS3(fyId, s3client=s3client, callingFuncName=funcName)
		if getUserData[0] == baseCodes.ERROR_C_1:
			return getUserData
		userData = getUserData[1]

		time_now = int(time.time())

		ids = [data["id"] for data in userData]
		basketIndex = ids.index(basketId)

		items = userData[basketIndex]["items"]
		itemids = [data["id"] for data in items]
		itemIndex = itemids.index(itemId)
		del items[itemIndex]
		userData[basketIndex]["time_update"] = time_now
		##If all items are deleted, then reset the basket
		if len(items) == 0:
			userData[basketIndex]["status_execute"] = 0

		updateFuncRet = INTERNAL_updateUserBasketsToS3(fyId, userData, s3client=s3client, callingFuncName=funcName)
		if updateFuncRet[0] == baseCodes.ERROR_C_1:
			return updateFuncRet

		return [baseCodes.SUCCESS_C_1, userData, ""]

	except ValueError as e:
		baseFunc.logEntryFunc2(baseDef.LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, err_msg=e)
		return [baseCodes.ERROR_C_1, baseCodes.ERROR_C_INV_INP, baseMsg.ERROR_M_INV_BASKET_ID]

	except Exception as e:
		baseFunc.logEntryFunc2(baseDef.LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, itemId, basketId, err_msg=e, fyId=fyId)
		return [baseCodes.ERROR_C_1, baseCodes.ERROR_C_UNKNOWN, baseMsg.ERROR_M_UNKNOWN_1]

def INTERNAL_getBasketOrderDetails(fyId, basketId, s3client=None, callingFuncName=""):
	funcName = "INTERNAL_getBasketOrderDetails"
	try:
		if s3client == None:
			# s3client = boto3.client(connDef.AWS_SERVICE_S3)
			s3client = connDef.AWS_BOTO3_S3_CONNECTION
		getUserData = INTERNAL_getUserBasketsFromS3(fyId, s3client=s3client, callingFuncName=funcName)
		if getUserData[0] == baseCodes.ERROR_C_1:
			return getUserData

		userData = getUserData[1]
		ids = [data["id"] for data in userData]
		basketIndex = ids.index(basketId)

		items = userData[basketIndex]["items"]
		return [baseCodes.SUCCESS_C_1, items, userData, basketIndex]

	except ValueError as e:
		baseFunc.logEntryFunc2(baseDef.LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, basketId, err_msg=e, fyId=fyId)
		return [baseCodes.ERROR_C_1, baseCodes.ERROR_C_INV_INP, baseMsg.ERROR_M_INV_BASKET_ID]

	except Exception as e:
		baseFunc.logEntryFunc2(baseDef.LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, err_msg=e, fyId=fyId)
		return [baseCodes.ERROR_C_1, baseCodes.ERROR_C_UNKNOWN, baseMsg.ERROR_M_UNKNOWN_1]

def INTERNAL_updateOrderDetailsToBasket(fyId, orderExecuteList, userData, basketIndex, s3client=None, callingFuncName=""):
	funcName = "INTERNAL_updateOrderDetailsToBasket"
	try:
		##Add the order placement status to basket
		if s3client == None:
			# s3client = boto3.client(connDef.AWS_SERVICE_S3)
			s3client = connDef.AWS_BOTO3_S3_CONNECTION
		# print(userData[basketIndex])

		userData[basketIndex]["time_execute"] = int(time.time())
		userData[basketIndex]["status_execute"] = 1
		for i in range(len(userData[basketIndex]["items"])):
			userData[basketIndex]["items"][i]["order_data"]["order_id"] = orderExecuteList[i].get("id","")
			userData[basketIndex]["items"][i]["order_data"]["message"] = orderExecuteList[i].get("message","")
			userData[basketIndex]["items"][i]["order_data"]["status"] = 1 if orderExecuteList[i]["s"] == "ok" else -1

		# print(userData[basketIndex])

		updateFuncRet = INTERNAL_updateUserBasketsToS3(fyId, userData, s3client=s3client, callingFuncName=funcName)
		if updateFuncRet[0] == baseCodes.ERROR_C_1:
			return updateFuncRet

		# return [baseCodes.SUCCESS_C_1, "", ""]
		return [baseCodes.SUCCESS_C_1, userData, ""]

	except Exception as e:
		baseFunc.logEntryFunc2(baseDef.LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, err_msg=e, fyId=fyId)
		return [baseCodes.ERROR_C_1, baseCodes.ERROR_C_UNKNOWN, baseMsg.ERROR_M_UNKNOWN_1]

def INTERNAL_resetBasket(fyId, basketId, callingFuncName=""):
	funcName = "INTERNAL_resetBasket"
	try:
		# s3client = boto3.client(connDef.AWS_SERVICE_S3)
		s3client = connDef.AWS_BOTO3_S3_CONNECTION
		getUserData = INTERNAL_getUserBasketsFromS3(fyId, s3client=s3client, callingFuncName=funcName)
		if getUserData[0] == baseCodes.ERROR_C_1:
			return getUserData
		
		userData = getUserData[1]
		ids = [data["id"] for data in userData]
		basketIndex = ids.index(basketId)

		# print(userData[basketIndex])

		# userData[basketIndex]["time_execute"] = 0
		userData[basketIndex]["status_execute"] = 0
		for i in range(len(userData[basketIndex]["items"])):
			userData[basketIndex]["items"][i]["order_data"]["status"] = 0
			userData[basketIndex]["items"][i]["order_data"]["order_id"] = ""
			userData[basketIndex]["items"][i]["order_data"]["message"] = ""

		# print(userData[basketIndex])

		updateFuncRet = INTERNAL_updateUserBasketsToS3(fyId, userData, s3client=s3client, callingFuncName=funcName)
		if updateFuncRet[0] == baseCodes.ERROR_C_1:
			return updateFuncRet

		return [baseCodes.SUCCESS_C_1, userData, ""]

	except ValueError as e:
		baseFunc.logEntryFunc2(baseDef.LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, basketId, err_msg=e, fyId=fyId)
		return [baseCodes.ERROR_C_1, baseCodes.ERROR_C_INV_INP, baseMsg.ERROR_M_INV_BASKET_ID]

	except Exception as e:
		baseFunc.logEntryFunc2(baseDef.LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, err_msg=e, fyId=fyId)
		return [baseCodes.ERROR_C_1, baseCodes.ERROR_C_UNKNOWN, baseMsg.ERROR_M_UNKNOWN_1]


def main():
	pass

if __name__ == '__main__':
	main()