import motor.motor_asyncio

from sample_config import MONGO_URL


class Database:
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.perm = self.db.permissions
        self.restr = self.db.restrictions

    def new_locks(self, chat_id, locked):
        return dict(
            chat_id=str(chat_id),
            audio=locked, voice=locked,
            contact=locked, video=locked,
            document=locked, photo=locked,
            sticker=locked, gif=locked,
            url=locked, bots=locked,
            forward=locked, game=locked,
            location=locked,
        )

    def new_restrictions(self, chat_id, locked):
        return dict(
            chat_id=str(chat_id),
            messages=locked, media=locked,
            other=locked, preview=locked,
        )

    async def add_locks(self, chat_id, locked):
        locks = self.new_locks(chat_id, locked)
        await self.perm.insert_one(locks)

    async def add_restrictions(self, chat_id, locked):
        restr = self.new_restrictions(chat_id, locked)
        await self.restr.insert_one(restr)

    async def is_locks_exist(self, chat_id):
        locks = await self.perm.find_one({'chat_id': str(chat_id)})
        return bool(locks)

    async def get_locks(self, chat_id):
        query = await self.perm.find_one({'chat_id': str(chat_id)})
        if query is not None:
            return query
        else:
            return None

    async def get_restrictions(self, chat_id):
        query = await self.restr.find_one({'chat_id': str(chat_id)})
        if query is not None:
            return query
        else:
            return None

    async def migrate_chat(self, old_chat_id, new_chat_id):
        await self.perm.update_one({'chat_id': str(old_chat_id)}, {'$set': {'chat_id': new_chat_id}})
        await self.restr.update_one({'chat_id': str(old_chat_id)}, {'$set': {'chat_id': new_chat_id}})

    async def update_locks(self, chat_id, lock_type, locked):
        if lock_type == "audio":
            await self.perm.update_one({'chat_id': str(chat_id)}, {'$set': {'audio': locked}})
        elif lock_type == "voice":
            await self.perm.update_one({'chat_id': str(chat_id)}, {'$set': {'voice': locked}})
        elif lock_type == "contact":
            await self.perm.update_one({'chat_id': str(chat_id)}, {'$set': {'contact': locked}})
        elif lock_type == "video":
            await self.perm.update_one({'chat_id': str(chat_id)}, {'$set': {'video': locked}})
        elif lock_type == "document":
            await self.perm.update_one({'chat_id': str(chat_id)}, {'$set': {'document': locked}})
        elif lock_type == "photo":
            await self.perm.update_one({'chat_id': str(chat_id)}, {'$set': {'photo': locked}})
        elif lock_type == "sticker":
            await self.perm.update_one({'chat_id': str(chat_id)}, {'$set': {'sticker': locked}})
        elif lock_type == "gif":
            await self.perm.update_one({'chat_id': str(chat_id)}, {'$set': {'gif': locked}})
        elif lock_type == 'url':
            await self.perm.update_one({'chat_id': str(chat_id)}, {'$set': {'url': locked}})
        elif lock_type == 'bots':
            await self.perm.update_one({'chat_id': str(chat_id)}, {'$set': {'bots': locked}})
        elif lock_type == 'forward':
            await self.perm.update_one({'chat_id': str(chat_id)}, {'$set': {'forward': locked}})
        elif lock_type == 'game':
            await self.perm.update_one({'chat_id': str(chat_id)}, {'$set': {'game': locked}})
        elif lock_type == 'location':
            await self.perm.update_one({'chat_id': str(chat_id)}, {'$set': {'location': locked}})

    async def update_restrictions(self, chat_id, restr_type, locked):
        if restr_type == "messages":
            await self.restr.update_one({'chat_id': str(chat_id)}, {'$set': {'messages': locked}})
        elif restr_type == "media":
            await self.restr.update_one({'chat_id': str(chat_id)}, {'$set': {'media': locked}})
        elif restr_type == "other":
            await self.restr.update_one({'chat_id': str(chat_id)}, {'$set': {'other': locked}})
        elif restr_type == "previews":
            await self.restr.update_one({'chat_id': str(chat_id)}, {'$set': {'preview': locked}})
        elif restr_type == "all":
            await self.restr.update_one({'chat_id': str(chat_id)}, {'$set': {'messages': locked}})
            await self.restr.update_one({'chat_id': str(chat_id)}, {'$set': {'media': locked}})
            await self.restr.update_one({'chat_id': str(chat_id)}, {'$set': {'other': locked}})
            await self.restr.update_one({'chat_id': str(chat_id)}, {'$set': {'preview': locked}})

    async def is_locked(self, chat_id, lock_type):
        curr_perm = await self.perm.find_one({'chat_id': str(chat_id)})

        if not curr_perm:
            return False

        elif lock_type == "sticker":
            return curr_perm['sticker']
        elif lock_type == "photo":
            return curr_perm['photo']
        elif lock_type == "audio":
            return curr_perm['audio']
        elif lock_type == "voice":
            return curr_perm['voice']
        elif lock_type == "contact":
            return curr_perm['contact']
        elif lock_type == "video":
            return curr_perm['video']
        elif lock_type == "document":
            return curr_perm['document']
        elif lock_type == "gif":
            return curr_perm['gif']
        elif lock_type == "url":
            return curr_perm['url']
        elif lock_type == "bots":
            return curr_perm['bots']
        elif lock_type == "forward":
            return curr_perm['forward']
        elif lock_type == "game":
            return curr_perm['game']
        elif lock_type == "location":
            return curr_perm['location']

    async def is_restr_locked(self, chat_id, lock_type):
        curr_restr = await self.restr.find_one({'chat_id': str(chat_id)})

        if not curr_restr:
            return False

        if lock_type == "messages":
            return curr_restr['messages']
        elif lock_type == "media":
            return curr_restr['media']
        elif lock_type == "other":
            return curr_restr['other']
        elif lock_type == "previews":
            return curr_restr['preview']
        elif lock_type == "all":
            return curr_restr['messages'] and curr_restr['media'] and curr_restr['other'] and curr_restr['preview']


lock_db = Database(MONGO_URL, 'UFSBOTZ')
