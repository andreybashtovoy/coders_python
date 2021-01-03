from telegram.ext import Updater, CallbackContext, CallbackQueryHandler
from telegram import Update
import warnings
import json
from components.user_stats import UserStats
from components.rating import Rating
from commands import CommandHandlers

warnings.filterwarnings('ignore')

if __name__ == "__main__":
    f = open('bot_data.json')
    json_object = json.load(f)

    updater = Updater(json_object["token"])

    updater.bot.send_message(-1001243947001, "О связь есть")

    menus = [UserStats(updater), Rating(updater)]

    def button_click_handler(update: Update, context: CallbackContext):
        for menu in menus:
            if update.callback_query.message.reply_to_message.text.startswith("/" + menu.command):
                menu.on_button_click(update, context)
                return
            
    updater.dispatcher.add_handler(CallbackQueryHandler(button_click_handler))

    CommandHandlers(updater)

    updater.start_polling()
    updater.idle()
    f.close()
