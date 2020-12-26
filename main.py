from telegram.ext import Updater
import warnings
import json
from components.user_stats import UserStats

warnings.filterwarnings('ignore')

if __name__ == "__main__":
    f = open('bot_data.json')
    json_object = json.load(f)

    updater = Updater(json_object["token"])

    updater.bot.send_message(-1001243947001, "Restarted")

    UserStats(updater)

    updater.start_polling()
    updater.idle()
    f.close()
