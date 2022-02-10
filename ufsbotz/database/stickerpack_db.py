import logging

from ufsbotz.database import stickerpacknamedb

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


async def get_packname(chat_id: int) -> str:
    text = stickerpacknamedb.find_one({"chat_id": chat_id})
    if not text:
        return ""
    return text["text"]


async def set_packname(chat_id: int, text: str):
    return stickerpacknamedb.update_one(
        {"chat_id": chat_id}, {"$set": {"text": text}}, upsert=True
    )


async def del_packname(chat_id: int):
    return stickerpacknamedb.delete_one({"chat_id": chat_id})