import threading
import bottle
import json
import os
import sys
import time
import uuid
import urllib.parse as urlparse
import symbolmaster_handler
import fyers_funct as fy_fun
import gc

sys.path.append("./")
module_name = "bottle_watchlist_app"
try:
    # Custom modules
    import request as req
    import response as res
    from fy_config.fy_base_functions import get_logger
    # from fy_config.fy_baskets_external_functions import fy_margin_basket

except Exception as e:
    print("ERR : %s : %s : %s" % (module_name, "Could not import module", e))
    sys.exit()

################################################ PATH DEFINES ##########################################################
# FY-TRADE
# For Fyers functions
FY_PATH_V1 = "/fy/v1"
FY_PATH_V2 = "/fy/v2"
FY_PATH_MOBILE = "/fy/mobile"
# FY_PATH_V1 = "/voyager/staging"
# FY_PATH_V2 = "/voyager/staging"
# FY_PATH_MOBILE = "/voyager/staging"

# For mobile testing functions
FY_PATH_BETA_V1 = "/fybeta/v1"
# FY_PATH_BETA_V1 = "/voyager/staging"

# For mobile
FY_PATH_DEV_MOBILE = "/fydev/mobile"
FY_PATH_DEV_V1 = "/fydev/v1"
# FY_PATH_DEV_MOBILE = "/voyager/staging"
# FY_PATH_DEV_V1 = "/voyager/staging"

FY_PATH_WATCHLIST = "/watchlist"
FY_PATH_WATCHLIST_WEB = "/watchlist/web"
FY_PATH_FUNDS = "/funds"
FY_PATH_FUNDS_DETAILS = "/funds/details"
FY_PATH_HOLDINGS = "/holdings"
# FY_PATH_MINQUANTITY = "/minquantity"
FY_PATH_ORDERS = "/orders"
FY_PATH_ORDERS_DETAILS = "/orders/details"
FY_PATH_POSITIONS = "/positions"
FY_PATH_EXIT_POSITIONS = "/exit_positions"
FY_PATH_SNAPSHOT = "/snapshot"
FY_PATH_SYMBOLS = "/symbols"
FY_PATH_TRADEBOOK = "/tradebook"
FY_PATH_MARGIN_V1 = "/margin/v1"
# FY_PATH_VALIDATE = "/validate"
# FY_PATH_VALIDATE_DETAILS = "/validate/details"
# FY_PATH_VALIDATE_BO = "/validate/BO"
# FY_PATH_GALLERY = "/gallery"
# FY_PATH_GET_PROFILE = "/get_profile"
# FY_PATH_TIMESTAMP = "/timestamp"
FY_PATH_BASKETS = "/baskets"
FY_PATH_BASKETS_ITEMS = "/baskets/items"
FY_PATH_BASKETS_EXECUTE = "/baskets/execute"
FY_PATH_BASKETS_RESET = "/baskets/reset"
# FY_PATH_ADMIN_ORDERS = "/admin/orders"
# FY_PATH_ADMIN_POSITIONS = "/admin/positions"
# FY_PATH_ADMIN_HOLDINGS = "/admin/holdings"
# FY_PATH_ADMIN_FUNDS = "/admin/funds"
# FY_PATH_ADMIN_TRADES = "/admin/trades"

ALB_T2_VOYAGER = "/v/v1"
# ALB_T2_VOYAGER = "/voyager/staging"

########################################################################################################################
app = bottle.app()
resp = res.Response()


def enable_cors(fn):
    def _enable_cors(*args, **kwargs):
        # set CORS headers
        header_dict = {}
        for i in bottle.request.headers:
            header_dict[i] = bottle.request.headers[i]
        if "Origin" in header_dict:
            bottle.response.headers["Access-Control-Allow-Origin"] = header_dict["Origin"]
            bottle.response.headers["Access-Control-Allow-Credentials"] = "true"
        else:
            bottle.response.headers["Access-Control-Allow-Origin"] = "*"
        bottle.response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS,PATCH"
        bottle.response.headers[
            "Access-Control-Allow-Headers"
        ] = "Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token, Authorization"

        if bottle.request.method != "OPTIONS":
            # calling function
            return fn(*args, **kwargs)

    return _enable_cors


def process_input_request(fn):
    def inner(*args, **kwargs):
        logger = get_logger()
        start = time.time()
        logger.set_requestId(bottle.request.headers.get("X-Amzn-Trace-Id", f"{uuid.uuid4()}"))
        logger.info(f"{bottle.request.path} {bottle.request.method}", extra={"LOG_TYPE": "REQUEST_IN"})
        try:
            body = {
                "headers": {
                    "cookie": bottle.request.headers.get("cookie", ""),
                    "authorization": bottle.request.headers.get("Authorization", ""),
                    "user_ip": "",
                }
            }
            if bottle.request.method == "GET":
                qs = bottle.request.query_string
                if qs != "":
                    body["queryStringParameters"] = {}
                    qs = urlparse.parse_qsl(qs)
                    body["queryStringParameters"].update(dict(qs))
            elif bottle.request.method in ["POST", "PUT", "DELETE", "PATCH"]:
                content_type = bottle.request.headers.get("content-type", "")
                if content_type == "application/x-www-form-urlencoded":
                    qs = bottle.request.body.read()
                    if qs != "":
                        body["body"] = {}
                        qs = urlparse.parse_qsl(qs)
                        qs = dict(qs)
                        qs = {
                            x.decode("utf-8"): y.decode("utf-8") for x, y in qs.items()
                        }
                        body["body"].update(qs)
                else:
                    body["body"] = {}
                    body["body"].update(json.loads(bottle.request.body.read().decode("utf-8")))

            reqObj = req.Request(body)
            response = fn(reqObj)
            try:
                deco_resp = response
                if type(deco_resp) == dict:
                    if 's' in deco_resp:
                        if deco_resp['s'] == 'error':
                            logger.error(deco_resp, extra={"LOG_TYPE": "REQUEST_OUT_ERROR"})

            except Exception as e:
                logger.exception(e, extra={"LOG_TYPE": "REQUEST_OUT_ERROR_INVALID_JSON"})

            end = time.time()
            if end - start > 1:
                logger.info(end-start, extra={"LOG_TYPE": "RESPONSE_TIME"})

            logger.clear_data()
            return response

        except Exception as e:
            logger.exception(e, extra={"LOG_TYPE": "REQUEST_OUT_ERROR_EXCEPTION"})
            end = time.time()
            logger.info(end-start, extra={"LOG_TYPE": "RESPONSE_TIME"})
            bottle.response.status = 500
            logger.clear_data()

            return bottle.response

    return inner


@app.get("/health_check")
def health_check():
    print("healthy")
    gc.collect()
    return "200"


############################################## FY_TRADE ################################################################
# Watchlist APIs
@app.route(FY_PATH_V1 + FY_PATH_WATCHLIST, method=["GET", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_WATCHLIST, method=["GET", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_WATCHLIST, method=["GET", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_WATCHLIST, method=["GET", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_WATCHLIST, method=["GET", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_WATCHLIST, method=["GET", "OPTIONS"])
@enable_cors
@process_input_request
def api_fyWlGET(body):
    result = fy_fun.fyWlGET(body, resp)
    return result


@app.route(FY_PATH_V1 + FY_PATH_WATCHLIST, method=["POST", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_WATCHLIST, method=["POST", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_WATCHLIST, method=["POST", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_WATCHLIST, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_WATCHLIST, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_WATCHLIST, method=["POST", "OPTIONS"])
@enable_cors
@process_input_request
def api_fyWlPOST(body):
    result = fy_fun.fyWlPOST(body, resp)
    return result


@app.route(FY_PATH_V1 + FY_PATH_WATCHLIST, method=["DELETE", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_WATCHLIST, method=["DELETE", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_WATCHLIST, method=["DELETE", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_WATCHLIST, method=["DELETE", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_WATCHLIST, method=["DELETE", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_WATCHLIST, method=["DELETE", "OPTIONS"])
@enable_cors
@process_input_request
def api_fyWlDELETE(body):
    result = fy_fun.fyWlDELETE(body, resp)
    return result


@app.route(FY_PATH_V1 + FY_PATH_WATCHLIST, method=["PUT", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_WATCHLIST, method=["PUT", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_WATCHLIST, method=["PUT", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_WATCHLIST, method=["PUT", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_WATCHLIST, method=["PUT", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_WATCHLIST, method=["PUT", "OPTIONS"])
@enable_cors
@process_input_request
def api_fyWlPUT(body):
    result = fy_fun.fyWlPUT(body, resp)
    return result


@app.route(FY_PATH_V1 + FY_PATH_WATCHLIST_WEB, method=["GET", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_WATCHLIST_WEB, method=["GET", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_WATCHLIST_WEB, method=["GET", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_WATCHLIST_WEB, method=["GET", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_WATCHLIST_WEB, method=["GET", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_WATCHLIST_WEB, method=["GET", "OPTIONS"])
@enable_cors
@process_input_request
def api_fyWlGETWeb(body):
    result = fy_fun.fyWlGETWeb(body, resp)
    # return result
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


@app.route(FY_PATH_V1 + FY_PATH_WATCHLIST_WEB, method=["POST", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_WATCHLIST_WEB, method=["POST", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_WATCHLIST_WEB, method=["POST", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_WATCHLIST_WEB, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_WATCHLIST_WEB, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_WATCHLIST_WEB, method=["POST", "OPTIONS"])
@enable_cors
@process_input_request
def api_fyWlPOSTWeb(body):
    result = fy_fun.fyWlPOSTWeb(body, resp)
    # return result
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


@app.route(FY_PATH_V1 + FY_PATH_WATCHLIST_WEB, method=["DELETE", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_WATCHLIST_WEB, method=["DELETE", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_WATCHLIST_WEB, method=["DELETE", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_WATCHLIST_WEB, method=["DELETE", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_WATCHLIST_WEB, method=["DELETE", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_WATCHLIST_WEB, method=["DELETE", "OPTIONS"])
@enable_cors
@process_input_request
def api_fyWlDELETEWeb(body):
    result = fy_fun.fyWlDELETEWeb(body, resp)
    # return result
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


# All GET APIS
@app.route(FY_PATH_V1 + FY_PATH_FUNDS, method=["GET", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_FUNDS, method=["GET", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_FUNDS, method=["GET", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_FUNDS, method=["GET", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_FUNDS, method=["GET", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_FUNDS, method=["GET", "OPTIONS"])
@enable_cors
@process_input_request
def api_funds(body):
    result = fy_fun.fyFundsGET(body, resp)
    return result


@app.route(FY_PATH_V1 + FY_PATH_FUNDS_DETAILS, method=["GET", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_FUNDS_DETAILS, method=["GET", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_FUNDS_DETAILS, method=["GET", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_FUNDS_DETAILS, method=["GET", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_FUNDS_DETAILS, method=["GET", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_FUNDS_DETAILS, method=["GET", "OPTIONS"])
@enable_cors
@process_input_request
def api_funds_details(body):
    result = fy_fun.fyFundsDetailsGET(body, resp)
    return result


@app.route(FY_PATH_V1 + FY_PATH_HOLDINGS, method=["GET", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_HOLDINGS, method=["GET", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_HOLDINGS, method=["GET", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_HOLDINGS, method=["GET", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_HOLDINGS, method=["GET", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_HOLDINGS, method=["GET", "OPTIONS"])
@enable_cors
@process_input_request
def api_funds_details(body):
    result = fy_fun.fyHoldingsGET(body, resp)
    return result


# @app.route(FY_PATH_V1 + FY_PATH_MINQUANTITY, method=["GET", "OPTIONS"])
# @app.route(FY_PATH_V2 + FY_PATH_MINQUANTITY, method=["GET", "OPTIONS"])
# @app.route(FY_PATH_MOBILE + FY_PATH_MINQUANTITY, method=["GET", "OPTIONS"])
# @app.route(FY_PATH_BETA_V1 + FY_PATH_MINQUANTITY, method=["GET", "OPTIONS"])
# @app.route(FY_PATH_DEV_MOBILE + FY_PATH_MINQUANTITY, method=["GET", "OPTIONS"])
# @app.route(FY_PATH_DEV_V1 + FY_PATH_MINQUANTITY, method=["GET", "OPTIONS"])
# @enable_cors
# @process_input_request
# def api_minquantity(body):
#     result = fy_fun.fyMinQtyGET(body, resp)
#     resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
#     return resp()


@app.route(FY_PATH_V1 + FY_PATH_ORDERS, method=["GET", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_ORDERS, method=["GET", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_ORDERS, method=["GET", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_ORDERS, method=["GET", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_ORDERS, method=["GET", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_ORDERS, method=["GET", "OPTIONS"])
@enable_cors
@process_input_request
def api_fyOrdersGET(body):
    result = fy_fun.fyOrdersGET(body, resp)
    return result


@app.route(FY_PATH_V1 + FY_PATH_ORDERS, method=["POST", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_ORDERS, method=["POST", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_ORDERS, method=["POST", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_ORDERS, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_ORDERS, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_ORDERS, method=["POST", "OPTIONS"])
@enable_cors
@process_input_request
def api_fyOrdersPOST(body):
    result = fy_fun.fyOrdersPOST(body, resp)
    return result


@app.route(FY_PATH_V1 + FY_PATH_ORDERS, method=["PATCH", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_ORDERS, method=["PATCH", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_ORDERS, method=["PATCH", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_ORDERS, method=["PATCH", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_ORDERS, method=["PATCH", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_ORDERS, method=["PATCH", "OPTIONS"])
@enable_cors
@process_input_request
def api_fyOrdersPATCH(body):
    result = fy_fun.fyOrdersPATCH(body, resp)
    return result


@app.route(FY_PATH_V1 + FY_PATH_ORDERS, method=["DELETE", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_ORDERS, method=["DELETE", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_ORDERS, method=["DELETE", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_ORDERS, method=["DELETE", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_ORDERS, method=["DELETE", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_ORDERS, method=["DELETE", "OPTIONS"])
@enable_cors
@process_input_request
def api_fyOrdersDELETE(body):
    result = fy_fun.fyOrdersDELETE(body, resp)
    return result


@app.route(FY_PATH_V1 + FY_PATH_ORDERS_DETAILS, method=["GET", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_ORDERS_DETAILS, method=["GET", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_ORDERS_DETAILS, method=["GET", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_ORDERS_DETAILS, method=["GET", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_ORDERS_DETAILS, method=["GET", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_ORDERS_DETAILS, method=["GET", "OPTIONS"])
@enable_cors
@process_input_request
def api_fyOrderDetailsGET(body):
    result = fy_fun.fyOrderDetailsGET(body, resp)
    return result


@app.route(FY_PATH_V1 + FY_PATH_POSITIONS, method=["GET", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_POSITIONS, method=["GET", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_POSITIONS, method=["GET", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_POSITIONS, method=["GET", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_POSITIONS, method=["GET", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_POSITIONS, method=["GET", "OPTIONS"])
@enable_cors
@process_input_request
def api_fyPosGET(body):
    result = fy_fun.fyPosGET(body, resp)
    return result


@app.route(FY_PATH_V1 + FY_PATH_POSITIONS, method=["POST", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_POSITIONS, method=["POST", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_POSITIONS, method=["POST", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_POSITIONS, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_POSITIONS, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_POSITIONS, method=["POST", "OPTIONS"])
@enable_cors
@process_input_request
def api_fyPosPOST(body):
    result = fy_fun.fyPosPOST(body, resp)
    return result


@app.route(FY_PATH_V1 + FY_PATH_EXIT_POSITIONS, method=["POST", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_EXIT_POSITIONS, method=["POST", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_EXIT_POSITIONS, method=["POST", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_EXIT_POSITIONS, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_EXIT_POSITIONS, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_EXIT_POSITIONS, method=["POST", "OPTIONS"])
@enable_cors
@process_input_request
def api_fyExitPos(body):
    result = fy_fun.fyExitPos(body, resp)
    return result


@app.route(FY_PATH_V1 + FY_PATH_SNAPSHOT, method=["POST", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_SNAPSHOT, method=["POST", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_SNAPSHOT, method=["POST", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_SNAPSHOT, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_SNAPSHOT, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_SNAPSHOT, method=["POST", "OPTIONS"])
@enable_cors
@process_input_request
def api_fySnapshotPOST(body):
    result = fy_fun.fySnapshotPOST(body, resp)
    return result


@app.route(FY_PATH_V1 + FY_PATH_SYMBOLS, method=["GET", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_SYMBOLS, method=["GET", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_SYMBOLS, method=["GET", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_SYMBOLS, method=["GET", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_SYMBOLS, method=["GET", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_SYMBOLS, method=["GET", "OPTIONS"])
@enable_cors
@process_input_request
def api_fySymbolsGET(body):
    result = fy_fun.fySymbolsGET(body, resp)
    return result


@app.route(FY_PATH_V1 + FY_PATH_TRADEBOOK, method=["GET", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_TRADEBOOK, method=["GET", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_TRADEBOOK, method=["GET", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_TRADEBOOK, method=["GET", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_TRADEBOOK, method=["GET", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_TRADEBOOK, method=["GET", "OPTIONS"])
@enable_cors
@process_input_request
def api_fyTradebookGET(body):
    result = fy_fun.fyTradebookGET(body, resp)
    return result


# @app.route(FY_PATH_V1 + FY_PATH_VALIDATE, method=["GET", "OPTIONS"])
# @app.route(FY_PATH_V2 + FY_PATH_VALIDATE, method=["GET", "OPTIONS"])
# @app.route(FY_PATH_MOBILE + FY_PATH_VALIDATE, method=["GET", "OPTIONS"])
# @app.route(FY_PATH_BETA_V1 + FY_PATH_VALIDATE, method=["GET", "OPTIONS"])
# @app.route(FY_PATH_DEV_MOBILE + FY_PATH_VALIDATE, method=["GET", "OPTIONS"])
# @app.route(FY_PATH_DEV_V1 + FY_PATH_VALIDATE, method=["GET", "OPTIONS"])
# @enable_cors
# @process_input_request
# def api_fyValidateGET(body):
#     result = fy_fun.fyValidateGET(body, resp)
#     resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
#     return resp()


# @app.route(FY_PATH_V1 + FY_PATH_VALIDATE_DETAILS, method=["GET", "OPTIONS"])
# @app.route(FY_PATH_V2 + FY_PATH_VALIDATE_DETAILS, method=["GET", "OPTIONS"])
# @app.route(FY_PATH_MOBILE + FY_PATH_VALIDATE_DETAILS, method=["GET", "OPTIONS"])
# @app.route(FY_PATH_BETA_V1 + FY_PATH_VALIDATE_DETAILS, method=["GET", "OPTIONS"])
# @app.route(FY_PATH_DEV_MOBILE + FY_PATH_VALIDATE_DETAILS, method=["GET", "OPTIONS"])
# @app.route(FY_PATH_DEV_V1 + FY_PATH_VALIDATE_DETAILS, method=["GET", "OPTIONS"])
# @enable_cors
# @process_input_request
# def api_fyValidateDetailsGET(body):
#     result = fy_fun.fyValidateDetailsGET(body, resp)
#     resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
#     return resp()


# @app.route(FY_PATH_V1 + FY_PATH_VALIDATE_BO, method=["GET", "OPTIONS"])
# @app.route(FY_PATH_V2 + FY_PATH_VALIDATE_BO, method=["GET", "OPTIONS"])
# @app.route(FY_PATH_MOBILE + FY_PATH_VALIDATE_BO, method=["GET", "OPTIONS"])
# @app.route(FY_PATH_BETA_V1 + FY_PATH_VALIDATE_BO, method=["GET", "OPTIONS"])
# @app.route(FY_PATH_DEV_MOBILE + FY_PATH_VALIDATE_BO, method=["GET", "OPTIONS"])
# @app.route(FY_PATH_DEV_V1 + FY_PATH_VALIDATE_BO, method=["GET", "OPTIONS"])
# @enable_cors
# @process_input_request
# def api_BOAuth(body):
#     result = fy_fun.BOAuth(body, resp)
#     resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
#     return resp()


# @app.route(FY_PATH_V1 + FY_PATH_GALLERY, method=["GET", "OPTIONS"])
# @app.route(FY_PATH_V2 + FY_PATH_GALLERY, method=["GET", "OPTIONS"])
# @app.route(FY_PATH_MOBILE + FY_PATH_GALLERY, method=["GET", "OPTIONS"])
# @app.route(FY_PATH_BETA_V1 + FY_PATH_GALLERY, method=["GET", "OPTIONS"])
# @app.route(FY_PATH_DEV_MOBILE + FY_PATH_GALLERY, method=["GET", "OPTIONS"])
# @app.route(FY_PATH_DEV_V1 + FY_PATH_GALLERY, method=["GET", "OPTIONS"])
# @enable_cors
# @process_input_request
# def api_fySnapShotGalleryGET(body):
#     result = fy_fun.fySnapShotGalleryGET(body, resp)
#     resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
#     return resp()


# @app.route(FY_PATH_V1 + FY_PATH_GET_PROFILE, method=["GET", "OPTIONS"])
# @app.route(FY_PATH_V2 + FY_PATH_GET_PROFILE, method=["GET", "OPTIONS"])
# @app.route(FY_PATH_MOBILE + FY_PATH_GET_PROFILE, method=["GET", "OPTIONS"])
# @app.route(FY_PATH_BETA_V1 + FY_PATH_GET_PROFILE, method=["GET", "OPTIONS"])
# @app.route(FY_PATH_DEV_MOBILE + FY_PATH_GET_PROFILE, method=["GET", "OPTIONS"])
# @app.route(FY_PATH_DEV_V1 + FY_PATH_GET_PROFILE, method=["GET", "OPTIONS"])
# @enable_cors
# @process_input_request
# def api_fyGetProfile(body):
#     result = fy_fun.fyGetProfile(body, resp)
#     resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
#     return resp()


# @app.route(FY_PATH_V1 + FY_PATH_TIMESTAMP, method=["GET", "OPTIONS"])
# @app.route(FY_PATH_V2 + FY_PATH_TIMESTAMP, method=["GET", "OPTIONS"])
# @app.route(FY_PATH_MOBILE + FY_PATH_TIMESTAMP, method=["GET", "OPTIONS"])
# @app.route(FY_PATH_BETA_V1 + FY_PATH_TIMESTAMP, method=["GET", "OPTIONS"])
# @app.route(FY_PATH_DEV_MOBILE + FY_PATH_TIMESTAMP, method=["GET", "OPTIONS"])
# @app.route(FY_PATH_DEV_V1 + FY_PATH_TIMESTAMP, method=["GET", "OPTIONS"])
# @enable_cors
# @process_input_request
# def api_fyGetTimestamp(body):
#     result = fy_fun.fyGetTimestamp(body, resp)
#     resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
#     return resp()


@app.route(FY_PATH_V1 + FY_PATH_BASKETS, method=["GET", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_BASKETS, method=["GET", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_BASKETS, method=["GET", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_BASKETS, method=["GET", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_BASKETS, method=["GET", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_BASKETS, method=["GET", "OPTIONS"])
@enable_cors
@process_input_request
def api_fyGetBaskets(body):
    result = fy_fun.fyGetBaskets(body, resp)
    return result


@app.route(FY_PATH_V1 + FY_PATH_BASKETS, method=["POST", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_BASKETS, method=["POST", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_BASKETS, method=["POST", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_BASKETS, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_BASKETS, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_BASKETS, method=["POST", "OPTIONS"])
@enable_cors
@process_input_request
def api_fyCreateBasket(body):
    result = fy_fun.fyCreateBasket(body, resp)
    return result


@app.route(FY_PATH_V1 + FY_PATH_BASKETS, method=["PUT", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_BASKETS, method=["PUT", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_BASKETS, method=["PUT", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_BASKETS, method=["PUT", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_BASKETS, method=["PUT", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_BASKETS, method=["PUT", "OPTIONS"])
@enable_cors
@process_input_request
def api_fyCreateBasket(body):
    result = fy_fun.fyModifyBasket(body, resp)
    return result


@app.route(FY_PATH_V1 + FY_PATH_BASKETS, method=["DELETE", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_BASKETS, method=["DELETE", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_BASKETS, method=["DELETE", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_BASKETS, method=["DELETE", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_BASKETS, method=["DELETE", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_BASKETS, method=["DELETE", "OPTIONS"])
@enable_cors
@process_input_request
def api_fyDeleteBasket(body):
    result = fy_fun.fyDeleteBasket(body, resp)
    return result


@app.route(FY_PATH_V1 + FY_PATH_BASKETS_ITEMS, method=["POST", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_BASKETS_ITEMS, method=["POST", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_BASKETS_ITEMS, method=["POST", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_BASKETS_ITEMS, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_BASKETS_ITEMS, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_BASKETS_ITEMS, method=["POST", "OPTIONS"])
@enable_cors
@process_input_request
def api_fyAddItemToBasket(body):
    result = fy_fun.fyAddItemToBasket(body, resp)
    return result


@app.route(FY_PATH_V1 + FY_PATH_BASKETS_ITEMS, method=["PUT", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_BASKETS_ITEMS, method=["PUT", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_BASKETS_ITEMS, method=["PUT", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_BASKETS_ITEMS, method=["PUT", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_BASKETS_ITEMS, method=["PUT", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_BASKETS_ITEMS, method=["PUT", "OPTIONS"])
@enable_cors
@process_input_request
def api_fyModifyItemsInBasket(body):
    result = fy_fun.fyModifyItemsInBasket(body, resp)
    return result

@app.route(FY_PATH_V1 + FY_PATH_BASKETS_ITEMS, method=["DELETE", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_BASKETS_ITEMS, method=["DELETE", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_BASKETS_ITEMS, method=["DELETE", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_BASKETS_ITEMS, method=["DELETE", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_BASKETS_ITEMS, method=["DELETE", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_BASKETS_ITEMS, method=["DELETE", "OPTIONS"])
@enable_cors
@process_input_request
def api_fyDeleteItemFromBasket(body):
    result = fy_fun.fyDeleteItemFromBasket(body, resp)
    return result


@app.route(FY_PATH_V1 + FY_PATH_BASKETS_EXECUTE, method=["POST", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_BASKETS_EXECUTE, method=["POST", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_BASKETS_EXECUTE, method=["POST", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_BASKETS_EXECUTE, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_BASKETS_EXECUTE, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_BASKETS_EXECUTE, method=["POST", "OPTIONS"])
@enable_cors
@process_input_request
def api_fyExecuteBasket(body):
    result = fy_fun.fyExecuteBasket(body, resp)
    return result


@app.route(FY_PATH_V1 + FY_PATH_BASKETS_RESET, method=["POST", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_BASKETS_RESET, method=["POST", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_BASKETS_RESET, method=["POST", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_BASKETS_RESET, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_BASKETS_RESET, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_BASKETS_RESET, method=["POST", "OPTIONS"])
@enable_cors
@process_input_request
def api_fyResetBasket(body):
    result = fy_fun.fyResetBasket(body, resp)
    return result


# @app.route(FY_PATH_V1 + FY_PATH_ADMIN_ORDERS, method=["GET", "OPTIONS"])
# @app.route(FY_PATH_V2 + FY_PATH_ADMIN_ORDERS, method=["GET", "OPTIONS"])
# @app.route(FY_PATH_MOBILE + FY_PATH_ADMIN_ORDERS, method=["GET", "OPTIONS"])
# @app.route(FY_PATH_BETA_V1 + FY_PATH_ADMIN_ORDERS, method=["GET", "OPTIONS"])
# @app.route(FY_PATH_DEV_MOBILE + FY_PATH_ADMIN_ORDERS, method=["GET", "OPTIONS"])
# @app.route(FY_PATH_DEV_V1 + FY_PATH_ADMIN_ORDERS, method=["GET", "OPTIONS"])
# @enable_cors
# @process_input_request
# def api_fyTechAdminOrderbook(body):
#     result = fy_fun.fyTechAdminOrderbook(body, resp)
#     resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
#     return resp()


# @app.route(FY_PATH_V1 + FY_PATH_ADMIN_POSITIONS, method=["GET", "OPTIONS"])
# @app.route(FY_PATH_V2 + FY_PATH_ADMIN_POSITIONS, method=["GET", "OPTIONS"])
# @app.route(FY_PATH_MOBILE + FY_PATH_ADMIN_POSITIONS, method=["GET", "OPTIONS"])
# @app.route(FY_PATH_BETA_V1 + FY_PATH_ADMIN_POSITIONS, method=["GET", "OPTIONS"])
# @app.route(FY_PATH_DEV_MOBILE + FY_PATH_ADMIN_POSITIONS, method=["GET", "OPTIONS"])
# @app.route(FY_PATH_DEV_V1 + FY_PATH_ADMIN_POSITIONS, method=["GET", "OPTIONS"])
# @enable_cors
# @process_input_request
# def api_fyTechAdminPositions(body):
#     result = fy_fun.fyTechAdminPositions(body, resp)
#     resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
#     return resp()


# @app.route(FY_PATH_V1 + FY_PATH_ADMIN_HOLDINGS, method=["GET", "OPTIONS"])
# @app.route(FY_PATH_V2 + FY_PATH_ADMIN_HOLDINGS, method=["GET", "OPTIONS"])
# @app.route(FY_PATH_MOBILE + FY_PATH_ADMIN_HOLDINGS, method=["GET", "OPTIONS"])
# @app.route(FY_PATH_BETA_V1 + FY_PATH_ADMIN_HOLDINGS, method=["GET", "OPTIONS"])
# @app.route(FY_PATH_DEV_MOBILE + FY_PATH_ADMIN_HOLDINGS, method=["GET", "OPTIONS"])
# @app.route(FY_PATH_DEV_V1 + FY_PATH_ADMIN_HOLDINGS, method=["GET", "OPTIONS"])
# @enable_cors
# @process_input_request
# def api_fyTechAdminHoldings(body):
#     result = fy_fun.fyTechAdminHoldings(body, resp)
#     resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
#     return resp()


# @app.route(FY_PATH_V1 + FY_PATH_ADMIN_FUNDS, method=["GET", "OPTIONS"])
# @app.route(FY_PATH_V2 + FY_PATH_ADMIN_FUNDS, method=["GET", "OPTIONS"])
# @app.route(FY_PATH_MOBILE + FY_PATH_ADMIN_FUNDS, method=["GET", "OPTIONS"])
# @app.route(FY_PATH_BETA_V1 + FY_PATH_ADMIN_FUNDS, method=["GET", "OPTIONS"])
# @app.route(FY_PATH_DEV_MOBILE + FY_PATH_ADMIN_FUNDS, method=["GET", "OPTIONS"])
# @app.route(FY_PATH_DEV_V1 + FY_PATH_ADMIN_FUNDS, method=["GET", "OPTIONS"])
# @enable_cors
# @process_input_request
# def api_fyTechAdminFunds(body):
#     result = fy_fun.fyTechAdminFunds(body, resp)
#     resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
#     return resp()


# @app.route(FY_PATH_V1 + FY_PATH_ADMIN_TRADES, method=["GET", "OPTIONS"])
# @app.route(FY_PATH_V2 + FY_PATH_ADMIN_TRADES, method=["GET", "OPTIONS"])
# @app.route(FY_PATH_MOBILE + FY_PATH_ADMIN_TRADES, method=["GET", "OPTIONS"])
# @app.route(FY_PATH_BETA_V1 + FY_PATH_ADMIN_TRADES, method=["GET", "OPTIONS"])
# @app.route(FY_PATH_DEV_MOBILE + FY_PATH_ADMIN_TRADES, method=["GET", "OPTIONS"])
# @app.route(FY_PATH_DEV_V1 + FY_PATH_ADMIN_TRADES, method=["GET", "OPTIONS"])
# @enable_cors
# @process_input_request
# def api_fyTechAdminTrades(body):
#     result = fy_fun.fyTechAdminTrades(body, resp)
#     resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
#     return resp()

@app.route(FY_PATH_V1 + FY_PATH_MARGIN_V1, method=["POST", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_MARGIN_V1, method=["POST", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_MARGIN_V1, method=["POST", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_MARGIN_V1, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_MARGIN_V1, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_MARGIN_V1, method=["POST", "OPTIONS"])
@enable_cors
@process_input_request
def api_marginTxView(body):
    result = fy_fun.marginTxView(body, resp)
    return result


@app.route(ALB_T2_VOYAGER + "/baskets/margin", method=["POST", "OPTIONS"])
@enable_cors
@process_input_request
def api_place_order(body):
    # body["body"] = {"basketid": body["basketid"]}
    result = fy_fun.marginBasketPost(body, resp)
    return result

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Invalid request. Valid request 'python filename.py port_number cpu_affinity number_of_threads'")
        sys.exit()
    port_num = int(sys.argv[1])
    cpu_affinity = sys.argv[2]
    num_threads = int(sys.argv[3])

    pid = 0
    affinity = os.sched_getaffinity(pid)
    affinity_mask = {int(cpu_affinity)}
    os.sched_setaffinity(0, affinity_mask)

    symbolmaster_handler.download_data_s3()
    # t = threading.Thread(target=symbolmaster_handler.subscribe_for_updates)
    # t.start()
    print("Server starting ...")
    from cheroot.wsgi import Server as CherryPyWSGIServer
    server = CherryPyWSGIServer(('0.0.0.0', port_num), app, numthreads=num_threads)
    server.start()
