import logging

from ufsbotz.database import welcomedb

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

DEFAULT_WELCOME = "Hey {first}, how are you?"
DEFAULT_GOODBYE = "Nice knowing ya!"


async def get_welcome(chat_id: int) -> str:
    text = welcomedb.find_one({"chat_id": chat_id})
    if not text:
        return ""
    return text["text"]


async def set_welcome(chat_id: int, text: str):
    return welcomedb.update_one(
        {"chat_id": chat_id}, {"$set": {"text": text}}, upsert=True
    )


async def del_welcome(chat_id: int):
    return welcomedb.delete_one({"chat_id": chat_id})