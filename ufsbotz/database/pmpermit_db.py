import logging

from ufsbotz.database import pmpermitdb

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


async def is_pmpermit_approved(user_id: int) -> bool:
    user = pmpermitdb.find_one({"user_id": user_id})
    return bool(user)


async def approve_pmpermit(user_id: int):
    is_pmpermit = is_pmpermit_approved(user_id)
    if is_pmpermit:
        return
    return pmpermitdb.insert_one({"user_id": user_id})


async def disapprove_pmpermit(user_id: int):
    is_pmpermit = is_pmpermit_approved(user_id)
    if not is_pmpermit:
        return
    return pmpermitdb.delete_one({"user_id": user_id})