from telethon import functions

from userbot import catub

from ..Config import Config
from ..core import CMD_INFO, GRP_INFO, PLG_INFO
from ..core.managers import edit_delete, edit_or_reply
from ..helpers.utils import reply_id

cmdprefix = Config.COMMAND_HAND_LER

plugin_category = "tools"

hemojis = {
    "admin": "👮‍♂️",
    "bot": "🤖",
    "fun": "🎨",
    "misc": "🧩",
    "tools": "🧰",
    "utils": "🗂",
    "extra": "➕",
}


def get_key(val):
    for key, value in PLG_INFO.items():
        for cmd in value:
            if val == cmd:
                return key
    return None


def getkey(val):
    for key, value in GRP_INFO.items():
        for plugin in value:
            if val == plugin:
                return key
    return None


async def cmdinfo(input_str, event, plugin=False):
    if input_str[0] == cmdprefix:
        input_str = input_str[1:]
    try:
        about = CMD_INFO[input_str]
    except KeyError:
        if plugin:
            await edit_delete(
                event,
                f"**لا يوجد أمر مثل **`{input_str}`** في البوت الخاص بك**",
            )
            return None
        await edit_delete(
            event, f"**لا يوجد أمر مثل **`{input_str}`** في البوت الخاص بك**"
        )
        return None
    except Exception as e:
        await edit_delete(event, f"**خطأ**\n`{str(e)}`")
        return None
    outstr = f"**الأمر :** `{cmdprefix}{input_str}`\n"
    plugin = get_key(input_str)
    if plugin is not None:
        outstr += f"**الإضافة :** `{plugin}`\n"
        category = getkey(plugin)
        if category is not None:
            outstr += f"**الفئة :** `{category}`\n\n"
    outstr += f"**✘  المقدمة :**\n{about[0]}"
    return outstr


async def plugininfo(input_str, event, flag):
    try:
        cmds = PLG_INFO[input_str]
    except KeyError:
        outstr = await cmdinfo(input_str, event, plugin=True)
        return outstr
    except Exception as e:
        await edit_delete(event, f"**اخطأ**\n`{str(e)}`")
        return None
    if len(cmds) == 1 and (flag is None or (flag and flag != "-p")):
        outstr = await cmdinfo(cmds[0], event, plugin=False)
        return outstr
    outstr = f"**الإضافة : **`{input_str}`\n"
    outstr += f"**الأوامر المتوفرة :** `{len(cmds)}`\n"
    category = getkey(input_str)
    if category is not None:
        outstr += f"**الفئة :** `{category}`\n\n"
    for cmd in cmds:
        outstr += f"•  **الأمر :** `{cmdprefix}{cmd}`\n"
        try:
            outstr += f"•  **معلومات :** `{CMD_INFO[cmd][1]}`\n\n"
        except IndexError:
            outstr += f"•  **معلومات :** `لا شيئ`\n\n"
    outstr += f"**👩‍💻 الإستخدام : ** `{cmdprefix}مساعدة <اسم الأمر>`\
        \n**ملاحظة : **إذا كان اسم الأمر هو نفسه اسم البرنامج المساعد ، فاستخدم هذا الاسم `{cmdprefix}مساعدة -c <اسم الأمر>`."
    return outstr


async def grpinfo():
    outstr = "**الإضافات في البوت برو هي:**\n\n"
    outstr += f"**👩‍💻 الإستخدام : ** `{cmdprefix}مساعدة < اسم الأمر>`\n\n"
    category = ["admin", "bot", "fun", "misc", "tools", "utils", "extra"]
    for cat in category:
        plugins = GRP_INFO[cat]
        outstr += f"**{hemojis[cat]} {cat.title()} **({len(plugins)})\n"
        for plugin in plugins:
            outstr += f"`{plugin}`  "
        outstr += "\n\n"
    return outstr


async def cmdlist():
    outstr = "**الأوامر في البوت برو هي :**\n\n"
    category = ["admin", "bot", "fun", "misc", "tools", "utils", "extra"]
    for cat in category:
        plugins = GRP_INFO[cat]
        outstr += f"**{hemojis[cat]} {cat.title()} ** - {len(plugins)}\n\n"
        for plugin in plugins:
            cmds = PLG_INFO[plugin]
            outstr += f"• **{plugin.title()} has {len(cmds)} الأوامر**\n"
            for cmd in cmds:
                outstr += f"  - `{cmdprefix}{cmd}`\n"
            outstr += "\n"
    outstr += f"**👩‍💻 الإستخدام : ** `{cmdprefix}مساعدة -c < اسم الأمر>`"
    return outstr


@catub.cat_cmd(
    pattern="مساعدة ?(-c|-p|-t)? ?([\s\S]*)?",
    command=("مساعدة", plugin_category),
    info={
        "header": "To get guide for catuserbot.",
        "description": "To get information or guide for the command or plugin",
        "note": "if command name and plugin name is same then you get guide for plugin. So by using this flag you get command guide",
        "flags": {
            "c": "To get info of command.",
            "p": "To get info of plugin.",
            "t": "To get all plugins in text format.",
        },
        "usage": [
            "{tr}help (plugin/command name)",
            "{tr}help -c (command name)",
        ],
        "examples": ["{tr}help help", "{tr}help -c help"],
    },
)
async def _(event):
    "للحصول على دليل للبوت برو"
    flag = event.pattern_match.group(1)
    input_str = event.pattern_match.group(2)
    reply_to_id = await reply_id(event)
    if flag and flag == "-c" and input_str:
        outstr = await cmdinfo(input_str, event)
        if outstr is None:
            return
    elif input_str:
        outstr = await plugininfo(input_str, event, flag)
        if outstr is None:
            return
    else:
        if flag == "-t":
            outstr = await grpinfo()
        else:
            results = await event.client.inline_query(Config.TG_BOT_USERNAME, "help")
            await results[0].click(event.chat_id, reply_to=reply_to_id, hide_via=True)
            await event.delete()
            return
    await edit_or_reply(event, outstr)


@catub.cat_cmd(
    pattern="اوامر برو(?:\s|$)([\s\S]*)",
    command=("اوامر برو", plugin_category),
    info={
        "header": "To show list of cmds.",
        "description": "if no input is given then will show list of all commands.",
        "usage": [
            "{tr}cmds for all cmds",
            "{tr}cmds <plugin name> for paticular plugin",
        ],
    },
)
async def _(event):
    "لعرض جميع أوامر البوت برو."
    input_str = event.pattern_match.group(1)
    if not input_str:
        outstr = await cmdlist()
    else:
        try:
            cmds = PLG_INFO[input_str]
        except KeyError:
            return await edit_delete(event, "__اسم البرنامج المساعد غير صالح أعد التحقق منه.__")
        except Exception as e:
            return await edit_delete(event, f"**خطأ**\n`{str(e)}`")
        outstr = f"• **{input_str.title()} يحتوي على {len(cmds)} من الأوامر**\n"
        for cmd in cmds:
            outstr += f"  - `{cmdprefix}{cmd}`\n"
        outstr += f"**👩‍💻 الإستخدام : ** `{cmdprefix}مساعدة -c <اسم الأمر>`"
    await edit_or_reply(
        event, outstr, aslink=True, linktext="مجموعة اوامر البوت برو هي :"
    )


@catub.cat_cmd(
    pattern="الامر ([\s\S]*)",
    command=("الامر", plugin_category),
    info={
        "header": "To search commands.",
        "examples": "{tr}s song",
    },
)
async def _(event):
    "للبحث في الأوامر."
    cmd = event.pattern_match.group(1)
    found = [i for i in sorted(list(CMD_INFO)) if cmd in i]
    if found:
        out_str = "".join(f"`{i}`    " for i in found)
        out = f"**لقد وجدت {len(found)} الأمر(الامر) ل: **`{cmd}`\n\n{out_str}"
        out += f"\n\n__لمزيد من المعلومات تحقق من {cmdprefix}مساعدة -c <الأمر>__"
    else:
        out = f"لا يمكنني العثور على أي أمر من هذا القبيل `{cmd}` في البوت برو"
    await edit_or_reply(event, out)


@catub.cat_cmd(
    pattern="dc$",
    command=("dc", plugin_category),
    info={
        "header": "To show dc of your account.",
        "description": "Dc of your account and list of dc's will be showed",
        "usage": "{tr}dc",
    },
)
async def _(event):
    "To get dc of your bot"
    result = await event.client(functions.help.GetNearestDcRequest())
    result = f"**Dc details of your account:**\
              \n**Country :** {result.country}\
              \n**Current Dc :** {result.this_dc}\
              \n**Nearest Dc :** {result.nearest_dc}\
              \n\n**List Of Telegram Data Centres:**\
              \n**DC1 : **Miami FL, USA\
              \n**DC2 :** Amsterdam, NL\
              \n**DC3 :** Miami FL, USA\
              \n**DC4 :** Amsterdam, NL\
              \n**DC5 : **Singapore, SG\
                "
    await edit_or_reply(event, result)
