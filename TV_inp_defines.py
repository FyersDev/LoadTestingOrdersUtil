#!/usr/bin/env python
# Header
TV_HEADER_AUTHZATN		= "Authorization"

## /accounts/{accountId}/state
TV_INP_LOCALE			= "locale"

## /accounts/{accountId}/orders POST
TV_INP_ORDER_INSTR 		= "instrument"
TV_INP_ORDER_QTY		= "qty"
TV_INP_ORDER_SIDE		= "side"
TV_INP_ORDER_TYPE		= "type"
TV_INP_ORDER_LIMIT_P	= "limitPrice"
TV_INP_ORDER_STOP_P 	= "stopPrice"
TV_INP_ORDER_DURATN_TY	= "durationType"
TV_INP_ORDER_DYRATN_TI	= "durationDateTime"
TV_INP_ORDER_STOP_L 	= "stopLoss"
TV_INP_ORDER_TAKE_PROF	= "takeProfit"

TV_INP_ORDER_SIDE_VAL 	= ["BUY", "SELL"]
TV_INP_ORDER_TYPE_VAL 	= ["MARKET", "STOP", "LIMIT", "STOPLIMIT"]

## /accounts/{accountId}/ordersHistory
TV_INP_MAX_COUNT		= "maxCount"
TV_INP_ORDER_HIST_MAX_CNT= "maxCount"