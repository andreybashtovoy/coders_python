from components.menu import Menu
from telegram import Update
from telegram.ext import Updater
from data.database import DB


class TestMenu(Menu):
    def __init__(self, updater: Updater):
        super().__init__(updater, 'components/user_stats/user_stats.xml', 'test_stats')

    def initial_state(self, update: Update):
        if update.message.reply_to_message is None:
            text = update.message.text.split()
            if len(text) > 1 and text[1][0] == '@':
                user = DB.get_by_username(text[1][1:])
            else:
                user = DB.get_by_username(update.message.from_user.username)
        else:
            print(update.message.reply_to_message.from_user.username)
            user = DB.get_by_username(update.message.reply_to_message.from_user.username)

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

        return message_text.format(username=user['username'].replace("_", " "),
                                   task_icon=task_icon,
                                   active_task=active_task['name'],
                                   task_time=active_task['time'],
                                   today=DB.get_user_useful_time(user['user_id'], 'today'),
                                   week=DB.get_user_useful_time(user['user_id'], 'week'),
                                   month=DB.get_user_useful_time(user['user_id'], 'month'),
                                   all=DB.get_user_useful_time(user['user_id'], 'all'))

    def sleep_menu_format(self, message_text, update: Update, state):
        user = DB.get_user_by_id(state['user_id'])
        return message_text.format(
            username=user['username'].replace("_", " "),
            average_duration="_9 часов 5 минут ± 1 часов 3 минут_",
            average_wake_up="_9:43 ± 0 часов 14 минут_",
            average_sleep_start="_00:15 +- 1 часов 38 минут_"
        )
