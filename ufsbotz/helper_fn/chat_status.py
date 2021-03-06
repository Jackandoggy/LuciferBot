from functools import wraps
from traceback import format_exc as err

from pyrogram.errors.exceptions.forbidden_403 import ChatWriteForbidden
from pyrogram.types import Message, Chat, ChatMember

from ufsbotz import *

from pyrogram.types import Message

from ufsbotz import SUDOERS, ufs
from ufsbotz.database.connection_db import active_connection


async def member_permissions(chat_id: int, user_id: int):
    perms = []
    try:
        member = await ufs.get_chat_member(chat_id, user_id)
    except Exception:
        return []
    if member.can_post_messages:
        perms.append("can_post_messages")
    if member.can_edit_messages:
        perms.append("can_edit_messages")
    if member.can_delete_messages:
        perms.append("can_delete_messages")
    if member.can_restrict_members:
        perms.append("can_restrict_members")
    if member.can_promote_members:
        perms.append("can_promote_members")
    if member.can_change_info:
        perms.append("can_change_info")
    if member.can_invite_users:
        perms.append("can_invite_users")
    if member.can_pin_messages:
        perms.append("can_pin_messages")
    if member.can_manage_voice_chats:
        perms.append("can_manage_voice_chats")
    return perms


def user_admin(func):
    @wraps(func)
    async def is_admin(client, message: Message, *args, **kwargs):
        user = message.from_user
        if user and await is_user_admin(message.chat, user.id):
            return await func(client, message, *args, **kwargs)

        elif not user:
            pass

        elif DEL_CMDS and " " not in message.text:
            await message.delete()

        else:
            await message.reply_text("Who This Non-Admin Telling Me What To Do?")

    return is_admin


async def is_user_admin(chat: Chat, user_id: int) -> bool:
    try:
        if chat.type == 'private' \
                or user_id in SUDOERS:
            return True

        member = await ufs.get_chat_member(chat.id, user_id)
        return member.status in ('administrator', 'creator')
    except:
        member = await ufs.get_chat_member(chat.id, user_id)
        return member.status in ('administrator', 'creator')


async def get_active_connection(client, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return '', '', False, f"You are anonymous admin. Use /connect {message.chat.id} in PM"

    chat_type = message.chat.type
    if chat_type == "private":
        grpid = await active_connection(str(userid))
        if grpid is not None:
            CHAT_ID = grpid
            try:
                chat = await client.get_chat(grpid)
                TITLE = chat.title
                return CHAT_ID, TITLE, True, ''
            except:
                return '', '', False, "Make sure I'm present in your group!!"
        else:
            return '', '', False, "I'm not connected to any groups!"

    elif chat_type in ["group", "supergroup"]:
        CHAT_ID = message.chat.id
        TITLE = message.chat.title
        return CHAT_ID, TITLE, True, ''

    else:
        return '', '', False, "Invalid Active Chat Group"


async def authorised(func, subFunc2, client, message, *args, **kwargs):
    chatID = message.chat.id
    try:
        await func(client, message, *args, **kwargs)
    except ChatWriteForbidden:
        await ufs.leave_chat(chatID)
    except Exception as e:
        try:
            await message.reply_text(str(e.MESSAGE))
        except AttributeError:
            await message.reply_text(str(e))
        e = err()
        print(e)
    return subFunc2


async def unauthorised(message: Message, permission, subFunc2):
    chatID = message.chat.id
    text = (
            "You don't have the required permission to perform this action."
            + f"\n**Permission:** __{permission}__"
    )
    try:
        await message.reply_text(text)
    except ChatWriteForbidden:
        await ufs.leave_chat(chatID)
    return subFunc2


def adminsOnly(permission):
    def subFunc(func):
        @wraps(func)
        async def subFunc2(client, message: Message, *args, **kwargs):
            chatID = message.chat.id
            if not message.from_user:
                # For anonymous admins
                if (
                        message.sender_chat
                        and message.sender_chat.id == message.chat.id
                ):
                    return await authorised(
                        func,
                        subFunc2,
                        client,
                        message,
                        *args,
                        **kwargs,
                    )
                return await unauthorised(message, permission, subFunc2)
            # For admins and sudo users
            userID = message.from_user.id
            permissions = await member_permissions(chatID, userID)
            if userID not in SUDOERS and permission not in permissions:
                return await unauthorised(message, permission, subFunc2)
            return await authorised(
                func, subFunc2, client, message, *args, **kwargs
            )

        return subFunc2

    return subFunc


def is_bot_admin(chat: Chat, bot_id: int, bot_member: ChatMember = None) -> bool:
    if chat.type == 'private':
        return True

    if not bot_member:
        bot_member = chat.get_member(bot_id)
    return bot_member.status in ('administrator', 'creator')


def bot_admin(func):
    @wraps(func)
    def is_admin(client: Client, message: Message, *args, **kwargs):
        if is_bot_admin(message.chat, BOT_ID):
            return func(client, message, *args, **kwargs)
        else:
            message.reply_text("I'm not admin!")

    return is_admin


def user_admin_no_reply(func):
    @wraps(func)
    async def is_admin(client: Client, message: Message, *args, **kwargs):
        user = message.from_user
        if user and await is_user_admin(message.chat, user.id):
            return await func(client, message, *args, **kwargs)

        elif not user:
            pass

        elif DEL_CMDS and " " not in message.text:
            await message.delete()

    return is_admin


def user_not_admin(func):
    @wraps(func)
    async def is_not_admin(client: Client, message: Message, *args, **kwargs):
        user = message.from_user
        if user and not await is_user_admin(message.chat, user.id):
            return await func(client, message, *args, **kwargs)

    return is_not_admin


def bot_can_delete(func):
    @wraps(func)
    async def delete_rights(client: Client, message: Message, *args, **kwargs):
        CHAT_ID, TITLE, STATUS, ERROR = await get_active_connection(client, message)
        # CHAT = client.get_chat(CHAT_ID)
        CHAT = await client.get_chat_member(CHAT_ID, BOT_ID)
        if can_delete(CHAT, BOT_ID):
            return await func(client, message, *args, **kwargs)
        else:
            await message.reply_text("I can't delete messages here! "
                               "Make sure I'm admin and can delete other user's messages.")

    return delete_rights


def can_delete(chat: Chat, bot_id: int) -> bool:
    # return chat.get_member(bot_id).can_delete_messages
    return chat.can_delete_messages
