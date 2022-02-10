import logging

from ufsbotz.database import gbansdb

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


async def get_gbans_count() -> int:
    users = gbansdb.find({"user_id": {"$gt": 0}})
    users = users.to_list(length=100000)
    return len(users)


async def is_gbanned_user(user_id: int) -> bool:
    user = gbansdb.find_one({"user_id": user_id})
    return bool(user)


async def add_gban_user(user_id: int):
    is_gbanned = is_gbanned_user(user_id)
    if is_gbanned:
        return
    return gbansdb.insert_one({"user_id": user_id})


async def remove_gban_user(user_id: int):
    is_gbanned = is_gbanned_user(user_id)
    if not is_gbanned:
        return
    return gbansdb.delete_one({"user_id": user_id})