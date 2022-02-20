import os
from datetime import datetime

from userbot import moussabot
#
from . import hmention, reply_id

"""
try:
    from . import PING_PIC, PING_TEXT
except:
    pass
"""

PING_PIC = os.environ.get("PING_PIC") or (
    "https://telegra.ph/file/30a31c94e3b80c147bc15.jpg"
)

JM_TXT = os.environ.get("PING_TEXT") or "مـن لا يتعلم من الماضي لا يرحمه المستقبل  . 🖤"


@moussabot.on(admin_cmd(pattern="بينغ$"))
async def _(event):
    if event.fwd_from:
        return
    reply_to_id = await reply_id(event)
    start = datetime.now()
    cat = await edit_or_reply(
        event, "<b><i>  ❤️⃝⃝⃝⃝⃝⃝⃝⃝⃝⃝⃝⃝⃝⃝⃟✨ البــــنك... 🍀⃝⃝⃟🍂 </b></i>", "html"
    )
    end = datetime.now()
    await cat.delete()
    ms = (end - start).microseconds / 1000
    if PING_PIC:
        caption = f"<b><i>{JM_TXT}<i><b>\n<code>┏━━━━━━━┓\n┃ ✦ {ms}\n┃ ✦ <b>{hmention}</b>\n┗━━━━━━━┛"
        await event.client.send_file(
            event.chat_id,
            PING_PIC,
            caption=caption,
            parse_mode="html",
            reply_to=reply_to_id,
            link_preview=False,
            allow_cache=True,
        )
    else:
        await event.edit_or_reply(
            event, "<code>يجـب اضـافة متـغير `PING_PIC`  اولا  f<code>", "html"
        )


# ======================================================================================================================================

CMD_HELP.update(
    {
        "البنك":".بنك\nجرب الامر بنفسك" 
        }
        )
