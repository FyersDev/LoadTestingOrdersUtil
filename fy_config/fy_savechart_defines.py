#!/usr/bin/python

# ERROR Codes
CODE_IMPROPER_DATA 			= "-1"
CODE_NO_IMAGE_CREATED 		= "-4"
CODE_IMAGE_LAYOUT_NOT_FOUND = "-5"
CODE_UNKNOWN_ERROR 			= "-99"
CODE_FINAL_IMAGE_NOT_CREATED = "-6"

TV_CONST_STR_BASE64 		= "data:image/png;base64,"
TV_BASE64_CONTENT 			= "content"
TV_CONTENT_WIDTH_STR 		= "contentWidth"
TV_CONTENT_HEIGHT_STR 		= "contentHeight"
TV_LAYOUT 					= "layout"
TV_HIDPI 					= "hidpiRatio"
TV_CHARTS 					= "charts"
TV_PANES 					= "panes"
TV_LEFT_AXIS 				= "leftAxis"
TV_RIGHT_AXIS 				= "rightAxis"
TV_TIME_AXIS				= "timeAxis"
TV_TIME_LHS_STUB 			= "lhsStub"
TV_TIME_RHS_STUB 			= "rhsStub"
TV_META_DATA 				= "meta"
TV_SYMBOL_STR 				= "symbol"
TV_OHLC						= "ohlc"
TV_COLOR 					= "colors"
TV_COLOR_TEXT 				= "text"
TV_COLOR_BG 				= "bg"
TV_COLOR_SCALE 				= "scales"
TV_CLIENT_PLATFORM          = "client"


# different layout codes sent in the JSON
TV_SINGLE_CHART_S			= 's'
TV_TWO_HORIZINTAL_2H		= "2h"
TV_THREE_HORIZINTAL_3H		= "3h"
TV_TWO_VERTICAL_2V			= "2v"
TV_THREE_VERTICAL_3V		= "3v"
TV_CHART_3S					= "3s"
TV_CHART_2_1				= "2-1"
TV_CHART_4					= '4'
TV_CHART_6					= '6'
TV_CHART_8					= '8'

SNAP_REQUIRED_FIELD_LIST	= [TV_LAYOUT,TV_HIDPI,TV_CHARTS]
SNAP_IMG_W_H_MAX 			= (2000,2000)
SNAP_DEFAULT_COLOR_TUPLE 	= (0,0,0,255)
SNAP_BG_COLOR				= (232,232,229)
SNAP_TEXT_COLOR_TUPLE		= (85,85,85)
SNAP_BORDER_COLOR			= (0,0,0)
SNAP_FONT_TYPE 				= "./fy_config/static/fonts/Calibri.ttf"
SNAP_FONT_SIZE 				= 15
SNAP_FONT_SIZE_BOTTOM		= 20
SANP_LINE_SPACING 			= 6
SNAP_WORD_SPACING 			= 4
SNAP_BOTTOM_BOARDER			= 50
SNAP_BOTTOM_WIDTH_ALIGN 	= 5
SNAP_BOTTOM_HEIGHT_ALIGN 	= 5

SNAP_BOTTOM_STRING 			= "Image created on "
SNAP_TIMESTAMP_STR			= "on "
SNAP_WATERMARK_IMAGE_NAME	= "Fyers_Logo_Monochrome_0.25opacity_60x60.png"
SANP_BOTTOM_IMAGE			= "trade_fyers_in.png"
SNAP_STATIC_IMAGE_PATH		= "./fy_config/static/images/"
SNAP_IMAGE_PATH 			= "./images/"

SNAP_TIME_ZONE				= "Asia/Calcutta"
SNAP_TIME_FORMAT			= "%B %d, %Y %H:%M"


# AWS
AWS_S3_BUCKET_SNAPSHOT 		= "user-chart-snapshot"
AWS_SNAPSHOT_FOLDER 		= "snapshot"

TRADE_FYERS_IN_URL			= "https://trade2.fyers.in"
SNAPSHOT_SUCCESS_URL		= "https://charts.fyers.in/"
SNAPSHOT_FAIL_URL			= "https://trade2.fyers.in/x/coming-soon"
SNAP_ERR_PARAM				= "?e="

# ERROR CODE Returned
SNAP_INVALID_INPUT_PARAMS	= "ERR:1" #when params is not found in post
SNAP_IMAGES_K_NOT_FOUND		= "ERR:2" #when images key is not found in post parameters
SNAP_UNKNOWN_ERROR			= "ERR:3" # last line of the function
SNAP_EXCEPTION_1			= "ERR:4"
SNAP_CONVERT_TO_PNG_FAIL 	= "ERR:5" # Converting failed coz function returned error
SNAP_PUT_TO_S3_FAIL			= "ERR:6" # put file to S3 failed
#auth related
SNAP_COOKIE_PARSE_EXCEPT	= "ERR:7" # exception occured while parsing the cookie
SNAP_COOKIE_EMPTY			= "ERR:8" # Cookie is empty
SNAP_AUTH_FAILED 			= "ERR:9" # user cookie authentication failed

