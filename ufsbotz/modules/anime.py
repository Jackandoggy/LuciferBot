import requests
from random import choice, randint
from pyrogram import filters
from pyrogram.types import Message
from ufsbotz import SUDOERS, ufs, BOT_USERNAME
from ufsbotz.core.decorators.errors import capture_err
from pyrogram.errors import MediaCaptionTooLong
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InlineQuery, InlineQueryResultArticle, \
    InputTextMessageContent
from jikanpy import Jikan


# temporary solution; will fork fakeuseragent to make it more stable
class ua():
    def random(self):
        user_agent_list = [
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
            "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:77.0) Gecko/20190101 Firefox/77.0"
        ]
        return choice(user_agent_list)


__MODULE__ = "Anime"
__HELP__ = """
/anime - Get Anime Info.
/manga - Get Manga Info.
/aquote - Get Random Anime Quote.
/aquote anime- Get Anime Quote From An Anime.
/cquote character - Get Quote From A Character.
"""


@ufs.on_message(filters.command(["anime", f"anime@{BOT_USERNAME}"]))
@capture_err
async def anime(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Send **/Anime AnimeName** to get info.")
    jikan = Jikan()
    message.command.pop(0)
    search_result = requests.get(f"https://kitsu.io/api/edge//anime?filter[text]={message.command}").json()['data'][0]
    try:
        return await message.reply_photo(photo=search_result['attributes']['posterImage']['original'],
                                         caption=f"**Title**:{search_result['attributes']['titles']['en']}\n**Japanese**:{search_result['attributes']['titles']['en_jp']}\n**PopularityRank**:{search_result['attributes']['popularityRank']}\n**Age Rating**:{search_result['attributes']['ageRatingGuide']}\n**Episode Count**:{search_result['attributes']['episodeCount']}\n**Synopsis**:{search_result['attributes']['synopsis']}",
                                         reply_markup=InlineKeyboardMarkup(
                                             [
                                                 [
                                                     InlineKeyboardButton("Open In Kitsu",
                                                                          url=f"https://kitsu.io/anime/{search_result['id']}")
                                                 ],
                                                 [
                                                     InlineKeyboardButton(text="Search Again",
                                                                          switch_inline_query_current_chat="anime")
                                                 ]
                                             ]
                                         ))
    except MediaCaptionTooLong:
        replyto = await message.reply_photo(photo=search_result['attributes']['posterImage']['original'])
        return await message.reply_text(
            f"**Title**:{search_result['attributes']['titles']['en']}\n**Japanese**:{search_result['attributes']['titles']['en_jp']}\n**PopularityRank**:{search_result['attributes']['popularityRank']}\n**Age Rating**:{search_result['attributes']['ageRatingGuide']}\n**Episode Count**:{search_result['attributes']['episodeCount']}\n**Synopsis**:{search_result['attributes']['synopsis']}",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Open In Kitsu", url=f"https://kitsu.io/manga/{search_result['id']}")
                    ],
                    [
                        InlineKeyboardButton(text="Search Again", switch_inline_query_current_chat="anime")
                    ]
                ]
            ), reply_to_message_id=replyto.message_id)


@ufs.on_message(filters.command(["manga", f"manga@{BOT_USERNAME}"]))
@capture_err
async def manga(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Send **/Manga MangaName** to get info.")
    jikan = Jikan()
    message.command.pop(0)
    search_result = requests.get(f"https://kitsu.io/api/edge//manga?filter[text]={message.command}").json()['data'][0]
    try:
        return await message.reply_photo(photo=search_result['attributes']['posterImage']['original'],
                                         caption=f"**Title**:{search_result['attributes']['titles']['en']}\n**Japanese**:{search_result['attributes']['titles']['en_jp']}\n**PopularityRank**:{search_result['attributes']['popularityRank']}\n**Age Rating**:{search_result['attributes']['ageRatingGuide']}\n**Chapter Count**:{search_result['attributes']['chapterCount']}\n**Synopsis**:{search_result['attributes']['synopsis']}",
                                         reply_markup=InlineKeyboardMarkup(
                                             [
                                                 [
                                                     InlineKeyboardButton("Open In Kitsu",
                                                                          url=f"https://kitsu.io/anime/{search_result['id']}")
                                                 ],
                                                 [
                                                     InlineKeyboardButton(text="Search Again",
                                                                          switch_inline_query_current_chat="anime")
                                                 ]
                                             ]
                                         ))
    except MediaCaptionTooLong:
        replyto = await message.reply_photo(photo=search_result['attributes']['posterImage']['original'])
        return await message.reply_text(
            f"**Title**:{search_result['attributes']['titles']['en']}\n**Japanese**:{search_result['attributes']['titles']['en_jp']}\n**PopularityRank**:{search_result['attributes']['popularityRank']}\n**Age Rating**:{search_result['attributes']['ageRatingGuide']}\n**Chapter Count**:{search_result['attributes']['chapterCount']}\n**Synopsis**:{search_result['attributes']['synopsis']}",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Open In Kitsu", url=f"https://kitsu.io/anime/{search_result['id']}")
                    ],
                    [
                        InlineKeyboardButton(text="Search Again", switch_inline_query_current_chat="anime")
                    ]
                ]
            ), reply_to_message_id=replyto.message_id)


@ufs.on_message(filters.command(["aquote", f"aquote@{BOT_USERNAME}"]))
@capture_err
async def manga(client, message: Message):
    if len(message.command) < 2:
        query = requests.get('https://animechan.vercel.app/api/random', headers={'User-Agent': ua.random()}).json()
        return await message.reply_text(f"`{query['quote']}`\n\n**{query['character']} ({query['anime']})**")
    else:
        message.command.pop(0)
        try:
            query = requests.get(
                f'https://animechan.vercel.app/api/quotes/anime?title={" ".join(message.command)}&page={randint(0, 5)}',
                headers={'User-Agent': ua.random()}).json()
            query = choice(query)
            return await message.reply_text(f"`{query['quote']}`\n\n**{query['character']} ({query['anime']})**")
        except:
            return await message.reply_text("No quotes found.")


@ufs.on_message(filters.command(["cquote", f"cquote@{BOT_USERNAME}"]))
@capture_err
async def manga(client, message: Message):
    if len(message.command) < 2:
        query = requests.get('https://animechan.vercel.app/api/random', headers={'User-Agent': ua.random()}).json()
        return await message.reply_text(f"`{query['quote']}`\n\n**~{query['character']} ({query['anime']})**")
    else:
        message.command.pop(0)
        try:
            query = requests.get(
                f'https://animechan.vercel.app/api/quotes/character?name={" ".join(message.command)}&page={randint(0, 5)}',
                headers={'User-Agent': ua.random()}).json()
            query = choice(query)
            return await message.reply_text(f"`{query['quote']}`\n\n**{query['character']} ({query['anime']})**")
        except:
            return await message.reply_text("No quotes found.")
