from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler
import warnings
import json
from components.user_stats import UserStats

warnings.filterwarnings('ignore')

if __name__ == "__main__":
    f = open('bot_data.json')
    json_object = json.load(f)

    updater = Updater(json_object["token"])

    UserStats(updater)

    updater.start_polling()
    updater.idle()
