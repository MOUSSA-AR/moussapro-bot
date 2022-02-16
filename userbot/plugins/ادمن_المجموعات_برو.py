import asyncio
from datetime import datetime

from telethon.errors import BadRequestError
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import ChatBannedRights
from telethon.utils import get_display_name

from userbot import catub

from ..core.managers import edit_delete, edit_or_reply
from ..helpers.utils import _format
from ..sql_helper import gban_sql_helper as gban_sql
from ..sql_helper.mute_sql import is_muted, mute, unmute
from . import BOTLOG, BOTLOG_CHATID, admin_groups, get_user_from_event

plugin_category = "admin"

BANNED_RIGHTS = ChatBannedRights(
    until_date=None,
    view_messages=True,
    send_messages=True,
    send_media=True,
    send_stickers=True,
    send_gifs=True,
    send_games=True,
    send_inline=True,
    embed_links=True,
)

UNBAN_RIGHTS = ChatBannedRights(
    until_date=None,
    send_messages=None,
    send_media=None,
    send_stickers=None,
    send_gifs=None,
    send_games=None,
    send_inline=None,
    embed_links=None,
)


@catub.cat_cmd(
    pattern="حظر(?:\s|$)([\s\S]*)",
    command=("حظر", plugin_category),
    info={
        "header": "To ban user in every group where you are admin.",
        "description": "Will ban the person in every group where you are admin only.",
        "usage": "{tr}gban <username/reply/userid> <reason (optional)>",
    },
)
async def catgban(event):  # sourcery no-metrics
    "To ban user in every group where you are admin."
    cate = await edit_or_reply(event, "`جاري حظر العضو.......`")
    start = datetime.now()
    user, reason = await get_user_from_event(event, cate)
    if not user:
        return
    if user.id == catub.uid:
        return await edit_delete(cate, "`لماذا احظر نفسي!`")
    if gban_sql.is_gbanned(user.id):
        await cate.edit(
            f"`العضو `[user](tg://user?id={user.id})` محظور بالفعل`"
        )
    else:
        gban_sql.catgban(user.id, reason)
    san = await admin_groups(event.client)
    count = 0
    sandy = len(san)
    if sandy == 0:
        return await edit_delete(cate, "`أنت لست ادمن في المجموعة` ")
    await cate.edit(
        f"`تم حظر العضو `[user](tg://user?id={user.id}) `في {len(san)} من المجموعات`"
    )
    for i in range(sandy):
        try:
            await event.client(EditBannedRequest(san[i], user.id, BANNED_RIGHTS))
            await asyncio.sleep(0.5)
            count += 1
        except BadRequestError:
            achat = await event.client.get_entity(san[i])
            await event.client.send_message(
                BOTLOG_CHATID,
                f"`ليس لديك الإذن المطلوب في :`\n**الدردشة :** {get_display_name(achat)}(`{achat.id}`)\n`للحظر هنا`",
            )
    end = datetime.now()
    cattaken = (end - start).seconds
    if reason:
        await cate.edit(
            f"[{user.first_name}](tg://user?id={user.id}) `تم حظره في {count} من المجموعات في {cattaken} ثانية`!!\n**السبب :** `{reason}`"
        )
    else:
        await cate.edit(
            f"[{user.first_name}](tg://user?id={user.id}) `تم حظره في {count} من المجموعات في {cattaken} ثانية`!!"
        )
    if BOTLOG and count != 0:
        reply = await event.get_reply_message()
        if reason:
            await event.client.send_message(
                BOTLOG_CHATID,
                f"#الحظر\
                \nحظر في المجموعات\
                \n**العضو : **[{user.first_name}](tg://user?id={user.id})\
                \n**الايدي : **`{user.id}`\
                \n**السبب :** `{reason}`\
                \n__حظر في {count} من المجموعات__\
                \n**الوقت المستغرق : **`{cattaken} ثانية`",
            )
        else:
            await event.client.send_message(
                BOTLOG_CHATID,
                f"#الحظر\
                \nحظر في المجموعات\
                \n**العضو : **[{user.first_name}](tg://user?id={user.id})\
                \n**الايدي : **`{user.id}`\
                \n__حظر في {count} من المجموعات__\
                \n**الوقت المستغرق : **`{cattaken} ثانية`",
            )
        try:
            if reply:
                await reply.forward_to(BOTLOG_CHATID)
                await reply.delete()
        except BadRequestError:
            pass


@catub.cat_cmd(
    pattern="الغاء حظر(?:\s|$)([\s\S]*)",
    command=("الغاء حظر", plugin_category),
    info={
        "header": "To unban the person from every group where you are admin.",
        "description": "will unban and also remove from your gbanned list.",
        "usage": "{tr}ungban <username/reply/userid>",
    },
)
async def catgban(event):
    "To unban the person from every group where you are admin."
    cate = await edit_or_reply(event, "`جاري الغاء حظر العضو.....`")
    start = datetime.now()
    user, reason = await get_user_from_event(event, cate)
    if not user:
        return
    if gban_sql.is_gbanned(user.id):
        gban_sql.catungban(user.id)
    else:
        return await edit_delete(
            cate, f"العضو [user](tg://user?id={user.id}) `ليس محظور`"
        )
    san = await admin_groups(event.client)
    count = 0
    sandy = len(san)
    if sandy == 0:
        return await edit_delete(cate, "`أنت لست ادمن في المجموعة `")
    await cate.edit(
        f"الغاء حظر العضو [user](tg://user?id={user.id}) في `{len(san)}` من المجموعات"
    )
    for i in range(sandy):
        try:
            await event.client(EditBannedRequest(san[i], user.id, UNBAN_RIGHTS))
            await asyncio.sleep(0.5)
            count += 1
        except BadRequestError:
            achat = await event.client.get_entity(san[i])
            await event.client.send_message(
                BOTLOG_CHATID,
                f"`ليس لديك الإذن المطلوب في :`\n**الدردشة :** {get_display_name(achat)}(`{achat.id}`)\n`لإلغاء الحظر هنا`",
            )
    end = datetime.now()
    cattaken = (end - start).seconds
    if reason:
        await cate.edit(
            f"[{user.first_name}](tg://user?id={user.id}`) تم الغاء حظره في {count} من المجموعات في {cattaken} ثانية`!!\n**السبب :** `{reason}`"
        )
    else:
        await cate.edit(
            f"[{user.first_name}](tg://user?id={user.id}) `تم الغاء حظره في {count} من المجموعات في {cattaken} ثانية`!!"
        )

    if BOTLOG and count != 0:
        if reason:
            await event.client.send_message(
                BOTLOG_CHATID,
                f"#الغاء_حظر\
                \nالغاء الحظر في المجموعات\
                \n**العضو : **[{user.first_name}](tg://user?id={user.id})\
                \n**الايدي : **`{user.id}`\
                \n**السبب :** `{reason}`\
                \n__تم الغاء حظره في {count} من المجموعات__\
                \n**الوقت المستغرق : **`{cattaken} ثانية`",
            )
        else:
            await event.client.send_message(
                BOTLOG_CHATID,
                f"#الغاء_حظر\
                \nالغاء الحظر في المجموعات\
                \n**المعرف : **[{user.first_name}](tg://user?id={user.id})\
                \n**الايدي : **`{user.id}`\
                \n__تم الغاء حظره في {count} من المجموعات__\
                \n**الوقت المستغرق : **`{cattaken} ثانية`",
            )


@catub.cat_cmd(
    pattern="المحظورين$",
    command=("المحظورين", plugin_category),
    info={
        "header": "Shows you the list of all gbanned users by you.",
        "usage": "{tr}listgban",
    },
)
async def gablist(event):
    "Shows you the list of all gbanned users by you."
    gbanned_users = gban_sql.get_all_gbanned()
    GBANNED_LIST = "المستخدمون المحظورون\n"
    if len(gbanned_users) > 0:
        for a_user in gbanned_users:
            if a_user.reason:
                GBANNED_LIST += f"👉 [{a_user.chat_id}](tg://user?id={a_user.chat_id}) إلى {a_user.reason}\n"
            else:
                GBANNED_LIST += (
                    f"👉 [{a_user.chat_id}](tg://user?id={a_user.chat_id}) لا يوجد سبب\n"
                )
    else:
        GBANNED_LIST = "لا يوجد مستخدمون محظورون (حتى الآن)"
    await edit_or_reply(event, GBANNED_LIST)


@catub.cat_cmd(
    pattern="كتم(?:\s|$)([\s\S]*)",
    command=("كتم", plugin_category),
    info={
        "header": "To mute a person in all groups where you are admin.",
        "description": "It doesnt change user permissions but will delete all messages sent by him in the groups where you are admin including in private messages.",
        "usage": "{tr}gmute username/reply> <reason (optional)>",
    },
)
async def startgmute(event):
    "To mute a person in all groups where you are admin."
    if event.is_private:
        await event.edit("`قد تحدث مشاكل غير متوقعة!`")
        await asyncio.sleep(2)
        userid = event.chat_id
        reason = event.pattern_match.group(1)
    else:
        user, reason = await get_user_from_event(event)
        if not user:
            return
        if user.id == catub.uid:
            return await edit_or_reply(event, "`عذرا, لا يمكنني كتم العضو`")
        userid = user.id
    try:
        user = (await event.client(GetFullUserRequest(userid))).user
    except Exception:
        return await edit_or_reply(event, "`آسف. أنا غير قادر على احضار العضو`")
    if is_muted(userid, "gmute"):
        return await edit_or_reply(
            event,
            f"{_format.mentionuser(user.first_name ,user.id)} ` مكتوم بالفعل`",
        )
    try:
        mute(userid, "gmute")
    except Exception as e:
        await edit_or_reply(event, f"**خطأ**\n`{str(e)}`")
    else:
        if reason:
            await edit_or_reply(
                event,
                f"{_format.mentionuser(user.first_name ,user.id)} `تم كتمه بنجاح`\n**السبب :** `{reason}`",
            )
        else:
            await edit_or_reply(
                event,
                f"{_format.mentionuser(user.first_name ,user.id)} `تم كتمه بنجاح`",
            )
    if BOTLOG:
        reply = await event.get_reply_message()
        if reason:
            await event.client.send_message(
                BOTLOG_CHATID,
                "#كتم\n"
                f"**العضو :** {_format.mentionuser(user.first_name ,user.id)} \n"
                f"**السبب :** `{reason}`",
            )
        else:
            await event.client.send_message(
                BOTLOG_CHATID,
                "#كتم\n"
                f"**العضو :** {_format.mentionuser(user.first_name ,user.id)} \n",
            )
        if reply:
            await reply.forward_to(BOTLOG_CHATID)


@catub.cat_cmd(
    pattern="الغاء كتم(?:\s|$)([\s\S]*)",
    command=("الغاء كتم", plugin_category),
    info={
        "header": "To unmute the person in all groups where you were admin.",
        "description": "This will work only if you mute that person by your gmute command.",
        "usage": "{tr}ungmute <username/reply>",
    },
)
async def endgmute(event):
    "To remove gmute on that person."
    if event.is_private:
        await event.edit("`قد تحدث مشاكل غير متوقعة!`")
        await asyncio.sleep(2)
        userid = event.chat_id
        reason = event.pattern_match.group(1)
    else:
        user, reason = await get_user_from_event(event)
        if not user:
            return
        if user.id == catub.uid:
            return await edit_or_reply(event, "`اعتذر, لا استطيع كتم نفسي`")
        userid = user.id
    try:
        user = (await event.client(GetFullUserRequest(userid))).user
    except Exception:
        return await edit_or_reply(event, "`اعتذر. أنا غير قادر على احضار المستخدم`")
    if not is_muted(userid, "gmute"):
        return await edit_or_reply(
            event, f"{_format.mentionuser(user.first_name ,user.id)} `ليس مكتوما`"
        )
    try:
        unmute(userid, "gmute")
    except Exception as e:
        await edit_or_reply(event, f"**خطأ**\n`{str(e)}`")
    else:
        if reason:
            await edit_or_reply(
                event,
                f"{_format.mentionuser(user.first_name ,user.id)} `تم الغاء كتمه بنجاح`\n**السبب :** `{reason}`",
            )
        else:
            await edit_or_reply(
                event,
                f"{_format.mentionuser(user.first_name ,user.id)} `تم الغاء كتمه بنجاح`",
            )
    if BOTLOG:
        if reason:
            await event.client.send_message(
                BOTLOG_CHATID,
                "#الغاء_كتم\n"
                f"**العضو :** {_format.mentionuser(user.first_name ,user.id)} \n"
                f"**السبب :** `{reason}`",
            )
        else:
            await event.client.send_message(
                BOTLOG_CHATID,
                "#الغاء_كتم\n"
                f"**العضو :** {_format.mentionuser(user.first_name ,user.id)} \n",
            )


@catub.cat_cmd(incoming=True)
async def watcher(event):
    if is_muted(event.sender_id, "gmute"):
        await event.delete()


@catub.cat_cmd(
    pattern="طرد(?:\s|$)([\s\S]*)",
    command=("طرد", plugin_category),
    info={
        "header": "kicks the person in all groups where you are admin.",
        "usage": "{tr}gkick <username/reply/userid> <reason (optional)>",
    },
)
async def catgkick(event):  # sourcery no-metrics
    "kicks the person in all groups where you are admin"
    cate = await edit_or_reply(event, "`جاري طرد العضو.......`")
    start = datetime.now()
    user, reason = await get_user_from_event(event, cate)
    if not user:
        return
    if user.id == catub.uid:
        return await edit_delete(cate, "`لامكنني طرد نفسي`")
    san = await admin_groups(event.client)
    count = 0
    sandy = len(san)
    if sandy == 0:
        return await edit_delete(cate, "`أنا لست ادمن في المجموعة` ")
    await cate.edit(
        f"`جاري طرد العضو `[user](tg://user?id={user.id}) `في {len(san)} من المجموعات`"
    )
    for i in range(sandy):
        try:
            await event.client.kick_participant(san[i], user.id)
            await asyncio.sleep(0.5)
            count += 1
        except BadRequestError:
            achat = await event.client.get_entity(san[i])
            await event.client.send_message(
                BOTLOG_CHATID,
                f"`ليس لديك الأذن المطلوب في :`\n**الدردشة :** {get_display_name(achat)}(`{achat.id}`)\n`لتستطيع الطرد هناك`",
            )
    end = datetime.now()
    cattaken = (end - start).seconds
    if reason:
        await cate.edit(
            f"[{user.first_name}](tg://user?id={user.id}) `تم طرده من {count} من المجموعات في {cattaken} ثانية`!!\n**السبب :** `{reason}`"
        )
    else:
        await cate.edit(
            f"[{user.first_name}](tg://user?id={user.id}) `تم طرده من {count} من المجموعات في {cattaken} ثانية`!!"
        )

    if BOTLOG and count != 0:
        reply = await event.get_reply_message()
        if reason:
            await event.client.send_message(
                BOTLOG_CHATID,
                f"#طرد\
                \nالطرد في المجموعات\
                \n**العضو : **[{user.first_name}](tg://user?id={user.id})\
                \n**الايدي : **`{user.id}`\
                \n**السبب :** `{reason}`\
                \n__تم طرده في {count} من المجموعات__\
                \n**الوقت المستغرق : **`{cattaken} ثانية`",
            )
        else:
            await event.client.send_message(
                BOTLOG_CHATID,
                f"#طرد\
                \nالطرد في المجموعات\
                \n**العضو : **[{user.first_name}](tg://user?id={user.id})\
                \n**الايدي : **`{user.id}`\
                \n__تم طرده في {count} من المجموعات__\
                \n**الوقت المستغرق : **`{cattaken} ثانية`",
            )
        if reply:
            await reply.forward_to(BOTLOG_CHATID)
