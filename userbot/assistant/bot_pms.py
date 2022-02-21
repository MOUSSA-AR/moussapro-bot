import re
from collections import defaultdict
from datetime import datetime
from typing import Optional, Union

from telethon import Button, events
from telethon.errors import UserIsBlockedError
from telethon.events import CallbackQuery, StopPropagation
from telethon.utils import get_display_name

from userbot import Config, moussabot

from ..core import check_owner, pool
from ..core.logger import logging
from ..core.session import tgbot
from ..helpers import reply_id
from ..helpers.utils import _format
from ..sql_helper.bot_blacklists import check_is_black_list
from ..sql_helper.bot_pms_sql import (
    add_user_to_db,
    get_user_id,
    get_user_logging,
    get_user_reply,
)
from ..sql_helper.bot_starters import add_starter_to_db, get_starter_details
from ..sql_helper.globals import delgvar, gvarstatus
from . import BOTLOG, BOTLOG_CHATID
from .botmanagers import ban_user_from_bot

LOGS = logging.getLogger(__name__)

plugin_category = "bot"
botusername = Config.TG_BOT_USERNAME


class FloodConfig:
    BANNED_USERS = set()
    USERS = defaultdict(list)
    MESSAGES = 3
    SECONDS = 6
    ALERT = defaultdict(dict)
    AUTOBAN = 10


async def check_bot_started_users(user, event):
    if user.id == Config.OWNER_ID:
        return
    check = get_starter_details(user.id)
    if check is None:
        start_date = str(datetime.now().strftime("%B %d, %Y"))
        notification = f"👤 {_format.mentionuser(user.first_name , user.id)}بدء.\
                \n**الايدي: **`{user.id}`\
                \n**الاسم: **{get_display_name(user)}"
    else:
        start_date = check.date
        notification = f"👤 {_format.mentionuser(user.first_name , user.id)} اعادة بدء.\
                \n**الايدي: **`{user.id}`\
                \n**الاسم: **{get_display_name(user)}"
    try:
        add_starter_to_db(user.id, get_display_name(user), start_date, user.username)
    except Exception as e:
        LOGS.error(str(e))
    if BOTLOG:
        await event.client.send_message(BOTLOG_CHATID, notification)


@moussabot.bot_cmd(
    pattern=f"^/start({botusername})?([\s]+)?$",
    incoming=True,
    func=lambda e: e.is_private,
)
async def bot_start(event):
    chat = await event.get_chat()
    user = await moussabot.get_me()
    if check_is_black_list(chat.id):
        return
    reply_to = await reply_id(event)
    mention = f"[{chat.first_name}](tg://user?id={chat.id})"
    my_mention = f"[{user.first_name}](tg://user?id={user.id})"
    first = chat.first_name
    last = chat.last_name
    fullname = f"{first} {last}" if last else first
    username = f"@{chat.username}" if chat.username else mention
    userid = chat.id
    my_first = user.first_name
    my_last = user.last_name
    my_fullname = f"{my_first} {my_last}" if my_last else my_first
    my_username = f"@{user.username}" if user.username else my_mention
    if chat.id != Config.OWNER_ID:
        customstrmsg = gvarstatus("START_TEXT") or None
        if customstrmsg is not None:
            start_msg = customstrmsg.format(
                mention=mention,
                first=first,
                last=last,
                fullname=fullname,
                username=username,
                userid=userid,
                my_first=my_first,
                my_last=my_last,
                my_fullname=my_fullname,
                my_username=my_username,
                my_mention=my_mention,
            )
        else:
            start_msg = f"اهلا! 👤{mention},\
                        \nأنا {my_mention}'المساعد الخاص.\
                        \nيمكنك الاتصال بسيدي من هنا.\
                        \n\nمشغل بواسطة [MOUSSA-PRO](Https://t.me/moussa_bot)"
        buttons = [
            (
                Button.url("سورس برو", "https://github.com/MOUSSA-AR/moussapro-bot"),
                Button.url(
                    "تنصيب",
                    "https://dashboard.heroku.com/new?button-url=https%3A%2F%2Fgithub.com%2FMOUSSA-AR%2Fmoussabot&template=https%3A%2F%2Fgithub.com%2FMOUSSA-AR%2Fmoussabot",
                ),
            )
        ]
    else:
        start_msg = "مرحبا سيدي!\
            \nكيف يمكنني مساعدتك ?"
        buttons = None
    try:
        await event.client.send_message(
            chat.id,
            start_msg,
            link_preview=False,
            buttons=buttons,
            reply_to=reply_to,
        )
    except Exception as e:
        if BOTLOG:
            await event.client.send_message(
                BOTLOG_CHATID,
                f"**خطأ**\nحدث خطأ أثناء بدء تشغيل البوت الخاص بك.\
                \n`{str(e)}`",
            )
    else:
        await check_bot_started_users(chat, event)


@moussabot.bot_cmd(incoming=True, func=lambda e: e.is_private)
async def bot_pms(event):  # sourcery no-metrics
    chat = await event.get_chat()
    if check_is_black_list(chat.id):
        return
    if chat.id != Config.OWNER_ID:
        msg = await event.forward_to(Config.OWNER_ID)
        try:
            add_user_to_db(msg.id, get_display_name(chat), chat.id, event.id, 0, 0)
        except Exception as e:
            LOGS.error(str(e))
            if BOTLOG:
                await event.client.send_message(
                    BOTLOG_CHATID,
                    f"**خطأ**\nأثناء تخزين تفاصيل الرسائل في قاعدة البيانات\n`{str(e)}`",
                )
    else:
        if event.text.startswith("/"):
            return
        reply_to = await reply_id(event)
        if reply_to is None:
            return
        users = get_user_id(reply_to)
        if users is None:
            return
        for usr in users:
            user_id = int(usr.chat_id)
            reply_msg = usr.reply_id
            user_name = usr.first_name
            break
        if user_id is not None:
            try:
                if event.media:
                    msg = await event.client.send_file(
                        user_id, event.media, caption=event.text, reply_to=reply_msg
                    )
                else:
                    msg = await event.client.send_message(
                        user_id, event.text, reply_to=reply_msg
                    )
            except UserIsBlockedError:
                return await event.reply("قام المستخدم بحظر البوت. ❌")
            except Exception as e:
                return await event.reply(f"**خطأ:**\n`{str(e)}`")
            try:
                add_user_to_db(
                    reply_to, user_name, user_id, reply_msg, event.id, msg.id
                )
            except Exception as e:
                LOGS.error(str(e))
                if BOTLOG:
                    await event.client.send_message(
                        BOTLOG_CHATID,
                        f"**خطأ**\nأثناء تخزين تفاصيل الرسائل في قاعدة البيانات\n`{str(e)}`",
                    )


@moussabot.bot_cmd(edited=True)
async def bot_pms_edit(event):  # sourcery no-metrics
    chat = await event.get_chat()
    if check_is_black_list(chat.id):
        return
    if chat.id != Config.OWNER_ID:
        users = get_user_reply(event.id)
        if users is None:
            return
        reply_msg = None
        for user in users:
            if user.chat_id == str(chat.id):
                reply_msg = user.message_id
                break
        if reply_msg:
            await event.client.send_message(
                Config.OWNER_ID,
                f"⬆️ **تم تحرير هذه الرسالة من قبل المستخدم** {_format.mentionuser(get_display_name(chat) , chat.id)} as :",
                reply_to=reply_msg,
            )
            msg = await event.forward_to(Config.OWNER_ID)
            try:
                add_user_to_db(msg.id, get_display_name(chat), chat.id, event.id, 0, 0)
            except Exception as e:
                LOGS.error(str(e))
                if BOTLOG:
                    await event.client.send_message(
                        BOTLOG_CHATID,
                        f"**خطأ**\nأثناء تخزين تفاصيل الرسائل في قاعدة البيانات\n`{str(e)}`",
                    )
    else:
        reply_to = await reply_id(event)
        if reply_to is not None:
            users = get_user_id(reply_to)
            result_id = 0
            if users is None:
                return
            for usr in users:
                if event.id == usr.logger_id:
                    user_id = int(usr.chat_id)
                    reply_msg = usr.reply_id
                    result_id = usr.result_id
                    break
            if result_id != 0:
                try:
                    await event.client.edit_message(
                        user_id, result_id, event.text, file=event.media
                    )
                except Exception as e:
                    LOGS.error(str(e))


@tgbot.on(events.MessageDeleted)
async def handler(event):
    for msg_id in event.deleted_ids:
        users_1 = get_user_reply(msg_id)
        users_2 = get_user_logging(msg_id)
        if users_2 is not None:
            result_id = 0
            for usr in users_2:
                if msg_id == usr.logger_id:
                    user_id = int(usr.chat_id)
                    result_id = usr.result_id
                    break
            if result_id != 0:
                try:
                    await event.client.delete_messages(user_id, result_id)
                except Exception as e:
                    LOGS.error(str(e))
        if users_1 is not None:
            reply_msg = None
            for user in users_1:
                if user.chat_id != Config.OWNER_ID:
                    reply_msg = user.message_id
                    break
            try:
                if reply_msg:
                    users = get_user_id(reply_msg)
                    for usr in users:
                        user_id = int(usr.chat_id)
                        user_name = usr.first_name
                        break
                    if check_is_black_list(user_id):
                        return
                    await event.client.send_message(
                        Config.OWNER_ID,
                        f"⬆️ **قام المستخدم بحذف الرسالة** {_format.mentionuser(user_name , user_id)}.",
                        reply_to=reply_msg,
                    )
            except Exception as e:
                LOGS.error(str(e))


@moussabot.bot_cmd(
    pattern=f"^/uinfo$",
    from_users=Config.OWNER_ID,
)
async def bot_start(event):
    reply_to = await reply_id(event)
    if not reply_to:
        return await event.reply("الرد على رسالة للحصول على معلومات الرسالة")
    info_msg = await event.client.send_message(
        event.chat_id,
        "`🔎 البحث عن هذا المستخدم في قاعدة البيانات الخاصة بي ...`",
        reply_to=reply_to,
    )
    users = get_user_id(reply_to)
    if users is None:
        return await info_msg.edit(
            "**خطأ:** \n`آسف !, لا يمكن العثور على هذا المستخدم في قاعدة البيانات الخاصة بي :(`"
        )
    for usr in users:
        user_id = int(usr.chat_id)
        user_name = usr.first_name
        break
    if user_id is None:
        return await info_msg.edit(
            "**خطأ:** \n`آسف !, لا يمكن العثور على هذا المستخدم في قاعدة البيانات الخاصة بي :(`"
        )
    uinfo = f"تم إرسال هذه الرسالة بواسطة 👤 {_format.mentionuser(user_name , user_id)}\
            \n**الاسم الأول:** {user_name}\
            \n**ايدي المستخدم:** `{user_id}`"
    await info_msg.edit(uinfo)


async def send_flood_alert(user_) -> None:
    # sourcery no-metrics
    buttons = [
        (
            Button.inline("🚫  حظر", data=f"bot_pm_ban_{user_.id}"),
            Button.inline(
                "➖ بوت العميل [OFF]",
                data="toggle_bot-antiflood_off",
            ),
        )
    ]
    found = False
    if FloodConfig.ALERT and (user_.id in FloodConfig.ALERT.keys()):
        found = True
        try:
            FloodConfig.ALERT[user_.id]["count"] += 1
        except KeyError:
            found = False
            FloodConfig.ALERT[user_.id]["count"] = 1
        except Exception as e:
            if BOTLOG:
                await moussabot.tgbot.send_message(
                    BOTLOG_CHATID, f"**خطأ:**\nأثناء تحديث عدد الفيضانات\n`{str(e)}`"
                )
        flood_count = FloodConfig.ALERT[user_.id]["count"]
    else:
        flood_count = FloodConfig.ALERT[user_.id]["count"] = 1

    flood_msg = (
        r"⚠️ **#تحذيرات_المزعجين**"
        "\n\n"
        f"  الايدي: `{user_.id}`\n"
        f"  الاسم: {get_display_name(user_)}\n"
        f"  👤 المعرف: {_format.mentionuser(get_display_name(user_), user_.id)}"
        f"\n\n**يقوم بإرسال بريد عشوائي إلى البوت الخاص بك !** ->  [ معدل الفيضان ({flood_count}) ]\n"
        "__إجراء سريع__: تم الحظر من البوت لفترة من الوقت."
    )

    if found:
        if flood_count >= FloodConfig.AUTOBAN:
            if user_.id in Config.SUDO_USERS:
                sudo_spam = (
                    f"**مستخدم_ثانوي** {_format.mentionuser(user_.first_name , user_.id)}:\n  ID: {user_.id}\n\n"
                    "يزعج البوت الخاص بك !, تفقد `.مساعدة ازالة مستخدم` لإزالة المستخدم من قائمة المستخدمين."
                )
                if BOTLOG:
                    await moussabot.tgbot.send_message(BOTLOG_CHATID, sudo_spam)
            else:
                await ban_user_from_bot(
                    user_,
                    f"حظر تلقائي للمزعجين [تجاوز معدل الازعاجات ({FloodConfig.AUTOBAN})]",
                )
                FloodConfig.USERS[user_.id].clear()
                FloodConfig.ALERT[user_.id].clear()
                FloodConfig.BANNED_USERS.remove(user_.id)
            return
        fa_id = FloodConfig.ALERT[user_.id].get("fa_id")
        if not fa_id:
            return
        try:
            msg_ = await catub.tgbot.get_messages(BOTLOG_CHATID, fa_id)
            if msg_.text != flood_msg:
                await msg_.edit(flood_msg, buttons=buttons)
        except Exception as fa_id_err:
            LOGS.debug(fa_id_err)
            return
    else:
        if BOTLOG:
            fa_msg = await moussabot.tgbot.send_message(
                BOTLOG_CHATID,
                flood_msg,
                buttons=buttons,
            )
        try:
            chat = await moussabot.tgbot.get_entity(BOTLOG_CHATID)
            await moussabot.tgbot.send_message(
                Config.OWNER_ID,
                f"⚠️  **[تحذير من المزعجين !](https://t.me/c/{chat.id}/{fa_msg.id})**",
            )
        except UserIsBlockedError:
            if BOTLOG:
                await moussabot.tgbot.send_message(BOTLOG_CHATID, "**قم بإلغاء حظر البوت الخاص بك !**")
    if FloodConfig.ALERT[user_.id].get("fa_id") is None and fa_msg:
        FloodConfig.ALERT[user_.id]["fa_id"] = fa_msg.id


@moussabot.tgbot.on(CallbackQuery(data=re.compile(b"bot_pm_ban_([0-9]+)")))
@check_owner
async def bot_pm_ban_cb(c_q: CallbackQuery):
    user_id = int(c_q.pattern_match.group(1))
    try:
        user = await moussabot.get_entity(user_id)
    except Exception as e:
        await c_q.answer(f"خطأ:\n{str(e)}")
    else:
        await c_q.answer(f"حظر المستخدم -> {user_id} ...", alert=False)
        await ban_user_from_bot(user, "Spamming Bot")
        await c_q.edit(f"✅ **اكتمل الحظر**  معرف المستخدم: {user_id}")


def time_now() -> Union[float, int]:
    return datetime.timestamp(datetime.now())


@pool.run_in_thread
def is_flood(uid: int) -> Optional[bool]:
    """يتحقق من المستخدم"""
    FloodConfig.USERS[uid].append(time_now())
    if (
        len(
            list(
                filter(
                    lambda x: time_now() - int(x) < FloodConfig.SECONDS,
                    FloodConfig.USERS[uid],
                )
            )
        )
        > FloodConfig.MESSAGES
    ):
        FloodConfig.USERS[uid] = list(
            filter(
                lambda x: time_now() - int(x) < FloodConfig.SECONDS,
                FloodConfig.USERS[uid],
            )
        )
        return True


@moussabot.tgbot.on(CallbackQuery(data=re.compile(b"toggle_bot-antiflood_off$")))
@check_owner
async def settings_toggle(c_q: CallbackQuery):
    if gvarstatus("bot_antif") is None:
        return await c_q.answer(f"تم تعطيل بوت الحماية بالفعل.", alert=False)
    delgvar("bot_antif")
    await c_q.answer(f"تم تعطيل بوت الحماية.", alert=False)
    await c_q.edit("BOT_ANTIFLOOD تم تعطيله الآن !")


@moussabot.bot_cmd(incoming=True, func=lambda e: e.is_private)
@moussabot.bot_cmd(edited=True, func=lambda e: e.is_private)
async def antif_on_msg(event):
    if gvarstatus("bot_antif") is None:
        return
    chat = await event.get_chat()
    if chat.id == Config.OWNER_ID:
        return
    user_id = chat.id
    if check_is_black_list(user_id):
        raise StopPropagation
    elif await is_flood(user_id):
        await send_flood_alert(chat)
        FloodConfig.BANNED_USERS.add(user_id)
        raise StopPropagation
    elif user_id in FloodConfig.BANNED_USERS:
        FloodConfig.BANNED_USERS.remove(user_id)
