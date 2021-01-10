from components.menu import Menu
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
from data.database import DB
import datetime
from math import ceil, floor


class ProjectsOfActivity(Menu):
    IN_PAGE = 5

    def __init__(self, updater: Updater, projects):
        super().__init__(updater, 'components/projects/projects.xml')
        self.projects = projects
        updater.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, self.on_message))

    def main_menu_format(self, message_text, update: Update, state):
        activity = DB.get_activity_by_id(state['a'])

        return message_text.format(
            activity_name=activity['name']
        )

    def select_project(self, state, update: Update, name):
        project = DB.get_project_by_name(state['u_id'], name)
        state['p_id'] = project['id']
        return state

    def action_custom_callback(self, update: Update, state):
        if update.callback_query is not None and update.callback_query.from_user.id != int(state['u_id']):
            update.callback_query.answer(text="Меню было вызвано другим пользователем.", show_alert=True)
            return False

        self.projects[0].open_menu("0", {
            "u_id": state['u_id'],
            "a": state['a'],
            "p_id": state['p_id']
        }, update)

    def get_projects_buttons(self, state, update: Update):
        def get_keyboard_by_names(names):
            keyboard = list()

            for name in names:
                button = {
                    "name": name,
                    "action": "select_project",
                    "callback": True
                }

                keyboard.append([button])

            return keyboard

        projects = DB.get_user_projects_by_activity_id(state['u_id'], state['a'])

        names = [project['name'] for project in projects]

        i = self.IN_PAGE * (int(state['page']) - 1)

        return get_keyboard_by_names(names[i:i + 3])

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
        length = len(DB.get_user_projects_by_activity_id(state['u_id'], state['a']))

        page_count = ceil(length/self.IN_PAGE)

        if page_count <= int(state['page']):
            return True
        return False

    def create(self, update: Update, state):
        if update.callback_query is not None and update.callback_query.from_user.id != int(state['u_id']):
            update.callback_query.answer(text="Меню было вызвано другим пользователем.", show_alert=True)
            return False

        update.callback_query.message.edit_text(
            text="🖍 *Напиши название проекта*",
            parse_mode="Markdown"
        )

        DB.set_user_dialog_state(state['u_id'], "PROJECT_NAME %s" % state['a'])

        return False

    def back(self, update: Update, state):
        if update.callback_query is not None and update.callback_query.from_user.id != int(state['u_id']):
            update.callback_query.answer(text="Меню было вызвано другим пользователем.", show_alert=True)
            return False

        self.projects[2].open_menu('0', {
            "u_id": state["u_id"],
            "page": "1",
            "a": "0"
        }, update)

        return False

    def on_message(self, update: Update, context: CallbackContext):
        dialog_state = DB.get_user_dialog_state(update.message.from_user.id)

        if dialog_state is not None:
            if dialog_state['dialog_state'].startswith('PROJECT_NAME'):
                state = dialog_state['dialog_state'].split()

                if len(update.message.text) <= 50:
                    project = DB.create_project(dialog_state['user_id'], state[1], update.message.text)

                    # update.message.reply_text("☑️ *Ты создал проект* _%s_.\n\n"
                    #                           "*Запустить его можешь в меню* /projects" % update.message.text,
                    #                           parse_mode="Markdown")

                    DB.set_user_dialog_state(dialog_state['user_id'], "NONE")

                    self.projects[0].open_menu("0", {
                        "u_id": str(project['user_id']),
                        "a": str(project['activity_id']),
                        "p_id": str(project['id'])
                    }, update, context, send=True)
                else:
                    update.message.reply_text("Название проектов не должно быть длиннее 50-ти символов.")
