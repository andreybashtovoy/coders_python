from components.menu import Menu
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from data.database import DB
from data.ds import Data


class UserStats(Menu):
    def __init__(self, updater: Updater):
        super().__init__(updater, 'components/user_stats/user_stats.xml')
        updater.dispatcher.add_handler(CommandHandler('stats', self.open))
        self.command = 'stats'

    def open(self, update: Update, context: CallbackContext):
        if DB.has_user_activities(update.message.from_user.id):
            self.send(update, context)
        else:
            update.message.reply_text(
                text="Чтобы получить личную статистику, необходимо запустить хотя бы одно занятие командой /start."
            )

    def initial_state(self, update: Update):
        if update.message.reply_to_message is None:
            text = update.message.text.split()
            if len(text) > 1 and text[1][0] == '@':
                user = DB.get_by_username(text[1][1:])
            else:
                user = DB.get_user_by_id(update.message.from_user.id)
        else:
            print(update.message.reply_to_message.from_user.username)
            user = DB.get_user_by_id(update.message.reply_to_message.from_user.id)

        if user is None:
            return {}
        else:
            return {
                "user_id": user['user_id']
            }

    def main_menu_format(self, message_text, update: Update, state):
        user = DB.get_user_by_id(state['user_id'])

        active_task = DB.get_active_task_user(user['user_id'])
        task_icon = "🟢" if active_task['active'] else "🔴"

        return message_text.format(username=user['username'].replace("_", "\_"),
                                   task_icon=task_icon,
                                   active_task=active_task['name'],
                                   task_time=active_task['time'],
                                   today=DB.get_user_useful_time(user['user_id'], 'today'),
                                   week=DB.get_user_useful_time(user['user_id'], 'week'),
                                   month=DB.get_user_useful_time(user['user_id'], 'month'),
                                   all=DB.get_user_useful_time(user['user_id'], 'all'))

    def sleep_menu_format(self, message_text, update: Update, state):
        user = DB.get_user_by_id(state['user_id'])

        duration = Data.get_average_sleep_duration(state['user_id'])
        start_sleep = Data.get_average_sleep_start_time(state['user_id'])
        wake_up = Data.get_average_wake_up_time(user['user_id'])

        return message_text.format(
            username=user['username'].replace("_", " "),
            average_duration="_{} ± {}_".format(*duration),
            average_wake_up="_{} ± {}_".format(*wake_up),
            average_sleep_start="_{} ± {}_".format(*start_sleep)
        )
