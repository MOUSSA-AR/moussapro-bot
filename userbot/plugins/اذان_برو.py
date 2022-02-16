# ported from uniborg
# https://github.com/muhammedfurkan/UniBorg/blob/master/stdplugins/ezanvakti.py
import json

import requests

from ..sql_helper.globals import gvarstatus
from . import catub, edit_delete, edit_or_reply

plugin_category = "extra"


@catub.cat_cmd(
    pattern="اذان(?:\s|$)([\s\S]*)",
    command=("اذان", plugin_category),
    info={
        "header": "Shows you the Islamic prayer times of the given city name.",
        "note": "you can set default city by using {tr}setcity command.",
        "usage": "{tr}azan <city name>",
        "examples": "{tr}azan hyderabad",
    },
)
async def get_adzan(adzan):
    "Shows you the Islamic prayer times of the given city name"
    input_str = adzan.pattern_match.group(1)
    LOKASI = gvarstatus("DEFCITY") or "Delhi" if not input_str else input_str
    url = f"http://muslimsalat.com/{LOKASI}.json?key=bd099c5825cbedb9aa934e255a81a5fc"
    request = requests.get(url)
    if request.status_code != 200:
        return await edit_delete(adzan, f"`تعذر جلب أي بيانات عن المدينة {LOKASI}`", 5)
    result = json.loads(request.text)
    catresult = f"<b>أوقات الصلاة الإسلامية </b>\
            \n\n<b>المدينة     : </b><i>{result['query']}</i>\
            \n<b>الدولة  : </b><i>{result['country']}</i>\
            \n<b>التاريخ     : </b><i>{result['items'][0]['date_for']}</i>\
            \n<b>الفجر     : </b><i>{result['items'][0]['fajr']}</i>\
            \n<b>الشروق    : </b><i>{result['items'][0]['shurooq']}</i>\
            \n<b>الظهر    : </b><i>{result['items'][0]['dhuhr']}</i>\
            \n<b>العصر    : </b><i>{result['items'][0]['asr']}</i>\
            \n<b>المغرب    : </b><i>{result['items'][0]['maghrib']}</i>\
            \n<b>العشاء     : </b><i>{result['items'][0]['isha']}</i>\
    "
    await edit_or_reply(adzan, catresult, "html")
