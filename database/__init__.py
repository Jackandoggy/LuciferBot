
from sample_config import *
from motor.motor_asyncio import AsyncIOMotorClient as MongoClient

# MongoDB client
print("[INFO]: INITIALIZING DATABASE")
mongo_client = MongoClient(MONGO_URL)
ufs_db = mongo_client.ufsbotz
