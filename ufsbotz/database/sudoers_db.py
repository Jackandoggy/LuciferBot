import logging

from ufsbotz.database import sudoersdb

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


async def get_sudoers() -> list:
    sudoers = sudoersdb.find_one({"sudo": "sudo"})
    if not sudoers:
        return []
    return sudoers["sudoers"]


async def add_sudo(user_id: int) -> bool:
    sudoers = get_sudoers()
    sudoers.append(user_id)
    sudoersdb.update_one(
        {"sudo": "sudo"}, {"$set": {"sudoers": sudoers}}, upsert=True
    )
    return True


async def remove_sudo(user_id: int) -> bool:
    sudoers = get_sudoers()
    sudoers.remove(user_id)
    sudoersdb.update_one(
        {"sudo": "sudo"}, {"$set": {"sudoers": sudoers}}, upsert=True
    )
    return True