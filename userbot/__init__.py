# @moussa_pro - < https://t.me/moussa_pro >
# Copyright (C) 2021 - MOUSSA-AR
# All rights reserved.
#
# This file is a part of < https://github.com/MOUSSA-AR/moussabot >
# Please read the GNU Affero General Public License in;
# < https://github.com/MOUSSA-AR/moussapro_bot/blob/master/LICENSE
# ===============================================================
import time

import heroku3

from .Config import Config
from .core.logger import logging
from .core.session import moussabot
from .sql_helper.globals import addgvar, delgvar, gvarstatus

__version__ = "1.0.0"
__license__ = "كتابة وتعديل موسى @u_5_1"
__author__ = "MOUSSA_pro <https://github.com/MOUSSA-AR/moussapro-bot>"
__copyright__ = "MOUSSA-PRO Team  (C) 2021 - 2022  " + __author__

moussabot.version = __version__
moussabot.tgbot.version = __version__
LOGS = logging.getLogger("ProUserbot")
bot = moussabot

StartTime = time.time()
proversion = "5.2.0"

if Config.UPSTREAM_REPO == "moussapro-bot":
    UPSTREAM_REPO_URL = "https://github.com/MOUSSA-AR/moussapro-bot"
elif Config.UPSTREAM_REPO == "moussa-ar":
    UPSTREAM_REPO_URL = "https://github.com/MOUSSA-AR/moussapro-bot"
else:
    UPSTREAM_REPO_URL = Config.UPSTREAM_REPO

if Config.PRIVATE_GROUP_BOT_API_ID == 0:
    if gvarstatus("PRIVATE_GROUP_BOT_API_ID") is None:
        Config.BOTLOG = False
        Config.BOTLOG_CHATID = "me"
    else:
        Config.BOTLOG_CHATID = int(gvarstatus("PRIVATE_GROUP_BOT_API_ID"))
        Config.PRIVATE_GROUP_BOT_API_ID = int(gvarstatus("PRIVATE_GROUP_BOT_API_ID"))
        Config.BOTLOG = True
else:
    if str(Config.PRIVATE_GROUP_BOT_API_ID)[0] != "-":
        Config.BOTLOG_CHATID = int("-" + str(Config.PRIVATE_GROUP_BOT_API_ID))
    else:
        Config.BOTLOG_CHATID = Config.PRIVATE_GROUP_BOT_API_ID
    Config.BOTLOG = True

if Config.PM_LOGGER_GROUP_ID == 0:
    if gvarstatus("PM_LOGGER_GROUP_ID") is None:
        Config.PM_LOGGER_GROUP_ID = -100
    else:
        Config.PM_LOGGER_GROUP_ID = int(gvarstatus("PM_LOGGER_GROUP_ID"))
elif str(Config.PM_LOGGER_GROUP_ID)[0] != "-":
    Config.PM_LOGGER_GROUP_ID = int("-" + str(Config.PM_LOGGER_GROUP_ID))

try:
    if Config.HEROKU_API_KEY is not None or Config.HEROKU_APP_NAME is not None:
        HEROKU_APP = heroku3.from_key(Config.HEROKU_API_KEY).apps()[
            Config.HEROKU_APP_NAME
        ]
    else:
        HEROKU_APP = None
except Exception:
    HEROKU_APP = None


# Global Configiables
COUNT_MSG = 0
USERS = {}
COUNT_PM = {}
LASTMSG = {}
CMD_HELP = {}
ISAFK = False
AFKREASON = None
CMD_LIST = {}
SUDO_LIST = {}
# for later purposes
INT_PLUG = ""
LOAD_PLUG = {}

# Variables
BOTLOG = Config.BOTLOG
BOTLOG_CHATID = Config.BOTLOG_CHATID
PM_LOGGER_GROUP_ID = Config.PM_LOGGER_GROUP_ID
