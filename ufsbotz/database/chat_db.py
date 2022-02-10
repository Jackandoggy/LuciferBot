import logging

from ufsbotz.database import groupsdb

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


async def is_served_chat(chat_id: int) -> bool:
    chat = groupsdb.find_one({"chat_id": chat_id})
    return bool(chat)


async def get_served_chats() -> list:
    chats = groupsdb.find({"chat_id": {"$lt": 0}})
    if not chats:
        return []
    chats_list = []
    for chat in chats.to_list(length=1000000000):
        chats_list.append(chat)
    return chats_list


async def add_served_chat(chat_id: int):
    is_served = is_served_chat(chat_id)
    if is_served:
        return
    return groupsdb.insert_one({"chat_id": chat_id})


async def remove_served_chat(chat_id: int):
    is_served = is_served_chat(chat_id)
    if not is_served:
        return
    return groupsdb.delete_one({"chat_id": chat_id})
