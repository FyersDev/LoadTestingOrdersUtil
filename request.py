#!/usr/bin/env python
import sys, os, time, json
import base64
import urllib
import urllib.parse

REQ_PATH_STR			= "path"
REQ_HTTP_METH 			= "httpMethod"
REQ_HTTP_HEADER 		= "headers"
REQ_HTTP_HEADER_COOKIE 	= "cookie"
REQ_QUERY_STR_PARAM 	= "queryStringParameters"
REQ_BODY 				= "body"
REQ_IS_BASE64 			= "isBase64Encoded"
REQ_CONTENT_TYPE        = "content-type"
CONTENT_TYPE_MULTIPART  = "multipart/form-data"

class Request(object):
	"""
	The request class initilized by ALB event.
	"""
	def __init__(self, eventDict):
		self.eventDict 		= None
		self.pathList 		= None
		self.pathListLen 	= 0
		if not isinstance(eventDict, dict):
			try:
				# print ("eventDict:", eventDict)
				self.eventDict = json.loads(eventDict)
			except Exception as e:
				print (e)
		else:
			self.eventDict = eventDict
		self._getPathList()

	def _getPathList(self):
		# print ("self.eventDict[path]", self.eventDict["path"], type(self.eventDict))
		if REQ_PATH_STR in self.eventDict:
			# if isinstance(self.eventDict["path"], str):
			try:
				self.eventDict[REQ_PATH_STR] = self.eventDict[REQ_PATH_STR].decode("utf-8")
			except Exception as e:
				pass
			# self.eventDict[REQ_PATH_STR] = self.eventDict[REQ_PATH_STR].encode("utf-8")
			self.eventDict[REQ_PATH_STR] = self.eventDict[REQ_PATH_STR].lstrip('/').rstrip('/')
			self.pathList = self.eventDict[REQ_PATH_STR].split("/")
			self.pathListLen = len(self.pathList)

	def getPathList(self):
		return self.pathList

	def getPathStr(self):
		if REQ_PATH_STR in self.eventDict:
			return self.eventDict[REQ_PATH_STR]

	def httpMeth(self):
		if REQ_HTTP_METH in self.eventDict:
			# return self.eventDict[REQ_HTTP_METH].encode("utf-8").upper()
			return self.eventDict[REQ_HTTP_METH].upper()

	def isAlb(self):
		if "requestContext" in self.eventDict:
			if "elb" in self.eventDict["requestContext"]:
				return True
		return False

	def getCookies(self):
		cookie = ""
		if REQ_HTTP_HEADER in self.eventDict:
			if REQ_HTTP_HEADER_COOKIE in self.eventDict[REQ_HTTP_HEADER]:
				cookie = self.eventDict[REQ_HTTP_HEADER][REQ_HTTP_HEADER_COOKIE]
		return cookie
		
	def getQueryParams(self, inpList):
		retDict = {}
		if REQ_QUERY_STR_PARAM in self.eventDict:
			for eachParam in inpList:
				if eachParam in self.eventDict[REQ_QUERY_STR_PARAM]:
					retDict[eachParam] = urllib.parse.unquote(self.eventDict[REQ_QUERY_STR_PARAM][eachParam])
		return retDict

	def getAllQueryParam(self):
		retDict = {}
		for eachParam in self.eventDict[REQ_QUERY_STR_PARAM]:
			self.eventDict[eachParam] = self.eventDict[REQ_QUERY_STR_PARAM][eachParam]
		return retDict

	def isBase64(self):
		if REQ_IS_BASE64 in self.eventDict:
			return self.eventDict[REQ_IS_BASE64]

	def getBody(self):
		if REQ_BODY in self.eventDict:
			body = self.eventDict[REQ_BODY]
			if REQ_IS_BASE64 in self.eventDict:
				encodedFlag = self.eventDict[REQ_IS_BASE64]
				if encodedFlag:
					if REQ_CONTENT_TYPE in self.eventDict[REQ_HTTP_HEADER]: 
						cType = self.eventDict[REQ_HTTP_HEADER][REQ_CONTENT_TYPE]
						cType = cType.split(';')
						multipart = cType[0]
						if multipart == CONTENT_TYPE_MULTIPART:
							boundary = cType[1].lstrip()
							remKey = '--'+boundary.split('=')[1]
							body = base64.b64decode(self.eventDict[REQ_BODY]).decode()
							if body.endswith('--'):
								body = body[:-2]
							cleansedDict = {}
							body = body.split(remKey)
							for i in range(1, len(body)-1):
								data = body[i].split('\r\n')
								key = data[1].split('; name=')[1].strip('"')
								cleansedDict[key] = data[3]
							body = cleansedDict
			return body

	def getHeaderParm(self, parmList):
		retDict = {}
		# print ("header:", self.eventDict[REQ_HTTP_HEADER])
		if REQ_HTTP_HEADER in self.eventDict:
			for eachInp in parmList:
				if eachInp in self.eventDict[REQ_HTTP_HEADER]:
					retDict[eachInp] = self.eventDict[REQ_HTTP_HEADER][eachInp]
		return retDict

def main():
	None

if __name__ == "__main__":
	main()