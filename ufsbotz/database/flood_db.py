import logging

from ufsbotz.database import flood_toggle_db

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


async def is_flood_on(chat_id: int) -> bool:
    chat = flood_toggle_db.find_one({"chat_id": chat_id})
    return not chat


async def flood_on(chat_id: int):
    is_flood = is_flood_on(chat_id)
    if is_flood:
        return
    return flood_toggle_db.delete_one({"chat_id": chat_id})


async def flood_off(chat_id: int):
    is_flood = is_flood_on(chat_id)
    if not is_flood:
        return
    return flood_toggle_db.insert_one({"chat_id": chat_id})