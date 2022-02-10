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
#
# # new db added
# connectiondb = ufs_db.connection
# settingsdb = ufs_db.settings

notesdb = ufs_db['notes']
filtersdb = ufs_db['filters']
warnsdb = ufs_db['warns']
karmadb = ufs_db['karma']
chatsdb = ufs_db['chats']
usersdb = ufs_db['users']
gbansdb = ufs_db['gban']
coupledb = ufs_db['couple']
captchadb = ufs_db['captcha']
solved_captcha_db = ufs_db['solved_captcha']
captcha_cachedb = ufs_db['captcha_cache']
antiservicedb = ufs_db['antiservice']
pmpermitdb = ufs_db['pmpermit']
welcomedb = ufs_db['welcome_text']
blacklist_filtersdb = ufs_db['blacklistFilters']
pipesdb = ufs_db['pipes']
sudoersdb = ufs_db['sudoers']
blacklist_chatdb = ufs_db['blacklistChat']
restart_stagedb = ufs_db['restart_stage']
flood_toggle_db = ufs_db['flood_toggle']
rssdb = ufs_db['rss']
stickerpackname = ufs_db['packname']
nsfw_filtersdb = ufs_db['nsfw_allowed']

# new db added
connectiondb = ufs_db['connection']
settingsdb = ufs_db['settings']


def obj_to_str(obj):
    if not obj:
        return False
    return codecs.encode(pickle.dumps(obj), "base64").decode()


def str_to_obj(string: str):
    return pickle.loads(codecs.decode(string.encode(), "base64"))


async def get_notes_count() -> dict:
    chats = notesdb.find({"chat_id": {"$exists": 1}})
    if not chats:
        return {}
    chats_count = 0
    notes_count = 0
    for chat in await chats.to_list(length=1000000000):
        notes_name = await get_note_names(chat["chat_id"])
        notes_count += len(notes_name)
        chats_count += 1
    return {"chats_count": chats_count, "notes_count": notes_count}


async def _get_notes(chat_id: int) -> Dict[str, int]:
    _notes = await notesdb.find_one({"chat_id": chat_id})
    if not _notes:
        return {}
    return _notes["notes"]


async def get_note_names(chat_id: int) -> List[str]:
    _notes = []
    for note in await _get_notes(chat_id):
        _notes.append(note)
    return _notes


async def get_note(chat_id: int, name: str) -> Union[bool, dict]:
    name = name.lower().strip()
    _notes = await _get_notes(chat_id)
    if name in _notes:
        return _notes[name]
    return False


async def save_note(chat_id: int, name: str, note: dict):
    name = name.lower().strip()
    _notes = await _get_notes(chat_id)
    _notes[name] = note

    await notesdb.update_one(
        {"chat_id": chat_id}, {"$set": {"notes": _notes}}, upsert=True
    )


async def delete_note(chat_id: int, name: str) -> bool:
    notesd = await _get_notes(chat_id)
    name = name.lower().strip()
    if name in notesd:
        del notesd[name]
        await notesdb.update_one(
            {"chat_id": chat_id},
            {"$set": {"notes": notesd}},
            upsert=True,
        )
        return True
    return False


async def get_filters_count() -> dict:
    chats = filtersdb.find({"chat_id": {"$lt": 0}})
    if not chats:
        return {}
    chats_count = 0
    filters_count = 0
    for chat in await chats.to_list(length=1000000000):
        filters_name = await get_filters_names(chat["chat_id"])
        filters_count += len(filters_name)
        chats_count += 1
    return {
        "chats_count": chats_count,
        "filters_count": filters_count,
    }


async def _get_filters(chat_id: int) -> Dict[str, int]:
    _filters = await filtersdb.find_one({"chat_id": chat_id})
    if not _filters:
        return {}
    return _filters["filters"]


async def get_filters_names(chat_id: int) -> List[str]:
    _filters = []
    for _filter in await _get_filters(chat_id):
        _filters.append(_filter)
    return _filters


async def get_filter(chat_id: int, name: str) -> Union[bool, dict]:
    name = name.lower().strip()
    _filters = await _get_filters(chat_id)
    if name in _filters:
        return _filters[name]
    return False


async def save_filter(chat_id: int, name: str, _filter: dict):
    name = name.lower().strip()
    _filters = await _get_filters(chat_id)
    _filters[name] = _filter
    await filtersdb.update_one(
        {"chat_id": chat_id},
        {"$set": {"filters": _filters}},
        upsert=True,
    )


async def delete_filter(chat_id: int, name: str) -> bool:
    filtersd = await _get_filters(chat_id)
    name = name.lower().strip()
    if name in filtersd:
        del filtersd[name]
        await filtersdb.update_one(
            {"chat_id": chat_id},
            {"$set": {"filters": filtersd}},
            upsert=True,
        )
        return True
    return False


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


async def get_warns_count() -> dict:
    chats = warnsdb.find({"chat_id": {"$lt": 0}})
    if not chats:
        return {}
    chats_count = 0
    warns_count = 0
    for chat in await chats.to_list(length=100000000):
        for user in chat["warns"]:
            warns_count += chat["warns"][user]["warns"]
        chats_count += 1
    return {"chats_count": chats_count, "warns_count": warns_count}


async def get_warns(chat_id: int) -> Dict[str, int]:
    warns = await warnsdb.find_one({"chat_id": chat_id})
    if not warns:
        return {}
    return warns["warns"]


async def get_warn(chat_id: int, name: str) -> Union[bool, dict]:
    name = name.lower().strip()
    warns = await get_warns(chat_id)
    if name in warns:
        return warns[name]


async def add_warn(chat_id: int, name: str, warn: dict):
    name = name.lower().strip()
    warns = await get_warns(chat_id)
    warns[name] = warn

    await warnsdb.update_one(
        {"chat_id": chat_id}, {"$set": {"warns": warns}}, upsert=True
    )


async def remove_warns(chat_id: int, name: str) -> bool:
    warnsd = await get_warns(chat_id)
    name = name.lower().strip()
    if name in warnsd:
        del warnsd[name]
        await warnsdb.update_one(
            {"chat_id": chat_id},
            {"$set": {"warns": warnsd}},
            upsert=True,
        )
        return True
    return False


async def get_karmas_count() -> dict:
    chats = karmadb.find({"chat_id": {"$lt": 0}})
    if not chats:
        return {}
    chats_count = 0
    karmas_count = 0
    for chat in await chats.to_list(length=1000000):
        for i in chat["karma"]:
            karma_ = chat["karma"][i]["karma"]
            if karma_ > 0:
                karmas_count += karma_
        chats_count += 1
    return {"chats_count": chats_count, "karmas_count": karmas_count}


async def user_global_karma(user_id) -> int:
    chats = karmadb.find({"chat_id": {"$lt": 0}})
    if not chats:
        return 0
    total_karma = 0
    for chat in await chats.to_list(length=1000000):
        karma = await get_karma(chat["chat_id"], await int_to_alpha(user_id))
        if karma and (int(karma["karma"]) > 0):
            total_karma += int(karma["karma"])
    return total_karma


async def get_karmas(chat_id: int) -> Dict[str, int]:
    karma = await karmadb.find_one({"chat_id": chat_id})
    if not karma:
        return {}
    return karma["karma"]


async def get_karma(chat_id: int, name: str) -> Union[bool, dict]:
    name = name.lower().strip()
    karmas = await get_karmas(chat_id)
    if name in karmas:
        return karmas[name]


async def update_karma(chat_id: int, name: str, karma: dict):
    name = name.lower().strip()
    karmas = await get_karmas(chat_id)
    karmas[name] = karma
    await karmadb.update_one(
        {"chat_id": chat_id}, {"$set": {"karma": karmas}}, upsert=True
    )


async def is_karma_on(chat_id: int) -> bool:
    chat = await karmadb.find_one({"chat_id_toggle": chat_id})
    return not chat


async def karma_on(chat_id: int):
    is_karma = await is_karma_on(chat_id)
    if is_karma:
        return
    return await karmadb.delete_one({"chat_id_toggle": chat_id})


async def karma_off(chat_id: int):
    is_karma = await is_karma_on(chat_id)
    if not is_karma:
        return
    return await karmadb.insert_one({"chat_id_toggle": chat_id})


async def is_served_chat(chat_id: int) -> bool:
    chat = await chatsdb.find_one({"chat_id": chat_id})
    return bool(chat)


async def get_served_chats() -> list:
    chats = chatsdb.find({"chat_id": {"$lt": 0}})
    if not chats:
        return []
    chats_list = []
    for chat in await chats.to_list(length=1000000000):
        chats_list.append(chat)
    return chats_list


async def add_served_chat(chat_id: int):
    is_served = await is_served_chat(chat_id)
    if is_served:
        return
    return await chatsdb.insert_one({"chat_id": chat_id})


async def remove_served_chat(chat_id: int):
    is_served = await is_served_chat(chat_id)
    if not is_served:
        return
    return await chatsdb.delete_one({"chat_id": chat_id})


async def is_served_user(user_id: int) -> bool:
    user = await usersdb.find_one({"user_id": user_id})
    return bool(user)


async def get_served_users() -> list:
    users = usersdb.find({"user_id": {"$gt": 0}})
    if not users:
        return []
    users_list = []
    for user in await users.to_list(length=1000000000):
        users_list.append(user)
    return users_list


async def add_served_user(user_id: int):
    is_served = await is_served_user(user_id)
    if is_served:
        return
    return await usersdb.insert_one({"user_id": user_id})


async def get_gbans_count() -> int:
    users = gbansdb.find({"user_id": {"$gt": 0}})
    users = await users.to_list(length=100000)
    return len(users)


async def is_gbanned_user(user_id: int) -> bool:
    user = await gbansdb.find_one({"user_id": user_id})
    return bool(user)


async def add_gban_user(user_id: int):
    is_gbanned = await is_gbanned_user(user_id)
    if is_gbanned:
        return
    return await gbansdb.insert_one({"user_id": user_id})


async def remove_gban_user(user_id: int):
    is_gbanned = await is_gbanned_user(user_id)
    if not is_gbanned:
        return
    return await gbansdb.delete_one({"user_id": user_id})


async def _get_lovers(chat_id: int):
    lovers = await coupledb.find_one({"chat_id": chat_id})
    if not lovers:
        return {}
    return lovers["couple"]


async def get_couple(chat_id: int, date: str):
    lovers = await _get_lovers(chat_id)
    if date in lovers:
        return lovers[date]
    return False


async def save_couple(chat_id: int, date: str, couple: dict):
    lovers = await _get_lovers(chat_id)
    lovers[date] = couple
    await coupledb.update_one(
        {"chat_id": chat_id},
        {"$set": {"couple": lovers}},
        upsert=True,
    )


async def is_captcha_on(chat_id: int) -> bool:
    chat = await captchadb.find_one({"chat_id": chat_id})
    return not chat


async def captcha_on(chat_id: int):
    is_captcha = await is_captcha_on(chat_id)
    if is_captcha:
        return
    return await captchadb.delete_one({"chat_id": chat_id})


async def captcha_off(chat_id: int):
    is_captcha = await is_captcha_on(chat_id)
    if not is_captcha:
        return
    return await captchadb.insert_one({"chat_id": chat_id})


async def has_solved_captcha_once(chat_id: int, user_id: int):
    has_solved = await solved_captcha_db.find_one(
        {"chat_id": chat_id, "user_id": user_id}
    )
    return bool(has_solved)


async def save_captcha_solved(chat_id: int, user_id: int):
    return await solved_captcha_db.update_one(
        {"chat_id": chat_id},
        {"$set": {"user_id": user_id}},
        upsert=True,
    )


async def is_antiservice_on(chat_id: int) -> bool:
    chat = await antiservicedb.find_one({"chat_id": chat_id})
    return not chat


async def antiservice_on(chat_id: int):
    is_antiservice = await is_antiservice_on(chat_id)
    if is_antiservice:
        return
    return await antiservicedb.delete_one({"chat_id": chat_id})


async def antiservice_off(chat_id: int):
    is_antiservice = await is_antiservice_on(chat_id)
    if not is_antiservice:
        return
    return await antiservicedb.insert_one({"chat_id": chat_id})


async def is_pmpermit_approved(user_id: int) -> bool:
    user = await pmpermitdb.find_one({"user_id": user_id})
    return bool(user)


async def approve_pmpermit(user_id: int):
    is_pmpermit = await is_pmpermit_approved(user_id)
    if is_pmpermit:
        return
    return await pmpermitdb.insert_one({"user_id": user_id})


async def disapprove_pmpermit(user_id: int):
    is_pmpermit = await is_pmpermit_approved(user_id)
    if not is_pmpermit:
        return
    return await pmpermitdb.delete_one({"user_id": user_id})


async def get_welcome(chat_id: int) -> str:
    text = await welcomedb.find_one({"chat_id": chat_id})
    if not text:
        return ""
    return text["text"]


async def set_welcome(chat_id: int, text: str):
    return await welcomedb.update_one(
        {"chat_id": chat_id}, {"$set": {"text": text}}, upsert=True
    )


async def del_welcome(chat_id: int):
    return await welcomedb.delete_one({"chat_id": chat_id})


async def update_captcha_cache(captcha_dict):
    pickle = obj_to_str(captcha_dict)
    await captcha_cachedb.delete_one({"captcha": "cache"})
    if not pickle:
        return
    await captcha_cachedb.update_one(
        {"captcha": "cache"},
        {"$set": {"pickled": pickle}},
        upsert=True,
    )


async def get_captcha_cache():
    cache = await captcha_cachedb.find_one({"captcha": "cache"})
    if not cache:
        return []
    return str_to_obj(cache["pickled"])


async def get_blacklist_filters_count() -> dict:
    chats = blacklist_filtersdb.find({"chat_id": {"$lt": 0}})
    if not chats:
        return {"chats_count": 0, "filters_count": 0}
    chats_count = 0
    filters_count = 0
    for chat in await chats.to_list(length=1000000000):
        filters = await get_blacklisted_words(chat["chat_id"])
        filters_count += len(filters)
        chats_count += 1
    return {
        "chats_count": chats_count,
        "filters_count": filters_count,
    }


async def get_blacklisted_words(chat_id: int) -> List[str]:
    _filters = await blacklist_filtersdb.find_one({"chat_id": chat_id})
    if not _filters:
        return []
    return _filters["filters"]


async def save_blacklist_filter(chat_id: int, word: str):
    word = word.lower().strip()
    _filters = await get_blacklisted_words(chat_id)
    _filters.append(word)
    await blacklist_filtersdb.update_one(
        {"chat_id": chat_id},
        {"$set": {"filters": _filters}},
        upsert=True,
    )


async def delete_blacklist_filter(chat_id: int, word: str) -> bool:
    filtersd = await get_blacklisted_words(chat_id)
    word = word.lower().strip()
    if word in filtersd:
        filtersd.remove(word)
        await blacklist_filtersdb.update_one(
            {"chat_id": chat_id},
            {"$set": {"filters": filtersd}},
            upsert=True,
        )
        return True
    return False


async def activate_pipe(from_chat_id: int, to_chat_id: int, fetcher: str):
    pipes = await show_pipes()
    pipe = {
        "from_chat_id": from_chat_id,
        "to_chat_id": to_chat_id,
        "fetcher": fetcher,
    }
    pipes.append(pipe)
    return await pipesdb.update_one(
        {"pipe": "pipe"}, {"$set": {"pipes": pipes}}, upsert=True
    )


async def deactivate_pipe(from_chat_id: int, to_chat_id: int):
    pipes = await show_pipes()
    if not pipes:
        return
    for pipe in pipes:
        if (
            pipe["from_chat_id"] == from_chat_id
            and pipe["to_chat_id"] == to_chat_id
        ):
            pipes.remove(pipe)
    return await pipesdb.update_one(
        {"pipe": "pipe"}, {"$set": {"pipes": pipes}}, upsert=True
    )


async def is_pipe_active(from_chat_id: int, to_chat_id: int) -> bool:
    for pipe in await show_pipes():
        if (
            pipe["from_chat_id"] == from_chat_id
            and pipe["to_chat_id"] == to_chat_id
        ):
            return True


async def show_pipes() -> list:
    pipes = await pipesdb.find_one({"pipe": "pipe"})
    if not pipes:
        return []
    return pipes["pipes"]


async def get_sudoers() -> list:
    sudoers = await sudoersdb.find_one({"sudo": "sudo"})
    if not sudoers:
        return []
    return sudoers["sudoers"]


async def add_sudo(user_id: int) -> bool:
    sudoers = await get_sudoers()
    sudoers.append(user_id)
    await sudoersdb.update_one(
        {"sudo": "sudo"}, {"$set": {"sudoers": sudoers}}, upsert=True
    )
    return True


async def remove_sudo(user_id: int) -> bool:
    sudoers = await get_sudoers()
    sudoers.remove(user_id)
    await sudoersdb.update_one(
        {"sudo": "sudo"}, {"$set": {"sudoers": sudoers}}, upsert=True
    )
    return True


async def blacklisted_chats() -> list:
    chats = blacklist_chatdb.find({"chat_id": {"$lt": 0}})
    return [chat["chat_id"] for chat in await chats.to_list(length=1000000000)]


async def blacklist_chat(chat_id: int) -> bool:
    if not await blacklist_chatdb.find_one({"chat_id": chat_id}):
        await blacklist_chatdb.insert_one({"chat_id": chat_id})
        return True
    return False


async def whitelist_chat(chat_id: int) -> bool:
    if await blacklist_chatdb.find_one({"chat_id": chat_id}):
        await blacklist_chatdb.delete_one({"chat_id": chat_id})
        return True
    return False


async def start_restart_stage(chat_id: int, message_id: int):
    await restart_stagedb.update_one(
        {"something": "something"},
        {
            "$set": {
                "chat_id": chat_id,
                "message_id": message_id,
            }
        },
        upsert=True,
    )


async def clean_restart_stage() -> dict:
    data = await restart_stagedb.find_one({"something": "something"})
    if not data:
        return {}
    await restart_stagedb.delete_one({"something": "something"})
    return {
        "chat_id": data["chat_id"],
        "message_id": data["message_id"],
    }


async def is_flood_on(chat_id: int) -> bool:
    chat = await flood_toggle_db.find_one({"chat_id": chat_id})
    return not chat


async def flood_on(chat_id: int):
    is_flood = await is_flood_on(chat_id)
    if is_flood:
        return
    return await flood_toggle_db.delete_one({"chat_id": chat_id})


async def flood_off(chat_id: int):
    is_flood = await is_flood_on(chat_id)
    if not is_flood:
        return
    return await flood_toggle_db.insert_one({"chat_id": chat_id})


async def add_rss_feed(chat_id: int, url: str, last_title: str):
    return await rssdb.update_one(
        {"chat_id": chat_id},
        {"$set": {"url": url, "last_title": last_title}},
        upsert=True,
    )


async def remove_rss_feed(chat_id: int):
    return await rssdb.delete_one({"chat_id": chat_id})


async def update_rss_feed(chat_id: int, last_title: str):
    return await rssdb.update_one(
        {"chat_id": chat_id},
        {"$set": {"last_title": last_title}},
        upsert=True,
    )


async def is_rss_active(chat_id: int) -> bool:
    return await rssdb.find_one({"chat_id": chat_id})


async def get_rss_feeds() -> list:
    feeds = rssdb.find({"chat_id": {"$exists": 1}})
    feeds = await feeds.to_list(length=10000000)
    if not feeds:
        return
    return [dict(
                chat_id=feed["chat_id"],
                url=feed["url"],
                last_title=feed["last_title"],
            ) for feed in feeds]


async def get_rss_feeds_count() -> int:
    feeds = rssdb.find({"chat_id": {"$exists": 1}})
    feeds = await feeds.to_list(length=10000000)
    return len(feeds)


async def get_packname(chat_id: int) -> str:
    text = await stickerpackname.find_one({"chat_id": chat_id})
    if not text:
        return ""
    return text["text"]


async def set_packname(chat_id: int, text: str):
    return await stickerpackname.update_one(
        {"chat_id": chat_id}, {"$set": {"text": text}}, upsert=True
    )


async def del_packname(chat_id: int):
    return await stickerpackname.delete_one({"chat_id": chat_id})


async def set_nsfw_status(chat_id: int, allowed: bool):
    return await nsfw_filtersdb.update_one(
        {"chat_id": chat_id}, {"$set": {"allowed": allowed}}, upsert=True
    )


async def get_nsfw_status(chat_id: int) -> bool:
    text = await nsfw_filtersdb.find_one({"chat_id": chat_id})
    if not text:
        return False
    return text["allowed"]


async def add_connection(group_id: str, user_id: str):
    # return await welcomedb.update_one(
    #     {"chat_id": str(chat_id)}, {"$set": {"text": text}}, upsert=True
    # )

    query = connectiondb.find_one(
        {"_id": user_id},
        {"_id": 0, "active_group": 0}
    )
    if query is not None:
        group_ids = [x["group_id"] for x in query["group_details"]]
        if group_id in group_ids:
            return False

    group_details = {
        "group_id": group_id
    }

    data = {
        '_id': user_id,
        'group_details': [group_details],
        'active_group': group_id,
    }

    if connectiondb.count_documents({"_id": user_id}) == 0:
        try:
            connectiondb.insert_one(data)
            return True
        except:
            print("[ERROR] Some Error Occured While Adding Connection!")
            # logger.exception('Some error occured!', exc_info=True)

    else:
        try:
            connectiondb.update_one(
                {'_id': user_id},
                {
                    "$push": {"group_details": group_details},
                    "$set": {"active_group": group_id}
                }
            )
            return True
        except:
            print("[ERROR] Some Error Occured While Adding Connection!")
            # logger.exception('Some error occured!', exc_info=True)


async def active_connection(user_id):
    query = connectiondb.find_one(
        {"_id": user_id},
        {"_id": 0, "group_details": 0}
    )
    if not query:
        return None

    group_id = query['active_group']
    if group_id is not None:
        return int(group_id)
    else:
        return None


async def all_connections(user_id):
    query = connectiondb.find_one(
        {"_id": user_id},
        {"_id": 0, "active_group": 0}
    )
    if query is not None:
        return [x["group_id"] for x in query["group_details"]]
    else:
        return None


async def if_active(user_id, group_id):
    query = connectiondb.find_one(
        {"_id": user_id},
        {"_id": 0, "group_details": 0}
    )
    return query is not None and query['active_group'] == group_id


async def make_active(user_id, group_id):
    update = connectiondb.update_one(
        {'_id': user_id},
        {"$set": {"active_group": group_id}}
    )
    return update.modified_count != 0


async def make_inactive(user_id):
    update = connectiondb.update_one(
        {'_id': user_id},
        {"$set": {"active_group": None}}
    )
    return update.modified_count != 0


async def delete_connection(user_id, group_id):
    try:
        update = connectiondb.update_one(
            {"_id": user_id},
            {"$pull": {"group_details": {"group_id": group_id}}}
        )
        if update.modified_count == 0:
            return False
        query = connectiondb.find_one(
            {"_id": user_id},
            {"_id": 0}
        )
        if len(query["group_details"]) >= 1:
            if query['active_group'] == group_id:
                prvs_group_id = query["group_details"][len(query["group_details"]) - 1]["group_id"]

                connectiondb.update_one(
                    {'_id': user_id},
                    {"$set": {"active_group": prvs_group_id}}
                )
        else:
            connectiondb.update_one(
                {'_id': user_id},
                {"$set": {"active_group": None}}
            )
        return True
    except Exception as e:
        print(f"[ERROR] Some error occurred! {e}")
        # logger.exception(f'Some error occurred! {e}', exc_info=True)
        return False


async def add_settings(group_id: str, lock: bool):
    query = settingsdb.find_one({'chat_id': str(group_id)})

    if query is not None:
        return False

    data = {
        'chat_id': group_id,
        'button': lock, 'botpm': lock,
        'file_secure': lock, 'imdb': lock,
        'spell_check': lock, 'welcome': lock,
        'auto_delete': lock, 'delete_time': lock,
    }

    if settingsdb.count_documents({"chat_id": group_id}) == 0:
        try:
            settingsdb.insert_one(data)
            return True
        except:
            print("[ERROR] Some Error Occurred While Adding Connection!")
            # logger.exception('Some error occurred!', exc_info=True)


async def is_settings_exist(chat_id):
    locks = await settingsdb.find_one({'chat_id': str(chat_id)})
    return bool(locks)


async def get_settings(chat_id):
    query = await settingsdb.find_one({'chat_id': str(chat_id)})
    if query is not None:
        return query
    else:
        return None


async def update_settings(chat_id, sett_type, lock, time):
    if sett_type == "button":
        await settingsdb.update_one({'chat_id': str(chat_id)}, {'$set': {'button': lock}})
    elif sett_type == "botpm":
        await settingsdb.update_one({'chat_id': str(chat_id)}, {'$set': {'botpm': lock}})
    elif sett_type == "file_secure":
        await settingsdb.update_one({'chat_id': str(chat_id)}, {'$set': {'file_secure': lock}})
    elif sett_type == "imdb":
        await settingsdb.update_one({'chat_id': str(chat_id)}, {'$set': {'imdb': lock}})
    elif sett_type == "spell_check":
        await settingsdb.update_one({'chat_id': str(chat_id)}, {'$set': {'spell_check': lock}})
    elif sett_type == "welcome":
        await settingsdb.update_one({'chat_id': str(chat_id)}, {'$set': {'welcome': lock}})
    elif sett_type == "delete":
        await settingsdb.update_one({'chat_id': str(chat_id)}, {'$set': {'auto_delete': lock, 'delete_time': time}})
