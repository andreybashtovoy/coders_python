from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackContext, CallbackQueryHandler
from data.ds import Data
from data.database import DB

class UserStats:
    def __init__(self, updater):
        updater.dispatcher.add_handler(CommandHandler('stats', self.stats))
        updater.dispatcher.add_handler(CommandHandler('stats', self.stats))
        updater.dispatcher.add_handler(CallbackQueryHandler(self.on_button_click))

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

        text = update.message.text.split()

        if len(text) > 1 and text[1][0] == '@':
            user_data = DB.get_by_username(text[1][1:])
            # (873181817, 0, 1607385300, 'sbarabas')
            print(user_data)
            username = text[1]
            user_id=user_data[0]
        else:
            username = '@'+update.message.from_user.username
            user_id = update.message.from_user.id

        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("*📊 Статистика пользователя "+username+"*\n\n"
                                  "🟢 У пользователя активно занятие \"_SEX_\" (_1 час 14 минут_)\n\n" \
                                  "⏱ *Время с пользой*\n" \
                                  "За сегодня: _" + DB.get_user_useful_time_today(user_id) + "_ часов\n" \
                                  "За неделю: _" + DB.get_user_useful_time_week(user_id) + "_ часов\n" \
                                  "За месяц: _" + DB.get_user_useful_time_month(user_id) + "_ часов\n" \
                                  "За все время: _" + DB.get_user_useful_time_all(user_id) + "_ часов\n", parse_mode="Markdown", reply_markup=reply_markup)

    def hello(self, update: Update, context: CallbackContext) -> None:
        context.bot.send_photo(update.effective_chat.id, Data.plot_sleep(update.effective_user.id))

    def on_button_click(self, update: Update, context):
        query = update.callback_query

        if query.data == "🔴":
            context.bot.send_dice(update.effective_chat.id)

        elif query.data == 'all_tasks':
            print(context.bot.send_dice(update.effective_chat.id))


        print(update)

        update.callback_query.delete_message()