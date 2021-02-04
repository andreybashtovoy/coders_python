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
        temp = update.message.text.split(" ")

        dur = "30"

        print(temp[1])

        if len(temp) > 1 and temp[1].isdecimal():
            dur = temp[1]

        return {
            "u_id": update.message.from_user.id,
            "a": "0",
            "p": "1",
            "dur": dur
        }

    def get_string_by_duration(self, duration):
        hours = abs(duration)//60
        minutes = abs(duration) % 60

        if duration < 0:
            if hours == 0:
                minutes = -minutes
            else:
                hours = -hours

        return "{} часов {} минут".format(hours, minutes)

    def text_format(self, message_text, update: Update, state):
        duration = int(state['dur'])

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

        activity_names = DB.get_user_accessible_activities(state['u_id'], update.effective_chat.id)

        names = []

        counted = DB.count_user_activities(state['u_id'])

        for obj in counted:
            if obj['name'] in [x['name'] for x in activity_names]:
                names.append(obj['name'])

        for activity in activity_names:
            if activity['name'] not in names and activity['id'] != 0:
                names.append(activity['name'])

        i = self.IN_PAGE * (int(state['p']) - 1)

        return get_keyboard_by_names(names[i:i + 4])

    def select_activity(self, state, update: Update, name):
        activity = DB.get_user_activity_by_name(name, state['u_id'], update.effective_chat.id)
        state['a'] = activity['id']
        return state

    def add_time(self, minutes, state, update: Update):
        state["dur"] = int(state["dur"]) + minutes

        return state

    def minus_10(self, state, update: Update):
        return self.add_time(-10, state, update)

    def minus_30(self, state, update: Update):
        return self.add_time(-30, state, update)

    def minus_60(self, state, update: Update):
        return self.add_time(-60, state, update)

    def plus_10(self, state, update: Update):
        return self.add_time(10, state, update)

    def plus_30(self, state, update: Update):
        return self.add_time(30, state, update)

    def plus_60(self, state, update: Update):
        return self.add_time(60, state, update)

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
        length = len(DB.get_user_accessible_activities(state['u_id'], update.effective_chat.id)) - 1

        page_count = ceil(length / self.IN_PAGE)

        if page_count <= int(state['p']):
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

        if int(state['dur']) == 0:
            update.callback_query.answer(text="Продолжительность не должна быть равна нулю.", show_alert=True)
            return False

        activity = DB.get_activity_by_id(state['a'])

        project = DB.get_active_project(state['u_id'], activity['name'])

        if project is not None:
            DB.add_activity(state['u_id'], state['a'], int(state['dur'])/60, project['id'])
        else:
            DB.add_activity(state['u_id'], state['a'], int(state['dur'])/60, None)

        string = ""

        if project is not None:
            string = "\n📂 *Проект:* _%s_" % project['name'].replace("_", "\_")


        update.callback_query.edit_message_text(
            text="✅ Ты добавил _{}_ к занятию *{}*\.\n{}".format(
                self.get_string_by_duration(int(state['dur'])),
                DB.get_activity_by_id(int(state['a']))['name'].replace("_", "\_"),
                string
            ),
            parse_mode="MarkdownV2"
        )

        return False

    def cancel(self, update: Update, state):
        if update.callback_query is not None and update.callback_query.from_user.id != int(state['u_id']):
            update.callback_query.answer(text="Меню было вызвано другим пользователем.", show_alert=True)
            return False

        try:
            update.callback_query.message.reply_to_message.delete()
            update.callback_query.message.delete()
        except:
            update.callback_query.message.edit_text(
                text="✖️ *Ты отменил занятие.*\n\n"
                     "`Чтобы бот мог удалять сообщения при отмене, ему нужны права администратора.`",
                parse_mode="Markdown"
            )

        return False