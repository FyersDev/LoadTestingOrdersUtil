moduleName = "vagator_sqlalchemy"

try:
    from sqlalchemy import create_engine
    from fy_base_functions import logEntryFunc2

except Exception as e:
    print("ERR : %s : %s : %s" % (moduleName, "Could not import module", e))

def create_sql_alchemy_engine(endpoint, echo_var=False, callingFuncName=""):
    funcName = "connectRedis"
    try:
        engine = create_engine(endpoint, echo=echo_var)
        return engine

    except Exception as e:
        logEntryFunc2("ERROR", moduleName, funcName, callingFuncName, e,-99,endpoint)
    return None