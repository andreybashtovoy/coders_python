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
from commands import CommandHandlers
from commands.activities import Activities
from scheduler import Scheduler

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

    menus = [UserStats(updater), Rating(updater), AddTime(updater), selecting_activity
             ]


    def button_click_handler(update: Update, context: CallbackContext):
        if "📁 Проект:" in update.callback_query.message.text:
            separate_project.on_button_click(update, context)
            return

        if "📂" in update.callback_query.message.text:
            projects_of_activity.on_button_click(update, context)
            return

        if update.callback_query.message.reply_to_message.text.startswith("/start"):
            start_activity.on_button_click(update, context)
            return

        for menu in menus:
            if update.callback_query.message.reply_to_message.text.startswith("/" + menu.command):
                menu.on_button_click(update, context)
                return


    updater.dispatcher.add_handler(CallbackQueryHandler(button_click_handler))

    has_message_handler = [projects[1]]


    def message_handler(update: Update, context: CallbackContext):
        for menu in has_message_handler:
            menu.on_message(update, context)


    updater.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, message_handler))

    CommandHandlers(updater)

    updater.start_polling()
    updater.idle()
    f.close()
