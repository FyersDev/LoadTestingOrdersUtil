import bottle
import json
import sys
import urllib.parse as urlparse

import fyers_funct as fy_fun

sys.path.append("./")
module_name = "bottle_app"
try:
    # Custom modules
    import request as req
    import response as res

except Exception as e:
    print("ERR : %s : %s : %s" % (module_name, "Could not import module", e))
    sys.exit()

################################################ PATH DEFINES ##########################################################
# TRADING VIEW
TV_PATH_V1 = "/tv/v1"

TV_PATH_AUTHORIZE = "/authorize"
TV_PATH_CONFIG = "/config"
TV_PATH_ACCOUNTS = "/accounts"
TV_PATH_ACCOUNTS_RESTID_STATE = "/accounts/REST-ID/state"
TV_PATH_ACCOUNTS_RESTID_ORDERS = "/accounts/REST-ID/orders"
TV_PATH_ACCOUNTS_RESTID_ORDERS_RESTID = "/accounts/REST-ID/orders/REST-ID"
TV_PATH_ACCOUNTS_RESTID_ORDERSHISTORY = "/accounts/REST-ID/ordersHistory"
TV_PATH_ACCOUNTS_RESTID_POSITIONS = "/accounts/REST-ID/positions"
TV_PATH_ACCOUNTS_RESTID_POSITIONS_RESTID = "/accounts/REST-ID/positions/REST-ID"
TV_PATH_ACCOUNTS_RESTID_EXECUTIONS = "/accounts/REST-ID/executions"
TV_PATH_ACCOUNTS_RESTID_INSTRUMENTS = "/accounts/REST-ID/instruments"
TV_PATH_MAPPING = "/mapping"
TV_PATH_SYMBOLINFO = "/symbol_info"
TV_PATH_HISTORY = "/history"
TV_PATH_QUOTES = "/quotes"
TV_PATH_STREAMING = "/streaming"

# FY-TRADE
# For Fyers functions
FY_PATH_V1 = "/fy/v1"
FY_PATH_V2 = "/fy/v2"
FY_PATH_MOBILE = "/fy/mobile"

# For mobile testing functions
FY_PATH_BETA_V1 = "/fybeta/v1"

# For mobile
FY_PATH_DEV_MOBILE = "/fydev/mobile"
FY_PATH_DEV_V1 = "/fydev/v1"

FY_PATH_FUNDS = "/funds"
FY_PATH_FUNDS_DETAILS = "/funds/details"
FY_PATH_HOLDINGS = "/holdings"
FY_PATH_LOGOUT = "/logout"
FY_PATH_MINQUANTITY = "/minquantity"
FY_PATH_ORDERS = "/orders"
FY_PATH_ORDERS_DETAILS = "/orders/details"
FY_PATH_POSITIONS = "/positions"
FY_PATH_EXIT_POSITIONS = "/exit_positions"
FY_PATH_SNAPSHOT = "/snapshot"
FY_PATH_SYMBOLS = "/symbols"
FY_PATH_TRADEBOOK = "/tradebook"
FY_PATH_VALIDATE = "/validate"
FY_PATH_VALIDATE_DETAILS = "/validate/details"
FY_PATH_VALIDATE_BO = "/validate/BO"
FY_PATH_VALIDATE_SSO = "/validate/SSO"
FY_PATH_WATCHLIST = "/watchlist"
FY_PATH_WATCHLIST_WEB = "/watchlist/web"
FY_PATH_GALLERY = "/gallery"
FY_PATH_AUTH = "/auth"
FY_PATH_CHANGEPWD = "/changepwd"
FY_PATH_FORGOTPWD = "/forgotpwd"
FY_PATH_RESETPWD = "/resetpwd"
FY_PATH_UNLOCK = "/unlock"
FY_PATH_FUNDTX_V1_VIEW = "/fundtx/v1/view"
FY_PATH_FUNDTX_V1_ADDFUNDS = "/fundtx/v1/addfunds"
FY_PATH_FUNDTX_V1_BANKDETAILS = "/fundtx/v1/bankdetails"
FY_PATH_FUNDTX_V1_MARGINUTILIZED = "/fundtx/v1/marginutilized"
FY_PATH_FUNDTX_V2_ADDFUNDS = "/fundtx/v2/addfunds"
FY_PATH_MOBILEAUTH = "/mobileauth"
FY_PATH_LOGIN = "/login"
FY_PATH_SIMPLIFIEDREG = "/simplifiedReg"
FY_PATH_APPVER = "/appVer"
FY_PATH_PUSHNOTI_REGISTER = "/PushNoti/register"
FY_PATH_GET_PROFILE = "/get_profile"
FY_PATH_GUESTUSER_REGISTER = "/guestUser/register"
FY_PATH_GUESTUSER_VALIDATE = "/guestUser/validate"
FY_PATH_APPRATING = "/appRating"
FY_PATH_MARGIN_V1 = "/margin/v1"
FY_PATH_TIMESTAMP = "/timestamp"
FY_PATH_BASKETS = "/baskets"
FY_PATH_BASKETS_ITEMS = "/baskets/items"
FY_PATH_BASKETS_EXECUTE = "/baskets/execute"
FY_PATH_BASKETS_RESET = "/baskets/reset"
FY_PATH_ADMIN_ORDERS = "/admin/orders"
FY_PATH_ADMIN_POSITIONS = "/admin/positions"
FY_PATH_ADMIN_HOLDINGS = "/admin/holdings"
FY_PATH_ADMIN_FUNDS = "/admin/funds"
FY_PATH_ADMIN_TRADES = "/admin/trades"
FY_PATH_ADMIN_ALLUSERS = "/admin/allusers"
FY_PATH_EDIS_TPIN = "/edis/tpin"
FY_PATH_EDIS_INDEX = "/edis/index"
FY_PATH_EDIS_DETAILS = "/edis/details"
FY_PATH_EDIS_INQUIRY = "/edis/inquiry"
########################################################################################################################

app = bottle.app()
resp = res.Response()


def enable_cors(fn):
    def _enable_cors(*args, **kwargs):
        # set CORS headers
        bottle.response.headers["Access-Control-Allow-Origin"] = "*"
        bottle.response.headers["Access-Control-Allow-Methods"] = "*"
        bottle.response.headers[
            "Access-Control-Allow-Headers"
        ] = "Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token, Authorization"

        if bottle.request.method != "OPTIONS":
            # calling function
            return fn(*args, **kwargs)

    return _enable_cors


def process_input_request(fn):
    def inner(*args, **kwargs):
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
            return fn(reqObj)
        except Exception as e:
            print(e)
            bottle.response.status = 500
            return bottle.response

    return inner


@app.get("/health_check")
def health_check():
    return "200"


############################################ TRADING-VIEW ##############################################################
@app.route(TV_PATH_V1 + TV_PATH_AUTHORIZE, method=["POST", "OPTIONS"])
@enable_cors
@process_input_request
def api_tvAuthorizePOST(body):
    result = fy_fun.tvAuthorizePOST(body, resp)
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


@app.route(TV_PATH_V1 + TV_PATH_CONFIG, method=["GET", "OPTIONS"])
@enable_cors
@process_input_request
def api_tvConfigGET(body):
    result = fy_fun.tvConfigGET(body, resp)
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


@app.route(TV_PATH_V1 + TV_PATH_ACCOUNTS, method=["GET", "OPTIONS"])
@enable_cors
@process_input_request
def api_tvAccGET(body):
    result = fy_fun.tvAccGET(body, resp)
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


@app.route(TV_PATH_V1 + TV_PATH_ACCOUNTS_RESTID_STATE, method=["GET", "OPTIONS"])
@enable_cors
@process_input_request
def api_tvAccStateGET(body):
    result = fy_fun.tvAccStateGET(body, resp)
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


@app.route(TV_PATH_V1 + TV_PATH_ACCOUNTS_RESTID_ORDERS, method=["GET", "OPTIONS"])
@enable_cors
@process_input_request
def api_tvAccOrdersGET(body):
    result = fy_fun.tvAccOrdersGET(body, resp)
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


@app.route(TV_PATH_V1 + TV_PATH_ACCOUNTS_RESTID_ORDERS, method=["POST", "OPTIONS"])
@enable_cors
@process_input_request
def api_tvAccOrdersPOST(body):
    result = fy_fun.tvAccOrdersPOST(body, resp)
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


@app.route(TV_PATH_V1 + TV_PATH_ACCOUNTS_RESTID_ORDERS_RESTID, method=["GET", "OPTIONS"])
@enable_cors
@process_input_request
def api_tvAccOrderIdGET(body):
    result = fy_fun.tvAccOrderIdGET(body, resp)
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


@app.route(TV_PATH_V1 + TV_PATH_ACCOUNTS_RESTID_ORDERS_RESTID, method=["PUT", "OPTIONS"])
@enable_cors
@process_input_request
def api_tvAccOrderIdPUT(body):
    result = fy_fun.tvAccOrderIdPUT(body, resp)
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


@app.route(TV_PATH_V1 + TV_PATH_ACCOUNTS_RESTID_ORDERS_RESTID, method=["DELETE", "OPTIONS"])
@enable_cors
@process_input_request
def api_tvAccOrderIdDEL(body):
    result = fy_fun.tvAccOrderIdDEL(body, resp)
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


@app.route(TV_PATH_V1 + TV_PATH_ACCOUNTS_RESTID_ORDERSHISTORY, method=["GET", "OPTIONS"])
@enable_cors
@process_input_request
def api_tvAccOrdersHistGET(body):
    result = fy_fun.tvAccOrdersHistGET(body, resp)
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


@app.route(TV_PATH_V1 + TV_PATH_ACCOUNTS_RESTID_POSITIONS, method=["GET", "OPTIONS"])
@enable_cors
@process_input_request
def api_tvAccPosnGET(body):
    result = fy_fun.tvAccPosnGET(body, resp)
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


@app.route(TV_PATH_V1 + TV_PATH_ACCOUNTS_RESTID_POSITIONS_RESTID, method=["GET", "OPTIONS"])
@enable_cors
@process_input_request
def api_tvAccPosnIdGET(body):
    result = fy_fun.tvAccPosnIdGET(body, resp)
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


@app.route(TV_PATH_V1 + TV_PATH_ACCOUNTS_RESTID_POSITIONS_RESTID, method=["PUT", "OPTIONS"])
@enable_cors
@process_input_request
def api_tvAccPosnIdPUT(body):
    result = fy_fun.tvAccPosnIdPUT(body, resp)
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


@app.route(TV_PATH_V1 + TV_PATH_ACCOUNTS_RESTID_POSITIONS_RESTID, method=["DELETE", "OPTIONS"])
@enable_cors
@process_input_request
def api_tvAccPosnIdDEL(body):
    result = fy_fun.tvAccPosnIdDEL(body, resp)
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


@app.route(TV_PATH_V1 + TV_PATH_ACCOUNTS_RESTID_EXECUTIONS, method=["GET", "OPTIONS"])
@enable_cors
@process_input_request
def api_tvAccExecGET(body):
    result = fy_fun.tvAccExecGET(body, resp)
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


@app.route(TV_PATH_V1 + TV_PATH_ACCOUNTS_RESTID_INSTRUMENTS, method=["GET", "OPTIONS"])
@enable_cors
@process_input_request
def api_tvAccInstruGET(body):
    result = fy_fun.tvAccInstruGET(body, resp)
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


@app.route(TV_PATH_V1 + TV_PATH_ACCOUNTS_RESTID_INSTRUMENTS, method=["GET", "OPTIONS"])
@enable_cors
@process_input_request
def api_tvAccInstruGET(body):
    result = fy_fun.tvAccInstruGET(body, resp)
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


@app.route(TV_PATH_V1 + TV_PATH_MAPPING, method=["GET", "OPTIONS"])
@enable_cors
@process_input_request
def api_tvMappingGET(body):
    result = fy_fun.tvMappingGET(body, resp)
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


@app.route(TV_PATH_V1 + TV_PATH_SYMBOLINFO, method=["GET", "OPTIONS"])
@enable_cors
@process_input_request
def api_tvSymInfoGET(body):
    result = fy_fun.tvSymInfoGET(body, resp)
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


@app.route(TV_PATH_V1 + TV_PATH_HISTORY, method=["GET", "OPTIONS"])
@enable_cors
@process_input_request
def api_tvHistGET(body):
    result = fy_fun.tvHistGET(body, resp)
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


@app.route(TV_PATH_V1 + TV_PATH_QUOTES, method=["GET", "OPTIONS"])
@enable_cors
@process_input_request
def api_tvQuotesGET(body):
    result = fy_fun.tvQuotesGET(body, resp)
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


@app.route(TV_PATH_V1 + TV_PATH_STREAMING, method=["GET", "OPTIONS"])
@enable_cors
@process_input_request
def api_tvStreamingGET(body):
    result = fy_fun.tvStreamingGET(body, resp)
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


############################################## FY_TRADE ################################################################
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
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


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
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


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
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


@app.route(FY_PATH_V1 + FY_PATH_LOGOUT, method=["POST", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_LOGOUT, method=["POST", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_LOGOUT, method=["POST", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_LOGOUT, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_LOGOUT, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_LOGOUT, method=["POST", "OPTIONS"])
@enable_cors
@process_input_request
def api_logout(body):
    result = fy_fun.fyLogoutPost(body, resp)
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


@app.route(FY_PATH_V1 + FY_PATH_MINQUANTITY, method=["GET", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_MINQUANTITY, method=["GET", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_MINQUANTITY, method=["GET", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_MINQUANTITY, method=["GET", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_MINQUANTITY, method=["GET", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_MINQUANTITY, method=["GET", "OPTIONS"])
@enable_cors
@process_input_request
def api_minquantity(body):
    result = fy_fun.fyMinQtyGET(body, resp)
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


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
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


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
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


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
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


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
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


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
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


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
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


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
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


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
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


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
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


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
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


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
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


@app.route(FY_PATH_V1 + FY_PATH_VALIDATE, method=["GET", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_VALIDATE, method=["GET", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_VALIDATE, method=["GET", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_VALIDATE, method=["GET", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_VALIDATE, method=["GET", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_VALIDATE, method=["GET", "OPTIONS"])
@enable_cors
@process_input_request
def api_fyValidateGET(body):
    result = fy_fun.fyValidateGET(body, resp)
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


@app.route(FY_PATH_V1 + FY_PATH_VALIDATE_DETAILS, method=["GET", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_VALIDATE_DETAILS, method=["GET", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_VALIDATE_DETAILS, method=["GET", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_VALIDATE_DETAILS, method=["GET", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_VALIDATE_DETAILS, method=["GET", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_VALIDATE_DETAILS, method=["GET", "OPTIONS"])
@enable_cors
@process_input_request
def api_fyValidateDetailsGET(body):
    result = fy_fun.fyValidateDetailsGET(body, resp)
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


@app.route(FY_PATH_V1 + FY_PATH_VALIDATE_BO, method=["GET", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_VALIDATE_BO, method=["GET", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_VALIDATE_BO, method=["GET", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_VALIDATE_BO, method=["GET", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_VALIDATE_BO, method=["GET", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_VALIDATE_BO, method=["GET", "OPTIONS"])
@enable_cors
@process_input_request
def api_BOAuth(body):
    result = fy_fun.BOAuth(body, resp)
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


@app.route(FY_PATH_V1 + FY_PATH_VALIDATE_SSO, method=["POST", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_VALIDATE_SSO, method=["POST", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_VALIDATE_SSO, method=["POST", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_VALIDATE_SSO, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_VALIDATE_SSO, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_VALIDATE_SSO, method=["POST", "OPTIONS"])
@enable_cors
@process_input_request
def api_MobileLogin(body):
    result = fy_fun.MobileLogin(body, resp)
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


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
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


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
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


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
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


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
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


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
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


@app.route(FY_PATH_V1 + FY_PATH_GALLERY, method=["GET", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_GALLERY, method=["GET", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_GALLERY, method=["GET", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_GALLERY, method=["GET", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_GALLERY, method=["GET", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_GALLERY, method=["GET", "OPTIONS"])
@enable_cors
@process_input_request
def api_fySnapShotGalleryGET(body):
    result = fy_fun.fySnapShotGalleryGET(body, resp)
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


@app.route(FY_PATH_V1 + FY_PATH_GALLERY, method=["DELETE", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_GALLERY, method=["DELETE", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_GALLERY, method=["DELETE", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_GALLERY, method=["DELETE", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_GALLERY, method=["DELETE", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_GALLERY, method=["DELETE", "OPTIONS"])
@enable_cors
@process_input_request
def api_fySnapShotGalleryDELETE(body):
    result = fy_fun.fySnapShotGalleryDELETE(body, resp)
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


@app.route(FY_PATH_V1 + FY_PATH_AUTH, method=["POST", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_AUTH, method=["POST", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_AUTH, method=["POST", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_AUTH, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_AUTH, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_AUTH, method=["POST", "OPTIONS"])
@enable_cors
@process_input_request
def api_fyLoginAuthPOST(body):
    result = fy_fun.fyLoginAuthPOST(body, resp)
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


@app.route(FY_PATH_V1 + FY_PATH_CHANGEPWD, method=["POST", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_CHANGEPWD, method=["POST", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_CHANGEPWD, method=["POST", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_CHANGEPWD, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_CHANGEPWD, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_CHANGEPWD, method=["POST", "OPTIONS"])
@enable_cors
@process_input_request
def api_fyChangePwdPOST(body):
    result = fy_fun.fyChangePwdPOST(body, resp)
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


@app.route(FY_PATH_V1 + FY_PATH_FORGOTPWD, method=["POST", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_FORGOTPWD, method=["POST", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_FORGOTPWD, method=["POST", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_FORGOTPWD, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_FORGOTPWD, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_FORGOTPWD, method=["POST", "OPTIONS"])
@enable_cors
@process_input_request
def api_fyForgotPwdPOST(body):
    result = fy_fun.fyForgotPwdPOST(body, resp)
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


@app.route(FY_PATH_V1 + FY_PATH_RESETPWD, method=["POST", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_RESETPWD, method=["POST", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_RESETPWD, method=["POST", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_RESETPWD, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_RESETPWD, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_RESETPWD, method=["POST", "OPTIONS"])
@enable_cors
@process_input_request
def api_fyResetPwdPOST(body):
    result = fy_fun.fyResetPwdPOST(body, resp)
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


@app.route(FY_PATH_V1 + FY_PATH_UNLOCK, method=["POST", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_UNLOCK, method=["POST", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_UNLOCK, method=["POST", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_UNLOCK, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_UNLOCK, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_UNLOCK, method=["POST", "OPTIONS"])
@enable_cors
@process_input_request
def api_fyUnlockPOST(body):
    result = fy_fun.fyUnlockPOST(body, resp)
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


@app.route(FY_PATH_V1 + FY_PATH_FUNDTX_V1_VIEW, method=["POST", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_FUNDTX_V1_VIEW, method=["POST", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_FUNDTX_V1_VIEW, method=["POST", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_FUNDTX_V1_VIEW, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_FUNDTX_V1_VIEW, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_FUNDTX_V1_VIEW, method=["POST", "OPTIONS"])
@enable_cors
@process_input_request
def api_fundTxView(body):
    result = fy_fun.fundTxView(body, resp)
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


@app.route(FY_PATH_V1 + FY_PATH_FUNDTX_V1_ADDFUNDS, method=["POST", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_FUNDTX_V1_ADDFUNDS, method=["POST", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_FUNDTX_V1_ADDFUNDS, method=["POST", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_FUNDTX_V1_ADDFUNDS, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_FUNDTX_V1_ADDFUNDS, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_FUNDTX_V1_ADDFUNDS, method=["POST", "OPTIONS"])
@enable_cors
@process_input_request
def api_fundTxAddFunds(body):
    result = fy_fun.fundTxAddFunds(body, resp)
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


@app.route(FY_PATH_V1 + FY_PATH_FUNDTX_V1_BANKDETAILS, method=["POST", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_FUNDTX_V1_BANKDETAILS, method=["POST", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_FUNDTX_V1_BANKDETAILS, method=["POST", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_FUNDTX_V1_BANKDETAILS, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_FUNDTX_V1_BANKDETAILS, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_FUNDTX_V1_BANKDETAILS, method=["POST", "OPTIONS"])
@enable_cors
@process_input_request
def api_fundTxBankDetails(body):
    result = fy_fun.fundTxBankDetails(body, resp)
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


@app.route(FY_PATH_V1 + FY_PATH_FUNDTX_V1_MARGINUTILIZED, method=["POST", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_FUNDTX_V1_MARGINUTILIZED, method=["POST", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_FUNDTX_V1_MARGINUTILIZED, method=["POST", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_FUNDTX_V1_MARGINUTILIZED, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_FUNDTX_V1_MARGINUTILIZED, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_FUNDTX_V1_MARGINUTILIZED, method=["POST", "OPTIONS"])
@enable_cors
@process_input_request
def api_fundTxMarginUtil(body):
    result = fy_fun.fundTxMarginUtil(body, resp)
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


@app.route(FY_PATH_V1 + FY_PATH_FUNDTX_V2_ADDFUNDS, method=["POST", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_FUNDTX_V2_ADDFUNDS, method=["POST", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_FUNDTX_V2_ADDFUNDS, method=["POST", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_FUNDTX_V2_ADDFUNDS, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_FUNDTX_V2_ADDFUNDS, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_FUNDTX_V2_ADDFUNDS, method=["POST", "OPTIONS"])
@enable_cors
@process_input_request
def api_fundTxAddFundsv2(body):
    result = fy_fun.fundTxAddFundsv2(body, resp)
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


@app.route(FY_PATH_V1 + FY_PATH_MOBILEAUTH, method=["POST", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_MOBILEAUTH, method=["POST", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_MOBILEAUTH, method=["POST", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_MOBILEAUTH, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_MOBILEAUTH, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_MOBILEAUTH, method=["POST", "OPTIONS"])
@enable_cors
@process_input_request
def api_fyMobileAuthId(body):
    result = fy_fun.fyMobileAuthId(body, resp)
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


@app.route(FY_PATH_V1 + FY_PATH_LOGIN, method=["POST", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_LOGIN, method=["POST", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_LOGIN, method=["POST", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_LOGIN, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_LOGIN, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_LOGIN, method=["POST", "OPTIONS"])
@enable_cors
@process_input_request
def api_fyMobileLogin(body):
    result = fy_fun.fyMobileLogin(body, resp)
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


@app.route(FY_PATH_V1 + FY_PATH_SIMPLIFIEDREG, method=["POST", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_SIMPLIFIEDREG, method=["POST", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_SIMPLIFIEDREG, method=["POST", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_SIMPLIFIEDREG, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_SIMPLIFIEDREG, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_SIMPLIFIEDREG, method=["POST", "OPTIONS"])
@enable_cors
@process_input_request
def api_fySimplifiedRegister(body):
    result = fy_fun.fySimplifiedRegister(body, resp)
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


@app.route(FY_PATH_V1 + FY_PATH_APPVER, method=["POST", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_APPVER, method=["POST", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_APPVER, method=["POST", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_APPVER, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_APPVER, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_APPVER, method=["POST", "OPTIONS"])
@enable_cors
@process_input_request
def api_fyAddAppVersion(body):
    result = fy_fun.fyAddAppVersion(body, resp)
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


@app.route(FY_PATH_V1 + FY_PATH_PUSHNOTI_REGISTER, method=["POST", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_PUSHNOTI_REGISTER, method=["POST", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_PUSHNOTI_REGISTER, method=["POST", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_PUSHNOTI_REGISTER, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_PUSHNOTI_REGISTER, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_PUSHNOTI_REGISTER, method=["POST", "OPTIONS"])
@enable_cors
@process_input_request
def api_fyNotiRegister(body):
    result = fy_fun.fyNotiRegister(body, resp)
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


@app.route(FY_PATH_V1 + FY_PATH_GET_PROFILE, method=["GET", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_GET_PROFILE, method=["GET", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_GET_PROFILE, method=["GET", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_GET_PROFILE, method=["GET", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_GET_PROFILE, method=["GET", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_GET_PROFILE, method=["GET", "OPTIONS"])
@enable_cors
@process_input_request
def api_fyGetProfile(body):
    result = fy_fun.fyGetProfile(body, resp)
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


@app.route(FY_PATH_V1 + FY_PATH_GUESTUSER_REGISTER, method=["POST", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_GUESTUSER_REGISTER, method=["POST", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_GUESTUSER_REGISTER, method=["POST", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_GUESTUSER_REGISTER, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_GUESTUSER_REGISTER, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_GUESTUSER_REGISTER, method=["POST", "OPTIONS"])
@enable_cors
@process_input_request
def api_fyGuestRegister(body):
    result = fy_fun.fyGuestRegister(body, resp)
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


@app.route(FY_PATH_V1 + FY_PATH_GUESTUSER_VALIDATE, method=["POST", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_GUESTUSER_VALIDATE, method=["POST", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_GUESTUSER_VALIDATE, method=["POST", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_GUESTUSER_VALIDATE, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_GUESTUSER_VALIDATE, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_GUESTUSER_VALIDATE, method=["POST", "OPTIONS"])
@enable_cors
@process_input_request
def api_fyGuestValidate(body):
    result = fy_fun.fyGuestValidate(body, resp)
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


@app.route(FY_PATH_V1 + FY_PATH_APPRATING, method=["POST", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_APPRATING, method=["POST", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_APPRATING, method=["POST", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_APPRATING, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_APPRATING, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_APPRATING, method=["POST", "OPTIONS"])
@enable_cors
@process_input_request
def api_fyUserRatingApp(body):
    result = fy_fun.fyUserRatingApp(body, resp)
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


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
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


@app.route(FY_PATH_V1 + FY_PATH_TIMESTAMP, method=["GET", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_TIMESTAMP, method=["GET", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_TIMESTAMP, method=["GET", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_TIMESTAMP, method=["GET", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_TIMESTAMP, method=["GET", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_TIMESTAMP, method=["GET", "OPTIONS"])
@enable_cors
@process_input_request
def api_fyGetTimestamp(body):
    result = fy_fun.fyGetTimestamp(body, resp)
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


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
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


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
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


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
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


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
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


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
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


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
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


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
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


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
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


@app.route(FY_PATH_V1 + FY_PATH_ADMIN_ORDERS, method=["GET", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_ADMIN_ORDERS, method=["GET", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_ADMIN_ORDERS, method=["GET", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_ADMIN_ORDERS, method=["GET", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_ADMIN_ORDERS, method=["GET", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_ADMIN_ORDERS, method=["GET", "OPTIONS"])
@enable_cors
@process_input_request
def api_fyTechAdminOrderbook(body):
    result = fy_fun.fyTechAdminOrderbook(body, resp)
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


@app.route(FY_PATH_V1 + FY_PATH_ADMIN_POSITIONS, method=["GET", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_ADMIN_POSITIONS, method=["GET", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_ADMIN_POSITIONS, method=["GET", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_ADMIN_POSITIONS, method=["GET", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_ADMIN_POSITIONS, method=["GET", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_ADMIN_POSITIONS, method=["GET", "OPTIONS"])
@enable_cors
@process_input_request
def api_fyTechAdminPositions(body):
    result = fy_fun.fyTechAdminPositions(body, resp)
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


@app.route(FY_PATH_V1 + FY_PATH_ADMIN_HOLDINGS, method=["GET", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_ADMIN_HOLDINGS, method=["GET", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_ADMIN_HOLDINGS, method=["GET", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_ADMIN_HOLDINGS, method=["GET", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_ADMIN_HOLDINGS, method=["GET", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_ADMIN_HOLDINGS, method=["GET", "OPTIONS"])
@enable_cors
@process_input_request
def api_fyTechAdminHoldings(body):
    result = fy_fun.fyTechAdminHoldings(body, resp)
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


@app.route(FY_PATH_V1 + FY_PATH_ADMIN_FUNDS, method=["GET", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_ADMIN_FUNDS, method=["GET", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_ADMIN_FUNDS, method=["GET", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_ADMIN_FUNDS, method=["GET", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_ADMIN_FUNDS, method=["GET", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_ADMIN_FUNDS, method=["GET", "OPTIONS"])
@enable_cors
@process_input_request
def api_fyTechAdminFunds(body):
    result = fy_fun.fyTechAdminFunds(body, resp)
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


@app.route(FY_PATH_V1 + FY_PATH_ADMIN_TRADES, method=["GET", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_ADMIN_TRADES, method=["GET", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_ADMIN_TRADES, method=["GET", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_ADMIN_TRADES, method=["GET", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_ADMIN_TRADES, method=["GET", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_ADMIN_TRADES, method=["GET", "OPTIONS"])
@enable_cors
@process_input_request
def api_fyTechAdminTrades(body):
    result = fy_fun.fyTechAdminTrades(body, resp)
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


@app.route(FY_PATH_V1 + FY_PATH_ADMIN_ALLUSERS, method=["POST", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_ADMIN_ALLUSERS, method=["POST", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_ADMIN_ALLUSERS, method=["POST", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_ADMIN_ALLUSERS, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_ADMIN_ALLUSERS, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_ADMIN_ALLUSERS, method=["POST", "OPTIONS"])
@enable_cors
@process_input_request
def api_fyGetLoggedUsers(body):
    result = fy_fun.fyGetLoggedUsers(body, resp)
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


@app.route(FY_PATH_V1 + FY_PATH_EDIS_TPIN, method=["POST", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_EDIS_TPIN, method=["POST", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_EDIS_TPIN, method=["POST", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_EDIS_TPIN, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_EDIS_TPIN, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_EDIS_TPIN, method=["POST", "OPTIONS"])
@enable_cors
@process_input_request
def api_fyEdisBoTpinGenPOST(body):
    result = fy_fun.fyEdisBoTpinGenPOST(body, resp)
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


@app.route(FY_PATH_V1 + FY_PATH_EDIS_INDEX, method=["POST", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_EDIS_INDEX, method=["POST", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_EDIS_INDEX, method=["POST", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_EDIS_INDEX, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_EDIS_INDEX, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_EDIS_INDEX, method=["POST", "OPTIONS"])
@enable_cors
@process_input_request
def api_fyEdisIndexPOST(body):
    result = fy_fun.fyEdisIndexPOST(body, resp)
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


@app.route(FY_PATH_V1 + FY_PATH_EDIS_DETAILS, method=["POST", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_EDIS_DETAILS, method=["POST", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_EDIS_DETAILS, method=["POST", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_EDIS_DETAILS, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_EDIS_DETAILS, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_EDIS_DETAILS, method=["POST", "OPTIONS"])
@enable_cors
@process_input_request
def api_fyEdisDetailsPOST(body):
    result = fy_fun.fyEdisDetailsPOST(body, resp)
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


@app.route(FY_PATH_V1 + FY_PATH_EDIS_INQUIRY, method=["POST", "OPTIONS"])
@app.route(FY_PATH_V2 + FY_PATH_EDIS_INQUIRY, method=["POST", "OPTIONS"])
@app.route(FY_PATH_MOBILE + FY_PATH_EDIS_INQUIRY, method=["POST", "OPTIONS"])
@app.route(FY_PATH_BETA_V1 + FY_PATH_EDIS_INQUIRY, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_MOBILE + FY_PATH_EDIS_INQUIRY, method=["POST", "OPTIONS"])
@app.route(FY_PATH_DEV_V1 + FY_PATH_EDIS_INQUIRY, method=["POST", "OPTIONS"])
@enable_cors
@process_input_request
def api_fyEdisInquiryPOST(body):
    result = fy_fun.fyEdisInquiryPOST(body, resp)
    resp.setResp(httpCode=200, httpCodeStr="200 OK", respBody=result)
    return resp()


if __name__ == "__main__":
    print("Server starting ...")
    # bottle.run(app, host='0.0.0.0', port=8080)
    from cheroot.wsgi import Server as CherryPyWSGIServer
    server = CherryPyWSGIServer(('0.0.0.0', 8080), app, numthreads=40)
    server.start()
