"""
.لإحضار تفاصيل التطبيق من متجر بلاي
.استخدم الأمر .تطبيق<اسم التطبيق> لجلب تفاصيل عن التطبيق
  © [معرف المطور](http://t.me/u_5_1)
"""
import bs4
import requests

from . import ALIVE_NAME, catub, edit_or_reply

plugin_category = "utils"


@catub.cat_cmd(
    pattern="تطبيق ([\s\S]*)",
    command=("تطبيق", plugin_category),
    info={
        "header": "To search any app in playstore",
        "description": "Searches the app in the playstore and provides the link to the app in playstore and fetchs app details",
        "usage": "{tr}app <name>",
    },
)
async def app_search(event):
    "To search any app in playstore."
    app_name = event.pattern_match.group(1)
    event = await edit_or_reply(event, "`يتم البحث، يرجى الإنتظار🧸🖤...`")
    try:
        remove_space = app_name.split(" ")
        final_name = "+".join(remove_space)
        page = requests.get(
            "https://play.google.com/store/search?q=" + final_name + "&c=apps"
        )
        str(page.status_code)
        soup = bs4.BeautifulSoup(page.content, "lxml", from_encoding="utf-8")
        results = soup.findAll("div", "ZmHEEd")
        app_name = (
            results[0].findNext("div", "Vpfmgd").findNext("div", "WsMG1c nnK0zc").text
        )
        app_dev = results[0].findNext("div", "Vpfmgd").findNext("div", "KoLSrc").text
        app_dev_link = (
            "https://play.google.com"
            + results[0].findNext("div", "Vpfmgd").findNext("a", "mnKHRc")["href"]
        )
        app_rating = (
            results[0]
            .findNext("div", "Vpfmgd")
            .findNext("div", "pf5lIe")
            .find("div")["aria-label"]
        )
        app_link = (
            "https://play.google.com"
            + results[0]
            .findNext("div", "Vpfmgd")
            .findNext("div", "vU6FJ p63iDd")
            .a["href"]
        )
        app_icon = (
            results[0]
            .findNext("div", "Vpfmgd")
            .findNext("div", "uzcko")
            .img["data-src"]
        )
        app_details = "<a href='" + app_icon + "'<📲&#8203;</a>"
        app_details += " <b>" + app_name + "</b>"
        app_details += (
            "\n\n<code>👨‍💻| المطور :</code> <a href='"
            + app_dev_link
            + "'>"
            + app_dev
            + "</a>"
        )
        app_details += "\n<code>🌟| تقييم التطبيق :</code> " + app_rating.replace(
            "Rated ", "⭐ "
        ).replace(" out of ", "/").replace(" stars", "", 1).replace(
            " stars", "⭐ "
        ).replace(
            "five", "5"
        )
        app_details += (
            "\n<code>💎| ميزات التطبيق :</code> <a href='" + app_link + "'>اضغط هنا</a>"
        )
        app_details += f"\n\n↠ {ALIVE_NAME} ↞"
        await event.edit(app_details, link_preview=True, parse_mode="HTML")
    except IndexError:
        await event.edit("تعذر العثور على التطبيق. يرجى إدخال **اسم تطبيق صالح**")
    except Exception as err:
        await event.edit("حدث استثناء:- " + str(err))
