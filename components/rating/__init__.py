from components.menu import Menu
from telegram import Update
from telegram.ext import Updater
from data.database import DB
from data.ds import Data
import datetime
from math import floor, ceil

class Rating(Menu):
    def __init__(self, updater: Updater):
        super().__init__(updater, 'components/rating/rating.xml', 'rating')

    def __get_string(self, period, chat_id):
        rating = DB.get_rating(period, chat_id)

        users = {}

        data_now = datetime.datetime.now()

        for obj in rating:
            duration = obj['sum']
            if obj['challenge']:
                data_start = datetime.datetime.strptime(obj['current_start_time'], '%Y-%m-%d %H:%M:%S')
                diff = (data_now - data_start).seconds / 3600
                duration += diff
            users[obj['user_id']] = duration

        sorted_users = dict(sorted(users.items(), key=lambda item: item[1], reverse=True))

        string = ""

        for key in sorted_users:
            for obj in rating:
                if obj['user_id'] == key:
                    task_icon = "🟢" if obj['challenge'] else "🔴"

                    duration = sorted_users[key]

                    hours = floor(duration) if duration > 0 else ceil(duration)
                    minutes = floor((duration % 1) * 60)
                    seconds = floor((((duration % 1) * 60) % 1) * 60)

                    string = string + "{} *{}* _{} часов {} минут {} секунд_\n".format(task_icon,
                                                                                     obj['username'].replace("_", " "),
                                                                                     hours, minutes, seconds
                                                                                     )

        return string

    def all_time(self, text, update: Update, state):
        return text.format(self.__get_string("all_time", update.effective_chat.id))

    def month(self, text, update: Update, state):
        return text.format(self.__get_string("month", update.effective_chat.id))

    def week(self, text, update: Update, state):
        return text.format(self.__get_string("week", update.effective_chat.id))

    def day(self, text, update: Update, state):
        return text.format(self.__get_string("day", update.effective_chat.id))
