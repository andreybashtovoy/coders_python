from components.menu import Menu
from telegram import Update
from telegram.ext import Updater
from data.database import DB
import datetime
from math import ceil, floor


class StartActivity(Menu):
    IN_PAGE = 4

    def __init__(self, updater: Updater):
        super().__init__(updater, 'components/start_activity/start_activity.xml', 'start')

    def initial_state(self, update: Update):
        return {
            "u_id": update.message.from_user.id,
            "page": "1",
            "a": "0"
        }

    def get_activity_buttons(self, state, update: Update):

        def get_keyboard_by_names(names):
            keyboard = list()
            i = 0

            for name in names:
                button = {
                    "name": name,
                    "action": "select_activity",
                    "callback": True
                }

                if i % 2 == 0:
                    keyboard.append([button])
                else:
                    keyboard[i // 2].append(button)
                i += 1

            return keyboard

        activity_names = DB.get_all_activity_names()

        names = []

        counted = DB.count_user_activities(state['u_id'])

        for obj in counted:
            names.append(obj['name'])

        for activity in activity_names:
            if activity['name'] not in names and activity['id'] != 0:
                names.append(activity['name'])

        i = self.IN_PAGE * (int(state['page']) - 1)

        return get_keyboard_by_names(names[i:i + 4])

    def next_page(self, state, update: Update):
        state['page'] = int(state['page']) + 1
        return state

    def prev_page(self, state, update: Update):
        state['page'] = int(state['page']) - 1
        return state

    def is_prev_hidden(self, state, update: Update):
        if int(state['page']) <= 1:
            return True
        return False

    def is_next_hidden(self, state, update: Update):
        length = len(DB.get_all_activity_names())

        if length // self.IN_PAGE <= int(state['page']):
            return True
        return False

    def select_activity(self, state, update: Update, name):
        activity = DB.get_activity_by_name(name)
        state['a'] = activity['id']
        return state

    def get_string_by_duration(self, duration):
        hours = floor(duration) if duration > 0 else ceil(duration)
        minutes = floor((abs(duration) % 1) * 60)
        seconds = floor((((abs(duration) % 1) * 60) % 1) * 60)

        return "{} часов {} минут {} секунд".format(hours, minutes, seconds)

    def start_activity(self, user_id, name, update: Update):
        active_activity = DB.get_active_activity(user_id)

        stopped_activity = None

        duration = 0

        if active_activity is not None:
            data_now = datetime.datetime.now()
            data_start = datetime.datetime.strptime(active_activity['start_time'], '%Y-%m-%d %H:%M:%S')
            duration = (data_now - data_start).seconds / 3600

            stopped_activity = active_activity
            stopped_activity['duration'] = duration

        DB.start_activity(user_id, name, duration)

        if stopped_activity is not None and stopped_activity['activity_id'] != 0:
            update.callback_query.message.reply_to_message.reply_text(
                text="✅ Занятие завершено ({})\n\n⏱ Продолжительность: {}.".format(
                    stopped_activity['name'],
                    self.get_string_by_duration(stopped_activity['duration'])
                ),
                parse_mode="Markdown"
            )

        if name != "Ничего":
            update.callback_query.message.edit_text(
                text="🧾 Ты начал занятие \"{}\".".format(name))

    def action_custom_callback(self, update: Update, state):
        if update.callback_query is not None and update.callback_query.from_user.id != int(state['u_id']):
            update.callback_query.answer(text="Меню было вызвано другим пользователем.", show_alert=True)
            return False

        name = DB.get_activity_by_id(int(state['a']))['name']

        self.start_activity(state['u_id'], name, update)

        return False
