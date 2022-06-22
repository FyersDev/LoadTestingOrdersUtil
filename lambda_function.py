#!/usr/bin/env python
import sys, os, time, json
# sys.path.append("./lib")
sys.path.append("./")
## Custom modules
import request as Req
import response as Res
import lambda_mapping as lm
import lambda_defines as ld
import fyers_inp_validatn as fyValid
import fy_config.fy_base_api_keys_values as fyBaseKV

def lambda_handler(event,context):
	try:
		# startT = time.time()
		# print("event",event)
		reqObj = Req.Request(event)
		resObj = Res.Response()
		# endTime = time.time()
		# print "time:", startT - endTime
		pathList = reqObj.getPathList()
		# print(pathList)
		checkevent = reqObj.isAlb()

		if not checkevent:
			from fy_config.cronFunction import fy_cronFunction
			funcRet = fy_cronFunction(event)
			resObj.setResp(httpCode = 200, httpCodeStr = "200 OK", respBody = funcRet)
			return resObj()

		# print "pathList:", pathList
		# resObj.setResp(httpCode = 200, httpCodeStr = "200 OK", respBody = event)
		# return resObj()
		# return {'body': '',
		# 	'headers':
		# 	{
		# 		'Access-Control-Allow-Origin': '*',
		# 		'Access-Control-Allow-Methods': 'GET,POST,PUT,PATCH,DELETE,OPTIONS',
		# 		'Access-Control-Allow-Credentials': "true",
		# 		'Content-Type': 'text/html; charset=utf-8',
		# 	},
		# 		'statusDescription': '200 OK',
		# 		'isBase64Encoded': False,
		# 		'statusCode': 200
		# }


		# ##Setting redis key for total requests count
		# try:
		# 	import fy_config.fy_set_redis_count as fyRedisSetCount
		# 	fyRedisSetCount.incr_redis_field(pathList[2:],reqObj.httpMeth())
		# except Exception as e:
		# 	print ("ERROR", "lambda_handler", "fy_set_redis_count", e)


		respDict = reqObj.getHeaderParm(["origin"])
		if "origin" in respDict:
			retDomValid = fyValid.validateDomain(respDict["origin"])
			if retDomValid[fyBaseKV.API_K_STATUS] == fyBaseKV.API_V_SUCCESS:
				## Success
				resObj.setHeader("Access-Control-Allow-Origin", str(respDict["origin"]))
				resObj.setHeader("Access-Control-Allow-Credentials", "true")
				resObj.setResp(httpCode = 200, httpCodeStr = "200 OK", respBody = "")
			else:
				## Error
				# print "ERROR", retDomValid
				resObj.setError(httpCode = 400, httpCodeStr = "400 ERROR", respBody = "Not authorized")
				return resObj()

		if reqObj.httpMeth().upper() == "OPTIONS":
			# print "options", pathList, event
			resObj.setHeader("Access-Control-Allow-Headers", "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token")
			# resObj.setHeader("Access-Control-Allow-Credentials", "true")
			resObj.setHeader("Access-Control-Allow-Methods", "GET,POST,PUT,PATCH,DELETE,OPTIONS")
			# print "resObj:",resObj()
			return resObj()

			# reqObj.
		if pathList == None:
			resObj.setError(httpCode = 400, httpCodeStr = "400 ERROR", respBody = "Invalid request")
			return resObj()
		if len(pathList) > 10:
			resObj.setError(httpCode = 400, httpCodeStr = "400 ERROR", respBody = "Invalid resource")
			return resObj()

		## For Trading-View functions
		if pathList[0] == "tv":
			if pathList[1] == "v1":
				resMap = lm.TV_RESOURCE_MAPPING
				pathList = pathList[2:]
			else:
				resObj.setError(httpCode = 400, httpCodeStr = "400 ERROR", respBody = "Invalid resource")
				return resObj()
		## For Fyers functions.
		elif pathList[0] == "fy":
			if pathList[1] == "v1" or pathList[1] == "v2" or pathList[1] == "mobile":
				resMap = lm.FY_TRADE_RESOURCE_MAPPING
				pathList = pathList[2:]
			else:
				resObj.setError(httpCode = 400, httpCodeStr = "400 ERROR", respBody = "Invalid resource")
				return resObj()
		## For mobile testing functions
		elif pathList[0] == "fybeta":
			if pathList[1] == "v1":
				resMap = lm.FY_TRADE_RESOURCE_MAPPING
				pathList = pathList[2:]
			else:
				resObj.setError(httpCode = 400, httpCodeStr = "400 ERROR", respBody = "Invalid resource")
				return resObj()

		## For mobile
		elif pathList[0] == "fydev":
			# print("pathList : ", pathList)

			if pathList[1] == "mobile" or pathList[1] == "v1":
				resMap = lm.FY_TRADE_RESOURCE_MAPPING
				pathList = pathList[2:]
			else:
				resObj.setError(httpCode = 400, httpCodeStr = "400 ERROR", respBody = "Invalid resource")
				return resObj()
		else:
			resObj.setError(httpCode = 400, httpCodeStr = "400 ERROR", respBody = "Invalid resource")
			return resObj()
		mapFlag = True
		resCount = 0
		for eachRes in pathList:
			if eachRes in resMap:
				resMap = resMap[eachRes]
				resCount += 1
			else:
				if ld.URL_REST_ID_STR in resMap:
					resMap = resMap[ld.URL_REST_ID_STR]
					resCount += 1
				else:
					mapFlag = False
					break

		if mapFlag:
			if reqObj.httpMeth() in resMap:
				try:
					respMeth = resMap[reqObj.httpMeth()](reqObj, resObj)
					if isinstance(respMeth, dict):
						resObj.setHeader("Content-Type", "application/json")
					resObj.setResp(httpCode = 200, httpCodeStr = "200 OK", respBody = respMeth)
				except Exception as e:
					print ("first e", e)
					resObj.setError(httpCode = 500, httpCodeStr = "500 ERROR", respBody = "Something went wrong")
				return resObj()
			else:
				resObj.setError(httpCode = 400, httpCodeStr = "400 ERROR", respBody = "Invalid request method")
				return resObj()

		resObj.setError(httpCode = 400, httpCodeStr = "400 ERROR", respBody = "Invalid resource")
		return resObj()
	except Exception as e:
		resObj = Res.Response()
		print ("second e", e)
		resObj.setError(httpCode = 500, httpCodeStr = "500 ERROR", respBody = "Something went wrong")
		return resObj()

def main():
	None

if __name__ == "__main__":
	main()
