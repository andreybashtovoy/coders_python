from components.menu import Menu
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
from data.database import DB
import datetime
from math import ceil, floor


class ProjectsSelectingActivity(Menu):
    IN_PAGE = 4

    def __init__(self, updater: Updater, projects):
        super().__init__(updater, 'components/projects/selecting_activity.xml', 'projects')
        self.projects = projects

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

        activity_names = DB.get_user_accessible_activities(state['u_id'], update.effective_chat.id)

        names = []

        counted = DB.count_user_activities(state['u_id'])

        for obj in counted:
            if obj['name'] in [x['name'] for x in activity_names]:
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
        length = len(DB.get_user_accessible_activities(state['u_id'], update.effective_chat.id)) - 1

        page_count = ceil(length / self.IN_PAGE)

        if page_count <= int(state['page']):
            return True
        return False

    def select_activity(self, state, update: Update, name):
        activity = DB.get_user_activity_by_name(name, state['u_id'], update.effective_chat.id)
        state['a'] = activity['id']
        return state

    def action_custom_callback(self, update: Update, state):
        if update.callback_query is not None and update.callback_query.from_user.id != int(state['u_id']):
            update.callback_query.answer(text="Меню было вызвано другим пользователем.", show_alert=True)
            return False

        self.projects[1].open_menu('0', {
            "u_id": state["u_id"],
            "a": state["a"],
            "p_id": "0",
            "page": "1"
        }, update)

        return False
