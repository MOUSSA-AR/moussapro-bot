from asyncio import sleep

from telethon import functions
from telethon.errors import (
    BadRequestError,
    ImageProcessFailedError,
    PhotoCropSizeSmallError,
)
from telethon.errors.rpcerrorlist import UserAdminInvalidError, UserIdInvalidError
from telethon.tl.functions.channels import (
    EditAdminRequest,
    EditBannedRequest,
    EditPhotoRequest,
)
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import (
    ChatAdminRights,
    ChatBannedRights,
    InputChatPhotoEmpty,
    MessageMediaPhoto,
)

from userbot import catub

from ..core.logger import logging
from ..core.managers import edit_delete, edit_or_reply
from ..helpers import media_type
from ..helpers.utils import _format, get_user_from_event
from ..sql_helper.mute_sql import is_muted, mute, unmute
from . import BOTLOG, BOTLOG_CHATID

# =================== STRINGS ============
PP_TOO_SMOL = "`الصورة صغيرة جدا`"
PP_ERROR = "`فشل أثناء معالجة الصورة`"
NO_ADMIN = "`أنا لست مشرف!`"
NO_PERM = "`ليس لدي أذونات كافية! هذا سيئ جدا.`"
CHAT_PP_CHANGED = "`تغيرت صورة الدردشة`"
INVALID_MEDIA = "`ملحق غير صالح`"

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

LOGS = logging.getLogger(__name__)
MUTE_RIGHTS = ChatBannedRights(until_date=None, send_messages=True)
UNMUTE_RIGHTS = ChatBannedRights(until_date=None, send_messages=False)

plugin_category = "admin"
# ================================================


@catub.cat_cmd(
    pattern="صورة( s| d)$",
    command=("صورة", plugin_category),
    info={
        "header": "For changing group display pic or deleting display pic",
        "description": "Reply to Image for changing display picture",
        "flags": {
            "-s": "To set group pic",
            "-d": "To delete group pic",
        },
        "usage": [
            "{tr}gpic -s <reply to image>",
            "{tr}gpic -d",
        ],
    },
    groups_only=True,
    require_admin=True,
)
async def set_group_photo(event):  # sourcery no-metrics
    "For changing Group dp"
    flag = (event.pattern_match.group(1)).strip()
    if flag == "s":
        replymsg = await event.get_reply_message()
        photo = None
        if replymsg and replymsg.media:
            if isinstance(replymsg.media, MessageMediaPhoto):
                photo = await event.client.download_media(message=replymsg.photo)
            elif "image" in replymsg.media.document.mime_type.split("/"):
                photo = await event.client.download_file(replymsg.media.document)
            else:
                return await edit_delete(event, INVALID_MEDIA)
        if photo:
            try:
                await event.client(
                    EditPhotoRequest(
                        event.chat_id, await event.client.upload_file(photo)
                    )
                )
                await edit_delete(event, CHAT_PP_CHANGED)
            except PhotoCropSizeSmallError:
                return await edit_delete(event, PP_TOO_SMOL)
            except ImageProcessFailedError:
                return await edit_delete(event, PP_ERROR)
            except Exception as e:
                return await edit_delete(event, f"خطأ : `{str(e)}`")
            process = "تم تحديثها بنجاح"
    else:
        try:
            await event.client(EditPhotoRequest(event.chat_id, InputChatPhotoEmpty()))
        except Exception as e:
            return await edit_delete(event, f"خطأ : `{str(e)}`")
        process = "تم حذفها بنجاح"
        await edit_delete(event, "```تم ازالة صورة المجموعة🧸🖤```")
    if BOTLOG:
        await event.client.send_message(
            BOTLOG_CHATID,
            "#صورة_المجموعة\n"
            f"الصورة {process}\n"
            f"المحادثة: {event.chat.title}(`{event.chat_id}`)",
        )


@catub.cat_cmd(
    pattern="رفع ادمن(?: |$)(.*)",
    command=("رفع ادمن", plugin_category),
    info={
        "header": "To give admin rights for a person",
        "description": "Provides admin rights to the person in the chat\
            \nNote : You need proper rights for this",
        "usage": [
            "{tr}promote <userid/username/reply>",
            "{tr}promote <userid/username/reply> <custom title>",
        ],
    },
    groups_only=True,
    require_admin=True,
)
async def promote(event):
    "To promote a person in chat"
    new_rights = ChatAdminRights(
        add_admins=False,
        invite_users=True,
        change_info=False,
        ban_users=True,
        delete_messages=True,
        pin_messages=True,
    )
    user, rank = await get_user_from_event(event)
    if not rank:
        rank = "Admin"
    if not user:
        return
    catevent = await edit_or_reply(event, "`انتظر لحظة...`")
    try:
        await event.client(EditAdminRequest(event.chat_id, user.id, new_rights, rank))
    except BadRequestError:
        return await catevent.edit(NO_PERM)
    await catevent.edit("`تم رفع العضو ادمن بنجاح.`")
    if BOTLOG:
        await event.client.send_message(
            BOTLOG_CHATID,
            f"#رفع_ادمن\
            \nالعضو: [{user.first_name}](tg://user?id={user.id})\
            \nالمحادثة: {event.chat.title} (`{event.chat_id}`)",
        )


@catub.cat_cmd(
    pattern="تنزيل ادمن(?: |$)(.*)",
    command=("تنزيل ادمن", plugin_category),
    info={
        "header": "To remove a person from admin list",
        "description": "Removes all admin rights for that peron in that chat\
            \nNote : You need proper rights for this and also u must be owner or admin who promoted that guy",
        "usage": [
            "{tr}demote <userid/username/reply>",
            "{tr}demote <userid/username/reply> <custom title>",
        ],
    },
    groups_only=True,
    require_admin=True,
)
async def demote(event):
    "To demote a person in group"
    user, _ = await get_user_from_event(event)
    if not user:
        return
    catevent = await edit_or_reply(event, "`انتظر لحظة...`")
    newrights = ChatAdminRights(
        add_admins=None,
        invite_users=None,
        change_info=None,
        ban_users=None,
        delete_messages=None,
        pin_messages=None,
    )
    rank = "admin"
    try:
        await event.client(EditAdminRequest(event.chat_id, user.id, newrights, rank))
    except BadRequestError:
        return await catevent.edit(NO_PERM)
    await catevent.edit("`تم تنزيل العضو من رتبة الأدمن.`")
    if BOTLOG:
        await event.client.send_message(
            BOTLOG_CHATID,
            f"#تنزيل_ادمن\
            \nالعضو: [{user.first_name}](tg://user?id={user.id})\
            \nالمحادثة: {event.chat.title}(`{event.chat_id}`)",
        )


@catub.cat_cmd(
    pattern="تقييد(?: |$)(.*)",
    command=("تقييد", plugin_category),
    info={
        "header": "Will ban the guy in the group where you used this command.",
        "description": "Permanently will remove him from this group and he can't join back\
            \nNote : You need proper rights for this.",
        "usage": [
            "{tr}ban <userid/username/reply>",
            "{tr}ban <userid/username/reply> <reason>",
        ],
    },
    groups_only=True,
    require_admin=True,
)
async def _ban_person(event):
    "To ban a person in group"
    user, reason = await get_user_from_event(event)
    if not user:
        return
    if user.id == event.client.uid:
        return await edit_delete(event, "__لا يمكنك تقييد هذا العضو.!__")
    catevent = await edit_or_reply(event, "`تم تقييد العضو بنجاح!`")
    try:
        await event.client(EditBannedRequest(event.chat_id, user.id, BANNED_RIGHTS))
    except BadRequestError:
        return await catevent.edit(NO_PERM)
    try:
        reply = await event.get_reply_message()
        if reply:
            await reply.delete()
    except BadRequestError:
        return await catevent.edit("`لا تمتلك اذونات كافية لهذا.!`")
    if reason:
        await catevent.edit(
            f"{_format.mentionuser(user.first_name ,user.id)}` تم تقييده !!`\n**السبب : **`{reason}`"
        )
    else:
        await catevent.edit(
            f"{_format.mentionuser(user.first_name ,user.id)} `تم تقييده !!`"
        )
    if BOTLOG:
        if reason:
            await event.client.send_message(
                BOTLOG_CHATID,
                f"#تقييد\
                \nالعضو: [{user.first_name}](tg://user?id={user.id})\
                \nالمحادثة: {event.chat.title}(`{event.chat_id}`)\
                \nالسبب : {reason}",
            )
        else:
            await event.client.send_message(
                BOTLOG_CHATID,
                f"#تقييد\
                \nالعضو: [{user.first_name}](tg://user?id={user.id})\
                \nالمحادثة: {event.chat.title}(`{event.chat_id}`)",
            )


@catub.cat_cmd(
    pattern="الغاء تقييد(?: |$)(.*)",
    command=("الغاء تقييد", plugin_category),
    info={
        "header": "Will unban the guy in the group where you used this command.",
        "description": "Removes the user account from the banned list of the group\
            \nNote : You need proper rights for this.",
        "usage": [
            "{tr}unban <userid/username/reply>",
            "{tr}unban <userid/username/reply> <reason>",
        ],
    },
    groups_only=True,
    require_admin=True,
)
async def nothanos(event):
    "To unban a person"
    user, _ = await get_user_from_event(event)
    if not user:
        return
    catevent = await edit_or_reply(event, "`انتظر لحظة...`")
    try:
        await event.client(EditBannedRequest(event.chat_id, user.id, UNBAN_RIGHTS))
        await catevent.edit(
            f"{_format.mentionuser(user.first_name ,user.id)} `تم الغاء تقييد العضو بنجاح.`"
        )
        if BOTLOG:
            await event.client.send_message(
                BOTLOG_CHATID,
                "#الغاء_تقييد\n"
                f"العضو: [{user.first_name}](tg://user?id={user.id})\n"
                f"المحادثة: {event.chat.title}(`{event.chat_id}`)",
            )
    except UserIdInvalidError:
        await catevent.edit("`تقييد العضو!`")
    except Exception as e:
        await catevent.edit(f"**خطأ :**\n`{e}`")


@catub.cat_cmd(incoming=True)
async def watcher(event):
    if is_muted(event.sender_id, event.chat_id):
        try:
            await event.delete()
        except Exception as e:
            LOGS.info(str(e))


@catub.cat_cmd(
    pattern="كتم(?: |$)(.*)",
    command=("كتم", plugin_category),
    info={
        "header": "To stop sending messages from that user",
        "description": "If is is not admin then changes his permission in group,\
            if he is admin or if you try in personal chat then his messages will be deleted\
            \nNote : You need proper rights for this.",
        "usage": [
            "{tr}mute <userid/username/reply>",
            "{tr}mute <userid/username/reply> <reason>",
        ],
    },  # sourcery no-metrics
)
async def startmute(event):
    "To mute a person in that paticular chat"
    if event.is_private:
        await event.edit("`قد تحدث مشكلات غير متوقعة أو أخطاء سيئة!`")
        await sleep(2)
        await event.get_reply_message()
        replied_user = await event.client(GetFullUserRequest(event.chat_id))
        if is_muted(event.chat_id, event.chat_id):
            return await event.edit(
                "`تم كتم هذا العضو بالفعل في هذه المحادثة..!~~lmfao sed rip~~`"
            )
        if event.chat_id == catub.uid:
            return await edit_delete(event, "`لا يمكنك كتم هذا العضو.!`")
        try:
            mute(event.chat_id, event.chat_id)
        except Exception as e:
            await event.edit(f"**خطأ **\n`{str(e)}`")
        else:
            await event.edit(
                "`تم كتم العضو بنجاح\n**ï½-Â´)âââï¾.*ï½¥ï½¡ï¾ **`"
            )
        if BOTLOG:
            await event.client.send_message(
                BOTLOG_CHATID,
                "#كتم\n"
                f"**العضو :** [{replied_user.user.first_name}](tg://user?id={event.chat_id})\n",
            )
    else:
        chat = await event.get_chat()
        admin = chat.admin_rights
        creator = chat.creator
        if not admin and not creator:
            return await edit_or_reply(
                event, "`يجب أن تكون أدمن في المحادثة` à²¥ï¹à²¥  "
            )
        user, reason = await get_user_from_event(event)
        if not user:
            return
        if user.id == catub.uid:
            return await edit_or_reply(event, "`آسف, لا يمكنني كتم هذا العضو`")
        if is_muted(user.id, event.chat_id):
            return await edit_or_reply(
                event, "`تم كتم هذا المستخدم بالفعل في هذه الدردشة ~~lmfao sed rip~~`"
            )
        result = await event.client(
            functions.channels.GetParticipantRequest(event.chat_id, user.id)
        )
        try:
            if result.participant.banned_rights.send_messages:
                return await edit_or_reply(
                    event,
                    "`تم كتم هذا المستخدم بالفعل في هذه الدردشة ~~lmfao sed rip~~`",
                )
        except AttributeError:
            pass
        except Exception as e:
            return await edit_or_reply(event, f"**خطأ : **`{str(e)}`", 10)
        try:
            await event.client(EditBannedRequest(event.chat_id, user.id, MUTE_RIGHTS))
        except UserAdminInvalidError:
            if "admin_rights" in vars(chat) and vars(chat)["admin_rights"] is not None:
                if chat.admin_rights.delete_messages is not True:
                    return await edit_or_reply(
                        event,
                        "`لا يمكنك كتم هذا العضو لأنك لست ادمن.! à²¥ï¹à²¥`",
                    )
            elif "creator" not in vars(chat):
                return await edit_or_reply(
                    event, "`لا يمكنك كتم هذا العضو لأنك لست ادمن.!` à²¥ï¹à²¥  "
                )
            mute(user.id, event.chat_id)
        except Exception as e:
            return await edit_or_reply(event, f"**خطأ : **`{str(e)}`", 10)
        if reason:
            await edit_or_reply(
                event,
                f"{_format.mentionuser(user.first_name ,user.id)} `تم كتمه في {event.chat.title}`\n"
                f"`Reason:`{reason}",
            )
        else:
            await edit_or_reply(
                event,
                f"{_format.mentionuser(user.first_name ,user.id)} `تم كتمه في {event.chat.title}`\n",
            )
        if BOTLOG:
            await event.client.send_message(
                BOTLOG_CHATID,
                "#كتم\n"
                f"**العضو :** [{user.first_name}](tg://user?id={user.id})\n"
                f"**المحادثة :** {event.chat.title}(`{event.chat_id}`)",
            )


@catub.cat_cmd(
    pattern="الغاء كتم(?: |$)(.*)",
    command=("الغاء كتم", plugin_category),
    info={
        "header": "To allow user to send messages again",
        "description": "Will change user permissions ingroup to send messages again.\
        \nNote : You need proper rights for this.",
        "usage": [
            "{tr}unmute <userid/username/reply>",
            "{tr}unmute <userid/username/reply> <reason>",
        ],
    },
)
async def endmute(event):
    "To mute a person in that paticular chat"
    if event.is_private:
        await event.edit("`قد تحدث مشكلات غير متوقعة أو أخطاء سيئة!`")
        await sleep(1)
        replied_user = await event.client(GetFullUserRequest(event.chat_id))
        if not is_muted(event.chat_id, event.chat_id):
            return await event.edit(
                "`__هذا العضو ليس مكتوما في المحادثة__\nï¼ ^_^ï¼oèªèªoï¼^_^ ï¼`"
            )
        try:
            unmute(event.chat_id, event.chat_id)
        except Exception as e:
            await event.edit(f"**خطأ **\n`{str(e)}`")
        else:
            await event.edit(
                "`تم رفع الكتم عن العضو بنجاح.\nä¹( â à±ªâ)ã    â(ï¿£Ð ï¿£)â`"
            )
        if BOTLOG:
            await event.client.send_message(
                BOTLOG_CHATID,
                "#الغاء_الكتم\n"
                f"**العضو :** [{replied_user.user.first_name}](tg://user?id={event.chat_id})\n",
            )
    else:
        user, _ = await get_user_from_event(event)
        if not user:
            return
        try:
            if is_muted(user.id, event.chat_id):
                unmute(user.id, event.chat_id)
            else:
                result = await event.client(
                    functions.channels.GetParticipantRequest(
                        channel=event.chat_id, user_id=user.id
                    )
                )
                if result.participant.banned_rights.send_messages:
                    await event.client(
                        EditBannedRequest(event.chat_id, user.id, UNBAN_RIGHTS)
                    )
        except AttributeError:
            return await edit_or_reply(
                event,
                "`هذا العضو اصبح بإمكانه إرسال الرسائل في المجوعة! ~~lmfao sed rip~~`",
            )
        except Exception as e:
            return await edit_or_reply(event, f"**خطأ : **`{str(e)}`")
        await edit_or_reply(
            event,
            f"{_format.mentionuser(user.first_name ,user.id)} `تم الغاء كتمه في {event.chat.title}\nä¹( â à±ªâ)ã    â(ï¿£Ð ï¿£)â`",
        )
        if BOTLOG:
            await event.client.send_message(
                BOTLOG_CHATID,
                "#الغاء_الكتم\n"
                f"**العضو :** [{user.first_name}](tg://user?id={user.id})\n"
                f"**المحادثة :** {event.chat.title}(`{event.chat_id}`)",
            )


@catub.cat_cmd(
    pattern="طرد(?: |$)(.*)",
    command=("طرد", plugin_category),
    info={
        "header": "To kick a person from the group",
        "description": "Will kick the user from the group so he can join back.\
        \nNote : You need proper rights for this.",
        "usage": [
            "{tr}kick <userid/username/reply>",
            "{tr}kick <userid/username/reply> <reason>",
        ],
    },
    groups_only=True,
    require_admin=True,
)
async def endmute(event):
    "use this to kick a user from chat"
    user, reason = await get_user_from_event(event)
    if not user:
        return
    catevent = await edit_or_reply(event, "`انتظر لحظة...`")
    try:
        await event.client.kick_participant(event.chat_id, user.id)
    except Exception as e:
        return await cateventedit(NO_PERM + f"\n{str(e)}")
    if reason:
        await catevent.edit(
            f"`طرد` [{user.first_name}](tg://user?id={user.id})`!`\nالسبب: {reason}"
        )
    else:
        await catevent.edit(f"`طرد` [{user.first_name}](tg://user?id={user.id})`!`")
    if BOTLOG:
        await event.client.send_message(
            BOTLOG_CHATID,
            "#طرد\n"
            f"العضو: [{user.first_name}](tg://user?id={user.id})\n"
            f"المحادثة: {event.chat.title}(`{event.chat_id}`)\n",
        )


@catub.cat_cmd(
    pattern="تثبيت( مكتوم|$)",
    command=("تثبيت", plugin_category),
    info={
        "header": "For pining messages in chat",
        "description": "reply to a message to pin it in that in chat\
        \nNote : You need proper rights for this if you want to use in group.",
        "options": {"loud": "To notify everyone without this.it will pin silently"},
        "usage": [
            "{tr}pin <reply>",
            "{tr}pin loud <reply>",
        ],
    },
)
async def pin(event):
    "To pin a message in chat"
    to_pin = event.reply_to_msg_id
    if not to_pin:
        return await edit_delete(event, "`يجب الرد على الرسالة لتثبيتها.!`", 5)
    options = event.pattern_match.group(1)
    is_silent = bool(options)
    try:
        await event.client.pin_message(event.chat_id, to_pin, notify=is_silent)
    except BadRequestError:
        return await edit_delete(event, NO_PERM, 5)
    except Exception as e:
        return await edit_delete(event, f"`{str(e)}`", 5)
    await edit_delete(event, "`تم تثبيت الرسالة بنجاح!`", 3)
    if BOTLOG and not event.is_private:
        await event.client.send_message(
            BOTLOG_CHATID,
            f"#تثبيت\
                \n__تم تثبيت الرسالة بنجاح__\
                \nالمحادثة: {event.chat.title}(`{event.chat_id}`)\
                \nبصوت عالي: {is_silent}",
        )


@catub.cat_cmd(
    pattern="الغاء تثبيت( الكل|$)",
    command=("الغاء تثبيت", plugin_category),
    info={
        "header": "For unpining messages in chat",
        "description": "reply to a message to unpin it in that in chat\
        \nNote : You need proper rights for this if you want to use in group.",
        "options": {"all": "To unpin all messages in the chat"},
        "usage": [
            "{tr}unpin <reply>",
            "{tr}unpin all",
        ],
    },
)
async def pin(event):
    "To unpin message(s) in the group"
    to_unpin = event.reply_to_msg_id
    options = (event.pattern_match.group(1)).strip()
    if not to_unpin and options != "الكل":
        return await edit_delete(
            event,
            "__قم بالرد على الرسالة لتتمكن من الغاء تثبيتها__",
            5,
        )
    try:
        if to_unpin and not options:
            await event.client.unpin_message(event.chat_id, to_unpin)
        elif options == "الكل":
            await event.client.unpin_message(event.chat_id)
        else:
            return await edit_delete(
                event,
                "`استخدم الأمر (.الغاء تثبيت الكل) لتتمكن من الغاء تثبيت جميع الرسائل.`",
                5,
            )
    except BadRequestError:
        return await edit_delete(event, NO_PERM, 5)
    except Exception as e:
        return await edit_delete(event, f"`{str(e)}`", 5)
    await edit_delete(event, "`تم الغاء تثبيت الرسالة بنجاح!`", 3)
    if BOTLOG and not event.is_private:
        await event.client.send_message(
            BOTLOG_CHATID,
            "#الغاء_تثبيت\
                \n__تم الغاء تثبيت جميع الرسائل بنجاح!__\
                \nالمحادثة: {event.chat.title}(`{event.chat_id}`)",
        )


@catub.cat_cmd(
    pattern="المحذوفات( u)?(?: |$)(\d*)?",
    command=("المحذوفات", plugin_category),
    info={
        "header": "To get recent deleted messages in group",
        "description": "To check recent deleted messages in group, by default will show 5. you can get 1 to 15 messages.",
        "flags": {
            "u": "use this flag to upload media to chat else will just show as media."
        },
        "usage": [
            "{tr}undlt <count>",
            "{tr}undlt -u <count>",
        ],
        "examples": [
            "{tr}undlt 7",
            "{tr}undlt -u 7 (this will reply all 7 messages to this message",
        ],
    },
    groups_only=True,
    require_admin=True,
)
async def _iundlt(event):  # sourcery no-metrics
    "To check recent deleted messages in group"
    catevent = await edit_or_reply(
        event, "`جاري البحث في الرسائل الأخيرة. انتظر قليلا....`"
    )
    flag = event.pattern_match.group(1)
    if event.pattern_match.group(2) != "":
        lim = int(event.pattern_match.group(2))
        if lim > 15:
            lim = int(15)
        if lim <= 0:
            lim = int(1)
    else:
        lim = int(5)
    adminlog = await event.client.get_admin_log(
        event.chat_id, limit=lim, edit=False, delete=True
    )
    deleted_msg = f"**عدد الرسائل المحذوفة في هذة المحادثة هي {lim} رسائل :**"
    if not flag:
        for msg in adminlog:
            ruser = (
                await event.client(GetFullUserRequest(msg.old.from_id.user_id))
            ).user
            _media_type = media_type(msg.old)
            if _media_type is None:
                deleted_msg += f"\n__{msg.old.message}__ **أرسلت بواسطة** {_format.mentionuser(ruser.first_name ,ruser.id)}\n"
            else:
                deleted_msg += f"\n__{_media_type}__ **ارسلت بواسطة** {_format.mentionuser(ruser.first_name ,ruser.id)}\n"
        await edit_or_reply(catevent, deleted_msg)
    else:
        main_msg = await edit_or_reply(catevent, deleted_msg)
        for msg in adminlog:
            ruser = (
                await event.client(GetFullUserRequest(msg.old.from_id.user_id))
            ).user
            _media_type = media_type(msg.old)
            if _media_type is None:
                await main_msg.reply(
                    f"{msg.old.message}\n**ارسلت بواسطة** {_format.mentionuser(ruser.first_name ,ruser.id)}\n"
                )
            else:
                await main_msg.reply(
                    f"{msg.old.message}\n**ارسلت بواسطة** {_format.mentionuser(ruser.first_name ,ruser.id)}\n",
                    file=msg.old.media,
                )
