import logging

from ufsbotz.database import antiservicedb

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


async def is_antiservice_on(chat_id: int) -> bool:
    chat = antiservicedb.find_one({"chat_id": chat_id})
    return not chat


async def antiservice_on(chat_id: int):
    is_antiservice = is_antiservice_on(chat_id)
    if is_antiservice:
        return
    return antiservicedb.delete_one({"chat_id": chat_id})


async def antiservice_off(chat_id: int):
    is_antiservice = is_antiservice_on(chat_id)
    if not is_antiservice:
        return
    return antiservicedb.insert_one({"chat_id": chat_id})
