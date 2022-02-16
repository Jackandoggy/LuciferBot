import logging
from typing import List

from ufsbotz.database import blacklist_filtersdb, blacklist_chatdb

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


async def get_blacklist_filters_count() -> dict:
    chats = blacklist_filtersdb.find({"chat_id": {"$lt": 0}})
    if not chats:
        return {"chats_count": 0, "filters_count": 0}
    chats_count = 0
    filters_count = 0
    for chat in chats.to_list(length=1000000000):
        filters = get_blacklisted_words(chat["chat_id"])
        filters_count += len(filters)
        chats_count += 1
    return {
        "chats_count": chats_count,
        "filters_count": filters_count,
    }


async def get_blacklisted_words(chat_id: int) -> List[str]:
    _filters = blacklist_filtersdb.find_one({"chat_id": chat_id})
    if not _filters:
        return []
    return _filters["filters"]


async def save_blacklist_filter(chat_id: int, word: str):
    word = word.lower().strip()
    _filters = get_blacklisted_words(chat_id)
    _filters.append(word)
    blacklist_filtersdb.update_one(
        {"chat_id": chat_id},
        {"$set": {"filters": _filters}},
        upsert=True,
    )


async def delete_blacklist_filter(chat_id: int, word: str) -> bool:
    filtersd = get_blacklisted_words(chat_id)
    word = word.lower().strip()
    if word in filtersd:
        filtersd.remove(word)
        blacklist_filtersdb.update_one(
            {"chat_id": chat_id},
            {"$set": {"filters": filtersd}},
            upsert=True,
        )
        return True
    return False


async def blacklisted_chats() -> list:
    chats = list(blacklist_chatdb.find({"chat_id": {"$lt": 0}}))
    return [chat["chat_id"] for chat in chats]      #.to_list(length=1000000000)


async def blacklist_chat(chat_id: int) -> bool:
    if not blacklist_chatdb.find_one({"chat_id": chat_id}):
        blacklist_chatdb.insert_one({"chat_id": chat_id})
        return True
    return False


async def whitelist_chat(chat_id: int) -> bool:
    if blacklist_chatdb.find_one({"chat_id": chat_id}):
        blacklist_chatdb.delete_one({"chat_id": chat_id})
        return True
    return False