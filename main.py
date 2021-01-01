from telegram.ext import Updater
import warnings
import json
from components.user_stats import UserStats
from components.test_menu import TestMenu

warnings.filterwarnings('ignore')

if __name__ == "__main__":
    f = open('bot_data.json')
    json_object = json.load(f)

    updater = Updater(json_object["token"])

    updater.bot.send_message(-1001243947001, "О связь есть")

    UserStats(updater)
    TestMenu(updater)

    updater.start_polling()
    updater.idle()
    f.close()
