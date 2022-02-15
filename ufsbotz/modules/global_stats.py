import asyncio

from pyrogram import filters
from pyrogram.errors import FloodWait

from ufsbotz import BOT_ID, BOT_NAME, SUDOERS, ufs
from ufsbotz.core.decorators.errors import capture_err
from ufsbotz.database.blacklist_filters_db import get_blacklist_filters_count
from ufsbotz.database.chat_db import get_served_chats, remove_served_chat
from ufsbotz.database.filters_db import get_filters_count
from ufsbotz.database.gbans_db import get_gbans_count
from ufsbotz.database.karma_db import get_karmas_count
from ufsbotz.database.note_db import get_notes_count
from ufsbotz.database.rss_db import get_rss_feeds_count
from ufsbotz.database.users_db import get_served_users
from ufsbotz.modules import ALL_MODULES
from ufsbotz.utils.http import get
from ufsbotz.utils.inlinefuncs import keywords_list


@ufs.on_message(
    filters.command("clean_db") & filters.user(SUDOERS) & ~filters.edited
)
@capture_err
async def clean_db(_, message):
    served_chats = [int(i["chat_id"]) for i in (await get_served_chats())]
    m = await message.reply(
        f"__**Cleaning database, Might take around {len(served_chats) * 2} seconds.**__",
    )
    for served_chat in served_chats:
        try:
            await ufs.get_chat_members(served_chat, BOT_ID)
            await asyncio.sleep(2)
        except FloodWait as e:
            await asyncio.sleep(int(e.x))
        except Exception:
            await remove_served_chat(served_chat)
            served_chats.remove(served_chat)
    await m.edit("**Database Cleaned.**")


@ufs.on_message(
    filters.command("gstats") & filters.user(SUDOERS) & ~filters.edited
)
@capture_err
async def global_stats(_, message):
    m = await ufs.send_message(
        message.chat.id,
        text="__**Analysing Stats...**__",
        disable_web_page_preview=True,
    )

    # For bot served chat and users count
    served_chats = len(await get_served_chats())
    served_users = len(await get_served_users())
    # Gbans count
    gbans = await get_gbans_count()
    _notes = await get_notes_count()
    notes_count = _notes["notes_count"]
    notes_chats_count = _notes["chats_count"]

    # Filters count across chats
    _filters = await get_filters_count()
    filters_count = _filters["filters_count"]
    filters_chats_count = _filters["chats_count"]

    # Blacklisted filters count across chats
    _filters = await get_blacklist_filters_count()
    blacklist_filters_count = _filters["filters_count"]
    blacklist_filters_chats_count = _filters["chats_count"]

    # Warns count across chats
    _warns = await get_warns_count()
    warns_count = _warns["warns_count"]
    warns_chats_count = _warns["chats_count"]

    # Karmas count across chats
    _karmas = await get_karmas_count()
    karmas_count = _karmas["karmas_count"]
    karmas_chats_count = _karmas["chats_count"]

    # Contributors/Developers count and commits on github
    url = "https://api.github.com/repos/jinspalakkattu/LuciferBot/contributors"
    rurl = "https://github.com/jinspalakkattu/LuciferBot"
    developers = await get(url)
    commits = sum(developer["contributions"] for developer in developers)
    developers = len(developers)

    # Rss feeds
    rss_count = await get_rss_feeds_count()
    # Modules info
    modules_count = len(ALL_MODULES)

    # Userbot info
    groups_ub = channels_ub = bots_ub = privates_ub = total_ub = 0

    msg = f"""
**Global Stats of {BOT_NAME}**:
    **{modules_count}** Modules Loaded.
    **{len(keywords_list)}** Inline Modules Loaded.
    **{rss_count}** Active RSS Feeds.
    **{gbans}** Globally banned users.
    **{filters_count}** Filters, Across **{filters_chats_count}** chats.
    **{blacklist_filters_count}** Blacklist Filters, Across **{blacklist_filters_chats_count}** chats.
    **{notes_count}** Notes, Across **{notes_chats_count}** chats.
    **{warns_count}** Warns, Across **{warns_chats_count}** chats.
    **{karmas_count}** Karma, Across **{karmas_chats_count}** chats.
    **{served_users}** Users, Across **{served_chats}** chats.
    **{developers}** Developers And **{commits}** Commits On **[Github]({rurl})**.

"""
    await m.edit(msg, disable_web_page_preview=True)
