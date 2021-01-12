from telegram import InlineKeyboardButton, Update, CallbackQuery, InlineKeyboardMarkup
from telegram.ext import CallbackContext, Updater, CommandHandler
from data.database import DB
import os
from math import floor


class CommandHandlers:
    def __init__(self, updater: Updater):
        self.__updater = updater
        updater.dispatcher.add_handler(CommandHandler('restart', self.restart))
        updater.dispatcher.add_handler(CommandHandler('get_chat_id', self.get_chat_id))
        updater.dispatcher.add_handler(CommandHandler('disable_tag', self.disable_tag))
        updater.dispatcher.add_handler(CommandHandler('enable_tag', self.enable_tag))
        updater.dispatcher.add_handler(CommandHandler('ranks', self.ranks))
        updater.dispatcher.add_handler(CommandHandler('status', self.status))

    def restart(self, update: Update, context):
        update.message.reply_text("До связи")
        os._exit(0)

    def get_chat_id(self, update: Update, context: CallbackContext):
        update.message.reply_text(update.effective_chat.id)

    def disable_tag(self, update: Update, context: CallbackContext):
        DB.disable_tag(update.message.from_user.id)
        update.message.reply_text("*Ок\. Вернуть теги можешь командой:*\n"
                                  "/enable\_tag", parse_mode="MarkdownV2")

    def enable_tag(self, update: Update, context: CallbackContext):
        DB.enable_tag(update.message.from_user.id)
        update.message.reply_text("*Ок\. Отключить теги можешь командой:*\n"
                                  "/disable\_tag", parse_mode="MarkdownV2")

    def ranks(self, update: Update, context: CallbackContext):
        ranks = DB.get_all_ranks()

        users = DB.get_all_users()

        string = "🧩 *Звания участников чата*\n\n"

        i = 0
        emoji = ["🔸", "🔹"]

        for user in users:
            hours = DB._get_user_useful_time(user['user_id'], 'all')['time']

            rank = ranks[0]['name']

            for obj in ranks:
                if obj['min_hours'] <= hours:
                    rank = obj['name']
                else:
                    break

            username = user['username'].replace("_","\_")
            username = username.replace(".", "\.")

            if hours < 0:
                hours = 0

            string += "%s `%s` \- *%s* \(%d часов с пользой\)\n" % (emoji[i % 2],
                                                                  username,
                                                                  rank,
                                                                  floor(hours))

        update.message.reply_text(
            text=string,
            parse_mode="MarkdownV2"
        )

    def status(self, update: Update, context: CallbackContext):
        activity = DB.get_active_task_user(update.message.from_user.id)

        task_icon = "🟢" if activity['active'] else "🔴"

        update.message.reply_text(
            text="%s *%s* (_%s_)" % (task_icon, activity['name'], activity['time']),
            parse_mode="Markdown"
        )
