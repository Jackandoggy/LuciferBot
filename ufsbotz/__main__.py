import asyncio
import importlib
import logging
import random
import re

# import uvloop
from pyrogram import filters, idle, Client
from pyrogram.errors import BadRequest
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from ufsbotz import (BOT_NAME, BOT_USERNAME, LOG_GROUP_ID,
                     aiohttpsession, ufs, IMPORTED)
from ufsbotz.database.restart_db import clean_restart_stage
from ufsbotz.modules import ALL_MODULES
from ufsbotz.modules.sudoers import bot_sys_stats
from ufsbotz.utils import paginate_modules
from ufsbotz.utils.constants import MARKDOWN
from sample_config import *

loop = asyncio.get_event_loop()

HELPABLE = {}


async def start_bot():
    global HELPABLE

    # for module in ALL_MODULES:
    #     imported_module = importlib.import_module("ufsbotz.modules." + module)
    #     if hasattr(imported_module, "__MODULE__") and imported_module.__MODULE__:
    #         imported_module.__MODULE__ = imported_module.__MODULE__
    #         if hasattr(imported_module, "__HELP__") and imported_module.__HELP__:
    #             HELPABLE[imported_module.__MODULE__.lower()] = imported_module

    for module_name in ALL_MODULES:
        imported_module = importlib.import_module("ufsbotz.modules." + module_name)

        if not hasattr(imported_module, "__MODULE__"):
            imported_module.__MODULE__ = imported_module.__name__

        if not imported_module.__MODULE__.lower() in IMPORTED:
            IMPORTED[imported_module.__MODULE__.lower()] = imported_module
        else:
            raise Exception("Can't Have Two Modules With The Same Name! Please Change One")

        if hasattr(imported_module, "__HELP__") and imported_module.__HELP__:
            HELPABLE[imported_module.__MODULE__.lower()] = imported_module

    bot_modules = ""
    j = 1
    for i in ALL_MODULES:
        if j == 4:
            bot_modules += "|{:<15}|\n".format(i)
            j = 0
        else:
            bot_modules += "|{:<15}".format(i)
        j += 1
    print("+===============================================================+")
    print("|                        𝙐𝙁𝙎 𝘽𝙤𝙩𝙯                                |")
    print("+===============+===============+===============+===============+")
    print(bot_modules)
    print("+===============+===============+===============+===============+")
    print(f"[INFO]: BOT STARTED AS {BOT_NAME}!")

    restart_data = await clean_restart_stage()

    try:
        print("[INFO]: SENDING ONLINE STATUS")
        if restart_data:
            await ufs.edit_message_text(
                restart_data["chat_id"],
                restart_data["message_id"],
                "**Restarted Successfully**",
            )

        else:
            await ufs.send_message(LOG_GROUP_ID, "**Bot Restarted Successfully**!")
    except Exception:
        pass

    await idle()

    await aiohttpsession.close()
    print("[INFO]: CLOSING AIOHTTP SESSION AND STOPPING BOT")
    await ufs.stop()
    print("[INFO]: Bye!")
    for task in asyncio.all_tasks():
        task.cancel()
    print("[INFO]: Turned off!")


home_keyboard_pm = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(
                text="Commands ❓", callback_data="bot_commands"
            ),
            InlineKeyboardButton(
                text="Repo 🛠",
                url="https://github.com/jinspalakkattu/LuciferBot",
            ),
        ],
        [
            InlineKeyboardButton(
                text="System Stats 🖥",
                callback_data="stats_callback",
            ),
        ],
        [
            InlineKeyboardButton(
                text="Add Me To Your Group 🎉",
                url=f"http://t.me/{BOT_USERNAME}?startgroup=new",
            )
        ],
    ]
)

home_text_pm = (
        "Hᴇʏ Dᴇᴀʀ **__{username}__**! \n        Mʏ Nᴀᴍᴇ Is **__{botname}__**, I'ᴍ Hᴇʀᴇ Tᴏ Hᴇʟᴘ Yᴏᴜ Mᴀɴᴀɢᴇ Yᴏᴜʀ Gʀᴏᴜᴘs! "
        "\nHɪᴛ /help Tᴏ Fɪɴᴅ Oᴜᴛ Mᴏʀᴇ Aʙᴏᴜᴛ Hᴏᴡ Tᴏ Usᴇ Mᴇ Tᴏ Mʏ Fᴜʟʟ Pᴏᴛᴇɴᴛɪᴀʟ."
        "\nJᴏɪɴ Mʏ [Nᴇᴡs Cʜᴀɴɴᴇʟ](https://t.me/joinchat/7qlEga5lO0o2MTg0) Tᴏ Gᴇᴛ Iɴғᴏʀᴍᴀᴛɪᴏɴ Oɴ Aʟʟ Tʜᴇ Lᴀᴛᴇsᴛ Uᴘᴅᴀᴛᴇs."
        # f"Hey there! My name is {BOT_NAME}. I can manage your "
        # + "group with lots of useful features, feel free to "
        # + "add me to your group."
)

keyboard = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(
                text="Help ❓",
                url=f"t.me/{BOT_USERNAME}?start=help",
            ),
            InlineKeyboardButton(
                text="Repo 🛠",
                url="https://github.com/jinspalakkattu/LuciferBot",
            ),
        ],
        [
            InlineKeyboardButton(
                text="System Stats 💻",
                callback_data="stats_callback",
            ),
        ],
    ]
)


@ufs.on_message(filters.command("start"))
async def start(_, message):
    if message.chat.type != "private":
        return await message.reply_photo(photo=random.choice(PICS),
                                         caption="Pm Me For More Details.", reply_markup=keyboard
                                         )
    if len(message.text.split()) > 1:
        name = (message.text.split(None, 1)[1]).lower()
        if name == "mkdwn_help":
            await message.reply(
                MARKDOWN, parse_mode="html", disable_web_page_preview=True
            )
        elif "_" in name:
            module = name.split("_", 1)[1]
            text = (
                    f"Here is the help for **{HELPABLE[module].__MODULE__}**:\n"
                    + HELPABLE[module].__HELP__
            )
            await message.reply(text, disable_web_page_preview=True)
        elif name == "help":
            text, keyb = await help_parser(message.from_user.first_name)
            await message.reply(
                text,
                reply_markup=keyb,
            )
    else:
        await message.reply_photo(photo=random.choice(PICS),
                                  caption=home_text_pm.format(username=message.from_user.first_name, botname=BOT_NAME),
                                  reply_markup=home_keyboard_pm,
                                  )
    return


@ufs.on_message(filters.command("help"))
async def help_command(_, message):
    if message.chat.type != "private":
        if len(message.command) >= 2:
            name = (message.text.split(None, 1)[1]).lower()
            if str(name) in HELPABLE:
                key = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="Click here",
                                url=f"t.me/{BOT_USERNAME}?start=help_{name}",
                            )
                        ],
                    ]
                )
                await message.reply(
                    f"Click on the below button to get help about {name}",
                    reply_markup=key,
                )
            else:
                await message.reply(
                    "PM Me For More Details.", reply_markup=keyboard
                )
        else:
            await message.reply(
                "Pm Me For More Details.", reply_markup=keyboard
            )
    elif len(message.command) >= 2:
        name = (message.text.split(None, 1)[1]).lower()
        if str(name) in HELPABLE:
            text = (
                    f"Here is the help for **{HELPABLE[name].__MODULE__}**:\n"
                    + HELPABLE[name].__HELP__
            )
            await message.reply(text, disable_web_page_preview=True)
        else:
            text, help_keyboard = await help_parser(
                message.from_user.first_name
            )
            await message.reply(
                text,
                reply_markup=help_keyboard,
                disable_web_page_preview=True,
            )
    else:
        text, help_keyboard = await help_parser(
            message.from_user.first_name
        )
        await message.reply(
            text, reply_markup=help_keyboard, disable_web_page_preview=True
        )
    return


async def help_parser(name, keyboard=None):
    if not keyboard:
        keyboard = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help"))
    return (
        """Hello {first_name}, My name is {bot_name}.
I'm a group management bot with some useful features.
You can choose an option below, by clicking a button.
Also you can ask anything in Support Group.
""".format(
            first_name=name,
            bot_name=BOT_NAME,
        ),
        keyboard,
    )


@ufs.on_callback_query(filters.regex("bot_commands"))
async def commands_callbacc(_, CallbackQuery):
    text, keyboard = await help_parser(CallbackQuery.from_user.mention)
    await ufs.send_message(
        CallbackQuery.message.chat.id,
        text=text,
        reply_markup=keyboard,
    )

    await CallbackQuery.message.delete()


@ufs.on_callback_query(filters.regex("stats_callback"))
async def stats_callbacc(_, CallbackQuery):
    text = await bot_sys_stats()
    await ufs.answer_callback_query(CallbackQuery.id, text, show_alert=True)


@ufs.on_callback_query(filters.regex(r"help_(.*?)"))
async def help_button(client: Client, query: CallbackQuery):
    home_match = re.match(r"help_home\((.+?)\)", query.data)
    mod_match = re.match(r"help_module\((.+?)\)", query.data)
    prev_match = re.match(r"help_prev\((.+?)\)", query.data)
    next_match = re.match(r"help_next\((.+?)\)", query.data)
    back_match = re.match(r"help_back", query.data)
    create_match = re.match(r"help_create", query.data)
    help_match = re.match(r"help_", query.data)
    close_match = re.match(r"close_btn", query.data)

    top_text = f"""
Hello {query.from_user.first_name}, My name is {BOT_NAME}.
I'm a group management bot with some usefule features.
You can choose an option below, by clicking a button.
Also you can ask anything in Support Group.

General command are:
 - /start: Start the bot
 - /help: Give this message
 """
    # ######################### MODULE HELP START #############################################################
    try:
        if mod_match:
            module = mod_match.group(1)
            text = "Here is the help for the **{}** module:\n".format(HELPABLE[module].__MODULE__) \
                   + HELPABLE[module].__HELP__
            await query.message.edit_text(text=text,
                                          parse_mode="markdown",
                                          reply_markup=InlineKeyboardMarkup(
                                              [[InlineKeyboardButton(text="Back", callback_data="help_back")]]))

        elif prev_match:
            curr_page = int(prev_match.group(1))
            await query.message.edit_text(top_text,
                                          parse_mode="markdown",
                                          reply_markup=InlineKeyboardMarkup(
                                              paginate_modules(curr_page - 1, HELPABLE, "help")))

        elif next_match:
            next_page = int(next_match.group(1))
            await query.message.edit_text(top_text,
                                          parse_mode="markdown",
                                          reply_markup=InlineKeyboardMarkup(
                                              paginate_modules(next_page + 1, HELPABLE, "help")))

        elif back_match:
            await query.message.edit_text(text=top_text,
                                          parse_mode="markdown",
                                          reply_markup=InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help")))

        elif help_match:
            await query.message.edit_text(text=top_text,
                                          parse_mode="markdown",
                                          reply_markup=InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help")))
        elif close_match:
            await query.message.edit_text(text=top_text,
                                          parse_mode="markdown",
                                          reply_markup=InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help")))
        elif home_match:
            await ufs.send_message(
                query.from_user.id,
                text=home_text_pm.format(username=query.from_user.first_name, botname=BOT_NAME),
                reply_markup=home_keyboard_pm,
            )
        elif create_match:
            text, keyboard = await help_parser(query)
            await query.message.edit(
                text=text,
                reply_markup=keyboard,
                disable_web_page_preview=True,
            )
        await query.message.delete()

        await client.answer_callback_query(query.id)
    except BadRequest as excp:
        if excp.MESSAGE == "Message Is Not Modified":
            pass
        elif excp.MESSAGE == "Query_id_invalid":
            pass
        elif excp.MESSAGE == "Message Can't Be Deleted":
            pass
        else:
            logging.exception("Exception In Help Buttons. %s", str(query.data))

    # ######################### MODULE HELP END #############################################################

    # if mod_match:
    #     module = mod_match.group(1)
    #     text = (
    #             "{} **{}**:\n".format(
    #                 "Here is the help for", HELPABLE[module].__MODULE__
    #             )
    #             + HELPABLE[module].__HELP__
    #     )
    #
    #     await query.message.edit(
    #         text=text,
    #         reply_markup=InlineKeyboardMarkup(
    #             [[InlineKeyboardButton("back", callback_data="help_back")]]
    #         ),
    #         disable_web_page_preview=True,
    #     )
    # elif home_match:
    #     await ufs.send_message(
    #         query.from_user.id,
    #         text=home_text_pm.format(username=query.from_user.first_name, botname=BOT_NAME),
    #         reply_markup=home_keyboard_pm,
    #     )
    #     await query.message.delete()
    # elif prev_match:
    #     curr_page = int(prev_match.group(1))
    #     await query.message.edit(
    #         text=top_text,
    #         reply_markup=InlineKeyboardMarkup(
    #             paginate_modules(curr_page - 1, HELPABLE, "help")
    #         ),
    #         disable_web_page_preview=True,
    #     )
    #
    # elif next_match:
    #     next_page = int(next_match.group(1))
    #     await query.message.edit(
    #         text=top_text,
    #         reply_markup=InlineKeyboardMarkup(
    #             paginate_modules(next_page + 1, HELPABLE, "help")
    #         ),
    #         disable_web_page_preview=True,
    #     )
    #
    # elif back_match:
    #     await query.message.edit(
    #         text=top_text,
    #         reply_markup=InlineKeyboardMarkup(
    #             paginate_modules(0, HELPABLE, "help")
    #         ),
    #         disable_web_page_preview=True,
    #     )
    #
    # elif create_match:
    #     text, keyboard = await help_parser(query)
    #     await query.message.edit(
    #         text=text,
    #         reply_markup=keyboard,
    #         disable_web_page_preview=True,
    #     )

    # return await client.answer_callback_query(query.id)


if __name__ == "__main__":
    # uvloop.install()
    try:
        try:
            logging.info("Successfully Loaded Modules: " + str(ALL_MODULES))
            loop.run_until_complete(start_bot())
        except asyncio.exceptions.CancelledError:
            pass
        loop.run_until_complete(asyncio.sleep(3.0))  # task cancel wait
    finally:
        loop.close()
