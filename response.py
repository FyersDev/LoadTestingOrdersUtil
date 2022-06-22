#!/usr/bin/env python
import sys, time, os, json
import bottle
import base64
from io import BytesIO
import gzip

RESP_STATUS_CODE_STR					= "statusCode"
RESP_STATUS_DESCR_STR					= "statusDescription"
RESP_IS_BASE64_ENCODE_STR				= "isBase64Encoded"
RESP_HEADERS_STR 						= "headers"
RESP_HEADERS_CONT_TYPE_STR 				= "Content-Type"
RESP_BODY_STR 							= "body"
RESP_CONTENT_TYPE_TEXT_HTML				= "text/html; charset=utf-8"
RESP_CONTENT_TYPE_JSON  				= "application/json"
RESP_CONTENT_ENCODING                   = "Content-Encoding"
RESP_GZIP                               = "gzip"

class Response(object):
	"""
	Response object that ALB is expecting. Default set to 400.
	"""
	def __init__(self):
		self.resp = {
						RESP_STATUS_CODE_STR		: 400,
						RESP_STATUS_DESCR_STR 		: "400 ERROR",
						RESP_IS_BASE64_ENCODE_STR	: False,
						RESP_HEADERS_STR			: {
														RESP_HEADERS_CONT_TYPE_STR: RESP_CONTENT_TYPE_JSON
														},
						RESP_BODY_STR				: "Unknown"
					}

	def setResp(self, httpCode = 200, httpCodeStr = "200 OK", respBody = ""):
		"""
		Set success response
		"""
		self.resp[RESP_STATUS_CODE_STR] 	= httpCode
		self.resp[RESP_STATUS_DESCR_STR] 	= httpCodeStr
		self.resp[RESP_BODY_STR] 			= respBody

	def setError(self, httpCode = 500, httpCodeStr = "500 ERROR", respBody = ""):
		"""
		Set error response
		"""
		self.resp[RESP_STATUS_CODE_STR] 	= httpCode
		self.resp[RESP_STATUS_DESCR_STR] 	= httpCodeStr
		self.resp[RESP_BODY_STR] 			= respBody

	def setContentType(self, contType):
		"""
		Set content type of the response
		"""
		self.resp[RESP_HEADERS_STR][RESP_HEADERS_CONT_TYPE_STR] = contType
	
	def setRespBody(self, body):
		"""
		Set response body
		"""
		self.resp[RESP_BODY_STR] = body

	def setHeader(self, hKey, hVal):
		"""
		Set header values
		"""
		self.resp[RESP_HEADERS_STR][hKey] = hVal

	def __dict__(self):
		if isinstance(self.resp[RESP_BODY_STR], dict):
			self.resp[RESP_BODY_STR] = json.dumps(self.resp[RESP_BODY_STR])
		return self.resp
	
	def __call__(self):
		if isinstance(self.resp[RESP_BODY_STR], dict):
			if 'gzip' in bottle.request.headers.get('Accept-Encoding', ''):
				bottle.response.headers[RESP_CONTENT_ENCODING] = RESP_GZIP
				gzip_payload = zip_payload(json.dumps(self.resp[RESP_BODY_STR]))
				self.resp[RESP_BODY_STR] = gzip_payload
			else:
				self.resp[RESP_BODY_STR] = json.dumps(self.resp[RESP_BODY_STR])
		bottle.response.content_type = RESP_CONTENT_TYPE_JSON
		bottle.response.status = self.resp[RESP_STATUS_CODE_STR]
		return self.resp[RESP_BODY_STR]
		
	def __str__(self):
		return json.dumps(self.resp)


def zip_payload(payload: str) -> bytes:
    btsio = BytesIO()
    g = gzip.GzipFile(fileobj=btsio, mode='w')
    g.write(bytes(payload, 'utf8'))
    g.close()
    return btsio.getvalue()


def main():
	None

if __name__ == "__main__":
	main()