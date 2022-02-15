import logging

import motor.motor_asyncio

from sample_config import MONGO_URL

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

# #################################################################################################

# async def get_warns_count() -> dict:
#     chats = warns_db.find({"chat_id": {"$lt": 0}})
#     if not chats:
#         return {}
#     chats_count = 0
#     warns_count = 0
#     for chat in chats.to_list(length=100000000):
#         for user in chat["warns"]:
#             warns_count += chat["warns"][user]["warns"]
#         chats_count += 1
#     return {"chats_count": chats_count, "warns_count": warns_count}
#
#
# async def get_warns(chat_id: int) -> Dict[str, int]:
#     warns = warns_db.find_one({"chat_id": chat_id})
#     if not warns:
#         return {}
#     return warns["warns"]
#
#
# async def get_warn(chat_id: int, name: str) -> Union[bool, dict]:
#     name = name.lower().strip()
#     warns = get_warns(chat_id)
#     if name in warns:
#         return warns[name]
#
#
# async def add_warn(chat_id: int, name: str, warn: dict):
#     name = name.lower().strip()
#     warns = get_warns(chat_id)
#     warns[name] = warn
#
#     warns_db.update_one(
#         {"chat_id": chat_id}, {"$set": {"warns": warns}}, upsert=True
#     )
#
#
# async def remove_warns(chat_id: int, name: str) -> bool:
#     warnsd = get_warns(chat_id)
#     name = name.lower().strip()
#     if name in warnsd:
#         del warnsd[name]
#         warns_db.update_one(
#             {"chat_id": chat_id},
#             {"$set": {"warns": warnsd}},
#             upsert=True,
#         )
#         return True
#     return False

#######################################################################################################


class Database:
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.warns = self.db.Warns
        self.f_warns = self.db.Warns_Filters
        self.s_warns = self.db.Warns_Settings

    def new_warns(self, user_id, chat_id, num_warns):
        return dict(
            user_id=int(user_id),
            chat_id=str(chat_id),
            num_warns=int(num_warns), ban_reason=dict(reasons='',),
        )

    def new_warn_filters(self, chat_id, keyword, reply):
        return dict(
            chat_id=str(chat_id),
            keyword=keyword, reply=reply,
        )

    def new_warn_settings(self, chat_id, warn_limit, soft_warn):
        return dict(
            chat_id=str(chat_id),
            warn_limit=warn_limit, soft_warn=soft_warn,
        )

    async def add_warns(self, user_id, chat_id, reasons=None):
        warn_user = await self.warns.find_one({'user_id': int(user_id), 'chat_id': str(chat_id)})

        if not warn_user:
            warn = self.new_warns(user_id, chat_id, 0)
            await self.warns.insert_one(warn)
            warn_user = await self.warns.find_one({'user_id': int(user_id), 'chat_id': str(chat_id)})

        num_warns = int(warn_user['num_warns']) + 1
        await self.warns.update_one({'user_id': int(user_id), 'chat_id': str(chat_id)}, {'$set': {'num_warns': num_warns}})

        if reasons:
            ban_reason = {
                "reasons": reasons
            }

            try:
                await self.warns.update_one(
                    {'user_id': int(user_id)},
                    {
                        "$push": {"ban_reason": ban_reason}
                    }
                )
            except:
                logger.exception('Some error occured!', exc_info=True)

        warn_user = await self.warns.find_one({'user_id': int(user_id), 'chat_id': str(chat_id)})
        if warn_user is not None:
            return warn_user["num_warns"], [x["reasons"] for x in warn_user["ban_reason"]]

    async def add_warn_filters(self, chat_id, keyword, reply):
        fwarns = self.new_warn_filters(chat_id, keyword, reply)
        await self.f_warns.insert_one(fwarns)

    async def add_warn_settings(self, chat_id, warn_limit, soft_warn):
        swarns = self.new_warn_settings(chat_id, warn_limit, soft_warn)
        await self.s_warns.insert_one(swarns)

    async def is_warns_exist(self, user_id, chat_id):
        warn = await self.warns.find_one({'user_id': int(user_id), 'chat_id': str(chat_id)})
        return bool(warn)

    async def is_fwarns_exist(self, chat_id):
        fwarn = await self.f_warns.find_one({'chat_id': str(chat_id)})
        return bool(fwarn)

    async def is_swarns_exist(self, chat_id):
        swarn = await self.s_warns.find_one({'chat_id': str(chat_id)})
        return bool(swarn)

    async def reset_warns(self, user_id, chat_id):
        try:
            await self.warns.update_one({'user_id': int(user_id), 'chat_id': str(chat_id)},
                                        {'$set': {'num_warns': 0}})
            return
        except Exception as e:
            logger.exception(f'Some error occured! {e}', exc_info=True)
            return

    async def get_warns(self, user_id, chat_id):
        query = await self.warns.find_one({'user_id': int(user_id), 'chat_id': str(chat_id)})
        if query is not None:
            result = (query['num_warns'], query['reasons'])
            return result
        else:
            return None

    async def get_warn_filters(self, chat_id, keyword):
        query = await self.f_warns.find_one({'chat_id': str(chat_id), 'keyword': keyword})
        if query is not None:
            return query
        else:
            return None

    async def get_chat_warn_filters(self, chat_id):
        query = await self.f_warns.find_one({'chat_id': str(chat_id)})
        if query is not None:
            return query
        else:
            return None

    async def get_warn_settings(self, chat_id):
        query = await self.s_warns.find_one({'chat_id': str(chat_id)})
        if query is not None:
            return query['warn_limit'], query['soft_warn']
        else:
            return 3, False

    async def remove_warn(self, user_id, chat_id):
        removed = False
        warned_user = await self.warns.find_one({'user_id': int(user_id), 'chat_id': str(chat_id)})

        if warned_user and int(warned_user['num_warns']) > 0:
            num_warns = int(warned_user['num_warns']) - 1
            await self.warns.update_one({'user_id': int(user_id), 'chat_id': str(chat_id)},
                                        {'$set': {'num_warns': num_warns}})
            removed = True
        return removed

    async def remove_warn_filters(self, chat_id, keyword):
        myquery = {'chat_id': str(chat_id), 'keyword': keyword}
        query = self.f_warns.count_documents(myquery)

        if query == 1:
            self.f_warns.delete_one(myquery)
            return f"Okey, I'll Stop Warning People For This `{keyword}` Word."
        else:
            return "Couldn't Find That Filter!"

    async def set_warn_limit(self, chat_id, warn_limit):
        await self.s_warns.update_one({'chat_id': str(chat_id)}, {'$set': {'warn_limit': warn_limit}})

    async def num_warns(self):
        count = await self.warns.aggregate([{'total': {'$sum': '$num_warns'}}])
        return count['total']

    async def num_warn_chats(self):
        count = await self.warns.distinct('chat_id')
        return len(count)

    async def num_warn_filters(self):
        count = await self.f_warns.count_documents({})
        return count

    async def num_warn_filter_chats(self):
        count = await self.f_warns.distinct('chat_id')
        return len(count)

    async def num_warn_chat_filters(self, chat_id):
        count = await self.f_warns.count_documents({'chat_id': str(chat_id)})
        return count

    async def migrate_chat(self, old_chat_id, new_chat_id):
        await self.warns.update_one({'chat_id': str(old_chat_id)}, {'$set': {'chat_id': new_chat_id}})
        await self.f_warns.update_one({'chat_id': str(old_chat_id)}, {'$set': {'chat_id': new_chat_id}})
        await self.s_warns.update_one({'chat_id': str(old_chat_id)}, {'$set': {'chat_id': new_chat_id}})


warns_db = Database(MONGO_URL, 'UFSBOTZ')
