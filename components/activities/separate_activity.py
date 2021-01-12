from components.menu import Menu
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
from data.database import DB
import datetime
from math import ceil, floor


class SeparateActivity(Menu):

    def __init__(self, updater: Updater, activities):
        super().__init__(updater, 'components/activities/separate_activity.xml')
        self.activities = activities

    def main_menu_format(self, message_text, update: Update, state):
        return message_text.format(
            activity_name=DB.get_activity_by_id(state['a'])['name']
        )

    def is_access_for_me_hidden(self, state, update):
        activity = DB.get_activity_by_id(state['a'])

        return activity['access'] != 1

    def is_access_for_chat_hidden(self, state, update):
        activity = DB.get_activity_by_id(state['a'])

        return activity['access'] != 2

    def is_with_benefit_hidden(self, state, update):
        activity = DB.get_activity_by_id(state['a'])

        return not bool(activity['challenge'])

    def is_without_benefit_hidden(self, state, update):
        activity = DB.get_activity_by_id(state['a'])

        return bool(activity['challenge'])

    def set_access_for_chat(self, update: Update, state):
        DB.set_activity_access(state['a'], 2)
        return True

    def set_access_for_me(self, update: Update, state):
        DB.set_activity_access(state['a'], 1)
        return True

    def set_without_benefit(self, update: Update, state):
        DB.set_activity_challenge(state['a'], 0)
        return True

    def set_with_benefit(self, update: Update, state):
        DB.set_activity_challenge(state['a'], 1)
        return True

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

        self.activities[0].open_menu('0', {
            "u_id": state["u_id"],
            "a": "0",
            "page": "1"
        }, update)

        return False

    def remove(self, update: Update, state):
        if update.callback_query is not None and update.callback_query.from_user.id != int(state['u_id']):
            update.callback_query.answer(text="Меню было вызвано другим пользователем.", show_alert=True)
            return False

        DB.remove_activity(state['a'])

        self.activities[0].open_menu('0', {
            "u_id": state["u_id"],
            "a": "0",
            "page": "1"
        }, update)

        return False
