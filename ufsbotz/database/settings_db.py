import motor.motor_asyncio
from ufsbotz import MONGO_URL


class Settings:
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.sett = self.db.Settings

    def new_settings(self, chat_id, lock, time):
        return dict(
            chat_id=str(chat_id),
            button=lock, botpm=lock,
            file_secure=lock, imdb=lock,
            spell_check=lock, welcome=lock,
            auto_delete=lock, delete_time=time,
        )

    async def add_settings(self, chat_id, locked, time):
        locks = self.new_settings(str(chat_id), locked, time)
        await self.sett.insert_one(locks)

    async def is_settings_exist(self, chat_id):
        locks = await self.sett.find_one({'chat_id': str(chat_id)})
        return bool(locks)

    async def get_settings(self, chat_id):
        query = await self.sett.find_one({'chat_id': str(chat_id)})
        if query is not None:
            return query
        else:
            return None

    async def update_settings(self, chat_id, sett_type, lock, time):
        if sett_type == "button":
            await self.sett.update_one({'chat_id': str(chat_id)}, {'$set': {'button': lock}})
        elif sett_type == "botpm":
            await self.sett.update_one({'chat_id': str(chat_id)}, {'$set': {'botpm': lock}})
        elif sett_type == "file_secure":
            await self.sett.update_one({'chat_id': str(chat_id)}, {'$set': {'file_secure': lock}})
        elif sett_type == "imdb":
            await self.sett.update_one({'chat_id': str(chat_id)}, {'$set': {'imdb': lock}})
        elif sett_type == "spell_check":
            await self.sett.update_one({'chat_id': str(chat_id)}, {'$set': {'spell_check': lock}})
        elif sett_type == "welcome":
            await self.sett.update_one({'chat_id': str(chat_id)}, {'$set': {'welcome': lock}})
        elif sett_type == "delete":
            await self.sett.update_one({'chat_id': str(chat_id)}, {'$set': {'auto_delete': lock, 'delete_time': time}})


sett_db = Settings(MONGO_URL, 'UFSBOTZ')
