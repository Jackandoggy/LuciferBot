from ufsbotz import ufs
from pyrogram import filters
from ufsbotz.core.decorators.errors import capture_err
from ufsbotz.utils.http import get,resp_get

__MODULE__ = "Cats"
__HELP__ = """/randomcat - To Get Random Photo of Cat.
/cats - To Get Photo of Cat. Use **/cats -s** to get photo as sticker.
/catfacts - To Get Facts About Cat.
"""


@ufs.on_message(filters.command("randomcat"))
@capture_err
async def randomcat(_, message):
    cat = await get("https://aws.random.cat/meow")
    await message.reply_photo(cat["file"])


@ufs.on_message(filters.command("cats"))
@capture_err
async def cats(_, message):
    cat = await get("https://thatcopy.pw/catapi/rest/")
    if len(message.command)<2:
        return await message.reply_photo(cat["url"])
    else:
        return await message.reply_sticker(cat["webpurl"])

