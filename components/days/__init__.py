from components.menu import Menu
from telegram import Update
from telegram.ext import Updater
from data.database import DB
from math import floor, ceil
from datetime import datetime, timedelta


class Days(Menu):
    def __init__(self, updater: Updater):
        super().__init__(updater, 'components/days/days.xml', 'days')

    def initial_state(self, update: Update):
        return {
            "u_id": update.message.from_user.id,
            "day": "0"
        }

    def get_string_by_duration(self, duration):
        hours = floor(duration) if duration > 0 else ceil(duration)
        minutes = floor((abs(duration) % 1) * 60)

        return "{} часов {} минут".format(hours, minutes)

    def text_format(self, message_text, update: Update, state):
        now = datetime.now()
        day = now - timedelta(days=abs(int(state['day'])))

        day_activities = DB.get_user_activities_by_day(state['u_id'], state['day'])

        string = ""

        sum_duration = 0

        for activity in day_activities:
            project_str = ""
            if activity['project_name'] is not None:
                pr_name = activity['project_name'].replace("_", "\_")
                pr_name = pr_name.replace("(", "\(")
                pr_name = pr_name.replace(")", "\)")
                pr_name = pr_name.replace(".", "\.")
                pr_name = pr_name.replace("-", "\-")

                project_str = "(%s)" % pr_name

            duration = activity['sum']

            if duration == 0:
                start = datetime.strptime(activity['start_time'], '%Y-%m-%d %H:%M:%S')
                duration = (now - start).seconds / 3600

            if activity['challenge']:
                sum_duration += duration

            ac_name = activity['activity_name'].replace("_", "\_")
            # ac_name = ac_name.replace("(", "\(")
            # ac_name = ac_name.replace(")", "\)")
            # ac_name = ac_name.replace("-", "\-")
            # ac_name = ac_name.replace(".", "\.")

            string += "*%s*: _%s_ %s\n" %\
                      (ac_name, self.get_string_by_duration(duration), project_str)

        return message_text.format(
            day=day.strftime('%d.%m.%Y'),
            stats=string,
            time="_%s_" % self.get_string_by_duration(sum_duration)
        )

    def is_prev_hidden(self, state, update: Update):
        return False

    def is_next_hidden(self, state, update: Update):
        return int(state['day']) >= 0

    def next_page(self, state, update: Update):
        state['day'] = int(state['day']) + 1
        return state

    def prev_page(self, state, update: Update):
        state['day'] = int(state['day']) - 1
        return state
