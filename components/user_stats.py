# telegram imports
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackContext, CallbackQueryHandler, Updater
from data.ds import Data
from data.database import DB
from components.separated_stats import SeparatedStats


class UserStats:
    def __init__(self, updater: Updater):
        updater.dispatcher.add_handler(CommandHandler('stats', self.stats))
        updater.dispatcher.add_handler(CommandHandler('stats', self.stats))
        updater.dispatcher.add_handler(CallbackQueryHandler(self.on_button_click))
        self.__updater = updater
        self.__separated_stats = SeparatedStats(updater)

    def stats(self, update: Update, context: CallbackContext) -> None:
        keyboard = [
            [
                InlineKeyboardButton("📅 Полезное время по дням", callback_data="🔴ф")
            ],
            [
                InlineKeyboardButton("🧩 Статистика всем занятиям", callback_data="🔴ф")
            ],
            [
                InlineKeyboardButton("🤹‍♂️ Статистика по каждому занятию отдельно", callback_data="separated_stats")
            ],
        ]

        result = update.message.text.split()

        if len(result)>1:
            print(DB.get_by_username(result[1]))

        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("*📊 Статистика пользователя @vasyanedown*\n\n"
                                  "🟢 У пользователя активно занятие \"_SEX_\" (_1 час 14 минут_)\n\n"
                                  "⏱ *Время с пользой*\n"
                                  "За сегодня: _1234_ часов\n"
                                  "За неделю: _123_ часов\n"
                                  "За все время: _777_ часов\n", parse_mode="Markdown", reply_markup=reply_markup)


    def hello(self, update: Update, context: CallbackContext) -> None:
        context.bot.send_photo(update.effective_chat.id, Data.plot_sleep(update.effective_user.id))

    def on_button_click(self, update: Update, context):
        query = update.callback_query

        if query.data == "🔴":
            context.bot.send_dice(update.effective_chat.id)

        elif query.data == 'separated_stats':
            self.__separated_stats.show_separated_stats(update)

        print(update)

        # query.delete_message()

