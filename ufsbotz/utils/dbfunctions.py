import codecs
import pickle
from typing import Dict, List, Union

from ufsbotz import ufs_db

# SOME THINGS ARE FUCKED UP HERE, LIKE TOGGLEABLES HAVE THEIR OWN COLLECTION
# (SHOULD FIX IT WITH SOMETHING LIKE TOGGLEDB), MOST OF THE CODE IS BAD AF
# AND NEEDS TO BE REWRITTEN, BUT I WON'T, AS IT WILL TAKE
# TOO MUCH TIME AND WILL BE BAD FOR ALREADY STORED DATA


# notesdb = ufs_db.notes
# filtersdb = ufs_db.filters
# warnsdb = ufs_db.warns
# karmadb = ufs_db.karma
# chatsdb = ufs_db.chats
# usersdb = ufs_db.users
# gbansdb = ufs_db.gban
# coupledb = ufs_db.couple
# captchadb = ufs_db.captcha
# solved_captcha_db = ufs_db.solved_captcha
# captcha_cachedb = ufs_db.captcha_cache
# antiservicedb = ufs_db.antiservice
# pmpermitdb = ufs_db.pmpermit
# welcomedb = ufs_db.welcome_text
# blacklist_filtersdb = ufs_db.blacklistFilters
# pipesdb = ufs_db.pipes
# sudoersdb = ufs_db.sudoers
# blacklist_chatdb = ufs_db.blacklistChat
# restart_stagedb = ufs_db.restart_stage
# flood_toggle_db = ufs_db.flood_toggle
# rssdb = ufs_db.rss
# stickerpackname = ufs_db.packname
# nsfw_filtersdb = ufs_db.nsfw_allowed

# notesdb = ufs_db['notes']
# filtersdb = ufs_db['filters']
# warnsdb = ufs_db['warns']
# karmadb = ufs_db['karma']
# chatsdb = ufs_db['chats']
# usersdb = ufs_db['users']
# gbansdb = ufs_db['gban']
# coupledb = ufs_db['couple']
# captchadb = ufs_db['captcha']
# solved_captcha_db = ufs_db['solved_captcha']
# captcha_cachedb = ufs_db['captcha_cache']
# antiservicedb = ufs_db['antiservice']
# pmpermitdb = ufs_db['pmpermit']
# welcomedb = ufs_db['welcome_text']
# blacklist_filtersdb = ufs_db['blacklistFilters']
# pipesdb = ufs_db['pipes']
# sudoersdb = ufs_db['sudoers']
# blacklist_chatdb = ufs_db['blacklistChat']
# restart_stagedb = ufs_db['restart_stage']
# flood_toggle_db = ufs_db['flood_toggle']
# rssdb = ufs_db['rss']
# stickerpackname = ufs_db['packname']
# nsfw_filtersdb = ufs_db['nsfw_allowed']
#
# # new db added
# connectiondb = ufs_db['connection']
# settingsdb = ufs_db['settings']


def obj_to_str(obj):
    if not obj:
        return False
    return codecs.encode(pickle.dumps(obj), "base64").decode()


def str_to_obj(string: str):
    return pickle.loads(codecs.decode(string.encode(), "base64"))


async def int_to_alpha(user_id: int) -> str:
    alphabet = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"]
    user_id = str(user_id)
    return "".join(alphabet[int(i)] for i in user_id)


async def alpha_to_int(user_id_alphabet: str) -> int:
    alphabet = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"]
    user_id = ""
    for i in user_id_alphabet:
        index = alphabet.index(i)
        user_id += str(index)
    user_id = int(user_id)
    return user_id
