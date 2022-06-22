#!/usr/bin/env python
import sys, os, json, time
import fy_config.fy_base_api_keys_values as fyBaseKV
import fy_config.fy_base_success_error_codes as fyBaseSEC

FYERS_DOMAIN_EXCEPTION_LIST = ["fyers.in","tradingview.com", "in.tradingview.com", "tradingview.in", "domyinc.net"]
FYERS_VALID_SUB_DOMAIN_LIST	= ["trade", "betatrade", "thematic", "dev", "test", "api"]

def validateDomain(inputDomain, fyValid = True):
	"""
	[Function]	: 	Validate the input domain given
	[Input]		: 	inputDomain	-> String contain input domian
					fyValid		-> Validate all the Fyers subdomains. 
	"""
	inputDomain = str(inputDomain)
	# if not isinstance(inputDomain, str):
	# 	return {fyBaseKV.API_K_STATUS:fyBaseKV.API_V_ERROR, fyBaseKV.API_K_CODE:fyBaseSEC.ERROR_C_INV_INP, fyBaseKV.API_K_MSG:"Invalid input type"}
	
	if inputDomain.lower().startswith("http://"):
		inputDomain = inputDomain[7:]
	if inputDomain.lower().startswith("https://"):
		inputDomain = inputDomain[8:]
	domCName = inputDomain
	if inputDomain.find('/') >= 0:
		domCName = inputDomain[:inputDomain.find('/')]
	domCName = domCName.lower()
	## Check for main domain and all the other allowed domains
	if domCName in FYERS_DOMAIN_EXCEPTION_LIST:
		return {fyBaseKV.API_K_STATUS:fyBaseKV.API_V_SUCCESS, fyBaseKV.API_K_DATA_1:domCName, fyBaseKV.API_K_MSG:""}
	
	## Validate sub domains
	# print "inputDomain:", domCName
	splitDomain = domCName.split(".")
	# print "splitDomain:", splitDomain
	if len(splitDomain) < 3:
		return {fyBaseKV.API_K_STATUS:fyBaseKV.API_V_ERROR, fyBaseKV.API_K_CODE:fyBaseSEC.ERROR_C_INV_INP, fyBaseKV.API_K_MSG:"Invalid subdomain: %s"%(domCName)}
	
	## the suffix has to be *.fyers.in
	if splitDomain[-2] != "fyers" and splitDomain[-1] != "in":
		return {fyBaseKV.API_K_STATUS:fyBaseKV.API_V_ERROR, fyBaseKV.API_K_CODE:fyBaseSEC.ERROR_C_INV_INP, fyBaseKV.API_K_MSG:"Invalid subdomain: %s"%(domCName)}
	
	## Success of all the subdomain of fyers
	if fyValid:
		return {fyBaseKV.API_K_STATUS:fyBaseKV.API_V_SUCCESS, fyBaseKV.API_K_DATA_1:domCName, fyBaseKV.API_K_MSG:""}

	## Validate only specific sub domains
	subDomain = '.'.join(splitDomain[:-2])
	# print "subDomain:", subDomain
	if subDomain in FYERS_VALID_SUB_DOMAIN_LIST:
		return {fyBaseKV.API_K_STATUS:fyBaseKV.API_V_SUCCESS, fyBaseKV.API_K_DATA_1:domCName, fyBaseKV.API_K_MSG:""}
		
	return {fyBaseKV.API_K_STATUS:fyBaseKV.API_V_ERROR, fyBaseKV.API_K_CODE:fyBaseSEC.ERROR_C_INV_INP, fyBaseKV.API_K_MSG:"Invalid subdomain: %s"%(domCName)}

def main():
	None

if __name__ == "__main__":
	main()