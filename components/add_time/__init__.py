from components.menu import Menu
from telegram import Update
from telegram.ext import Updater
from data.database import DB
from data.ds import Data
from math import floor, ceil


class AddTime(Menu):
    IN_PAGE = 4

    def __init__(self, updater: Updater):
        super().__init__(updater, 'components/add_time/add_time.xml', 'add')

    def initial_state(self, update: Update):
        return {
            "u_id": update.message.from_user.id,
            "a": "0",
            "p": "1",
            "dur": "0.5"
        }

    def get_string_by_duration(self, duration):
        hours = floor(duration) if duration > 0 else ceil(duration)
        minutes = floor((abs(duration) % 1) * 60)
        if hours == 0 and duration < 0:
            minutes = -minutes
        seconds = floor((((abs(duration) % 1) * 60) % 1) * 60)

        return "{} часов {} минут {} секунд".format(hours, minutes, seconds)

    def text_format(self, message_text, update: Update, state):
        duration = float(state['dur'])

        name = "Не выбрано"

        if state['a'] != '0':
            name = DB.get_activity_by_id(int(state['a']))['name']

        return message_text.format(
            action_name=name,
            duration_string=self.get_string_by_duration(duration)
        )

    def get_activity_buttons(self, state, update: Update):

        def get_keyboard_by_names(names):
            keyboard = list()
            i = 0

            for name in names:
                button = {
                    "name": name,
                    "action": "select_activity"
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

        i = self.IN_PAGE * (int(state['p']) - 1)

        return get_keyboard_by_names(names[i:i + 4])

    def select_activity(self, state, update: Update, name):
        activity = DB.get_activity_by_name(name)
        state['a'] = activity['id']
        return state

    def add_time(self, minutes, state, update: Update):
        state["dur"] = round(float(state["dur"]) + minutes / 60, 5)

        return state

    def minus_10(self, state, update: Update):
        return self.add_time(-10, state, update)

    def minus_30(self, state, update: Update):
        return self.add_time(-30, state, update)

    def plus_10(self, state, update: Update):
        return self.add_time(10, state, update)

    def plus_30(self, state, update: Update):
        return self.add_time(30, state, update)

    def next_page(self, state, update: Update):
        state['p'] = int(state['p']) + 1
        return state

    def prev_page(self, state, update: Update):
        state['p'] = int(state['p']) - 1
        return state

    def is_prev_hidden(self, state, update: Update):
        if int(state['p']) <= 1:
            return True
        return False

    def is_next_hidden(self, state, update: Update):
        length = len(DB.get_all_activity_names())

        if length // self.IN_PAGE <= int(state['p']):
            return True
        return False

    def check(self, update: Update, state):
        if update.callback_query is not None and update.callback_query.from_user.id != int(state['u_id']):
            update.callback_query.answer(text="Меню было вызвано другим пользователем.", show_alert=True)
            return False
        return True

    def done(self, update: Update, state):
        if update.callback_query is not None and update.callback_query.from_user.id != int(state['u_id']):
            update.callback_query.answer(text="Меню было вызвано другим пользователем.", show_alert=True)
            return False

        if state['a'] == '0':
            update.callback_query.answer(text="Ты не выбрал занятие.", show_alert=True)
            return False

        DB.add_activity(state['u_id'], state['a'], state['dur'])

        update.callback_query.edit_message_text(
            text="✅ Ты добавил _{}_ к занятию *{}*.".format(
                self.get_string_by_duration(float(state['dur'])),
                DB.get_activity_by_id(int(state['a']))['name']
            ),
            parse_mode="Markdown"
        )

        return False
