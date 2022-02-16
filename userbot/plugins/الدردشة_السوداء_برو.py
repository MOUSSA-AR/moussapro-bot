from datetime import datetime

from telethon.utils import get_display_name

from userbot import catub
from userbot.core.logger import logging

from ..core.data import blacklist_chats_list
from ..core.managers import edit_delete, edit_or_reply
from ..sql_helper import global_collectionjson as sql
from ..sql_helper.globals import addgvar, delgvar, gvarstatus

plugin_category = "tools"

LOGS = logging.getLogger(__name__)


@catub.cat_cmd(
    pattern="الدردشة السوداء (on|off)$",
    command=("الدردشة السوداء", plugin_category),
    info={
        "header": "To enable and disable chats blacklist.",
        "description": "If you turn this on, then your userbot won't work on the chats stored\
         in database by addblkchat cmd. If you turn it off even though you added chats to database\
         userbot won't stop working in that chat.",
        "usage": "{tr}chatblacklist <on/off>",
    },
)
async def chat_blacklist(event):
    "To enable and disable chats blacklist."
    input_str = event.pattern_match.group(1)
    blkchats = blacklist_chats_list()
    if input_str == "on":
        if gvarstatus("blacklist_chats") is not None:
            return await edit_delete(event, "__تم تمكينه بالفعل.__")
        addgvar("blacklist_chats", "true")
        text = "__من الآن فصاعدًا ، لن يعمل البوت برو في الدردشات المخزنة في قاعدة البيانات.__"
        if len(blkchats) != 0:
            text += (
                "**يقوم البوت بإعادة التحميل لتطبيق التغييرات.  من فضلك انتظر دقيقة**"
            )
            msg = await edit_or_reply(
                event,
                text,
            )
            return await event.client.reload(msg)
        else:
            text += "**لم تقم بإضافة أي دردشة إلى القائمة السوداء.**"
            return await edit_or_reply(
                event,
                text,
            )
    if gvarstatus("blacklist_chats") is not None:
        delgvar("blacklist_chats")
        text = "__إن البوت برو الخاص بك بوضع ممتاز ، وهو يعمل في كل محادثة.__"
        if len(blkchats) != 0:
            text += (
                "**يقوم البوت بإعادة التحميل لتطبيق التغييرات.  من فضلك انتظر دقيقة**"
            )
            msg = await edit_or_reply(
                event,
                text,
            )
            return await event.client.reload(msg)
        else:
            text += "**لم تقم بإضافة أي دردشة إلى القائمة السوداء.**"
            return await edit_or_reply(
                event,
                text,
            )
    await edit_delete(event, "تم إيقاف تشغيله بالفعل")


@catub.cat_cmd(
    pattern="اضف دردشة(s)?(?:\s|$)([\s\S]*)",
    command=("اضف دردشة", plugin_category),
    info={
        "header": "To add chats to blacklist.",
        "description": "to add the chats to database so your bot doesn't work in\
         thoose chats. Either give chatids as input or do this cmd in the chat\
         which you want to add to db.",
        "usage": [
            "{tr}addblkchat <chat ids>",
            "{tr}addblkchat in the chat which you want to add",
        ],
    },
)
async def add_blacklist_chat(event):
    "To add chats to blacklist."
    input_str = event.pattern_match.group(2)
    errors = ""
    result = ""
    blkchats = blacklist_chats_list()
    try:
        blacklistchats = sql.get_collection("blacklist_chats_list").json
    except AttributeError:
        blacklistchats = {}
    if input_str:
        input_str = input_str.split(" ")
        for chatid in input_str:
            try:
                chatid = int(chatid.strip())
                if chatid in blkchats:
                    errors += f"**اثناء اضافة الدردشة {chatid}** - __تم بالفعل وضع هذه الدردشة في القائمة السوداء__\n"
                    continue
                chat = await event.client.get_entity(chatid)
                date = str(datetime.now().strftime("%B %d, %Y"))
                chatdata = {
                    "chat_id": chat.id,
                    "chat_name": get_display_name(chat),
                    "chat_username": chat.username,
                    "date": date,
                }
                blacklistchats[str(chat.id)] = chatdata
                result += (
                    f"تم اضافة {get_display_name(chat)} إلى القائمة السوداء للدردشات.\n"
                )
            except Exception as e:
                errors += f"**اثناء اضافة الدردشة {chatid}** - __{str(e)}__\n"
    else:
        chat = await event.get_chat()
        try:
            chatid = chat.id
            if chatid in blkchats:
                errors += f"**اثناء اضافة الدردشة {chatid}**__تم بالفعل وضع هذه الدردشة في القائمة السوداء__\n"
            else:
                date = str(datetime.now().strftime("%B %d, %Y"))
                chatdata = {
                    "chat_id": chat.id,
                    "chat_name": get_display_name(chat),
                    "chat_username": chat.username,
                    "date": date,
                }
                blacklistchats[str(chat.id)] = chatdata
                result += (
                    f"تم اضافة {get_display_name(chat)} إلى القائمة السوداء للدردشات.\n"
                )
        except Exception as e:
            errors += f"**جاري اضافة الدردشة {chatid}** - __{str(e)}__\n"
    sql.del_collection("blacklist_chats_list")
    sql.add_collection("blacklist_chats_list", blacklistchats, {})
    output = ""
    if result != "":
        output += f"**نجاح:**\n{result}\n"
    if errors != "":
        output += f"**فشل:**\n{errors}\n"
    if result != "":
        output += "**يقوم البوت بإعادة التحميل لتطبيق التغييرات.  من فضلك انتظر دقيقة**"
    msg = await edit_or_reply(event, output)
    await event.client.reload(msg)


@catub.cat_cmd(
    pattern="اازالة دردشة(s)?(?:\s|$)([\s\S]*)",
    command=("ازالة دردشة", plugin_category),
    info={
        "header": "To remove chats to blacklist.",
        "description": "to remove the chats from database so your bot will work in\
         those chats. Either give chatids as input or do this cmd in the chat\
         which you want to remove from db.",
        "usage": [
            "{tr}rmblkchat <chat ids>",
            "{tr}rmblkchat in the chat which you want to add",
        ],
    },
)
async def add_blacklist_chat(event):
    "To remove chats from blacklisted chats."
    input_str = event.pattern_match.group(2)
    errors = ""
    result = ""
    blkchats = blacklist_chats_list()
    try:
        blacklistchats = sql.get_collection("blacklist_chats_list").json
    except AttributeError:
        blacklistchats = {}
    if input_str:
        input_str = input_str.split(" ")
        for chatid in input_str:
            try:
                chatid = int(chatid.strip())
                if chatid in blkchats:
                    chatname = blacklistchats[str(chatid)]["chat_name"]
                    del blacklistchats[str(chatid)]
                    result += (
                        f"تم ازالة {chatname} من القائمة السوداء للدردشات.\n"
                    )
                else:
                    errors += f"العضو {chatid} لا يوجد في قاعدة البيانات الخاصة بك.  هذا العضو لم يتم إدراجه في القائمة السوداء.\n"
            except Exception as e:
                errors += f"**اثناء ازالة الدردشة {chatid}** - __{str(e)}__\n"
    else:
        chat = await event.get_chat()
        try:
            chatid = chat.id
            if chatid in blkchats:
                chatname = blacklistchats[str(chatid)]["chat_name"]
                del blacklistchats[str(chatid)]
                result += f"تم ازالة {chatname} من القائمة السوداء للدردشات.\n"
            else:
                errors += f"العضو {chatid} لا يوجد في قاعدة البيانات الخاصة بك.  هذا العضو لم يتم إدراجه في القائمة السوداء.\n"
        except Exception as e:
            errors += f"**اثناء ازالة العضو {chatid}** - __{str(e)}__\n"
    sql.del_collection("blacklist_chats_list")
    sql.add_collection("blacklist_chats_list", blacklistchats, {})
    output = ""
    if result != "":
        output += f"**نجاح:**\n{result}\n"
    if errors != "":
        output += f"**فشل:**\n{errors}\n"
    if result != "":
        output += "**يقوم البوت بإعادة التحميل لتطبيق التغييرات.  من فضلك انتظر دقيقة**"
    msg = await edit_or_reply(event, output)
    await event.client.reload(msg)


@catub.cat_cmd(
    pattern="الدردشة السوداء$",
    command=("الدردشة السوداء", plugin_category),
    info={
        "header": "To list all blacklisted chats.",
        "description": "Will show you the list of all blacklisted chats",
        "usage": [
            "{tr}listblkchat",
        ],
    },
)
async def add_blacklist_chat(event):
    "To show list of chats which are blacklisted."
    blkchats = blacklist_chats_list()
    try:
        blacklistchats = sql.get_collection("blacklist_chats_list").json
    except AttributeError:
        blacklistchats = {}
    if len(blkchats) == 0:
        return await edit_delete(
            event, "__لا توجد محادثات في القائمة السوداء في البوت الخاص بك .__"
        )
    result = "**قائمة الدردشات المدرجة في القائمة السوداء هي :**\n\n"
    for chat in blkchats:
        result += f"☞ {blacklistchats[str(chat)]['chat_name']}\n"
        result += f"**ايدي الدردشة :** `{chat}`\n"
        username = blacklistchats[str(chat)]["chat_username"] or "__مجموعة خاصة__"
        result += f"**معرف الدردشة :** {username}\n"
        result += f"اضافة في {blacklistchats[str(chat)]['date']}\n\n"
    await edit_or_reply(event, result)
