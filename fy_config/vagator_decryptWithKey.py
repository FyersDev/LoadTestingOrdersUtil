moduleName = "vagator_decryptWithKey"

try:
    from fy_base_functions import logEntryFunc2
    from cryptography.fernet import Fernet

except Exception as e:
    print("ERR : %s : %s : %s" % (moduleName, "Could not import module", e))

SUCCESS_C_1                     = 1
LOG_STATUS_ERROR_1      = "ERROR"
ERROR_C_UNKNOWN                     = -99
ERROR_C_1                       = -1
ERROR_C_FY_DECRYPTION               = -103
ERROR_M_MF_INV_TOKEN_ID             = "Invalid token"


def INTERNAL_decreptWithKey(encryptedText, decryptionKey, callingFuncName = ""):
    """
        [FUNCTION]
        INTERNAL_decreptWithKey : Will decrypt the input text with the input decryption key
        [PARAMS]    :
            encryptedText : The text which needs to be decrypted
            decryptionKey: The decryptionKey key which will be used
        [RETURN]
            Success : [SUCCESS_C_1,deryptedText,""]
            Failure : [ERROR_C_1,ERROR_C_FY_DECRYPTION,""]
    """
    funcName = "INTERNAL_decreptWithKey"
    try:
        cipher = Fernet(decryptionKey)
        encryptedText = encryptedText.encode('utf-8')
        decryptBytes = cipher.decrypt(encryptedText)
        decryptBytes = decryptBytes.decode('utf-8')
        return [SUCCESS_C_1, decryptBytes, ""]
    except Exception as e:
        logEntryFunc2(LOG_STATUS_ERROR_1, moduleName, funcName, callingFuncName, e, ERROR_C_UNKNOWN,
                      encryptedText, decryptionKey)
    return [ERROR_C_1, ERROR_C_FY_DECRYPTION, ERROR_M_MF_INV_TOKEN_ID, ""]