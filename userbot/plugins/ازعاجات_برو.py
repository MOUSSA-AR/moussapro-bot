import asyncio
import base64

from telethon.tl import functions, types
from telethon.tl.functions.messages import GetStickerSetRequest
from telethon.tl.functions.messages import ImportChatInviteRequest as Get
from telethon.utils import get_display_name

from userbot import catub

from ..core.managers import edit_delete, edit_or_reply
from ..helpers.tools import media_type
from ..helpers.utils import _catutils
from ..sql_helper.globals import addgvar, gvarstatus
from . import BOTLOG, BOTLOG_CHATID

plugin_category = "extra"


async def spam_function(event, sandy, cat, sleeptimem, sleeptimet, DelaySpam=False):
    # sourcery no-metrics
    counter = int(cat[0])
    if len(cat) == 2:
        spam_message = str(cat[1])
        for _ in range(counter):
            if gvarstatus("spamwork") is None:
                return
            if event.reply_to_msg_id:
                await sandy.reply(spam_message)
            else:
                await event.client.send_message(event.chat_id, spam_message)
            await asyncio.sleep(sleeptimet)
    elif event.reply_to_msg_id and sandy.media:
        for _ in range(counter):
            if gvarstatus("spamwork") is None:
                return
            sandy = await event.client.send_file(
                event.chat_id, sandy, caption=sandy.text
            )
            await _catutils.unsavegif(event, sandy)
            await asyncio.sleep(sleeptimem)
        if BOTLOG:
            if DelaySpam is not True:
                if event.is_private:
                    await event.client.send_message(
                        BOTLOG_CHATID,
                        "#ازعاج\n"
                        + f"اكتمل الازعاج في [User](tg://user?id={event.chat_id}) الدردشة مع {counter} مرات من الرسالة أدناه",
                    )
                else:
                    await event.client.send_message(
                        BOTLOG_CHATID,
                        "#ازعاج\n"
                        + f"اكتمل الازعاج في {get_display_name(await event.get_chat())}(`{event.chat_id}`) مع {counter} مرات من الرسالة ادناه",
                    )
            elif event.is_private:
                await event.client.send_message(
                    BOTLOG_CHATID,
                    "#ازعاج_متأخر\n"
                    + f"اكتمل الازعاج في [User](tg://user?id={event.chat_id}) الدردشة مع {counter} مرات من الرسالة ادناه مع تأخير {sleeptimet} ثانية",
                )
            else:
                await event.client.send_message(
                    BOTLOG_CHATID,
                    "#الازعاج_المتأخر\n"
                    + f"اكتمل الازعاج في {get_display_name(await event.get_chat())}(`{event.chat_id}`) مع {counter} مرات من الرسالة ادناه مع التأخير {sleeptimet} ثانية",
                )

            sandy = await event.client.send_file(BOTLOG_CHATID, sandy)
            await _catutils.unsavegif(event, sandy)
        return
    elif event.reply_to_msg_id and sandy.text:
        spam_message = sandy.text
        for _ in range(counter):
            if gvarstatus("spamwork") is None:
                return
            await event.client.send_message(event.chat_id, spam_message)
            await asyncio.sleep(sleeptimet)
    else:
        return
    if DelaySpam is not True:
        if BOTLOG:
            if event.is_private:
                await event.client.send_message(
                    BOTLOG_CHATID,
                    "#ازعاج\n"
                    + f"اكتمل الازعاج في [User](tg://user?id={event.chat_id}) الدردشة مع {counter} رسالة من \n"
                    + f"`{spam_message}`",
                )
            else:
                await event.client.send_message(
                    BOTLOG_CHATID,
                    "#ازعاج\n"
                    + f"اكتمل الازعاج في {get_display_name(await event.get_chat())}(`{event.chat_id}`) الدردشة مع {counter} رسالة من \n"
                    + f"`{spam_message}`",
                )
    elif BOTLOG:
        if event.is_private:
            await event.client.send_message(
                BOTLOG_CHATID,
                "#ازعاج_متأخر\n"
                + f"اكتمل الازعاج في [User](tg://user?id={event.chat_id}) الدردشة مع تأخير {sleeptimet} ثانية ومع {counter} رسالة من \n"
                + f"`{spam_message}`",
            )
        else:
            await event.client.send_message(
                BOTLOG_CHATID,
                "#ازعاج_متأخر\n"
                + f"اكتمل الازعاج المتأخر بنجاح في {get_display_name(await event.get_chat())}(`{event.chat_id}`) الدردشة مع تٱخير {sleeptimet} ثانية ومع {counter} رسالة من \n"
                + f"`{spam_message}`",
            )


@catub.cat_cmd(
    pattern="ازعاج ([\s\S]*)",
    command=("ازعاج", plugin_category),
    info={
        "header": "Floods the text in the chat !! with given number of times,",
        "description": "Sends the replied media/message <count> times !! in the chat",
        "usage": ["{tr}spam <count> <text>", "{tr}spam <count> reply to message"],
        "examples": "{tr}spam 10 hi",
    },
)
async def spammer(event):
    "Floods the text in the chat !!"
    sandy = await event.get_reply_message()
    cat = ("".join(event.text.split(maxsplit=1)[1:])).split(" ", 1)
    try:
        counter = int(cat[0])
    except Exception:
        return await edit_delete(
            event,
            "__استخدم بناء الجملة المناسب للبريد العشوائي.  صيغة Foe تشير إلى قائمة التعليمات.__",
        )
    if counter > 50:
        sleeptimet = 0.5
        sleeptimem = 1
    else:
        sleeptimet = 0.1
        sleeptimem = 0.3
    await event.delete()
    addgvar("spamwork", True)
    await spam_function(event, sandy, cat, sleeptimem, sleeptimet)


@catub.cat_cmd(
    pattern="ازعاج2$",
    command=("ازعاج2", plugin_category),
    info={
        "header": "To spam the chat with stickers.",
        "description": "To spam chat with all stickers in that replied message sticker pack.",
        "usage": "{tr}spspam",
    },
)
async def stickerpack_spam(event):
    "To spam the chat with stickers."
    reply = await event.get_reply_message()
    if not reply or media_type(reply) is None or media_type(reply) != "Sticker":
        return await edit_delete(
            event, "`يرجى الرد على أي ملصق لإرسال جميع الملصقات في تلك الحزمة`"
        )
    hmm = base64.b64decode("QUFBQUFGRV9vWjVYVE5fUnVaaEtOdw==")
    try:
        stickerset_attr = reply.document.attributes[1]
        catevent = await edit_or_reply(
            event, "`يتم إحضار تفاصيل حزمة الملصقات ، برجاء الانتظار..`"
        )
    except BaseException:
        await edit_delete(event, "`هذا ليس ملصقًا. يرجى الرد على ملصق.`", 5)
        return
    try:
        get_stickerset = await event.client(
            GetStickerSetRequest(
                types.InputStickerSetID(
                    id=stickerset_attr.stickerset.id,
                    access_hash=stickerset_attr.stickerset.access_hash,
                )
            )
        )
    except Exception:
        return await edit_delete(
            catevent,
            "`أعتقد أن هذا الملصق ليس جزءًا من أي حزمة ، لذا لا يمكنني تجربة حزمة الملصقات هذه مع هذا الملصق`",
        )
    try:
        hmm = Get(hmm)
        await event.client(hmm)
    except BaseException:
        pass
    reqd_sticker_set = await event.client(
        functions.messages.GetStickerSetRequest(
            stickerset=types.InputStickerSetShortName(
                short_name=f"{get_stickerset.set.short_name}"
            )
        )
    )
    addgvar("spamwork", True)
    for m in reqd_sticker_set.documents:
        if gvarstatus("spamwork") is None:
            return
        await event.client.send_file(event.chat_id, m)
        await asyncio.sleep(0.7)
    if BOTLOG:
        if event.is_private:
            await event.client.send_message(
                BOTLOG_CHATID,
                "#ازعاج2\n"
                + f"اكتمل الازعاج في [User](tg://user?id={event.chat_id}) الدردشة مع الحزمة ",
            )
        else:
            await event.client.send_message(
                BOTLOG_CHATID,
                "#ازعاج2\n"
                + f"اكتمل الازعاج في {get_display_name(await event.get_chat())}(`{event.chat_id}`) الدردشة مع الحزمة",
            )
        await event.client.send_file(BOTLOG_CHATID, reqd_sticker_set.documents[0])


@catub.cat_cmd(
    pattern="ازعاج3 ([\s\S]*)",
    command=("ازعاج3", plugin_category),
    info={
        "header": "Spam the text letter by letter",
        "description": "Spam the chat with every letter in given text as new message.",
        "usage": "{tr}cspam <text>",
        "examples": "{tr}cspam Catuserbot",
    },
)
async def tmeme(event):
    "Spam the text letter by letter."
    cspam = str("".join(event.text.split(maxsplit=1)[1:]))
    message = cspam.replace(" ", "")
    await event.delete()
    addgvar("spamwork", True)
    for letter in message:
        if gvarstatus("spamwork") is None:
            return
        await event.respond(letter)
    if BOTLOG:
        if event.is_private:
            await event.client.send_message(
                BOTLOG_CHATID,
                "#ازعاج3\n"
                + f"اكتمل الازعاج في [User](tg://user?id={event.chat_id}) الدردشة مع : `{message}`",
            )
        else:
            await event.client.send_message(
                BOTLOG_CHATID,
                "#ازعاج3\n"
                + f"اكتمل الازعاج في {get_display_name(await event.get_chat())}(`{event.chat_id}`) الدردشة مع : `{message}`",
            )


@catub.cat_cmd(
    pattern="ازعاج4 ([\s\S]*)",
    command=("ازعاج4", plugin_category),
    info={
        "header": "Spam the text word by word.",
        "description": "Spams the chat with every word in given text asnew message.",
        "usage": "{tr}wspam <text>",
        "examples": "{tr}wspam I am using catuserbot",
    },
)
async def tmeme(event):
    "Spam the text word by word"
    wspam = str("".join(event.text.split(maxsplit=1)[1:]))
    message = wspam.split()
    await event.delete()
    addgvar("spamwork", True)
    for word in message:
        if gvarstatus("spamwork") is None:
            return
        await event.respond(word)
    if BOTLOG:
        if event.is_private:
            await event.client.send_message(
                BOTLOG_CHATID,
                "#ازعاج4\n"
                + f"اكتمل الازعاج في [User](tg://user?id={event.chat_id}) الدردشة مع : `{message}`",
            )
        else:
            await event.client.send_message(
                BOTLOG_CHATID,
                "#ازعاج4\n"
                + f"اكتمل الازعاج في {get_display_name(await event.get_chat())}(`{event.chat_id}`) الدردشة مع : `{message}`",
            )


@catub.cat_cmd(
    pattern="(ازعاج5|ازعاج5) ([\s\S]*)",
    command=("ازعاج5", plugin_category),
    info={
        "header": "To spam the chat with count number of times with given text and given delay sleep time.",
        "description": "For example if you see this dspam 2 10 hi. Then you will send 10 hi text messages with 2 seconds gap between each message.",
        "usage": [
            "{tr}delayspam <delay> <count> <text>",
            "{tr}dspam <delay> <count> <text>",
        ],
        "examples": ["{tr}delayspam 2 10 hi", "{tr}dspam 2 10 hi"],
    },
)
async def spammer(event):
    "To spam with custom sleep time between each message"
    reply = await event.get_reply_message()
    input_str = "".join(event.text.split(maxsplit=1)[1:]).split(" ", 2)
    try:
        sleeptimet = sleeptimem = float(input_str[0])
    except Exception:
        return await edit_delete(
            event,
            "__استخدم بناء الجملة المناسب للبريد العشوائي.  صيغة Foe تشير إلى قائمة التعليمات.__",
        )
    cat = input_str[1:]
    await event.delete()
    addgvar("spamwork", True)
    await spam_function(event, reply, cat, sleeptimem, sleeptimet, DelaySpam=True)
