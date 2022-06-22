#!/usr/bin/env python
import lambda_defines as ld
import fyers_funct as fy_fun

TV_RESOURCE_MAPPING = {
	"authorize"	: {
		"POST"	: fy_fun.tvAuthorizePOST,
	},
	"config"	: {
		"GET"	:fy_fun.tvConfigGET,
	},
	"accounts"	: {
		"GET"	: fy_fun.tvAccGET,
		ld.URL_REST_ID_STR: {
			"state" : {
				"GET" : fy_fun.tvAccStateGET
			},
			"orders" : {
				"GET" : fy_fun.tvAccOrdersGET,
				"POST" : fy_fun.tvAccOrdersPOST,
				ld.URL_REST_ID_STR :{
					"GET" 	: fy_fun.tvAccOrderIdGET,
					"PUT" 	: fy_fun.tvAccOrderIdPUT,
					"DELETE" : fy_fun.tvAccOrderIdDEL,
				},
			},
			"ordersHistory" : {
				"GET" : fy_fun.tvAccOrdersHistGET,
			},
			"positions" : {
				"GET": fy_fun.tvAccPosnGET,
				ld.URL_REST_ID_STR : {
					"GET" : fy_fun.tvAccPosnIdGET,
					"PUT" : fy_fun.tvAccPosnIdPUT,
					"DELETE" : fy_fun.tvAccPosnIdDEL,
				},
			},
			"executions" : {
				"GET" : fy_fun.tvAccExecGET,
			},
			"instruments" : {
				"GET" : fy_fun.tvAccInstruGET,
			},
		},
	},
	"mapping" : {
		"GET" : fy_fun.tvMappingGET,
	},
	"symbol_info" : {
		"GET" : fy_fun.tvSymInfoGET,
	},
	"history" : {
		"GET" : fy_fun.tvHistGET,
	},
	"quotes" : {
		"GET" : fy_fun.tvQuotesGET,
	},
	"streaming" : {
		"GET" : fy_fun.tvStreamingGET,
	},
}

FY_TRADE_RESOURCE_MAPPING = {
	# "chart"	: {
	# 	"GET" 	: fy_fun.fyChartGET,
	# 	"POST"	: fy_fun.fyChartPOST,
	# 	"auth"	: {
	# 		"POST"	: fy_fun.fyChartAuthPOST,
	# 	},
	# 	# "popout"	: {
	# 	# 	"GET"	: fy_fun.fyChartPopoutGET,
	# 		# "POST"	: fy_fun.fyChartPopoutPOST,
	# 	# },
	# },
	"funds"	: {
		"GET"	: fy_fun.fyFundsGET,
		"details" : {
			"GET" : fy_fun.fyFundsDetailsGET,
		},
	},
	"holdings" 	: {
		"GET"	: fy_fun.fyHoldingsGET,
	},
	"logout"	: {
		"POST"	: fy_fun.fyLogoutPost,
	},
	"minquantity" : {
		"GET"	: fy_fun.fyMinQtyGET,
	},
	"orders"	: {
		"GET"	: fy_fun.fyOrdersGET,
		"POST"	: fy_fun.fyOrdersPOST,
		"PATCH"	: fy_fun.fyOrdersPATCH,
		"DELETE": fy_fun.fyOrdersDELETE,
		"details" : {
			"GET" : fy_fun.fyOrderDetailsGET,
		},
	},
	"positions" : {
		"GET"	: fy_fun.fyPosGET,
		"POST"	: fy_fun.fyPosPOST,
	},
	"exit_positions" : {
		"POST"	: fy_fun.fyExitPos,
	},
	"snapshot":{
		"POST"	: fy_fun.fySnapshotPOST,
	},
	"symbols"	: {
		"GET"	: fy_fun.fySymbolsGET,
	},
	"tradebook"	: {
		"GET"	: fy_fun.fyTradebookGET,
	},

	"validate"	: {
		"GET"	: fy_fun.fyValidateGET,
		"details"	:{
			"GET"	: fy_fun.fyValidateDetailsGET,
		},
		"BO"	:{
			"GET": fy_fun.BOAuth
		},
		"SSO"	:{
			"POST": fy_fun.MobileLogin,
		},
	},
	"watchlist"	: {
		"GET"		: fy_fun.fyWlGET,
		"POST"		: fy_fun.fyWlPOST,
		"DELETE"	: fy_fun.fyWlDELETE,
		"PUT"		: fy_fun.fyWlPUT,
		"web" : {
			"GET"	: fy_fun.fyWlGETWeb,
			"POST"	: fy_fun.fyWlPOSTWeb,
			"DELETE": fy_fun.fyWlDELETEWeb,
		},
	},

	"gallery":{
		"GET":fy_fun.fySnapShotGalleryGET,
		"DELETE":fy_fun.fySnapShotGalleryDELETE
	},
	## Login Changes Palash 20190717 - Palash
	"auth":{
		"POST":fy_fun.fyLoginAuthPOST
	},
	"changepwd":{
		"POST":fy_fun.fyChangePwdPOST
	},
	"forgotpwd":{
		"POST":fy_fun.fyForgotPwdPOST
	},
	"resetpwd":{
		"POST":fy_fun.fyResetPwdPOST
	},
	"unlock":{
		"POST":fy_fun.fyUnlockPOST
	},

	## Fund Tx Ajay 2019-08-05
	"fundtx":{
		"v1":{
			"view":{
				"POST": fy_fun.fundTxView,
			},
			"addfunds":{
				"POST": fy_fun.fundTxAddFunds,
			},
			"bankdetails": {
				"POST": fy_fun.fundTxBankDetails,
			},
			"marginutilized":{
				"POST": fy_fun.fundTxMarginUtil,
			},
			# "withdraw":{
			# 	"POST": fy_fun.fundTxWithdraw,
			# },
		},
		"v2":{
			"addfunds":{
				"POST": fy_fun.fundTxAddFundsv2,
			},
		},
	},

	"mobileauth":{
		"POST":fy_fun.fyMobileAuthId
	},
	"login":{
		"POST":fy_fun.fyMobileLogin
	},

	"simplifiedReg":{
		"POST":fy_fun.fySimplifiedRegister
	},

	"appVer":{
		"POST":fy_fun.fyAddAppVersion
	},

	"PushNoti" : {
		"register" : {
			"POST" : fy_fun.fyNotiRegister,
		},
	},

	"get_profile":{
		"GET":fy_fun.fyGetProfile
	},

	"guestUser":{
		"register" : {
			"POST":fy_fun.fyGuestRegister
		},
		"validate" : {
			"POST":fy_fun.fyGuestValidate
		},
	},

	"appRating":{
		"POST":fy_fun.fyUserRatingApp
	},

	"margin":{
		"v1":{
			"POST":fy_fun.marginTxView,
		},
	},

	"timestamp":{
		"GET":fy_fun.fyGetTimestamp
	},

	"baskets":{
		"GET":fy_fun.fyGetBaskets,
		"POST":fy_fun.fyCreateBasket,
		"PUT":fy_fun.fyModifyBasket,
		"DELETE":fy_fun.fyDeleteBasket,
		"items":{
			"POST":fy_fun.fyAddItemToBasket,
			"PUT":fy_fun.fyModifyItemsInBasket,
			"DELETE":fy_fun.fyDeleteItemFromBasket,
		},
		"execute":{
			"POST":fy_fun.fyExecuteBasket,
		},
		"reset":{
			"POST":fy_fun.fyResetBasket,
		},
	},

	"admin" : {
		"orders":{
			"GET":fy_fun.fyTechAdminOrderbook,
		},
		"positions":{
			"GET":fy_fun.fyTechAdminPositions,
		},
		"holdings":{
			"GET":fy_fun.fyTechAdminHoldings,
		},
		"funds":{
			"GET":fy_fun.fyTechAdminFunds,
		},
		"trades":{
			"GET":fy_fun.fyTechAdminTrades,
		}
	},

	"allusers" : {
		"POST":fy_fun.fyGetLoggedUsers,
	},
	# EDIS
	"edis":{
		"tpin":{
			"POST":fy_fun.fyEdisBoTpinGenPOST
		},
		"index":{
			"POST":fy_fun.fyEdisIndexPOST
		},
		"details":{
			"POST":fy_fun.fyEdisDetailsPOST
		},
		"inquiry":{
			"POST":fy_fun.fyEdisInquiryPOST
		}
	},
}

if __name__ == "__main__":
	None
