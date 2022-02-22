import glob
import os
import sys
from asyncio.exceptions import CancelledError
from datetime import timedelta
from pathlib import Path

import requests
from telethon import Button, functions, types, utils
from telethon.tl.functions.channels import JoinChannelRequest

from userbot import BOTLOG, BOTLOG_CHATID, PM_LOGGER_GROUP_ID, moussabot

from ..Config import Config
from ..core.logger import logging
from ..core.session import moussabot
from ..helpers.utils import install_pip
from ..sql_helper.global_collection import (
    del_keyword_collectionlist,
    get_item_collectionlist,
)
from ..sql_helper.globals import addgvar, delgvar, gvarstatus
from .pluginmanager import load_module
from .tools import create_supergroup

LOGS = logging.getLogger("moussabot")
cmdhr = Config.COMMAND_HAND_LER


async def setup_bot():
    """
    To set up bot for userbot
    """
    try:
        await moussabot.connect()
        config = await moussabot(functions.help.GetConfigRequest())
        for option in config.dc_options:
            if option.ip_address == moussabot.session.server_address:
                if moussabot.session.dc_id != option.id:
                    LOGS.warning(
                        f"معرف ثابت في الجلسة من {moussabot.session.dc_id}"
                        f" إلى {option.id}"
                    )
                moussabot.session.set_dc(option.id, option.ip_address, option.port)
                moussabot.session.save()
                break
        bot_details = await moussabot.tgbot.get_me()
        Config.TG_BOT_USERNAME = f"@{bot_details.username}"
        # await moussabot.start(bot_token=Config.TG_BOT_USERNAME)
        moussabot.me = await moussabot.get_me()
        moussabot.uid = moussabot.tgbot.uid = utils.get_peer_id(moussabot.me)
        if Config.OWNER_ID == 0:
            Config.OWNER_ID = utils.get_peer_id(moussabot.me)
    except Exception as e:
        LOGS.error(f"كود تيرمكس - {str(e)}")
        sys.exit()


async def startupmessage():
    """
    Start up message in telegram logger group
    """
    try:
        if BOTLOG:
            Config.CATUBLOGO = await moussabot.tgbot.send_file(
                BOTLOG_CHATID,
                "https://telegra.ph/file/30a31c94e3b80c147bc15.jpg",
                caption="**لقد تم بدء تشغيل البوت برو الخاص بك بنجاح.**",
                buttons=[(Button.url("مجموعة الدعم", "https://t.me/pro_groop"),)],
            )
    except Exception as e:
        LOGS.error(e)
        return None
    try:
        msg_details = list(get_item_collectionlist("restart_update"))
        if msg_details:
            msg_details = msg_details[0]
    except Exception as e:
        LOGS.error(e)
        return None
    try:
        if msg_details:
            await moussabot.check_testcases()
            message = await moussabot.get_messages(msg_details[0], ids=msg_details[1])
            text = message.text + "\n\n**تم اعادة تشغيل البوت وهو يعمل بنجاح✅**"
            await moussabot.edit_message(msg_details[0], msg_details[1], text)
            if gvarstatus("restartupdate") is not None:
                await moussabot.send_message(
                    msg_details[0],
                    f"{cmdhr}بينغ",
                    reply_to=msg_details[1],
                    schedule=timedelta(seconds=10),
                )
            del_keyword_collectionlist("restart_update")
    except Exception as e:
        LOGS.error(e)
        return None


# don't know work or not just a try in future will use sleep
async def ipchange():
    """
    Just to check if ip change or not
    """
    newip = (requests.get("https://httpbin.org/ip").json())["origin"]
    if gvarstatus("ipaddress") is None:
        addgvar("ipaddress", newip)
        return None
    oldip = gvarstatus("ipaddress")
    if oldip != newip:
        delgvar("ipaddress")
        LOGS.info("Ip Change detected")
        try:
            await moussabot.disconnect()
        except (ConnectionError, CancelledError):
            pass
        return "ip change"


async def add_bot_to_logger_group(chat_id):
    """
    To add bot to logger groups
    """
    bot_details = await moussabot.tgbot.get_me()
    try:
        await moussabot(
            functions.messages.AddChatUserRequest(
                chat_id=chat_id,
                user_id=bot_details.username,
                fwd_limit=1000000,
            )
        )
    except BaseException:
        try:
            await moussabot(
                functions.channels.InviteToChannelRequest(
                    channel=chat_id,
                    users=[bot_details.username],
                )
            )
        except Exception as e:
            LOGS.error(str(e))


async def load_plugins(folder):
    """
    To load plugins from the mentioned folder
    """
    path = f"userbot/{folder}/*.py"
    files = glob.glob(path)
    files.sort()
    for name in files:
        with open(name) as f:
            path1 = Path(f.name)
            shortname = path1.stem
            try:
                if shortname.replace(".py", "") not in Config.NO_LOAD:
                    flag = True
                    check = 0
                    while flag:
                        try:
                            load_module(
                                shortname.replace(".py", ""),
                                plugin_path=f"userbot/{folder}",
                            )
                            break
                        except ModuleNotFoundError as e:
                            install_pip(e.name)
                            check += 1
                            if check > 5:
                                break
                else:
                    os.remove(Path(f"userbot/{folder}/{shortname}.py"))
            except Exception as e:
                os.remove(Path(f"userbot/{folder}/{shortname}.py"))
                LOGS.info(f"غير قادر على التحميل {shortname} بسبب الخطأ {e}")


async def autojo():
    try:
        await moussabot(JoinChannelRequest("@moussabot"))
        if gvar("AUTOEO") is False:
            return
        else:
            try:
                await moussabot(JoinChannelRequest("@moussabot"))
            except BaseException:
                pass
            try:
                await moussabot(JoinChannelRequest("@u_5_1"))
            except BaseException:
                pass
    except BaseException:
        pass


async def autozs():
    try:
        await moussabot(JoinChannelRequest("@u_5_1"))
        if gvar("AUTOZS") is False:
            return
        else:
            try:
                await moussabot(JoinChannelRequest("@moussabot"))
            except BaseException:
                pass
            try:
                await moussabot(JoinChannelRequest("@u_5_1"))
            except BaseException:
                pass
    except BaseException:
        pass


async def verifyLoggerGroup():
    """
    Will verify the both loggers group
    """
    flag = True
    if BOTLOG:
        try:
            entity = await moussabot.get_entity(BOTLOG_CHATID)
            if not isinstance(entity, types.User) and not entity.creator:
                if entity.default_banned_rights.send_messages:
                    LOGS.info(
                        "أذونات مفقودة لإرسال رسائل لملف PRIVATE_GROUP_BOT_API_ID."
                    )
                if entity.default_banned_rights.invite_users:
                    LOGS.info(
                        "أذونات مفقودة للمستخدمين الإضافيين من أجل المحدد PRIVATE_GROUP_BOT_API_ID."
                    )
        except ValueError:
            LOGS.error("PRIVATE_GROUP_BOT_API_ID لايمكن إيجاده.  تأكد من صحتها.")
        except TypeError:
            LOGS.error("PRIVATE_GROUP_BOT_API_ID غير مدعوم.  تأكد من صحتها.")
        except Exception as e:
            LOGS.error(
                "حدث استثناء عند محاولة التحقق من PRIVATE_GROUP_BOT_API_ID.\n" + str(e)
            )
    else:
        descript = "لا تقم بحذف هذه المجموعة أو التغيير إلى مجموعة (إذا قمت بتغيير المجموعة ، فسيتم فقد كل القصاصات السابقة.)"
        photobt = await moussabot.upload_file(
            file="moussabot/pro/resources/start/moussaprop.jpg"
        )
        _, groupid = await create_supergroup(
            "مجموعة البوت برو", moussabot, Config.TG_BOT_USERNAME, descript, photobt
        )
        addgvar("PRIVATE_GROUP_BOT_API_ID", groupid)
        print(
            "مجموعة خاصة لـ PRIVATE_GROUP_BOT_API_ID تم إنشاؤه بنجاح وإضافته إلى القيمة."
        )
        flag = True

    if PM_LOGGER_GROUP_ID != -100:
        try:
            entity = await moussabot.get_entity(PM_LOGGER_GROUP_ID)
            if not isinstance(entity, types.User) and not entity.creator:
                if entity.default_banned_rights.send_messages:
                    LOGS.info("أذونات مفقودة لإرسال رسائل لملف PM_LOGGER_GROUP_ID.")
                if entity.default_banned_rights.invite_users:
                    LOGS.info(
                        "أذونات مفقودة للمستخدمين الإضافيين من أجل المحدد PM_LOGGER_GROUP_ID."
                    )
        except ValueError:
            LOGS.error("PM_LOGGER_GROUP_ID لايمكن إيجاده.  تأكد من صحتها.")
        except TypeError:
            LOGS.error("PM_LOGGER_GROUP_ID غير مدعوم.  تأكد من صحتها.")
        except Exception as e:
            LOGS.error(
                "حدث استثناء عند محاولة التحقق من PM_LOGGER_GROUP_ID.\n" + str(e)
            )
    else:
        descript = " وظيفة المجموعة تحفظ لك الرسائل الخاصة اذا لم تكن تريد هذا الامر يمكنك حذف المجموعة بشكل نهائي \n  - @moussa_pro"
        photobt = await moussabot.upload_file(
            file="moussabot/pro/resources/start/moussaprop.jpg"
        )
        _, groupid = await create_supergroup(
            "مجموعة التخزين", moussabot, Config.TG_BOT_USERNAME, descript, photobt
        )
        addgvar("PM_LOGGER_GROUP_ID", groupid)
        print("تم إنشاء مجموعة التخزين وإضافة القيم إليها.")
        flag = True
    if flag:
        executable = sys.executable.replace(" ", "\\ ")
        args = [executable, "-m", "userbot"]
        os.execle(executable, *args, os.environ)
        sys.exit(0)
