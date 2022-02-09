from ufsbotz import app
from pyrogram import filters
from ufsbotz.core.decorators.errors import capture_err
from ufsbotz.utils.http import get, resp_get
from bs4 import BeautifulSoup

__MODULE__ = "CricInfo"
__HELP__ = """
/cricinfo - Get the latest score of the match.
"""


@app.on_message(filters.command("cricinfo"))
@capture_err
async def catfacts(client, message):
    score_page = "http://static.cricinfo.com/rss/livescores.xml"
    page = await get(score_page)
    soup = BeautifulSoup(page, "html.parser")
    result = soup.find_all("description")
    Sed = "".join("<code>" + match.get_text() + "</code>\n\n" for match in result)
    return await message.reply(Sed, parse_mode="html")
