from components.menu import Menu
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
from data.database import DB
import datetime
from math import ceil, floor


class SeparateProject(Menu):

    def __init__(self, updater: Updater, projects):
        super().__init__(updater, 'components/projects/separate_project.xml')
        self.projects = projects

    def get_string_by_duration(self, duration):
        hours = floor(duration) if duration > 0 else ceil(duration)
        minutes = floor((abs(duration) % 1) * 60)
        seconds = floor((((abs(duration) % 1) * 60) % 1) * 60)

        return "{} часов {} минут {} секунд".format(hours, minutes, seconds)

    def main_menu_format(self, message_text, update: Update, state):
        project = DB.get_project_by_id(state['p_id'])
        time = self.get_string_by_duration(float(DB.get_project_time(state['p_id'])['duration']))

        is_active = bool(project['active'])

        return message_text.format(
            project_name=project['name'],
            activity_name=DB.get_activity_by_id(state['a'])['name'],
            time=time,
            status="🟢 *Проект активен*" if is_active else "🔴 *Проект не активен*"
        )

    def is_activate_hidden(self, state, update):
        project = DB.get_project_by_id(state['p_id'])
        is_active = bool(project['active'])

        return is_active

    def is_stop_hidden(self, state, update):
        project = DB.get_project_by_id(state['p_id'])
        is_active = bool(project['active'])

        return not is_active

    def activate_project(self, update: Update, state):
        if update.callback_query is not None and update.callback_query.from_user.id != int(state['u_id']):
            update.callback_query.answer(text="Меню было вызвано другим пользователем.", show_alert=True)
            return False

        DB.activate_project(state['p_id'], state['u_id'], state['a'])

        return True

    def stop_project(self, update: Update, state):
        if update.callback_query is not None and update.callback_query.from_user.id != int(state['u_id']):
            update.callback_query.answer(text="Меню было вызвано другим пользователем.", show_alert=True)
            return False

        DB.stop_project(state['p_id'])

        return True

    def back(self, update: Update, state):
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

    def remove(self, update: Update, state):
        if update.callback_query is not None and update.callback_query.from_user.id != int(state['u_id']):
            update.callback_query.answer(text="Меню было вызвано другим пользователем.", show_alert=True)
            return False

        DB.remove_project(state['p_id'])

        self.projects[1].open_menu('0', {
            "u_id": state["u_id"],
            "a": state["a"],
            "p_id": "0",
            "page": "1"
        }, update)

        return False
