from telegram.ext import Updater, CallbackContext, CallbackQueryHandler, MessageHandler, Filters
from telegram import Update
import warnings
import json
from components.user_stats import UserStats
from components.rating import Rating
from components.add_time import AddTime
from components.start_activity import StartActivity
from components.projects import ProjectsSelectingActivity
from components.projects.projects import ProjectsOfActivity
from components.projects.separate_project import SeparateProject
from components.activities import Activities
from components.activities.separate_activity import SeparateActivity
from components.rating_graph import RatingGraph
from components.chat import Chat
from components.help import Help
from components.days import Days
from components.reset import Reset
from commands import CommandHandlers
from scheduler import Scheduler

import webserver

warnings.filterwarnings('ignore')

if __name__ == "__main__":
    f = open('bot_data.json')
    json_object = json.load(f)

    updater = Updater(json_object["token"])

    updater.bot.send_message(-1001243947001, "О связь есть")

    Scheduler(updater)

    projects = []

    separate_project = SeparateProject(updater, projects)
    projects.append(separate_project)
    projects_of_activity = ProjectsOfActivity(updater, projects)
    projects.append(projects_of_activity)
    selecting_activity = ProjectsSelectingActivity(updater, projects)
    projects.append(selecting_activity)

    start_activity = StartActivity(updater)

    activities = []

    activities_obj = Activities(updater, activities)
    activities.append(activities_obj)
    separate_activity = SeparateActivity(updater, activities)
    activities.append(separate_activity)

    menus = [UserStats(updater), RatingGraph(updater), Rating(updater), AddTime(updater),
             selecting_activity, activities_obj, Days(updater), Help(updater), Chat(updater), Reset(updater)
             ]


    def button_click_handler(update: Update, context: CallbackContext):
        if update.callback_query.message.text is not None:
            if "посмотреть проекты" in update.callback_query.message.text:
                selecting_activity.on_button_click(update, context)
                return

            if "🎲 Занятие:" in update.callback_query.message.text:
                separate_activity.on_button_click(update, context)
                return

            if "📁 Проект:" in update.callback_query.message.text:
                separate_project.on_button_click(update, context)
                return

            if "📂 Проекты занятия" in update.callback_query.message.text:
                projects_of_activity.on_button_click(update, context)
                return

            if "🧩 Твои личные занятия" in update.callback_query.message.text:
                activities[0].on_button_click(update, context)
                return

        if update.callback_query.message.reply_to_message.text.startswith("/start"):
            start_activity.on_button_click(update, context)
            return

        for menu in menus:
            if update.callback_query.message.reply_to_message.text.startswith("/" + menu.command):
                menu.on_button_click(update, context)
                return


    updater.dispatcher.add_handler(CallbackQueryHandler(button_click_handler))

    has_message_handler = [projects[1], activities[0]]


    def message_handler(update: Update, context: CallbackContext):
        for menu in has_message_handler:
            menu.on_message(update, context)


    updater.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, message_handler))

    CommandHandlers(updater)

    updater.start_polling()
    updater.idle()
    f.close()
