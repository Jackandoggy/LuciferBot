from dotenv import load_dotenv
from os import environ, path


if path.exists("config.env"):
    load_dotenv("config.env")

BOT_TOKEN = environ.get("BOT_TOKEN", '1635091229:AAE40V_s07MAKJRDM-LTL2dPIXyG9iW8rBk')
API_ID = int(environ.get("API_ID", 3607361))
API_HASH = environ.get("API_HASH", "c57bcc4b09591db4f90f60b469e8870f")
USERBOT_ID = int(environ.get("OWNER_ID", 631110062))
SUDO_USERS_ID = [int(x) for x in environ.get("SUDO_USERS_ID", "631110062").split()]
LOG_GROUP_ID = int(environ.get("LOG_GROUP_ID", '-724048562'))
GBAN_LOG_GROUP_ID = int(environ.get("GBAN_LOG_GROUP_ID", '0'))
MESSAGE_DUMP_CHAT = int(environ.get("MESSAGE_DUMP_CHAT", '0'))
WELCOME_DELAY_KICK_SEC = int(environ.get("WELCOME_DELAY_KICK_SEC", '0'))
MONGO_URL = environ.get("MONGO_URL", 'mongodb+srv://jmjsoft:jins2010@ufstest.nqmjo.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')
ARQ_API_URL = environ.get("ARQ_API_URL", None)
ARQ_API_KEY = environ.get("ARQ_API_KEY", None)
RSS_DELAY = int(environ.get("RSS_DELAY", '0'))
PICS = (environ.get('PICS', 'https://telegra.ph/file/0ff51496ce70215e999b7.jpg https://telegra.ph/file/b5a8a390351662d134f64.jpg')).split()
UPSTREAM_REPO = environ.get("UPSTREAM_REPO", "https://github.com/rozari0/NezukoBot.git")
