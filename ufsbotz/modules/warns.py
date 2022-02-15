import html
import re

import pyrogram
from pyrogram import filters
from pyrogram.errors import ChatAdminRequired, BadRequest
from pyrogram.types import User, Chat, InlineKeyboardMarkup, InlineKeyboardButton

from ufsbotz import *
from ufsbotz.core.decorators.errors import capture_err

from ufsbotz.database.warns_db import warns_db
from ufsbotz.helper_fn.chat_status import user_admin, get_active_connection, is_user_admin, adminsOnly, bot_admin, \
    user_admin_no_reply
from ufsbotz.helper_fn.misc import CustomFilters
from ufsbotz.helper_fn.string_handling import split_quotes, split_message
from ufsbotz.utils.filter_groups import WARN_HANDLER_GROUP
from ufsbotz.utils.functions import extract_userid, extract_user_and_reason, extract_text

CURRENT_WARNING_FILTER_STRING = "<b>Current Warning Filters In This Chat: </b>"


def warn(user: User, chat: Chat, reason: str, message: Message, warner: User = None) -> str:
    if is_user_admin(chat, user.id):
        message.reply_text("Damn admins, can't even be warned!")
        return ""

    if warner:
        warner_tag = warner.mention  # mention_html(warner.id, warner.first_name)
    else:
        warner_tag = "Automated Warn Filter."

    limit, soft_warn = warns_db.get_warn_settings(chat.id)
    num_warns, reasons = warns_db.add_warns(user.id, chat.id, reason)
    if num_warns >= limit:
        warns_db.reset_warns(user.id, chat.id)
        if soft_warn:  # kick
            chat.unban_member(user.id)
            reply = "{} warnings, {} has been kicked!".format(limit, user.mention)

        else:  # ban
            chat.ban_member(user.id)
            reply = "{} warnings, {} has been banned!".format(limit, user.mention)

        for warn_reason in reasons:
            reply += "\n - {}".format(html.escape(warn_reason))

        # message.bot.send_sticker(chat.id, BAN_STICKER)  #Coffin Elvira sticker
        keyboard = []
        log_reason = "<b>{}:</b>" \
                     "\n#WARN_BAN" \
                     "\n<b>Admin:</b> {}" \
                     "\n<b>User:</b> {}" \
                     "\n<b>Reason:</b> {}" \
                     "\n<b>Counts:</b> <code>{}/{}</code>".format(html.escape(chat.title),
                                                                  warner_tag, user.mention,
                                                                  reason, num_warns, limit)

    else:
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Remove warn (Admin only)", callback_data="rm_warn({})".format(user.id))]])

        reply = "{} has {}/{} warnings... watch out!".format(user.mention, num_warns, limit)
        if reason:
            reply += "\nReason for last warn:\n{}".format(html.escape(reason))

        log_reason = "<b>{}:</b>" \
                     "\n#WARN" \
                     "\n<b>Admin:</b> {}" \
                     "\n<b>User:</b> {}" \
                     "\n<b>Reason:</b> {}" \
                     "\n<b>Counts:</b> <code>{}/{}</code>".format(html.escape(chat.title),
                                                                  warner_tag, user.mention,
                                                                  reason, num_warns, limit)

    try:
        message.reply_text(reply, reply_markup=keyboard)
    except BadRequest as excp:
        if excp.MESSAGE == "Reply message not found":
            # Do not reply
            message.reply_text(reply, reply_markup=keyboard, quote=False)
        else:
            raise
    return log_reason


@ufs.on_message(filters.command("warn") & filters.group & ~filters.edited)
@user_admin
@adminsOnly("can_restrict_members")
@capture_err
async def warn_user(client, message):
    CHAT = message.chat
    WARNER = message.from_user

    user_id, reason = extract_user_and_reason(message)

    if user_id:
        if message.reply_to_message and message.reply_to_message.from_user.id == user_id:
            log_reason = warn(message.reply_to_message.from_user, CHAT, reason, message.reply_to_message, WARNER)
        else:
            log_reason = warn(CHAT.get_member(user_id).user, CHAT, reason, message, WARNER)

        if LOG_CHANNEL:
            try:
                return await client.send_message(LOG_CHANNEL, log_reason)
            except ChatAdminRequired:
                await message.reply_text("Log Channel Error, Should Be Log Channel Admin With Write Permission")
                return
        else:
            return
    else:
        message.reply_text("No user was designated!")
    return


@ufs.on_message(filters.command(["resetwarn", "resetwarns"]) & filters.group & ~filters.edited)
@user_admin
@bot_admin
@capture_err
async def reset_warns(client, message):
    CHAT = message.chat

    args = message.text.split(None, 1)

    user_id = extract_userid(message, args[1]) or message.from_user.id

    if user_id:
        warns_db.reset_warns(user_id, CHAT.id)
        await message.reply_text("Warnings have been reset!")
        warned = CHAT.get_member(user_id).user
        log = "<b>{}:</b>" \
              "\n#RESETWARNS" \
              "\n<b>Admin:</b> {}" \
              "\n<b>User:</b> {}".format(html.escape(CHAT.title), message.from_user.mention, warned.mention)

        if LOG_CHANNEL:
            try:
                return await client.send_message(LOG_CHANNEL, log)
            except ChatAdminRequired:
                await message.reply_text("Log Channel Error, Should Be Log Channel Admin With Write Permission")
                return
        else:
            return
    else:
        message.reply_text("No user has been designated!")
    return ""


@ufs.on_message(filters.command("warns") & filters.group & ~filters.edited)
async def warns(client, message):
    CHAT = message.chat

    args = message.text.split(None, 1)

    user_id = extract_userid(message, args[1]) or message.from_user.id
    result = await warns_db.get_warns(user_id, CHAT.id)

    if result and result[0] != 0:
        num_warns, reasons = result
        limit, soft_warn = await warns_db.get_warn_settings(CHAT.id)

        if reasons:
            text = "This user has {}/{} warnings, for the following reasons:".format(num_warns, limit)
            for reason in reasons:
                text += "\n - {}".format(reason)

            msgs = split_message(text)
            for msg in msgs:
                await message.reply_text(msg)
        else:
            await message.reply_text(
                "User has {}/{} warnings, but no reasons for any of them.".format(num_warns, limit))
    else:
        await message.reply_text("This user hasn't got any warnings!")


@ufs.on_callback_query(filters.regex('rm_warn'))
@user_admin_no_reply
@bot_admin
@capture_err
async def cbh_rm_warn(client, query):
    global log
    user = query.from_user
    match = re.match(r"rm_warn\((.+?)\)", query.data)
    if match:
        user_id = match.group(1)
        chat = query.chat
        res = await warns_db.remove_warn(user_id, chat.id)
        if res:
            await query.message.edit_text("Warn Removed by {}.".format(user.mention))
            user_member = chat.get_member(user_id)
            log = "<b>{}:</b>" \
                  "\n#UNWARN" \
                  "\n<b>Admin:</b> {}" \
                  "\n<b>User:</b> {}".format(html.escape(chat.title), user.mention, user_member.user.mention)
        else:
            await query.message.edit_text("User has already has no warns.".format(user.mention))

        if LOG_CHANNEL:
            try:
                return await client.send_message(LOG_CHANNEL, log)
            except ChatAdminRequired:
                await query.message.reply_text("Log Channel Error, Should Be Log Channel Admin With Write Permission")
                return
        else:
            return

    return ""


@ufs.on_message(filters.command("addwarn") & filters.private & ~filters.edited)
@user_admin
@capture_err
def add_warn_filter(client, message):
    CHAT_ID, TITLE, STATUS, ERROR = get_active_connection(client, message)

    if not STATUS:
        message.reply_text(ERROR, quote=True)
        return

    args = message.text.split(None, 1)

    if len(args) < 2:
        return

    extracted = split_quotes(args[1])

    if len(extracted) >= 2:
        keyword = extracted[0].lower()
        content = extracted[1]

    else:
        return

    warns_db.add_warns(CHAT_ID, keyword, content)

    message.reply_text("Warn Handler Added For `{}`!".format(keyword))
    return


@ufs.on_message(filters.command(["nowarn", "stopwarn"]) & filters.private & ~filters.edited)
@user_admin
@capture_err
def remove_warn_filter(client, message):
    CHAT_ID, TITLE, STATUS, ERROR = get_active_connection(client, message)

    if not STATUS:
        message.reply_text(ERROR, quote=True)
        return

    args = message.text.split(None, 1)  # use python's maxsplit to separate Cmd, keyword, and reply_text

    if len(args) < 2:
        return

    extracted = split_quotes(args[1])

    if len(extracted) < 1:
        return

    to_remove = extracted[0]

    chat_filters = warns_db.get_chat_warn_filters(CHAT_ID)

    if not chat_filters:
        message.reply_text("No Warning Filters Are Active Here!")
        return

    for filt in chat_filters:
        if filt['keyword'] == to_remove:
            msg = warns_db.remove_warn_filters(CHAT_ID, to_remove)
            message.reply_text(msg, quote=True)
            return

    message.reply_text(f"That's Not A Current Warning Filter - Run /warnlist "
                       f"For All Active Warning Filters For Your Chat `{TITLE}`.")


@ufs.on_message(filters.command(["warnlist", "warnfilters"]) & filters.private & ~filters.edited)
@capture_err
async def list_warn_filters(client, message):
    CHAT_ID, TITLE, STATUS, ERROR = get_active_connection(client, message)

    if not STATUS:
        await message.reply_text(ERROR, quote=True)
        return

    all_handlers = warns_db.get_chat_warn_filters(CHAT_ID)

    if not all_handlers:
        await message.reply_text("No Warning Filters Are Active Here!")
        return

    filter_list = CURRENT_WARNING_FILTER_STRING + "<b>" + TITLE + "</b>\n"
    for keyword in all_handlers:
        entry = " - `{}`\n".format(keyword['keyword'])
        if len(entry) + len(filter_list) > MAX_MESSAGE_LENGTH:
            await message.reply_text(filter_list)
            filter_list = entry
        else:
            filter_list += entry

    if not filter_list == CURRENT_WARNING_FILTER_STRING:
        await message.reply_text(filter_list)


@ufs.on_message(CustomFilters.has_text & filters.group, group=WARN_HANDLER_GROUP)
@capture_err
async def reply_filter(client, message):
    global log_reason
    chat = message.chat

    chat_warn_filters = await warns_db.get_chat_warn_filters(chat.id)
    to_match = extract_text(message)
    if not to_match:
        return ""

    for keyword in chat_warn_filters:
        pattern = r"( |^|[^\w])" + re.escape(keyword['keyword']) + r"( |$|[^\w])"
        if re.search(pattern, to_match, flags=re.IGNORECASE):
            user = message.from_user
            warn_filter = await warns_db.get_warn_filters(chat.id, keyword)
            log_reason = warn(user, chat, warn_filter.reply, message)

    if LOG_CHANNEL:
        try:
            return await client.send_message(LOG_CHANNEL, log_reason)
        except ChatAdminRequired:
            await message.reply_text("Log Channel Error, Should Be Log Channel Admin With Write Permission")
            return
    else:
        return


@ufs.on_message(filters.command("warnlimit") & filters.private & ~filters.edited)
@user_admin
@capture_err
async def set_warn_limit(client, message):
    CHAT_ID, TITLE, STATUS, ERROR = get_active_connection(client, message)

    if not STATUS:
        await message.reply_text(ERROR, quote=True)
        return

    args = message.text.split(None, 1)

    if args:
        if args[1].isdigit():
            if int(args[1]) < 3:
                await message.reply_text("The Minimum Warn Limit Is 3!")
            else:
                await warns_db.set_warn_limit(CHAT_ID, int(args[1]))
                await message.reply_text("Updated The Warn Limit To {}".format(args[1]))
                log = "**{}:**" \
                      "\n#SET_WARN_LIMIT" \
                      "\n**Admin:** {}" \
                      "\nSet The Warn Limit To <code>{}</code>.".format(TITLE, message.from_user.mention,
                                                                        str(args[1]).lower())
                if LOG_CHANNEL:
                    try:
                        return await client.send_message(LOG_CHANNEL, log)
                    except ChatAdminRequired:
                        await message.reply_text("Log Channel Error, Should Be Log Channel Admin With Write Permission")
                        return
                else:
                    return
        else:
            await message.reply_text("Give Me A Number As An Arg!")
    else:
        limit, soft_warn = await warns_db.get_warn_settings(CHAT_ID)

        await message.reply_text("The Current Warn Limit Is {}".format(limit))
    return


@ufs.on_message(filters.command("strongwarn") & filters.private & ~filters.edited)
@user_admin
@capture_err
async def set_warn_strength(client, message):
    global log
    CHAT_ID, TITLE, STATUS, ERROR = get_active_connection(client, message)

    if not STATUS:
        await message.reply_text(ERROR, quote=True)
        return

    args = message.text.split(None, 1)

    if args:
        if args[1].lower() in ("on", "yes"):
            await warns_db.set_warn_strength(CHAT_ID, False)
            await message.reply_text("Too many warns will now result in a ban!")

            log = "**{}:**" \
                  "\n#STRONG_WARNS" \
                  "\n**Admin:** {}" \
                  "\nHas Enabled Strong Warns. Users Will Be Banned.".format(TITLE, message.from_user.mention)

        elif args[0].lower() in ("off", "no"):
            await warns_db.set_warn_strength(CHAT_ID, True)
            await message.reply_text(
                "Too many warns will now result in a kick! Users will be able to join again after.")

            log = "**{}:**" \
                  "\n#STRONG_WARNS" \
                  "\n**Admin:** {}" \
                  "\nHas disabled strong warns. Users will only be kicked.".format(TITLE, message.from_user.mention)

        else:
            await message.reply_text("I Only Understand on/yes/no/off!")

        if LOG_CHANNEL:
            try:
                return await client.send_message(LOG_CHANNEL, log)
            except ChatAdminRequired:
                await message.reply_text("Log Channel Error, Should Be Log Channel Admin With Write Permission")
                return
        else:
            return
    else:
        limit, soft_warn = await warns_db.get_warn_settings(CHAT_ID)
        if soft_warn:
            await message.reply_text("Warns are currently set to **kick** users when they exceed the limits.")
        else:
            await message.reply_text("Warns are currently set to **ban** users when they exceed the limits.")
    return


def __stats__():
    return "{} overall warns, across {} chats.\n" \
           "{} warn filters, across {} chats.".format(warns_db.num_warns(), warns_db.num_warn_chats(),
                                                      warns_db.num_warn_filters(),
                                                      warns_db.num_warn_filter_chats())


def __import_data__(chat_id, data):
    for user_id, count in data.get('warns', {}).items():
        for x in range(int(count)):
            warns_db.add_warns(user_id, chat_id)


def __migrate__(old_chat_id, new_chat_id):
    warns_db.migrate_chat(old_chat_id, new_chat_id)


def __chat_settings__(chat_id, user_id):
    num_warn_filters = warns_db.num_warn_chat_filters(chat_id)
    limit, soft_warn = warns_db.get_warn_settings(chat_id)
    return "This chat has `{}` warn filters. It takes `{}` warns " \
           "before the user gets **{}**.".format(num_warn_filters, limit, "kicked" if soft_warn else "banned")


__HELP__ = """
 - /warns <userhandle>: get a user's number, and reason, of warnings.
 - /warnlist: list of all current warning filters
*Admin only:*
 - /warn <userhandle>: warn a user. After 3 warns, the user will be banned from the group. Can also be used as a reply.
 - /resetwarn <userhandle>: reset the warnings for a user. Can also be used as a reply.
 - /addwarn <keyword> <reply message>: set a warning filter on a certain keyword. If you want your keyword to \
be a sentence, encompass it with quotes, as such: `/addwarn "very angry" This is an angry user`. 
 - /nowarn <keyword>: stop a warning filter
 - /warnlimit <num>: set the warning limit
 - /strongwarn <on/yes/off/no>: If set to on, exceeding the warn limit will result in a ban. Else, will just kick.
"""

__MODULE__ = "Warnings"
