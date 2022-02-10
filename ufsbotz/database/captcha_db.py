import logging

from ufsbotz.database import captchadb, solved_captcha_db, captcha_cachedb
from ufsbotz.utils.dbfunctions import obj_to_str, str_to_obj

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


async def is_captcha_on(chat_id: int) -> bool:
    chat = captchadb.find_one({"chat_id": chat_id})
    return not chat


async def captcha_on(chat_id: int):
    is_captcha = is_captcha_on(chat_id)
    if is_captcha:
        return
    return captchadb.delete_one({"chat_id": chat_id})


async def captcha_off(chat_id: int):
    is_captcha = is_captcha_on(chat_id)
    if not is_captcha:
        return
    return captchadb.insert_one({"chat_id": chat_id})


async def has_solved_captcha_once(chat_id: int, user_id: int):
    has_solved = solved_captcha_db.find_one(
        {"chat_id": chat_id, "user_id": user_id}
    )
    return bool(has_solved)


async def save_captcha_solved(chat_id: int, user_id: int):
    return solved_captcha_db.update_one(
        {"chat_id": chat_id},
        {"$set": {"user_id": user_id}},
        upsert=True,
    )


async def update_captcha_cache(captcha_dict):
    pickle = obj_to_str(captcha_dict)
    captcha_cachedb.delete_one({"captcha": "cache"})
    if not pickle:
        return
    captcha_cachedb.update_one(
        {"captcha": "cache"},
        {"$set": {"pickled": pickle}},
        upsert=True,
    )


async def get_captcha_cache():
    cache = captcha_cachedb.find_one({"captcha": "cache"})
    if not cache:
        return []
    return str_to_obj(cache["pickled"])
