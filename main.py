from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler
import warnings
import json


from data import Data

warnings.filterwarnings('ignore')


class CommandHandlers:



    def __init__(self):
        f = open('babySemenToken.json')
        json_object = json.load(f)

        updater = Updater(json_object["token"])
        updater.dispatcher.add_handler(CommandHandler('stats', self.stats))
        updater.dispatcher.add_handler(CommandHandler('stats', self.stats))
        updater.dispatcher.add_handler(CallbackQueryHandler(self.on_button_click))

        updater.start_polling()
        updater.idle()

    def stats(self, update: Update, context: CallbackContext) -> None:
        keyboard = [
            [
                InlineKeyboardButton("📅 Полезное время по дням", callback_data="🔴ф")
            ],
            [
                InlineKeyboardButton("🧩 Статистика всем занятиям", callback_data="🔴ф")
            ],
            [
                InlineKeyboardButton("🤹‍♂️ Статистика по каждому занятию отдельно", callback_data="all_tasks")
            ],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("*📊 Статистика пользователя @vasyanedown*\n\n"
                                  "🟢 У пользователя активно занятие \"_SEX_\" (_1 час 14 минут_)\n\n" \
                                  "⏱ *Время с пользой*\n" \
                                  "За сегодня: _1234_ часов\n" \
                                  "За неделю: _123_ часов\n" \
                                  "За все время: _777_ часов\n", parse_mode="Markdown", reply_markup=reply_markup)

    def on_button_click(self, update: Update, context):
        query = update.callback_query

        if query.data == "🔴":
            context.bot.send_dice(update.effective_chat.id)

        elif query.data == 'all_tasks':
            print(context.bot.send_dice(update.effective_chat.id))


        print(update)

        update.callback_query.delete_message()


CommandHandlers()
