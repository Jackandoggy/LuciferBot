import logging

from ufsbotz.database import usersdb

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


async def is_served_user(user_id: int) -> bool:
    user = usersdb.find_one({"user_id": user_id})
    return bool(user)


async def get_served_users() -> list:
    users = usersdb.find({"user_id": {"$gt": 0}})
    if not users:
        return []
    users_list = []
    for user in users.to_list(length=1000000000):
        users_list.append(user)
    return users_list


async def add_served_user(user_id: int):
    is_served = await is_served_user(user_id)
    if is_served:
        return
    return usersdb.insert_one({"user_id": user_id})
