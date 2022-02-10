from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from ufsbotz import ufs, SUDOERS
from ufsbotz.database.connection_db import active_connection
from ufsbotz.database.settings_db import sett_db


@ufs.on_message(filters.command('settings') & filters.private & ~filters.edited)
async def settings(client, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(f"You are anonymous admin. Use /connect {message.chat.id} in PM")
    chat_type = message.chat.type
    args = message.text.html.split(None, 1)

    if chat_type == "private":
        grpid = await active_connection(str(userid))
        if grpid is not None:
            grp_id = grpid
            try:
                chat = await client.get_chat(grpid)
                title = chat.title
            except:
                await message.reply_text("Make sure I'm present in your group!!", quote=True)
                return
        else:
            await message.reply_text("I'm not connected to any groups!", quote=True)
            return

    elif chat_type in ["group", "supergroup"]:
        grp_id = message.chat.id
        title = message.chat.title

    else:
        return

    st = await client.get_chat_member(grp_id, userid)
    if (
            st.status != "administrator"
            and st.status != "creator"
            and str(userid) not in SUDOERS
    ):
        return

    if not await sett_db.is_settings_exist(str(grp_id)):
        await sett_db.add_settings(str(grp_id), True, 120)

    settings = await sett_db.get_settings(str(grp_id))

    if settings is not None:
        buttons = [
            [
                InlineKeyboardButton('Fɪʟᴛᴇʀ Bᴜᴛᴛᴏɴ',
                                     callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}#{settings["delete_time"]}'),
                InlineKeyboardButton('Sɪɴɢʟᴇ' if settings["button"] else 'Dᴏᴜʙʟᴇ',
                                     callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}#{settings["delete_time"]}')
            ],
            [
                InlineKeyboardButton('Bᴏᴛ PM',
                                     callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}#{settings["delete_time"]}'),
                InlineKeyboardButton('✅ Yᴇs' if settings["botpm"] else '❌ Nᴏ',
                                     callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}#{settings["delete_time"]}')
            ],
            [
                InlineKeyboardButton('Fɪʟᴇ Sᴇᴄᴜʀᴇ',
                                     callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}#{settings["delete_time"]}'),
                InlineKeyboardButton('✅ Yᴇs' if settings["file_secure"] else '❌ Nᴏ',
                                     callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}#{settings["delete_time"]}')
            ],
            [
                InlineKeyboardButton('Iᴍᴅʙ',
                                     callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}#{settings["delete_time"]}'),
                InlineKeyboardButton('✅ Yᴇs' if settings["imdb"] else '❌ Nᴏ',
                                     callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}#{settings["delete_time"]}')
            ],
            [
                InlineKeyboardButton('Sᴘᴇʟʟ Cʜᴇᴄᴋ',
                                     callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}#{settings["delete_time"]}'),
                InlineKeyboardButton('✅ Yᴇs' if settings["spell_check"] else '❌ Nᴏ',
                                     callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}#{settings["delete_time"]}')
            ],
            [
                InlineKeyboardButton('Aᴜᴛᴏ Dᴇʟᴇᴛᴇ',
                                     callback_data=f'setgs#delete#{settings["auto_delete"]}#{str(grp_id)}#{settings["delete_time"]}'),
                InlineKeyboardButton(f'{settings["delete_time"]} Sᴇᴄ' if settings["auto_delete"] else '❌ Nᴏ',
                                     callback_data=f'setgs#delete#{settings["auto_delete"]}#{str(grp_id)}#{settings["delete_time"]}')
            ],
            [
                InlineKeyboardButton('Wᴇʟᴄᴏᴍᴇ',
                                     callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}#{settings["delete_time"]}'),
                InlineKeyboardButton('✅ Yᴇs' if settings["welcome"] else '❌ Nᴏ',
                                     callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}#{settings["delete_time"]}')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)

        await message.reply_text(
            text=f"<b>Change Your Filter Settings As Your Wish ⚙\n\nThis Settings For Group</b> <code>{title}</code>",
            reply_markup=reply_markup,
            disable_web_page_preview=True,
            parse_mode="html",
            reply_to_message_id=message.message_id
        )


@ufs.on_callback_query(filters.regex('setgs'))
async def cbh_settings(client, query):
    if query.data.startswith("setgs"):
        ident, set_type, status, grp_id, time = query.data.split("#")
        grpid = await active_connection(str(query.from_user.id))

        if str(grp_id) != str(grpid):
            await query.message.edit("Your Active Connection Has Been Changed. Go To /settings.")
            return

        if set_type == "delete":
            time = int(time) + 30
            await sett_db.update_settings(grp_id, set_type, True if (0 < int(time) <= 180) else False,
                                          time if (0 < int(time) <= 180) else 0)
        else:
            await sett_db.update_settings(grp_id, set_type, False if status == "True" else True, 0)

        settings = await sett_db.get_settings(str(grp_id))

        if settings is not None:
            buttons = [
                [
                    InlineKeyboardButton('Fɪʟᴛᴇʀ Bᴜᴛᴛᴏɴ',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}#{settings["delete_time"]}'),
                    InlineKeyboardButton('Sɪɴɢʟᴇ' if settings["button"] else 'Dᴏᴜʙʟᴇ',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}#{settings["delete_time"]}')
                ],
                [
                    InlineKeyboardButton('Bᴏᴛ PM',
                                         callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}#{settings["delete_time"]}'),
                    InlineKeyboardButton('✅ Yᴇs' if settings["botpm"] else '❌ Nᴏ',
                                         callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}#{settings["delete_time"]}')
                ],
                [
                    InlineKeyboardButton('Fɪʟᴇ Sᴇᴄᴜʀᴇ',
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}#{settings["delete_time"]}'),
                    InlineKeyboardButton('✅ Yᴇs' if settings["file_secure"] else '❌ Nᴏ',
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}#{settings["delete_time"]}')
                ],
                [
                    InlineKeyboardButton('Iᴍᴅʙ',
                                         callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}#{settings["delete_time"]}'),
                    InlineKeyboardButton('✅ Yᴇs' if settings["imdb"] else '❌ Nᴏ',
                                         callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}#{settings["delete_time"]}')
                ],
                [
                    InlineKeyboardButton('Sᴘᴇʟʟ Cʜᴇᴄᴋ',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}#{settings["delete_time"]}'),
                    InlineKeyboardButton('✅ Yᴇs' if settings["spell_check"] else '❌ Nᴏ',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}#{settings["delete_time"]}')
                ],
                [
                    InlineKeyboardButton('Aᴜᴛᴏ Dᴇʟᴇᴛᴇ',
                                         callback_data=f'setgs#delete#{settings["auto_delete"]}#{str(grp_id)}#{settings["delete_time"]}'),
                    InlineKeyboardButton(f'{settings["delete_time"]} Sᴇᴄ' if settings["auto_delete"] else '❌ Nᴏ',
                                         callback_data=f'setgs#delete#{settings["auto_delete"]}#{str(grp_id)}#{settings["delete_time"]}')
                ],
                [
                    InlineKeyboardButton('Wᴇʟᴄᴏᴍᴇ',
                                         callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}#{settings["delete_time"]}'),
                    InlineKeyboardButton('✅ Yᴇs' if settings["welcome"] else '❌ Nᴏ',
                                         callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}#{settings["delete_time"]}')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            await query.message.edit_reply_markup(reply_markup)