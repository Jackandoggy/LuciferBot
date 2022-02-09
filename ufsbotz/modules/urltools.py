from pyrogram import filters

from ufsbotz import ufs
from ufsbotz.core.decorators.errors import capture_err
from ufsbotz.utils.http import get, resp_get

__MODULE__ = "Url Tools"
__HELP__ = """/short - To Short a url. Use **/short url coustom** to get coustom link.
/unshort - To unshort a url."""


@ufs.on_message(filters.command("short") & ~filters.edited)
@capture_err
async def short(_, message):
    if len(message.command) < 2:
        return await message.reply_text("**/short sho.rt/url** To short a url.")
    url = message.command[1]
    if not url.startswith("http"):
        url = "http://" + url
    try:
        short = message.command[2]
        shortRequest = await get(f"https://api.1pt.co/addURL?long={url}&short={short}")
        short = shortRequest["short"]
        return await message.reply_text(f"**URL After Short: `https://1pt.co/{short}`**")
    except IndexError:
        shortRequest = await get(f"https://api.1pt.co/addURL?long={url}")
        short = shortRequest["short"]
        return await message.reply_text(f"**URL After Short: `https://1pt.co/{short}`**")
    except Exception as e:
        return await message.reply_text(f"**{e}**")


@ufs.on_message(filters.command("unshort"))
@capture_err
async def unshort(_, message):
    if len(message.command) < 2:
        return await message.reply_text("**/unshort url** To unshort a url.")
    url = message.command[1]
    if not url.startswith("http"):
        url = "http://" + url
    try:
        mainurl = await resp_get(url)
        return await message.reply_text(f"**URL After Unshort: `{mainurl.url}`**")
    except Exception as e:
        return await message.reply_text(f"**{e}**")
