moduleName = "fy_common_external_functions"
try:
    import sys
    from fy_common_internal_functions import *
    from fy_login_defines import *
    from fy_common_api_keys_values import *
except Exception as e:
    print ("ERR : %s : %s : %s" % (moduleName, "Could not import module", e))
    sys.exit()

def createHtmlRedirectScriptWithGetParams(keyValuesDict,redirectUrl = LOGIN_PAGE_URL_1,newTabFlag=0,callingFuncName=""):
    funcName = "createHtmlRedirectScriptWithGetParams"
    try:
        import urllib
        finalUrl = redirectUrl
        if len(keyValuesDict) > 0:
            urlParams = urllib.urlencode(keyValuesDict)
            finalUrl += "?"
            finalUrl += urlParams

        returnVariable = """<html><script type = "text/javascript">window.location = "%s";</script></html>""" %(finalUrl)
        if newTabFlag == 1:
            returnVariable = """<html><script type = "text/javascript">window.open("%s","_blank").focus();</script></html>""" %(finalUrl)
        return returnVariable
    except Exception as e:
        logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName,
                      callingFuncName, e, ERROR_C_UNKNOWN,keyValuesDict,redirectUrl)
        return """<html><script type = "text/javascript">window.location = "%s?%s=%s";</script></html>"""\
               %(LOGIN_PAGE_URL_1, API_K_MSG, ERROR_M_LOGIN_UNKNOWN_ERROR_1)

def createHtmlStatusMessage(messageToBeDisplayed, alertType = HTML_MSG_TYPE_NEUTRAL,callingFuncName=""):
    funcName = "createHtmlStatusMessage"
    try:
        if alertType == "":
            alertType = HTML_MSG_TYPE_NEUTRAL
        if alertType == HTML_MSG_TYPE_NEUTRAL:
            htmlMsg = """<div class='alert alert-info'>%s</div>""" %(messageToBeDisplayed)
        elif alertType == HTML_MSG_TYPE_SUCCESS:
            htmlMsg = """<div class='alert alert-success'>%s</div>""" %(messageToBeDisplayed)
        elif alertType == HTML_MSG_TYPE_FAIL:
            htmlMsg = """<div class='alert alert-danger'>%s</div>""" % (messageToBeDisplayed)
        elif alertType == HTML_MSG_TYPE_WARNING:
            htmlMsg = """<div class='alert alert-warning'>%s</div>""" % (messageToBeDisplayed)
        else:
            htmlMsg = ""
        return htmlMsg
    except Exception as e:
        logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, e,ERROR_C_UNKNOWN, messageToBeDisplayed, alertType)
        return """<div class='alert alert-warning'></div>"""

def createUrlParamsString(keyValuesDict, callingFuncName = ""):
    funcName = "createUrlParamsString"
    try:
        import urllib
        finalString = ""
        if len(keyValuesDict) > 0:
            urlParams = urllib.parse.urlencode(keyValuesDict)
            finalString += "?"
            finalString += urlParams
        return finalString
    except Exception as e:
        logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, e,ERROR_C_UNKNOWN, keyValuesDict)
        return ""

def createSimplePopup(urlForPopup,tabName,width=800,height=600,callingFuncName=""):
    funcName = "createSimplePopup"
    try:
        retScript = """
        <html><script type = "text/javascript">
            window.open("%s","%s", "width=%s,height=%s");
        </script></html>
        """ %(urlForPopup,tabName,width,height)
        return retScript
    except Exception as e:
        logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, e, ERROR_C_UNKNOWN,urlForPopup,tabName)
        return ""


def main():
    None

if __name__ == "__main__":
    main()