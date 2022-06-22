moduleName = "fy_trading_internal_functions_funds_details"
try:
    import sys

    from fy_base_defines import LOG_STATUS_ERROR_1
    from fy_base_success_error_codes import ERROR_C_1, SUCCESS_C_1, \
     ERROR_C_UNKNOWN
    from fy_data_and_trade_defines import BEWARE_CLIENTS_LIST    
    from fy_trading_defines import API_OMS_K_TOKEN_ID_2, API_OMS_K_CLIENT_ID_1, \
     API_OMS_K_REQ_SOURCE, API_OMS_K_ROW_START, API_OMS_V_PAGINATION_START, \
     API_OMS_K_ROW_END, API_OMS_V_PAGINATION_END, REQ_URL_OMS_MAIN_2, \
     API_OMS_REQ_PATH_FUNDS_LIMIT_DET

    from fy_base_functions import logEntryFunc2
    from fy_connections import connectRedis
    from fy_trading_internal_functions import INTERNAL_getToken_checkStatus, \
     INTERNAL_createAndSendOmsRequest, INTERNAL_decryptOmsResponse

except Exception as e:
    print("ERR : %s : %s : %s" % (moduleName, "Could not import module", e))
    sys.exit()


def INTERNAL_limitDetails(tokenHash, callingFuncName='',userIp=""):
    funcName = 'INTERNAL_limitDetails'
    try:
        localMemory = connectRedis(callingFuncName=callingFuncName)
        tokenHash = str(tokenHash)
        fyTokenList = INTERNAL_getToken_checkStatus(tokenHash, localMemory=localMemory, callingFuncName=callingFuncName)
        if fyTokenList[0] == ERROR_C_1:
            return fyTokenList
        fyId = fyTokenList[1][0]
        omsTokenId = fyTokenList[1][1]
        aesKey = fyTokenList[1][2]
        appId       = fyTokenList[2]
        source      = fyTokenList[3]

        if fyId in BEWARE_CLIENTS_LIST:
            return [SUCCESS_C_1, [], ""]

        paramsForEncryption = {API_OMS_K_TOKEN_ID_2: omsTokenId, API_OMS_K_CLIENT_ID_1: fyId, API_OMS_K_REQ_SOURCE: source, API_OMS_K_ROW_START: API_OMS_V_PAGINATION_START,
                               API_OMS_K_ROW_END: API_OMS_V_PAGINATION_END}
        urlForRequest = REQ_URL_OMS_MAIN_2 + API_OMS_REQ_PATH_FUNDS_LIMIT_DET
        sendOMSReq = INTERNAL_createAndSendOmsRequest(fyId, omsTokenId, aesKey, paramsForEncryption, urlForRequest, callingFuncName=callingFuncName,userIp=userIp)
        if sendOMSReq[0] == ERROR_C_1:
            return sendOMSReq
        omsResponse = sendOMSReq[1]

        readOmsResFuncRet = INTERNAL_decryptOmsResponse(omsResponse, aesKey, callingFuncName=callingFuncName)
        if readOmsResFuncRet[0] == ERROR_C_1:
            return readOmsResFuncRet
        detailsResponse = readOmsResFuncRet[1]

        if len(detailsResponse) > 0:
            pendingEqCNC = {'id':1, 'groupId':1, 'title': 'Pending Equity CNC', "Amount":detailsResponse['Pending Equity CNC']}
            pendingEqmarg = {'id':2, 'groupId':1, 'title': 'Pending Equity Margin', "Amount":detailsResponse['Pending Equity Margin']}
            pendingEqInt = {'id':3, 'groupId':1, 'title': 'Pending Equity Intraday', "Amount":detailsResponse['Pending Equity Intraday']}
            pendingEqHyb = {'id':4, 'groupId':1, 'title': 'Pending Equity Hybrid', 'Amount':detailsResponse["Pending Equity Hybrid"]}
            pendingEqMTF = {'id':5, 'groupId':1, 'title': 'Pending Equity MTF', 'Amount':detailsResponse['Pending Equity MTF']}
            executedEqCNC = {'id':6, 'groupId':1, 'title': 'Executed Equity CNC', "Amount":detailsResponse['Executed Equity CNC']}
            executedEqmarg = {'id':7, 'groupId':1, 'title': 'Executed Equity Margin', "Amount":detailsResponse['Executed Equity Margin']}
            executedEqInt = {'id':8, 'groupId':1, 'title': 'Executed Equity Intraday', "Amount":detailsResponse['Executed Equity Intraday']}
            executedEqHyb = {'id':9, 'groupId':1, 'title': 'Executed Equity Hybrid', 'Amount':detailsResponse['Executed Equity Hybrid']}
            executedEqMTF = {'id':10, 'groupId':1, 'title': 'Executed Equity MTF', 'Amount':detailsResponse['Executed Equity MTF']}
            coEqmarg = {'id':11, 'groupId':1, 'title': 'CO Equity', 'Amount':detailsResponse['CO Equity']}
            boEqmarg = {'id':12, 'groupId':1, 'title': 'BO Equity', 'Amount':detailsResponse['BO Equity']}
            totUtilEq = {'id':13, 'groupId':1, 'title': 'Total Utilised Amount Equity', 'Amount':detailsResponse['Total Utilised Amount Equity']}

            pendingDrvMarg = {'id':14, 'groupId':2, 'title':'Pending Derivative Margin', 'Amount':detailsResponse['Pending Derivative Margin']}
            pendingDrvInt = {'id':15, 'groupId':2, 'title':'Pending Derivative Intraday', 'Amount':detailsResponse['Pending Derivative Intraday']}
            executedDrvIntSpan = {'id':16, 'groupId':2, 'title':'Executed Derivative SPAN Intraday', 'Amount':detailsResponse['Executed Derivative SPAN Intraday']}
            executedDrvMrgSpan = {'id':17, 'groupId':2, 'title':'Executed Derivative SPAN Margin', 'Amount':detailsResponse['Executed Derivative SPAN Margin']}
            executedDrvExpoSpan = {'id':18, 'groupId':2, 'title':'Executed Derivative Exposure Intraday', 'Amount':detailsResponse['Executed Derivative Exposure Intraday']}
            executedDrvExpoMrgSpan = {'id':19, 'groupId':2, 'title':'Executed Derivative Exposure Margin', 'Amount':detailsResponse['Executed Derivative Exposure Margin']}
            coDrv = {'id':20, 'groupId':2, 'title':'CO Derivatives', 'Amount':detailsResponse['CO Derivatives']}
            boDrv = {'id':21, 'groupId':2, 'title':'BO Derivatives', 'Amount':detailsResponse['BO Derivatives']}
            totUtilDrv = {'id':22, 'groupId':2, 'title':'Total Utilised Amount Derivatives', 'Amount':detailsResponse['Total Utilised Amount Derivatives']}

            pendingCurrMrg = {'id':23, 'groupId':3, 'title':'Pending Currency Margin', 'Amount':detailsResponse['Pending Currency Margin']}
            pendingCurrInt = {'id':24, 'groupId':3, 'title':'Pending Currency Intraday', 'Amount':detailsResponse['Pending Currency Intraday']}
            executedCurrSpanInt = {'id':25, 'groupId':3, 'title':'Executed Currency SPAN Intraday', 'Amount':detailsResponse['Executed Currency SPAN Intraday']}
            executedCurrSpanMrg = {'id':26, 'groupId':3, 'title':'Executed Currency SPAN Margin', 'Amount':detailsResponse['Executed Currency SPAN Margin']}
            executedCurrExpoSpanInt = {'id':27, 'groupId':3, 'title':'Executed Currency Exposure Intraday', 'Amount':detailsResponse['Executed Currency Exposure Intraday']}
            executedCurrExpoSpanMrg = {'id':28, 'groupId':3, 'title':'Executed Currency Exposure Margin', 'Amount':detailsResponse['Executed Currency Exposure Margin']}
            coCurr = {'id':29, 'groupId':3, 'title':'CO Currency', 'Amount':detailsResponse['CO Currency']}
            boCurr = {'id':30, 'groupId':3, 'title':'BO Currency', 'Amount':detailsResponse['BO Currency']}
            totUtilCurr = {'id':31, 'groupId':3, 'title':'Total Utilised Amount Currency', 'Amount':detailsResponse['Total Utilised Amount Currency']}

            pendingCommMrg = {'id':32, 'groupId':4, 'title':'Pending Commodity Margin', 'Amount':detailsResponse['Pending Commodity Margin']}
            pendingCommInt = {'id':33, 'groupId':4, 'title':'Pending Commodity Intraday', 'Amount':detailsResponse['Pending Commodity Intraday']}
            executedCommSpanInt = {'id':34, 'groupId':4, 'title':'Executed Commodity SPAN Intraday', 'Amount':detailsResponse['Executed Commodity SPAN Intraday']}
            executedCommSpanMrg = {'id':35, 'groupId':4, 'title':'Executed Commodity SPAN Margin', 'Amount':detailsResponse['Executed Commodity SPAN Margin']}
            executedCommExpoInt = {'id':36, 'groupId':4, 'title':'Executed Commodity Exposure Intraday', 'Amount':detailsResponse['Executed Commodity Exposure Intraday']}
            executedCommExpoMrg = {'id':37, 'groupId':4, 'title':'Executed Commodity Exposure Margin', 'Amount':detailsResponse['Executed Commodity Exposure Margin']}
            coComm = {'id':38, 'groupId':4, 'title':'CO Commodity', 'Amount':detailsResponse['CO Commodity']}
            boComm = {'id':39, 'groupId':4, 'title':'BO Commodity', 'Amount':detailsResponse['BO Commodity']}
            totUtilComm = {'id':40, 'groupId':4, 'title':'Total Utilised Amount Commodity', 'Amount':detailsResponse['Total Utilised Amount Commodity']}

            eqNse = {'id':41, 'groupId':5, 'title':'Receivables Equity NSE', 'Amount':detailsResponse['Receivables Equity NSE']}
            eqBse = {'id':42, 'groupId':5, 'title':'Receivables Equity BSE', 'Amount':detailsResponse['Receivables Equity BSE']}

            eqIntRpnl = {'id':43, 'groupId':6, 'title':'Realised P&L Equity Intraday', 'Amount':detailsResponse['Realised P&L Equity Intraday']}
            eqMrgRpnl = {'id':44, 'groupId':6, 'title':'Realised P&L Equity Margin', 'Amount':detailsResponse['Realised P&L Equity Margin']}
            eqCncRpnl = {'id':45, 'groupId':6, 'title':'Realised P&L Equity CNC', 'Amount':detailsResponse['Realised P&L Equity CNC']}
            eqCoRpnl = {'id':46, 'groupId':6, 'title':'Realised P&L Equity CO', 'Amount':detailsResponse['Realised P&L Equity CO']}
            eqBocRpnl = {'id':47, 'groupId':6, 'title':'Realised P&L Equity BO', 'Amount':detailsResponse['Realised P&L Equity BO']}
            eqHybRpnl = {'id':48, 'groupId':6, 'title':'Realised P&L Equity Hybrid', 'Amount':detailsResponse['Realised P&L Equity Hybrid']}
            eqMtfRpnl = {'id':49, 'groupId':6, 'title':'Realised P&L Equity MTF', 'Amount':detailsResponse['Realised P&L Equity MTF']}

            drvIntRpnl = {'id':50, 'groupId':6, 'title':'Realised P&L Derivatives Intraday', 'Amount':detailsResponse['Realised P&L Derivatives Intraday']}
            drvMrgRpnl = {'id':51, 'groupId':6, 'title':'Realised P&L Derivatives Margin', 'Amount':detailsResponse['Realised P&L Derivatives Margin']}
            drvCoRpnl = {'id':52, 'groupId':6, 'title':'Realised P&L Derivative CO', 'Amount':detailsResponse['Realised P&L Derivative CO']}
            drvBoRpnl = {'id':53, 'groupId':6, 'title':'Realised P&L Derivative BO', 'Amount':detailsResponse['Realised P&L Derivative BO']}

            currIntRpnl = {'id':54, 'groupId':6, 'title':'Realised P&L Currency Intraday', 'Amount':detailsResponse['Realised P&L Currency Intraday']}
            currMrgRpnl = {'id':55, 'groupId':6, 'title':'Realised P&L Currency Margin', 'Amount':detailsResponse['Realised P&L Currency Margin']}
            currCoRpnl = {'id':56, 'groupId':6, 'title':'Realised P&L Currency CO', 'Amount':detailsResponse['Realised P&L Currency CO']}
            currBoRpnl = {'id':57, 'groupId':6, 'title':'Realised P&L Currency BO', 'Amount':detailsResponse['Realised P&L Currency BO']}

            commIntRpnl = {'id':58, 'groupId':6, 'title':'Realised P&L Commodity Intraday', 'Amount':detailsResponse['Realised P&L Commodity Intraday']}
            commMrgRpnl = {'id':59, 'groupId':6, 'title':'Realised P&L Commodity Margin', 'Amount':detailsResponse['Realised P&L Commodity Margin']}
            commCoRpnl = {'id':60, 'groupId':6, 'title':'Realised P&L Commodity CO', 'Amount':detailsResponse['Realised P&L Commodity CO']}
            commBoRpnl = {'id':61, 'groupId':6, 'title':'Realised P&L Commodity BO', 'Amount':detailsResponse['Realised P&L Commodity BO']}

            optBuyDrvInt = {'id':62, 'groupId':7, 'title':'Option Buy Value Derivative Intraday', 'Amount':detailsResponse['Option Buy Value Derivative Intraday']}
            optBuyDrvMrg = {'id':63, 'groupId':7, 'title':'Option Buy Value Derivative Margin', 'Amount':detailsResponse['Option Buy Value Derivative Margin']}
            optBuyCurrInt = {'id':64, 'groupId':7, 'title':'Option Buy Value Currency Intraday', 'Amount':detailsResponse['Option Buy Value Currency Intraday']}
            optBuyCurrMrg = {'id':65, 'groupId':7, 'title':'Option Buy Value Currency Margin', 'Amount':detailsResponse['Option Buy Value Currency Margin']}
            optBuyCommInt = {'id':66, 'groupId':7, 'title':'Option Buy Value Commodity Intraday', 'Amount':detailsResponse['Option Buy Value Commodity Intraday']}
            optBuyCommMrg = {'id':67, 'groupId':7, 'title':'Option Buy Value Commodity Margin', 'Amount':detailsResponse['Option Buy Value Commodity Margin']}
            optSellPreDrv = {'id':68, 'groupId':8, 'title':'Option Sell Premium Received Derivative', 'Amount':detailsResponse['Option Sell Premium Received Derivative']}
            optSellPreCur = {'id':69, 'groupId':8, 'title':'Option Sell Premium Received Currency', 'Amount':detailsResponse['Option Sell Premium Received Currency']}
            optSellPreCom = {'id':70, 'groupId':8, 'title':'Option Sell Premium Received Commodity', 'Amount':detailsResponse['Option Sell Premium Received Commodity']}

            retList = [pendingEqCNC,pendingEqmarg,pendingEqInt,pendingEqHyb,pendingEqMTF,executedEqCNC,executedEqmarg,executedEqInt,executedEqHyb,executedEqMTF,coEqmarg,boEqmarg,totUtilEq,pendingDrvMarg,pendingDrvInt,executedDrvIntSpan,executedDrvMrgSpan,executedDrvExpoSpan,executedDrvExpoMrgSpan,coDrv,boDrv,totUtilDrv,pendingCurrMrg,pendingCurrInt,executedCurrSpanInt,executedCurrSpanMrg,executedCurrExpoSpanInt,executedCurrExpoSpanMrg,coCurr,boCurr,totUtilCurr,pendingCommMrg,pendingCommInt,executedCommSpanInt,executedCommSpanMrg,executedCommExpoInt,executedCommExpoMrg,coComm,boComm,totUtilComm,eqNse,eqBse,eqIntRpnl,eqMrgRpnl,eqCncRpnl,eqCoRpnl,eqBocRpnl,eqHybRpnl,eqMtfRpnl,drvIntRpnl,drvMrgRpnl,drvCoRpnl,drvBoRpnl,currIntRpnl,currMrgRpnl,currCoRpnl,currBoRpnl,commIntRpnl,commMrgRpnl,commCoRpnl,commBoRpnl,optBuyDrvInt,optBuyDrvMrg,optBuyCurrInt,optBuyCurrMrg,optBuyCommInt,optBuyCommMrg,optSellPreDrv,optSellPreCur,optSellPreCom]
            return [SUCCESS_C_1, retList, ""]
        else:
            return [ERROR_C_1, "", ""]
    except Exception as e:
        logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, e,
                      ERROR_C_UNKNOWN)
        return [ERROR_C_1, ERROR_C_UNKNOWN, e]


def main():
    None


if __name__ == "__main__":
    main()
