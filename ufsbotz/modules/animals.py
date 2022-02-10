from ufsbotz import ufs
from pyrogram import filters
from ufsbotz.core.decorators.errors import capture_err
from ufsbotz.utils.http import get, resp_get

__MODULE__ = "Animals"
__HELP__ = """/catfacts - To Get Facts About Cat.
/dogfacts - To Get Facts About Dog.
/animalfacts - To Get Facts About Animal.
"""


@ufs.on_message(filters.command("catfacts"))
@capture_err
async def catfacts(client, message):
    """
    Get cat facts
    """
    message = await message.reply_text("`Getting cat facts...`")
    resp = await get("https://cat-fact.herokuapp.com/facts/random")
    return await message.edit(resp["text"])


@ufs.on_message(filters.command("animalfacts"))
@capture_err
async def animalfacts(client, message):
    somerandomvariable = await get("https://axoltlapi.herokuapp.com/")
    return await message.reply_photo(somerandomvariable["url"], caption=somerandomvariable["facts"])


@ufs.on_message(filters.command("dogfacts"))
@capture_err
async def dogfacts(client, message):
    somerandomvariable = await get("https://dog-facts-api.herokuapp.com/api/v1/resources/dogs?number=1")
    return await message.reply_text(somerandomvariable[0]["fact"])
