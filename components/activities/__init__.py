from components.menu import Menu
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
from data.database import DB
import datetime
from math import ceil, floor


class Activities(Menu):
    IN_PAGE = 4

    def __init__(self, updater: Updater, activities):
        super().__init__(updater, 'components/activities/activities.xml', 'activities')
        self.activities = activities

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

        activity_names = DB.get_user_personal_activities(state['u_id'])

        names = []

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
        length = len(DB.get_user_personal_activities(state['u_id']))

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

        self.activities[1].open_menu('0', {
            "u_id": state["u_id"],
            "a": state["a"]
        }, update)

        return False

    def create(self, update: Update, state):
        if update.callback_query is not None and update.callback_query.from_user.id != int(state['u_id']):
            update.callback_query.answer(text="Меню было вызвано другим пользователем.", show_alert=True)
            return False

        update.callback_query.message.edit_text(
            text="🖍 *Напиши название занятия*",
            parse_mode="Markdown"
        )

        DB.set_user_dialog_state(state['u_id'], "ACTIVITY_NAME")

        return False

    def on_message(self, update: Update, context: CallbackContext):
        dialog_state = DB.get_user_dialog_state(update.message.from_user.id)

        if dialog_state is not None:
            if dialog_state['dialog_state'].startswith('ACTIVITY_NAME'):

                if len(update.message.text) <= 50:
                    activity = DB.create_activity(dialog_state['user_id'], update.message.text)

                    # update.message.reply_text("☑️ *Ты создал занятие* _%s_.\n\n"
                    #                           "*Настроить его можешь в меню* /activities" % update.message.text,
                    #                           parse_mode="Markdown")

                    DB.set_user_dialog_state(dialog_state['user_id'], "NONE")

                    self.activities[1].open_menu("0", {
                        "u_id": str(activity['owner']),
                        "a": str(activity['id'])
                    }, update, context, send=True)
                else:
                    update.message.reply_text("Название занятия не должно быть длиннее 50-ти символов.")
