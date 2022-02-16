"""
idea from lynda and rose bot
made by @u_5_1
"""
from telethon.errors import BadRequestError
from telethon.errors.rpcerrorlist import UserAdminInvalidError, UserIdInvalidError
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights

from userbot import catub

from ..core.managers import edit_or_reply
from ..helpers.utils import _format
from . import BOTLOG, BOTLOG_CHATID, extract_time, get_user_from_event

plugin_category = "admin"

# =================== CONSTANT ===================
NO_ADMIN = "`انا لست مشرف!`"
NO_PERM = "`ليس لدي اذونات كافية!`"


@catub.cat_cmd(
    pattern="كتم مؤقت(?:\s|$)([\s\S]*)",
    command=("كتم مؤقت", plugin_category),
    info={
        "header": "To stop sending messages permission for that user",
        "description": "Temporary mutes the user for given time.",
        "Time units": {
            "s": "seconds",
            "m": "minutes",
            "h": "Hours",
            "d": "days",
            "w": "weeks",
        },
        "usage": [
            "{tr}tmute <userid/username/reply> <time>",
            "{tr}tmute <userid/username/reply> <time> <reason>",
        ],
        "examples": ["{tr}tmute 2d to test muting for 2 days"],
    },
    groups_only=True,
    require_admin=True,
)
async def tmuter(event):  # sourcery no-metrics
    "To mute a person for specific time"
    catevent = await edit_or_reply(event, "`جاري الكتم....`")
    user, reason = await get_user_from_event(event, catevent)
    if not user:
        return
    if not reason:
        return await catevent.edit(" لم تذكر الوقت ، تحقق من `.مساعدة كتم مؤقت`")
    reason = reason.split(" ", 1)
    hmm = len(reason)
    cattime = reason[0].strip()
    reason = "".join(reason[1:]) if hmm > 1 else None
    ctime = await extract_time(catevent, cattime)
    if not ctime:
        return
    if user.id == event.client.uid:
        return await catevent.edit(f"آسف ، لا يمكنني كتم صوتي")
    try:
        await catevent.client(
            EditBannedRequest(
                event.chat_id,
                user.id,
                ChatBannedRights(until_date=ctime, send_messages=True),
            )
        )
        # Announce that the function is done
        if reason:
            await catevent.edit(
                f"{_format.mentionuser(user.first_name ,user.id)} تم كتم الصوت في {event.chat.title}\n"
                f"**كتم الصوت لـ : **{cattime}\n"
                f"**السبب : **__{reason}__"
            )
            if BOTLOG:
                await event.client.send_message(
                    BOTLOG_CHATID,
                    "#كتم مؤقت\n"
                    f"**المستخدم : **[{user.first_name}](tg://user?id={user.id})\n"
                    f"**المحادثة : **{event.chat.title}(`{event.chat_id}`)\n"
                    f"**كتم الصوت لـ : **`{cattime}`\n"
                    f"**السبب : **`{reason}``",
                )
        else:
            await catevent.edit(
                f"{_format.mentionuser(user.first_name ,user.id)} تم كتم الصوت في {event.chat.title}\n"
                f"كتم الصوت لـ {cattime}\n"
            )
            if BOTLOG:
                await event.client.send_message(
                    BOTLOG_CHATID,
                    "#كتم2\n"
                    f"**المستخدم : **[{user.first_name}](tg://user?id={user.id})\n"
                    f"**المحادثة : **{event.chat.title}(`{event.chat_id}`)\n"
                    f"**كتم الصوت لـ : **`{cattime}`",
                )
        # Announce to logging group
    except UserIdInvalidError:
        return await catevent.edit("`كتم صوتي قد كسر!`")
    except UserAdminInvalidError:
        return await catevent.edit(
            "`إما أنك لست مسؤولاً أو أنك حاولت تجاهل مسؤول لم تقم بترقيته`"
        )
    except Exception as e:
        return await catevent.edit(f"`{str(e)}`")


@catub.cat_cmd(
    pattern="حظر مؤقت(?:\s|$)([\s\S]*)",
    command=("حظر مؤقت", plugin_category),
    info={
        "header": "To remove a user from the group for specified time.",
        "description": "Temporary bans the user for given time.",
        "Time units": {
            "s": "seconds",
            "m": "minutes",
            "h": "Hours",
            "d": "days",
            "w": "weeks",
        },
        "usage": [
            "{tr}tban <userid/username/reply> <time>",
            "{tr}tban <userid/username/reply> <time> <reason>",
        ],
        "examples": ["{tr}tban 2d to test baning for 2 days"],
    },
    groups_only=True,
    require_admin=True,
)
async def tban(event):  # sourcery no-metrics
    "To ban a person for specific time"
    catevent = await edit_or_reply(event, "`جاري الحظر....`")
    user, reason = await get_user_from_event(event, catevent)
    if not user:
        return
    if not reason:
        return await catevent.edit("لم تذكر الوقت ، تحقق من `.مساعدة حظر مؤقت`")
    reason = reason.split(" ", 1)
    hmm = len(reason)
    cattime = reason[0].strip()
    reason = "".join(reason[1:]) if hmm > 1 else None
    ctime = await extract_time(catevent, cattime)
    if not ctime:
        return
    if user.id == event.client.uid:
        return await catevent.edit(f"آسف ، لا يمكنني حظر نفسي")
    await catevent.edit("`ضرب الآفة!`")
    try:
        await event.client(
            EditBannedRequest(
                event.chat_id,
                user.id,
                ChatBannedRights(until_date=ctime, view_messages=True),
            )
        )
    except UserAdminInvalidError:
        return await catevent.edit(
            "`إما أنك لست مسؤولاً أو أنك حاولت حظر مسؤول لم تقم بترقيته`"
        )
    except BadRequestError:
        return await catevent.edit(NO_PERM)
    # Helps ban group join spammers more easily
    try:
        reply = await event.get_reply_message()
        if reply:
            await reply.delete()
    except BadRequestError:
        return await catevent.edit("`ليس لدي الحقوق اللازمة!  لكنه ما زال ممنوعا!`")
    # Delete message and then tell that the command
    # is done gracefully
    # Shout out the ID, so that fedadmins can fban later
    if reason:
        await catevent.edit(
            f"{_format.mentionuser(user.first_name ,user.id)} تم حظره في {event.chat.title}\n"
            f"تم حظر {cattime}\n"
            f"السبب:`{reason}`"
        )
        if BOTLOG:
            await event.client.send_message(
                BOTLOG_CHATID,
                "#حظر مؤقت\n"
                f"**المستخدم : **[{user.first_name}](tg://user?id={user.id})\n"
                f"**المحادثة : **{event.chat.title}(`{event.chat_id}`)\n"
                f"**محظور حتى : **`{cattime}`\n"
                f"**السبب : **__{reason}__",
            )
    else:
        await catevent.edit(
            f"{_format.mentionuser(user.first_name ,user.id)} تم حظره في {event.chat.title}\n"
            f"تم حظر {cattime}\n"
        )
        if BOTLOG:
            await event.client.send_message(
                BOTLOG_CHATID,
                "#حظر مؤقت\n"
                f"**المستخدم : **[{user.first_name}](tg://user?id={user.id})\n"
                f"**المحادثة : **{event.chat.title}(`{event.chat_id}`)\n"
                f"**محظور حتى : **`{cattime}`",
            )
