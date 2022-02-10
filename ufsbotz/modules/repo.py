from pyrogram import filters

from ufsbotz import ufs
from ufsbotz.core.decorators.errors import capture_err
from ufsbotz.utils.http import get

__MODULE__ = "Repo"
__HELP__ = "/repo - To Get My Github Repository Link " "And Support Group Link"


@ufs.on_message(filters.command("repo") & ~filters.edited)
@capture_err
async def repo(_, message):
    users = await get(
        "https://api.github.com/repos/jinspalakkattu/LuciferBot/contributors"
    )
    list_of_users = "".join(
        f"**{count}.** [{user['login']}]({user['html_url']})\n"
        for count, user in enumerate(users, start=1)
    )

    text = f"""[Github](https://github.com/jinspalakkattu/LuciferBot) | [Group](t.me/UFSBotzSupport)
```----------------
| Contributors |
----------------```
{list_of_users}"""
    await ufs.send_message(
        message.chat.id, text=text, disable_web_page_preview=True
    )
