from components.menu import Menu
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from data.database import DB
from data.ds import Data
import datetime
from math import floor, ceil

class RatingGraph(Menu):
    def __init__(self, updater: Updater):
        super().__init__(updater, 'components/rating_graph/rating_graph.xml')
        updater.dispatcher.add_handler(CommandHandler('rating_graph', self.open))
        self.command = 'rating_graph'

    def open(self, update: Update, context: CallbackContext):
        if DB.has_chat_activities(update.effective_chat.id):
            self.send(update, context)
        else:
            update.message.reply_text(
                text="Чтобы получить график изменения рейтинга участников чата по времени с пользой, необходимо, "
                     "чтобы хотя бы один участник запустил *полезное* занятие командой /start"
                     " и завершил командой /stop. Также чат должен существовать не менее одного дня.\n\n"
                     "Посмотреть текущий рейтинг участников чата можно командой /rating.",
                parse_mode="Markdown"
            )

    def initial_state(self, update: Update):
        active_days = DB.get_chat_active_days(update.effective_chat.id)
        members_count = len(DB.get_chat_users(update.effective_chat.id))

        return {
            "members": members_count if members_count < 7 else 7,
            "days": active_days,
            "md": active_days,
            "mm": members_count
        }

    def text_format(self, message_text, update: Update, state):
        endings = ["ов", "", "а", "а", "а", "ов", "ов", "ов", "ов", "ов"]
        return message_text.format(
            members_count=state['members'],
            days=state['days'],
            ending=endings[int(state['days']) % 10]
        )

    def add_days(self, days, state, update: Update):
        state["days"] = int(state["days"]) + days

        return state

    def minus_1_day(self, state, update: Update):
        return self.add_days(-1, state, update)

    def minus_5_days(self, state, update: Update):
        return self.add_days(-5, state, update)

    def plus_1_day(self, state, update: Update):
        return self.add_days(1, state, update)

    def plus_5_days(self, state, update: Update):
        return self.add_days(5, state, update)

    def add_members(self, members, state, update: Update):
        state["members"] = int(state["members"]) + members

        return state

    def plus_1_member(self, state, update: Update):
        return self.add_members(1, state, update)

    def minus_1_member(self, state, update: Update):
        return self.add_members(-1, state, update)

    def is_minus_5_hidden(self, state, update: Update):
        if int(state['days']) <= 7:
            return True
        return False

    def is_minus_1_hidden(self, state, update: Update):
        if int(state['days']) <= 2:
            return True
        return False

    def is_plus_5_hidden(self, state, update: Update):
        if int(state['md']) - int(state['days']) < 5:
            return True
        return False

    def is_plus_1_hidden(self, state, update: Update):
        if int(state['md']) - int(state['days']) < 1:
            return True
        return False

    def is_minus_1_member_hidden(self, state, update: Update):
        if int(state['members']) <= 1:
            return True
        return False

    def is_plus_1_member_hidden(self, state, update: Update):
        if int(state['members']) >= int(state['mm']):
            return True
        return False
