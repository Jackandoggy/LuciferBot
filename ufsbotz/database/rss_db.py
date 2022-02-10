import logging

from ufsbotz.database import rssdb

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


async def add_rss_feed(chat_id: int, url: str, last_title: str):
    return rssdb.update_one(
        {"chat_id": chat_id},
        {"$set": {"url": url, "last_title": last_title}},
        upsert=True,
    )


async def remove_rss_feed(chat_id: int):
    return rssdb.delete_one({"chat_id": chat_id})


async def update_rss_feed(chat_id: int, last_title: str):
    return rssdb.update_one(
        {"chat_id": chat_id},
        {"$set": {"last_title": last_title}},
        upsert=True,
    )


async def is_rss_active(chat_id: int) -> bool:
    return rssdb.find_one({"chat_id": chat_id})


async def get_rss_feeds() -> list:
    feeds = rssdb.find({"chat_id": {"$exists": 1}})
    feeds = feeds.to_list(length=10000000)
    if not feeds:
        return
    return [dict(
                chat_id=feed["chat_id"],
                url=feed["url"],
                last_title=feed["last_title"],
            ) for feed in feeds]


async def get_rss_feeds_count() -> int:
    feeds = rssdb.find({"chat_id": {"$exists": 1}})
    feeds = feeds.to_list(length=10000000)
    return len(feeds)