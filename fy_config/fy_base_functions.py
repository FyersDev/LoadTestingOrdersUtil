moduleName = "fy_base_functions"
try:
    import sys
    import json
    import traceback
    import datetime

    from logging.handlers import TimedRotatingFileHandler
    from pathlib import Path

except Exception as e:
    print("ERR : %s : %s : %s" % (moduleName, "Could not import a module", e))

try:
    from fyers_logger import FyersLogger
    from fy_config.fy_base_defines import LOG_STATUS_SUCCESS_1, LOG_STATUS_ERROR_1
    from fy_config.fy_base_success_error_codes import SUCCESS_C_1, ERROR_C_UNKNOWN, \
     ERROR_C_1

except Exception as e:
    print("ERR : %s : %s : %s" % (moduleName, "Could not import module", e))
    sys.exit()

#### LOGGING DICTCONFIG DEFINES #####
LOGGING = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'verbose': {
                    'format': '%(name)s - %(levelname)s - %(message)s'
                }
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'level': 'DEBUG',
                    'formatter': 'verbose',
                }
            },
            'loggers': {
                'MOBILE_WEB': {
                    'handlers': ['console'],
                    'level': 'DEBUG',
                    'propagate': False,
                }
            },
        }

################################################################
log_path = str(Path.home()) + '/logs'
filename = "albEC2.log"
logger = FyersLogger(
    "VOYAGER", "DEBUG", logger_handler=TimedRotatingFileHandler(log_path + '/' + filename, when='midnight')
)


def logEntryFunc2(status, moduleName, funcName, callingFuncName, *logArgs, **kwargs):
    """
    This will log success and failure entries into either a file system or will print onto the console

        [PARAMS]    : (status,funcName,**logArgs=> Is a list which can have n number of elements that will get printed into logs)
                    :   status: SUCCESS/ERROR;
                        moduleName: The name of the module to which the function belongs
                        funcName: The name of the function which is calling this function
                        callingFuncName: The name of the function which has called the running function

        [RETURN]
            Success : Will either log the input parameters into a file system or will print to the console
            Failure : Will print error message
    """
    try:
        msg = ""
        log_kwargs = {}
        log_kwargs["moduleName"] = moduleName
        log_kwargs["functionName"] = funcName
        log_kwargs["callingFuncName"] = callingFuncName
        log_kwargs["logArgs"] = logArgs
        log_kwargs["extra"] = kwargs
        if "err_msg" in kwargs and isinstance(kwargs["err_msg"], (int, float)) and kwargs["err_msg"] < 1:
            return
        if "message" in kwargs and isinstance(kwargs["message"], (int, float)) and kwargs["message"] < 1:
            return
        if status == LOG_STATUS_SUCCESS_1:
            logger.debug(msg, extra=log_kwargs)
        elif status == LOG_STATUS_ERROR_1:
            exc = traceback.format_exc()
            if "NoneType: None" in exc:
                logger.error(msg, extra=log_kwargs)
            else:
                logger.exception(msg, extra=log_kwargs)
        elif status == "RS-Log":
            if "error" in json.dumps(log_kwargs):
                exc = traceback.format_exc()
                if "NoneType: None" in exc:
                    logger.error(msg, extra=log_kwargs)
                else:
                    logger.exception(msg, extra=log_kwargs)
            else:
                logger.debug(msg, extra=log_kwargs)
        else:
            logger.info(msg, extra=log_kwargs)
        return
    except Exception as e:
        print("ERR: logEntryFunc2: %s : %s" % (funcName, e))


def get_logger():
    """
    This will be used to filter the logger object to get the specified logger object based on the status 
    """
    return logger


def INTERNAL_convertTimestampToDateString(timeStamp, dateFormatString, callingFuncName=""):
    """
    This function will convert the timestamp to the requested data format
        :param timeStamp: This the unix timestamp
        :param dateFormatString: Python recognizable data string format Eg: "%Y-%m-%d"
        :param callingFuncName: The function that is calling this function
    :return:
        Success => [SUCCESS_C_1, "datestring", ""]
        Error   => [ERROR_C_1, errorCode, "error message"]
    """
    funcName = "INTERNAL_convertTimestampToDateString"
    try:
        timeStamp = int(timeStamp)
        dateString = datetime.datetime.fromtimestamp(timeStamp).strftime(dateFormatString)
        return [SUCCESS_C_1, dateString, ""]
    except Exception as e:
        logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName,callingFuncName, e, ERROR_C_UNKNOWN,
                      timeStamp, dateFormatString)
        return [ERROR_C_1, ERROR_C_UNKNOWN, ""]


def main():
    pass  # Do testing here


if __name__ == "__main__":
    main()
