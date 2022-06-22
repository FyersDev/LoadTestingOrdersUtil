moduleName = "fy_savechart_functions"
try:
    import sys
    import boto3
    from PIL import Image
    from PIL import ImageDraw, ImageFont, ImageOps
    from io import BytesIO
    import hashlib
    import datetime
    import pytz
    import time
    import json
    import base64
    import urllib.parse

    from fy_base_api_keys_values import API_V_ERROR, API_K_DATA_1
    from fy_base_defines import ENCODING_TYPE_UTF8, LOG_STATUS_ERROR_1
    from fy_base_success_error_codes import SUCCESS_C_1, ERROR_C_1
    from fy_common_api_keys_values import API_K_SAVE_CHART_IMAGES
    from fy_connections_defines import AWS_SERVICE_S3
    from fy_login_defines import LOGIN_PAGE_URL_1
    from fy_savechart_defines import SNAP_AUTH_FAILED, SNAPSHOT_FAIL_URL, \
      SNAP_ERR_PARAM, SNAP_INVALID_INPUT_PARAMS, AWS_S3_BUCKET_SNAPSHOT, \
      AWS_SNAPSHOT_FOLDER, SNAPSHOT_SUCCESS_URL, SNAP_PUT_TO_S3_FAIL, \
      SNAP_CONVERT_TO_PNG_FAIL, SNAP_IMAGES_K_NOT_FOUND, SNAP_EXCEPTION_1, \
      SNAP_FONT_TYPE, SNAP_FONT_SIZE, SNAP_FONT_SIZE_BOTTOM, CODE_IMPROPER_DATA, \
      SNAP_REQUIRED_FIELD_LIST, SNAP_STATIC_IMAGE_PATH, SNAP_WATERMARK_IMAGE_NAME, \
      TV_CHARTS, TV_PANES, TV_LEFT_AXIS, TV_CONTENT_WIDTH_STR, TV_RIGHT_AXIS, \
      TV_CONTENT_HEIGHT_STR, TV_TIME_AXIS, TV_TIME_LHS_STUB, TV_TIME_RHS_STUB, \
      SNAP_IMG_W_H_MAX, SNAP_BG_COLOR, TV_META_DATA, TV_OHLC, SANP_LINE_SPACING, \
      SNAP_DEFAULT_COLOR_TUPLE, SNAP_TEXT_COLOR_TUPLE, SNAP_WORD_SPACING, \
      SNAP_BORDER_COLOR, CODE_FINAL_IMAGE_NOT_CREATED, TV_LAYOUT, \
      TV_SINGLE_CHART_S, SNAP_BOTTOM_BOARDER, TV_TWO_HORIZINTAL_2H, \
      TV_THREE_HORIZINTAL_3H, TV_TWO_VERTICAL_2V, TV_THREE_VERTICAL_3V, \
      TV_CHART_3S, TV_CHART_2_1, TV_CHART_4, TV_CHART_6, TV_CHART_8, \
      CODE_IMAGE_LAYOUT_NOT_FOUND, SNAP_BOTTOM_STRING, SNAP_BOTTOM_WIDTH_ALIGN, \
      SNAP_BOTTOM_HEIGHT_ALIGN, SANP_BOTTOM_IMAGE, SNAP_TIMESTAMP_STR, \
      SNAP_TIME_ZONE, SNAP_TIME_FORMAT, CODE_NO_IMAGE_CREATED, TV_BASE64_CONTENT, \
      TV_CONST_STR_BASE64
    from vagator_auth_check import API_K_STATUS

    from fy_auth_functions import initial_validate_access_token
    from fy_base_functions import logEntryFunc2

except Exception as e:
    print ("ERR : %s : %s : %s" % (moduleName, "Could not import module", e))
    sys.exit()


def putFileToS3(s3Client, bucketName, folderPath, fyersID, fileName, fileContent, fileExt=".txt",
                contentType='text/plain'):
    # Put object to S3
    """
    response:
    {
        'ETag': '"fd9e7dbbc045a99570e860f3f191b3f6"', #entry tag for the uploaded object
        'ResponseMetadata':
        {
            'HTTPStatusCode': 200,
            'RetryAttempts': 0,
            'HostId': '6U0MBWCkUUoJueUNYcfkpRLYwAo8qyMP2H/71zdBnaFpKPUEXU66VAK1VcXRfZTeXsg7kc3BBbE=',
            'RequestId': 'EAD8D62CCAC28546',
            'HTTPHeaders':
            {
                'content-length': '0',
                'x-amz-id-2': '6U0MBWCkUUoJueUNYcfkpRLYwAo8qyMP2H/71zdBnaFpKPUEXU66VAK1VcXRfZTeXsg7kc3BBbE=',
                'server': 'AmazonS3',
                'x-amz-request-id': 'EAD8D62CCAC28546',
                'etag': '"fd9e7dbbc045a99570e860f3f191b3f6"',
                'date': 'Fri, 13 Oct 2017 10:36:39 GMT'
            }
        }
    }
    """
    funcName = "putFileToS3"
    try:
        fileNameFull = "%s/%s/%s%s" % (folderPath, fyersID, fileName, fileExt)
        response = s3Client.put_object(
            Body=fileContent,
            Bucket=bucketName,
            Key=fileNameFull,
            ContentType=contentType
        )

        if "ETag" in response:
            if response["ETag"] != '' or response["ETag"] != None:
                if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
                    return [SUCCESS_C_1, fileNameFull, "Insertion Success"]
                else:
                    return [ERROR_C_1, fileNameFull, response["ResponseMetadata"]["HTTPStatusCode"]]
            else:
                return [ERROR_C_1, fileNameFull, "ETag: empty/None"]
        else:
            return [ERROR_C_1, fileNameFull, "ETag: not found"]

    except Exception as e:
        logEntryFunc2(LOG_STATUS_ERROR_1, funcName, "Exception", e)
        return [ERROR_C_1, fileNameFull, str(e)]
    return [ERROR_C_1, fileNameFull, "ERR : -99"]


def getFileFromS3(s3Client, bucketName, folderPath, fyersID, fileName):
    """
    Get
    response:
    {
        u"Body": <botocore.response.StreamingBody object at 0x7f40f066bc10>, u"AcceptRanges": "bytes",
        u"ContentType": "text/plain",
        "ResponseMetadata": {"HTTPStatusCode": 200, "RetryAttempts": 0, "HostId": "AxWt23z+1sglTL+eGgu7FnG7WF2dpzQeAn6Ye43JQgtZdCh0IfBo9xEZZThmKqf5vcIvmEzBjCE=", "RequestId": "59E5112A6A1BC4C5", "HTTPHeaders": {"content-length": "15000", "x-amz-id-2": "AxWt23z+1sglTL+eGgu7FnG7WF2dpzQeAn6Ye43JQgtZdCh0IfBo9xEZZThmKqf5vcIvmEzBjCE=", "accept-ranges": "bytes", "server": "AmazonS3", "last-modified": "Fri, 13 Oct 2017 11:57:39 GMT", "x-amz-request-id": "59E5112A6A1BC4C5", "etag": ""83849dae2e8daad96356a1c706cc1906"", "date": "Fri, 13 Oct 2017 11:59:13 GMT", "content-type": "text/plain"}}, u"LastModified": datetime.datetime(2017, 10, 13, 11, 57, 39, tzinfo=tzutc()), u"ContentLength": 15000, u"ETag": ""83849dae2e8daad96356a1c706cc1906"", u"Metadata": {}}


    """
    funcName = "getFileFromS3"
    try:
        fileNameFull = "%s/%s/%s.txt" % (folderPath, fyersID, fileName)
        response = s3Client.get_object(
            Bucket=bucketName,
            Key=fileNameFull,
        )
        if ("Body" in response) and "ResponseMetadata" in response:
            if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
                return [SUCCESS_C_1, fileNameFull, response["Body"].read()]  # only one success case
            else:
                return [ERROR_C_1, fileNameFull, "ERR : 1 data not found."]
        else:
            return [ERROR_C_1, fileNameFull, "ERR : 2 data not found."]
    except Exception as e:
        return [ERROR_C_1, fileNameFull, "ERR: u:" + str(e)]
    return [ERROR_C_1, fileNameFull, "ERR : -99"]


def deleteFromS3(s3Client, bucketName, folderPath, fyersID, chartid):
    """
    {'ResponseMetadata':
        {
            'HTTPStatusCode': 204, 'RetryAttempts': 0, 'HostId': 'mjAeJJoNzVM+OHPKg17rZ+AZiOt5xUd4rGR+jPId69NnhhyFuw264mhCzSokeWz6OBWsNszM1lM=',
            'RequestId': 'AA6CC35B36EE0C45',
            'HTTPHeaders':
            {
                'x-amz-id-2': 'mjAeJJoNzVM+OHPKg17rZ+AZiOt5xUd4rGR+jPId69NnhhyFuw264mhCzSokeWz6OBWsNszM1lM=',
                'date': 'Fri, 13 Oct 2017 12:11:35 GMT',
                'x-amz-request-id': 'AA6CC35B36EE0C45',
                'server': 'AmazonS3'
            }
        }
    }
    """
    funcName = "deleteFromS3"
    try:
        fileNameFull = "%s/%s/%s.txt" % (folderPath, fyersID, chartid)
        response = s3Client.delete_object(
            Bucket=bucketName,
            Key=fileNameFull,
        )
        if response["ResponseMetadata"]["HTTPStatusCode"] >= 200 and response["ResponseMetadata"][
            "HTTPStatusCode"] < 300:
            return [SUCCESS_C_1, fileNameFull, "Success"]  # only one success case
        else:
            return [ERROR_C_1, fileNameFull, response]
    except Exception as e:
        return [ERROR_C_1, fileNameFull, "ERR: u:" + str(e)]
    return [ERROR_C_1, fileNameFull, "ERR : -99"]


def snapShotFunction(kwargs):
    funcName = "snapShotFunction"
    try:
        validate_return = initial_validate_access_token(kwargs, snapshot_flag=True)
        if validate_return[API_K_STATUS] == API_V_ERROR:
            return LOGIN_PAGE_URL_1 + "/?message=" + SNAP_AUTH_FAILED
        token_id = validate_return[API_K_DATA_1][0]
        fyersID = validate_return[API_K_DATA_1][1]

        if "params" in kwargs:
            if isinstance(kwargs["params"], dict):
                kwargs[API_K_SAVE_CHART_IMAGES] = kwargs["params"][API_K_SAVE_CHART_IMAGES]
            else:
                postParams = urllib.parse.parse_qs(kwargs["params"])
                for eachParam in postParams:
                    try:
                        urlDecodedKey = urllib.unquote(eachParam).decode(ENCODING_TYPE_UTF8)
                        kwargs[urlDecodedKey] = urllib.unquote(postParams[eachParam][0]).decode(ENCODING_TYPE_UTF8)
                    except Exception as e:
                        continue
        else:
            # when params is not found in post
            return SNAPSHOT_FAIL_URL + SNAP_ERR_PARAM + SNAP_INVALID_INPUT_PARAMS

        if API_K_SAVE_CHART_IMAGES in kwargs:
            converterReturn = convertToPng(kwargs[API_K_SAVE_CHART_IMAGES])
            if converterReturn[0] == SUCCESS_C_1:
                fyersId_MD5 = hashlib.md5(fyersID.encode(ENCODING_TYPE_UTF8)).hexdigest()
                chartName_Md5 = hashlib.md5(str(time.time()).encode(ENCODING_TYPE_UTF8)).hexdigest()

                s3Client = boto3.client(AWS_SERVICE_S3)
                imageBytesFile = BytesIO()
                converterReturn[1].save(imageBytesFile, format="png")

                putReturn = putFileToS3(s3Client, AWS_S3_BUCKET_SNAPSHOT, AWS_SNAPSHOT_FOLDER, fyersId_MD5,
                                        chartName_Md5, imageBytesFile.getvalue(), fileExt=".png",
                                        contentType="image/png")
                if putReturn[0] == SUCCESS_C_1:
                    return SNAPSHOT_SUCCESS_URL + fyersId_MD5 + '/' + chartName_Md5 + ".png"
                else:
                    return SNAPSHOT_FAIL_URL + SNAP_ERR_PARAM + SNAP_PUT_TO_S3_FAIL
            else:
                return SNAPSHOT_FAIL_URL + SNAP_ERR_PARAM + SNAP_CONVERT_TO_PNG_FAIL

        else:
            # when images key is not found in post parameters
            # return str(kwargs)
            return SNAPSHOT_FAIL_URL + SNAP_ERR_PARAM + SNAP_IMAGES_K_NOT_FOUND

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print ("this is the exception:", e, "Line Number: %s"%str(exc_tb.tb_lineno))
        return SNAPSHOT_FAIL_URL + SNAP_ERR_PARAM + SNAP_EXCEPTION_1

    # last line of the function
    return SNAPSHOT_FAIL_URL + SNAP_ERR_PARAM + SNAP_UNKNOWN_ERROR

def convertToPng(data):
    """
    [output]:
                ERROR: [ERROR_C_1, ERROR_CODE, "ERROR_MESSAGE"]
                ERR : 1 -> improper JSON
                ERR : 2 -> No input data found
                ERR : 3 -> required params not there in the list
                ERR : 4 -> No images were created

                SUCCESS : [SUCCESS_C_1, IMAGE_OBJECT, LAYOUT_TYPE]

    """
    funcName = "convertToPng"
    try:
        SNAP_FONT = ImageFont.truetype(font=SNAP_FONT_TYPE, size=SNAP_FONT_SIZE)  # , index=0,  encoding="RGBA"
        SNAP_FONT_BOTTOM = ImageFont.truetype(font=SNAP_FONT_TYPE, size=SNAP_FONT_SIZE_BOTTOM)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logEntryFunc2(LOG_STATUS_ERROR_1, funcName, "Exception", "Font cannot be loaded.", str(e), "Line Number: %s"%str(exc_tb.tb_lineno))
        SNAP_FONT_BOTTOM = SNAP_FONT = ImageFont.load_default()  # when font file camnnot be opened it will throw an exception and the fonts will be of default type.

    jsonData = {}
    try:
        jsonData = json.loads(data)
    except Exception as e:
        return [ERROR_C_1, CODE_IMPROPER_DATA, "ERR : 1." + str(e)]

    if len(jsonData) <= 0:
        return [ERROR_C_1, CODE_IMPROPER_DATA, "ERR : 2."]

    # Level-1 validation
    for eachVal in SNAP_REQUIRED_FIELD_LIST:
        if eachVal not in jsonData:
            return [ERROR_C_1, CODE_IMPROPER_DATA, "ERR : 3."]

    # Fyers Image for watermarker
    fyersMarkerImg = None
    try:
        fyersMarkerImg = Image.open(SNAP_STATIC_IMAGE_PATH + SNAP_WATERMARK_IMAGE_NAME).convert("RGBA")
    except Exception as e:
        logEntryFunc2(LOG_STATUS_ERROR_1, funcName, "Exception",
                     "ERR : cannot open image %s. Exception: %s" % (SNAP_WATERMARK_IMAGE_NAME, e))
        fyersMarkerImg = None

    allImageList = []  # This will contain all the image/s
    # imageCount = 0 # this variable used for tessting
    for eachChart in jsonData[TV_CHARTS]:
        try:
            mainImg = None
            mainContentWidth = 0
            mainContentHeight = 0

            # To select the color send from the front-end
            # textColor   = eachChart[TV_COLOR][TV_COLOR_TEXT]
            # bgColor     = eachChart[TV_COLOR][TV_COLOR_BG]
            # scaleColor  = eachChart[TV_COLOR][TV_COLOR_SCALE]
            # [textColorMode,   textColorTuple]     = getColorTuple(textColor)
            # [bgColorMode,     bgColorTuple]       = getColorTuple(bgColor)
            # [scaleColorMode, scaleColorTuple]     = getColorTuple(scaleColor)
            # textColorTuple = list(textColorTuple).append(255)
            # print "textColorTuple:", textColorTuple,type(textColorTuple)
            # textColorTuple = (85,85,85)

            leftWidth = eachChart[TV_PANES][0][TV_LEFT_AXIS][TV_CONTENT_WIDTH_STR]
            rightWidth = eachChart[TV_PANES][0][TV_RIGHT_AXIS][TV_CONTENT_WIDTH_STR]
            mainWidth = eachChart[TV_PANES][0][TV_CONTENT_WIDTH_STR]
            totalWidthChart = leftWidth + mainWidth + rightWidth
            mainImg = Image.new(mode="RGBA", size=(2000, 2000), color=(255, 255, 255, 255))
            if mainImg == None:
                logEntryFunc2(LOG_STATUS_ERROR_1, funcName, "ERR", "Cannot create the image")
                continue

            heightCounter = 0
            lhsWidth = 0
            for eachPane in eachChart[TV_PANES]:
                leftAxisImg = None
                rightAxisImg = None

                subImgHeight = 0 ## Ajay 20181101
                subImgWidth = 0 ## Ajay 20181101
                leftAxisData = eachPane[TV_LEFT_AXIS]
                returnParse = parseChartData(leftAxisData)
                if returnParse[0] != ERROR_C_1 and returnParse[1] != None:
                    leftAxisImg = returnParse[1]
                    if leftAxisData[TV_CONTENT_WIDTH_STR] > lhsWidth:
                        lhsWidth = leftAxisData[TV_CONTENT_WIDTH_STR]
                    mainImg.paste(leftAxisImg, (0, heightCounter))
                    if returnParse[1].size[1] > subImgHeight: subImgHeight = returnParse[1].size[1]
                    subImgWidth += returnParse[1].size[0]
                else:
                    None

                returnParse = parseChartData(eachPane)
                if returnParse[0] != ERROR_C_1 and returnParse[1] != None:
                    mainImg.paste(returnParse[1], (subImgWidth, heightCounter))
                    if returnParse[1].size[1] > subImgHeight: subImgHeight = returnParse[1].size[1]
                    subImgWidth += returnParse[1].size[0]
                else:
                    # If this happens we dont have the main chart. So dont process it
                    logEntryFunc2(LOG_STATUS_ERROR_1, funcName, LOG_STATUS_ERROR_1, str(returnParse))
                    continue

                rightAxisData = eachPane[TV_RIGHT_AXIS]
                returnParse = parseChartData(rightAxisData)
                if returnParse[0] != ERROR_C_1 and returnParse[1] != None:
                    rightAxisImg = returnParse[1]
                    mainImg.paste(returnParse[1], (subImgWidth, heightCounter))
                    if returnParse[1].size[1] > subImgHeight: subImgHeight = returnParse[1].size[1]
                    subImgWidth += returnParse[1].size[0]
                else:
                    None

                if subImgHeight > eachPane[TV_CONTENT_HEIGHT_STR]:
                    heightCounter += subImgHeight
                else:
                    heightCounter += eachPane[TV_CONTENT_HEIGHT_STR]

                if subImgWidth > eachPane[TV_CONTENT_WIDTH_STR]: 
                    eachPane[TV_CONTENT_WIDTH_STR] = subImgWidth
                    totalWidthChart = subImgWidth
                if subImgHeight > eachPane[TV_CONTENT_HEIGHT_STR]: eachPane[TV_CONTENT_HEIGHT_STR] = subImgHeight

                if eachPane[TV_CONTENT_WIDTH_STR] > mainContentWidth:
                    mainContentWidth = eachPane[TV_CONTENT_WIDTH_STR]

                if eachPane[TV_CONTENT_HEIGHT_STR] > mainContentHeight:
                    mainContentHeight = eachPane[TV_CONTENT_HEIGHT_STR]

            timeData = eachChart[TV_TIME_AXIS]
            returnParse = parseChartData(timeData)
            if returnParse[0] != ERROR_C_1 and returnParse[1] != None:
                mainImg.paste(returnParse[1], (lhsWidth, heightCounter))

                timeLhsStub = eachChart[TV_TIME_AXIS][TV_TIME_LHS_STUB]
                returnParse = parseChartData(timeLhsStub)
                if returnParse[0] != ERROR_C_1 and returnParse[1] != None:
                    mainImg.paste(returnParse[1], (0, heightCounter))
                else:
                    None

                timeRhsStub = eachChart[TV_TIME_AXIS][TV_TIME_RHS_STUB]
                returnParse = parseChartData(timeRhsStub)
                if returnParse[0] != ERROR_C_1 and returnParse[1] != None:
                    mainImg.paste(returnParse[1], (lhsWidth + mainContentWidth, heightCounter))
                else:
                    None
            else:
                None

            heightCounter += timeData[TV_CONTENT_HEIGHT_STR]
            mainImg = mainImg.crop((0, 0, totalWidthChart, heightCounter))

            textImg = Image.new("RGBA", SNAP_IMG_W_H_MAX, color=SNAP_BG_COLOR)
            draw = ImageDraw.Draw(textImg, mode="RGBA")
            textWidth, textHeight = draw.textsize(str(eachChart[TV_META_DATA]), SNAP_FONT)

            # insert metadata on top of the image
            metaDataList = []  # This list contain all the data that needs to be inserted in each chart
            try:
                metaDataList.append(["O", eachChart[TV_OHLC][0]])
                metaDataList.append(["H", eachChart[TV_OHLC][1]])
                metaDataList.append(["L", eachChart[TV_OHLC][2]])
                metaDataList.append(["C", eachChart[TV_OHLC][3]])
                metaDataList.append(["Symbol", eachChart[TV_META_DATA]["symbol"]])

            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logEntryFunc2(LOG_STATUS_ERROR_1, funcName, "Exception", "while reading metadata values:%s" % (str(e)), "Line Number: %s"%str(exc_tb.tb_lineno))

            textWidth, textHeight = 0, 0
            # This loop will insert the text on top of the image and auto adjusts if the the text if width is more than image
            for eachMeta in metaDataList:
                keyText, valueText = eachMeta[0] + ':', eachMeta[1]
                textDimenKey = draw.textsize(str(keyText), SNAP_FONT)
                textDimenVal = draw.textsize(str(valueText), SNAP_FONT)

                if (textDimenKey[0] + textDimenVal[
                    0]) >= totalWidthChart:  # This will happen when the text we are trying to write is more than the width of the main chart
                    textWidth = 0
                    textHeight += (textDimenVal[1] + SANP_LINE_SPACING)

                elif (textWidth + textDimenKey[0] + textDimenVal[0] + 2) >= totalWidthChart:
                    textWidth = 0
                    textHeight += (textDimenVal[1] + SANP_LINE_SPACING)

                draw.text((textWidth, textHeight), str(keyText), fill=SNAP_DEFAULT_COLOR_TUPLE, font=SNAP_FONT)
                textWidth += textDimenKey[0]
                draw.text((textWidth, textHeight), str(valueText), fill=SNAP_TEXT_COLOR_TUPLE, font=SNAP_FONT)
                textWidth += textDimenVal[0] + SNAP_WORD_SPACING

            textHeight += SNAP_FONT_SIZE + SANP_LINE_SPACING
            textImg = textImg.crop((0, 0, totalWidthChart, textHeight))  # Crop only required size from text

            mainImg = ImageOps.expand(mainImg, border=1, fill=SNAP_BORDER_COLOR)  # add border to the image

            completeImg = Image.new("RGBA", SNAP_IMG_W_H_MAX, color=SNAP_BG_COLOR)
            completeImg.paste(textImg, (0, 0))  # Paste text at the top
            completeImg.paste(mainImg, (0, textHeight))  # Paste image below text
            completeImg = completeImg.crop((0, 0, totalWidthChart + 2, mainImg.size[1] + textHeight))

            if fyersMarkerImg != None:
                completeImg.paste(fyersMarkerImg, ((totalWidthChart - fyersMarkerImg.size[0]) // 2, (completeImg.size[1] - fyersMarkerImg.size[0]) // 2),mask=fyersMarkerImg)  # Add watermark fyers image 

            completeImg = ImageOps.expand(completeImg, border=5,
                                          fill=SNAP_BG_COLOR)  # Add gray border to the entire image
            allImageList.append(completeImg)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logEntryFunc2(LOG_STATUS_ERROR_1, funcName, "Exception", "Exception occured while creating the image", e, "Line Number: %s"%str(exc_tb.tb_lineno))

    # chart alignment when two or more charts are saved
    if len(allImageList) > 0:
        completeImg = Image.new("RGBA", SNAP_IMG_W_H_MAX, color=SNAP_BG_COLOR)
        if completeImg == None:
            logEntryFunc2(LOG_STATUS_ERROR_1, funcName, "ERR", "Cannot create new image to combine all pieces.")
            return [ERROR_C_1, CODE_FINAL_IMAGE_NOT_CREATED,
                    "ERR : 7.Cannot create new image to combine all pieces."]

        widthImg, heightImg = 0, 0
        if jsonData[TV_LAYOUT].lower() == TV_SINGLE_CHART_S:
            completeImg.paste(allImageList[0], (0, 0))
            completeImg = completeImg.crop(
                (0, 0, allImageList[0].size[0] + 1, allImageList[0].size[1] + SNAP_BOTTOM_BOARDER))

        elif jsonData[TV_LAYOUT].lower() == TV_TWO_HORIZINTAL_2H:
            completeImg = combineHorizontalImages(completeImg, allImageList)

        elif jsonData[TV_LAYOUT].lower() == TV_THREE_HORIZINTAL_3H:
            completeImg = combineHorizontalImages(completeImg, allImageList)

        elif jsonData[TV_LAYOUT].lower() == TV_TWO_VERTICAL_2V:
            for eachImage in allImageList:
                completeImg.paste(eachImage, (0, heightImg))
                heightImg += eachImage.size[1]
                if eachImage.size[0] > widthImg:
                    widthImg = eachImage.size[0]
            completeImg = completeImg.crop((0, 0, widthImg, heightImg + SNAP_BOTTOM_BOARDER))

        elif jsonData[TV_LAYOUT].lower() == TV_THREE_VERTICAL_3V:
            for eachImage in allImageList:
                completeImg.paste(eachImage, (0, heightImg))
                heightImg += eachImage.size[1]
                if eachImage.size[0] > widthImg:
                    widthImg = eachImage.size[0]
            completeImg = completeImg.crop((0, 0, widthImg, heightImg + SNAP_BOTTOM_BOARDER))

        elif jsonData[TV_LAYOUT].lower() == TV_CHART_3S:
            completeImg.paste(allImageList[0], (widthImg, heightImg))
            widthImg = allImageList[0].size[0]
            if len(allImageList) > 1:
                completeImg.paste(allImageList[1], (widthImg, heightImg))
                widthImg += allImageList[1].size[0]
                heightImg = allImageList[1].size[1]
            if len(allImageList) > 2:
                completeImg.paste(allImageList[2], (allImageList[0].size[0], heightImg))
                heightImg += allImageList[2].size[1]
            completeImg = completeImg.crop((0, 0, widthImg, heightImg + SNAP_BOTTOM_BOARDER))

        elif jsonData[TV_LAYOUT].lower() == TV_CHART_2_1:
            completeImg.paste(allImageList[0], (widthImg, heightImg))
            widthImg = allImageList[0].size[0]
            heightImg = allImageList[0].size[1]
            if len(allImageList) > 1:
                completeImg.paste(allImageList[1], (0, heightImg))
                heightImg += allImageList[1].size[1]
            if len(allImageList) > 2:
                completeImg.paste(allImageList[2], (widthImg, 0))
                widthImg += allImageList[2].size[0]
            completeImg = completeImg.crop((0, 0, widthImg, heightImg + SNAP_BOTTOM_BOARDER))

        elif jsonData[TV_LAYOUT].lower() == TV_CHART_4:
            completeImg = combineImageInList(completeImg, allImageList, 2, 2)

        elif jsonData[TV_LAYOUT].lower() == TV_CHART_6:
            completeImg = combineImageInList(completeImg, allImageList, 2, 3)

        elif jsonData[TV_LAYOUT].lower() == TV_CHART_8:
            completeImg = combineImageInList(completeImg, allImageList, 2, 4)

        else:
            return [ERROR_C_1, CODE_IMAGE_LAYOUT_NOT_FOUND,
                    "ERR : 5.This is undefined jsonData[TV_LAYOUT].lower():" + str(jsonData[TV_LAYOUT].lower())]

        if completeImg != None:
            bottomDimension = (0, 0)
            try:
                bottomDraw = ImageDraw.Draw(completeImg, mode="RGBA")
                bottomDimension = bottomDraw.textsize(str(SNAP_BOTTOM_STRING), SNAP_FONT_BOTTOM)

                bottomDraw.text(
                    (SNAP_BOTTOM_WIDTH_ALIGN, completeImg.size[1] - SNAP_BOTTOM_BOARDER + SNAP_BOTTOM_HEIGHT_ALIGN),
                    str(SNAP_BOTTOM_STRING),
                    fill=SNAP_TEXT_COLOR_TUPLE,
                    font=SNAP_FONT_BOTTOM
                )
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logEntryFunc2(LOG_STATUS_ERROR_1, funcName, "Exception:pasting bottom text", e, "Line Number: %s"%str(exc_tb.tb_lineno))

            fyersBottomLogoWidth = 0
            try:
                smallFyLogo = Image.open(SNAP_STATIC_IMAGE_PATH + SANP_BOTTOM_IMAGE).convert("RGBA")
                completeImg.paste(smallFyLogo, (
                    bottomDimension[0] + 2, completeImg.size[1] - SNAP_BOTTOM_BOARDER + SNAP_BOTTOM_HEIGHT_ALIGN - 1),
                                  mask=smallFyLogo)
                fyersBottomLogoWidth = smallFyLogo.size[0]
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logEntryFunc2(LOG_STATUS_ERROR_1, funcName,
                             "Exception:while pasting bottom fy_icon image:%s" % (SANP_BOTTOM_IMAGE), e, "Line Number: %s"%str(exc_tb.tb_lineno))

            try:
                timeStr = SNAP_TIMESTAMP_STR + datetime.datetime.now(pytz.timezone(SNAP_TIME_ZONE)).strftime(
                    SNAP_TIME_FORMAT)
                bottomDraw.text(
                    (SNAP_BOTTOM_WIDTH_ALIGN + bottomDimension[0] + 2 + fyersBottomLogoWidth,
                     completeImg.size[1] - SNAP_BOTTOM_BOARDER + SNAP_BOTTOM_HEIGHT_ALIGN),
                    str(timeStr),
                    fill=SNAP_TEXT_COLOR_TUPLE,
                    font=SNAP_FONT_BOTTOM)
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logEntryFunc2(LOG_STATUS_ERROR_1, funcName, "Exception:while updating bottom Time", e, "Line Number: %s"%str(exc_tb.tb_lineno))
            return [SUCCESS_C_1, completeImg, jsonData[TV_LAYOUT].lower()]

        else:
            return [ERROR_C_1, CODE_FINAL_IMAGE_NOT_CREATED, "ERR : 6.CompleteImg is None"]
    else:
        return [ERROR_C_1, CODE_NO_IMAGE_CREATED, "ERR : 4.None of the images were created properly."]


def combineImageInList(completeImg, allImageList, numberOfImagesV, numberOfImagesH):
    """
    [Function]  :combine multiple images in the array and forms a new image.
    [Input]     :
                completeImg     : The image in which all the images are pasted
                allImageList    : List of images
                numberOfImagesV : Number of vertical Images
                numberOfImagesH : Number of horizontal Images
    [Return]    :
                completeImg     : Which will have all the images combined
    """
    funcName = "combineImageInList"
    widthImg, heightImg = 0, 0
    maxHeight, maxWidth = 0, 0
    minHeight, minWidth = 0, 0
    for eachImage in allImageList:
        if eachImage.size[0] > maxWidth:
            maxWidth = eachImage.size[0]
        else:
            minWidth = eachImage.size[0]
        if eachImage.size[1] > maxHeight:
            maxHeight = eachImage.size[1]
        else:
            minHeight = eachImage.size[1]
    countImg = 0
    for eachImage in allImageList:
        countImg += 1
        if countImg % 2 != 0:
            heightImg = maxHeight - eachImage.size[1]
        else:
            heightImg = maxHeight + (maxHeight - eachImage.size[1])
        completeImg.paste(eachImage, (widthImg, heightImg))
        if countImg % 2 == 0:
            widthImg += maxWidth

    completeImg = completeImg.crop(
        (0, 0, (maxWidth * numberOfImagesH) + 1, (maxHeight * numberOfImagesV) + SNAP_BOTTOM_BOARDER))
    return completeImg


def combineHorizontalImages(completeImg, allImageList):
    """
    [Function]  :combine multiple images in the array and forms a new image.
    [Input]     :
                completeImg     : The image in which all the images are pasted
                allImageList    : List of images
    [Return]    :
                completeImg     : Which will have all the images combined
    """
    funcName = "combineHorizontalImages"
    widthImg = 0
    heightImg = 0
    maxHeight = 0
    for eachImage in allImageList:
        if eachImage.size[1] > maxHeight:
            maxHeight = eachImage.size[1]
    for eachImage in allImageList:
        deltaHeight = 0
        if eachImage.size[1] != maxHeight:
            deltaHeight = maxHeight - eachImage.size[1]
        completeImg.paste(eachImage, (widthImg, deltaHeight))
        widthImg += eachImage.size[0]
    completeImg = completeImg.crop((0, 0, widthImg + 1, maxHeight + SNAP_BOTTOM_BOARDER))
    return completeImg


def parseChartData(chartDataDict):
    """
    [Function]  : parse chart data send from the front end and open the the data as file
    [Input]     :
                chartDataDict : dictionary containing the chart data
    [Return]    :
                Success     : [SUCCESS_C_1, image_File_object, ""]
                fail        : [ERROR_C_1, None, "Error message"]
    """
    funcName = "parseChartData"
    try:
        if chartDataDict[TV_BASE64_CONTENT].startswith(TV_CONST_STR_BASE64):
            base64Data = chartDataDict[TV_BASE64_CONTENT]
            base64Data = base64Data[len(TV_CONST_STR_BASE64):]
            try:
                openLikeFile = BytesIO(base64.b64decode(base64Data))
                imageFile = Image.open(openLikeFile)
                
            except Exception as e:
                print("DEBUG Exception :", e, funcName)
            return [SUCCESS_C_1, imageFile, ""]
        else:
            return [ERROR_C_1, None, "parseChartData() chart data doesnot start with: '%s'" % (TV_CONST_STR_BASE64)]
    except Exception as e:
        return [ERROR_C_1, None, "ERR : parseChartData() exception occured: %s" % (e)]


def main():
    Pass  # Test here


if __name__ == "__main__":
    main()
