from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackContext, CallbackQueryHandler, Updater
from data.ds import Data
from data.database import DB
from components.separated_stats import SeparatedStats

class UserStats:
    def __init__(self, updater: Updater):
        updater.dispatcher.add_handler(CommandHandler('stats', self.stats))
        updater.dispatcher.add_handler(CommandHandler('test', self.hello))
        updater.dispatcher.add_handler(CommandHandler('get_chat_id', self.get_chat_id))
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

        text = update.message.text.split()

        if len(text) > 1 and text[1][0] == '@':
            user_data = DB.get_by_username(text[1][1:])
            if user_data is None:
                return
            username = text[1]
            user_id=user_data[0]
        else:
            username = '@'+update.message.from_user.username
            user_id = update.message.from_user.id
            user_data = DB.get_by_username(update.message.from_user.username)
            if user_data is None:
                return

        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("*📊 Статистика пользователя "+username+"*\n\n"
                                  "🟢 У пользователя активно занятие \"_SEX_\" (_1 час 14 минут_)\n\n" +
                                  "⏱ *Время с пользой*\n" +
                                  "За сегодня: " + DB.get_user_useful_time_today(user_id) + "\n" +
                                  "За неделю: " + DB.get_user_useful_time_week(user_id) + "\n" +
                                  "За месяц: " + DB.get_user_useful_time_month(user_id) + "\n" +
                                  "За все время: " + DB.get_user_useful_time_all(user_id) + "\n", parse_mode="Markdown", reply_markup=reply_markup)

    def hello(self, update: Update, context: CallbackContext) -> None:
        #context.bot.send_photo(update.effective_chat.id, Data.plot_sleep(update.effective_user.id))
        context.bot.send_photo(update.effective_chat.id, Data.plot_time_with_benefit(update.effective_user.id))

    def get_chat_id(self, update: Update, context: CallbackContext) -> None:
        update.message.reply_text(update.effective_chat.id)

    def on_button_click(self, update: Update, context):
        query = update.callback_query

        if query.data == "🔴":
            context.bot.send_dice(update.effective_chat.id)

        elif query.data == 'separated_stats':
            self.__separated_stats.show_separated_stats(update)

        print(update)

        # query.delete_message()

