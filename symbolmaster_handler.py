
import sys

sys.path.append("./fy_config")
from fy_config.fy_connections import connectRedis
from fy_config.fy_base_functions import get_logger
import requests
# import logging
# import redis

logger = get_logger()

SYMBOL_MASTER_KEY = "master_updated_"
REDIS_CHANNEL = f"*keyspace@0__:{SYMBOL_MASTER_KEY}*"
SYMBOL_MASTER_REDIS_TICKER = {}
SYMBOL_MASTER_S3_TICKER = {}
SYMBOL_MASTER_REDIS_FYTOKEN = {}
SYMBOL_MASTER_S3_FYTOKEN = {}

S3_LINKS = {
    "NSE_CM": "https://public.fyers.in/sym_details/NSE_CM_sym_master.json",
    "BSE_CM": "https://public.fyers.in/sym_details/BSE_CM_sym_master.json",
    "NSE_FO": "https://public.fyers.in/sym_details/NSE_FO_sym_master.json",
    "NSE_CD": "https://public.fyers.in/sym_details/NSE_CD_sym_master.json",
    "MCX_COM": "https://public.fyers.in/sym_details/MCX_COM_sym_master.json",
}


def remove_expiry_fytoken(fytoken):
    return f"{fytoken[:4]}{fytoken[10:]}"


def download_data_s3(files=["NSE_CM", "BSE_CM", "NSE_FO", "NSE_CD", "MCX_COM"]):
    logger.info(f"Updating Symbol master for {files} from s3....")
    new_data = {}
    for link in files:
        r = requests.get(S3_LINKS[link])
        if r.status_code == 200:
            data = r.json()
            new_data.update(data)
        else:
            logger.error(
                f"Update failed for {link} with status {r.status_code} and data {r.content}"
            )
    global SYMBOL_MASTER_S3_TICKER, SYMBOL_MASTER_S3_FYTOKEN
    SYMBOL_MASTER_S3_TICKER = new_data
    SYMBOL_MASTER_S3_FYTOKEN = {
        remove_expiry_fytoken(v["fyToken"]): v
        for k, v in SYMBOL_MASTER_S3_TICKER.items()
    }
    logger.info("Symbol master updated from s3")


def subscribe_for_updates():
    redis_instance = connectRedis()
    pubsub = redis_instance.pubsub()
    pubsub.psubscribe(REDIS_CHANNEL)
    logger.info("Subscribed for keyspace notifications")
    for message in pubsub.listen():
        if message["data"] != 1:
            if (
                "channel" in message
                and f"__keyspace@0__:{SYMBOL_MASTER_KEY}"
                in message["channel"].decode("utf-8")
                and message["data"].decode("utf-8") == "set"
            ):
                if "s3" in message["channel"].decode("utf-8"):
                    key = message["channel"].decode("utf-8").split(":")[-1]
                    filename = key.rsplit("_", 1)[-2]
                    filename = filename.split("_", 2)[-1]
                    download_data_s3([filename])
    logger.info("Unsubscribed for keyspace notifications")
