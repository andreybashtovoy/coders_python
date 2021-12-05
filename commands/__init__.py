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
        updater.dispatcher.add_handler(CommandHandler('toggle_tag', self.toggle_tag))
        updater.dispatcher.add_handler(CommandHandler('ranks', self.ranks))
        updater.dispatcher.add_handler(CommandHandler('status', self.status))
        updater.dispatcher.add_handler(CommandHandler('calendar', self.calendar))

    def restart(self, update: Update, context):
        update.message.reply_text("До связи")
        os._exit(0)

    def get_chat_id(self, update: Update, context: CallbackContext):
        update.message.reply_text(update.effective_chat.id)

    def toggle_tag(self, update: Update, context: CallbackContext):
        user = DB.get_user_by_id(update.message.from_user.id)

        if user['tag']:
            DB.disable_tag(update.message.from_user.id)
            update.message.reply_text("☑️ *Ты выключил теги\. Вернуть можешь командой:*\n"
                                      "/toggle\_tag", parse_mode="MarkdownV2")
        else:
            DB.enable_tag(update.message.from_user.id)
            update.message.reply_text("☑️ *Ты включил теги\. Выключить можешь командой:*\n"
                                      "/toggle\_tag", parse_mode="MarkdownV2")

    def ranks(self, update: Update, context: CallbackContext):
        ranks = DB.get_all_ranks()

        users = DB.get_chat_users(update.effective_chat.id)

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

        print(activity)

        task_icon = "🟢" if activity['active'] else "🔴"

        project_str = ""
        if activity['project_name'] is not None:
            project_str = f" ({activity['project_name']})"

        update.message.reply_text(
            text="%s *%s*%s: _%s_" % (task_icon, activity['name'], project_str, activity['time']),
            parse_mode="Markdown"
        )

    def calendar(self, update: Update, context: CallbackContext):
        update.message.reply_text(
            text=f"http://161.97.155.140/activities/{update.message.from_user.id}",
            parse_mode="Markdown"
        )
