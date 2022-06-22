import datetime
import pytz

from fy_base_success_error_codes import ERROR_C_1, ERROR_C_UNKNOWN, SUCCESS_C_1
from fy_base_defines import LOG_STATUS_ERROR_1

from fy_base_functions import logEntryFunc2

moduleName = "helper"

def getSecondsToNextDayTillSix(callingFuncName=""):
    funcName = "getSecondsToNextDayTillSix"
    try:
        tz = pytz.timezone("Asia/Kolkata")
        today = datetime.datetime.now(tz).date()
        one_day = datetime.timedelta(days=1)
        tomorrow = today + one_day
        tomorrow_at_six = datetime.datetime.combine(
            tomorrow, datetime.datetime.strptime("0600", "%H%M").time()
        )
        time_till_tommorow_six = tomorrow_at_six - datetime.datetime.now()
        seconds_till_tomorrow_six = time_till_tommorow_six.seconds

        return [SUCCESS_C_1, seconds_till_tomorrow_six, ""]

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, e, ERROR_C_UNKNOWN,"Line Number: %s"%str(exc_tb.tb_lineno))
        return [ERROR_C_1, "helper function getSecondsToNextDayTillSix error", str(e)]


def main():
    print(getSecondsToNextDayTillSix())


if __name__ == '__main__':
    main()
