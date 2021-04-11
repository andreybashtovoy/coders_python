from components.menu import Menu
from telegram import Update, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackContext
from data.database import DB
import datetime
from math import ceil, floor


class StartProject(Menu):
    IN_PAGE = 4

    def __init__(self, updater: Updater, start_activity):
        super().__init__(updater, 'components/start_project/start_project.xml')
        updater.dispatcher.add_handler(CommandHandler('start_project', self.start))
        self.start_activity = start_activity

    def initial_state(self, update: Update):
        temp = update.message.text.split(" ")

        dur = "0"

        if len(temp) > 1 and temp[1].isdigit():
            dur = temp[1]

        return {
            "u_id": update.message.from_user.id,
            "page": "1",
            "dur": dur
        }

    def main_message_format(self, message_text, update: Update, state):
        delay = ""

        if int(state['dur']) != 0:
            delay = "\n\n\+%s минут" % state['dur']

        return message_text.format(
            delay
        )

    def start(self, update: Update, context: CallbackContext):

        temp = update.message.text.split(" ")

        if len(temp) > 1 and not temp[1].isdigit():
            project = DB.get_user_project_by_query(update.effective_user.id, temp[1])
            if project is not None:
                activity_name = DB.get_activity_by_id(project['activity_id'])['name']

                self.start_activity.start_activity(
                    update.effective_user.id,
                    activity_name,
                    update,
                    edit=False,
                    project=project
                )
                return

        self.send(update, context)

        DB.update_user_and_chat(update.message.from_user, update.effective_chat)

    def get_project_buttons(self, state, update: Update):

        def get_keyboard_by_projects(projects):
            keyboard = list()
            i = 0

            for project in projects:
                button = {
                    "name": project['name'],
                    #"action": "select_project",
                    "callback": str(project['id'])
                }

                if i % 2 == 0:
                    keyboard.append([button])
                else:
                    keyboard[i // 2].append(button)
                i += 1

            return keyboard

        all_user_projects = DB.get_user_projects(state['u_id'])

        projects = DB.get_last_projects(state['u_id'])

        for project in all_user_projects:
            temp = {
                'id': project['id'],
                'name': project['name']
            }

            if temp not in projects:
                projects.append(temp)

        i = self.IN_PAGE * (int(state['page']) - 1)

        return get_keyboard_by_projects(projects[i:i + 4])

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
        length = len(DB.get_user_projects(state['u_id'])) - 1

        page_count = ceil(length / self.IN_PAGE)

        if page_count <= int(state['page']):
            return True
        return False

    #def select_project(self, state, update: Update, name):
    #    activity = DB.get_activity_by_name(name)
    #    state['a'] = activity['id']
    #    return state

    def get_string_by_duration(self, duration):
        hours = floor(duration) if duration > 0 else ceil(duration)
        minutes = floor((abs(duration) % 1) * 60)
        seconds = floor((((abs(duration) % 1) * 60) % 1) * 60)

        return "{} часов {} минут {} секунд".format(hours, minutes, seconds)

    def action_custom_callback(self, update: Update, state, project_id):
        if update.callback_query is not None and update.callback_query.from_user.id != int(state['u_id']):
            update.callback_query.answer(text="Меню было вызвано другим пользователем.", show_alert=True)
            return False

        activity = DB.get_activity_by_project_id(project_id)
        project = DB.get_project_by_id(project_id)

        self.start_activity.start_activity(state['u_id'], activity['name'], update, delay=int(state['dur']), project=project)

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
