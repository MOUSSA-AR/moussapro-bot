from telethon.tl.types import ChannelParticipantsAdmins

from userbot import catub

from ..helpers.utils import get_user_from_event, reply_id

plugin_category = "extra"


@catub.cat_cmd(
    pattern="(تاغ للكل|للكل)(?:\s|$)([\s\S]*)",
    command=("تاغ للكل", plugin_category),
    info={
        "header": "عمل تاغ ل100 شخص في المجموعة",
        "usage": [
            "{tr}للكل <text>",
            "{tr}تاغ للكل",
        ],
    },
)
async def _(event):

    "عمل تاغ للجميع."

    reply_to_id = await reply_id(event)

    input_str = event.pattern_match.group(2)

    mentions = input_str or "**تم عمل تاغ ل100 عضو🧸🖤.**"

    chat = await event.get_input_chat()

    async for x in event.client.iter_participants(chat, 100):

        mentions += f"[\u2063](tg://user?id={x.id})"

    await event.client.send_message(event.chat_id, mentions, reply_to=reply_to_id)

    await event.delete()


@catub.cat_cmd(
    pattern="تاغ للادمن$",
    command=("تاغ للادمن", plugin_category),
    info={
        "header": "عمل تاغ لأدمنية المجموعة",
        "usage": "{tr}تاغ للادمن",
    },
)
async def _(event):

    "عمل تاغ لأدمنية المجموعة."

    mentions = "**تم عمل تاغ للأدمنية🧸🖤**: **Spam Spotted**"

    chat = await event.get_input_chat()

    reply_to_id = await reply_id(event)

    async for x in event.client.iter_participants(
        chat, filter=ChannelParticipantsAdmins
    ):

        if not x.bot:

            mentions += f"[\u2063](tg://user?id={x.id})"

    await event.client.send_message(event.chat_id, mentions, reply_to=reply_to_id)

    await event.delete()


@catub.cat_cmd(
    pattern="تاغ ([\s\S]*)",
    command=("تاغ", plugin_category),
    info={
        "header": "عمل تاغ لشخص بنص معين",
        "usage": [
            "{tr}men username/userid text",
            "text (username/mention)[custom text] text",
        ],
        "examples": ["{tr}men @mrconfused hi", "Hi @mrconfused[How are you?]"],
    },
)
async def _(event):

    "عمل تاغ لشخص بنص معين."

    user, input_str = await get_user_from_event(event)

    if not user:

        return

    reply_to_id = await reply_id(event)

    await event.delete()

    await event.client.send_message(
        event.chat_id,
        f"<a href= tg://user?id={user.id} >{input_str}</a>",
        parse_mode="HTML",
        reply_to=reply_to_id,
    )
