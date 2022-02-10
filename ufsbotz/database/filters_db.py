import logging
from typing import Dict, List, Union

from ufsbotz.database import filtersdb, nsfw_filtersdb

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


async def get_filters_count() -> dict:
    chats = filtersdb.find({"chat_id": {"$lt": 0}})
    if not chats:
        return {}
    chats_count = 0
    filters_count = 0
    for chat in chats.to_list(length=1000000000):
        filters_name = get_filters_names(chat["chat_id"])
        filters_count += len(filters_name)
        chats_count += 1
    return {
        "chats_count": chats_count,
        "filters_count": filters_count,
    }


async def _get_filters(chat_id: int) -> Dict[str, int]:
    _filters = filtersdb.find_one({"chat_id": chat_id})
    if not _filters:
        return {}
    return _filters["filters"]


async def get_filters_names(chat_id: int) -> List[str]:
    _filters = []
    for _filter in await _get_filters(chat_id):
        _filters.append(_filter)
    return _filters


async def get_filter(chat_id: int, name: str) -> Union[bool, dict]:
    name = name.lower().strip()
    _filters = _get_filters(chat_id)
    if name in _filters:
        return _filters[name]
    return False


async def save_filter(chat_id: int, name: str, _filter: dict):
    name = name.lower().strip()
    _filters = _get_filters(chat_id)
    _filters[name] = _filter
    filtersdb.update_one(
        {"chat_id": chat_id},
        {"$set": {"filters": _filters}},
        upsert=True,
    )


async def delete_filter(chat_id: int, name: str) -> bool:
    filtersd = _get_filters(chat_id)
    name = name.lower().strip()
    if name in filtersd:
        del filtersd[name]
        filtersdb.update_one(
            {"chat_id": chat_id},
            {"$set": {"filters": filtersd}},
            upsert=True,
        )
        return True
    return False


async def set_nsfw_status(chat_id: int, allowed: bool):
    return nsfw_filtersdb.update_one(
        {"chat_id": chat_id}, {"$set": {"allowed": allowed}}, upsert=True
    )


async def get_nsfw_status(chat_id: int) -> bool:
    text = nsfw_filtersdb.find_one({"chat_id": chat_id})
    if not text:
        return False
    return text["allowed"]