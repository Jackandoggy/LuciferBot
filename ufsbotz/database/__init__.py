from pymongo import MongoClient

from sample_config import MONGO_URL

myclient = MongoClient(MONGO_URL)

# Your Data Base
mydb = myclient['UFSBOTZ']

# Your Collections
antiservicedb = mydb['Antiservice']
blacklist_filtersdb = mydb['BF_Filters']
blacklist_chatdb = mydb['BC_Filters']
welcomedb = mydb['Welcome']
welcome_url_db = mydb['Welcome_Urls']
leave_db = mydb['Leave_Urls']
usersdb = mydb['Users']
# warns_db = mydb['Warns']
f_warns_db = mydb['Warn_Filters']
s_warns_db = mydb['Warn_Settings']
sudoersdb = mydb['Sudoers']
stickerpacknamedb = mydb['Stick_Pack']
rssdb = mydb['Rss']
restart_stagedb = mydb['Restart']
pmpermitdb = mydb['PM_Permit']
pipesdb = mydb['Pipes']
notedb = mydb['Notes']
karmadb = mydb['Karma']
gbansdb = mydb['GBans']
flood_toggle_db = mydb['Flood']
filtersdb = mydb['Filters']
nsfw_filtersdb = mydb['NSFW_Filters']
coupledb = mydb['Couple']
conndb = mydb['Connection']
groupsdb = mydb['Groups']
captchadb = mydb['Captcha']
solved_captcha_db = mydb['Solved_Captcha']
captcha_cachedb = mydb['Cache_Captcha']