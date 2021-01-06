import schedule
import time
import threading
from telegram.ext import Updater
from data.database import DB
import datetime
from math import floor, ceil


class Scheduler:
    def __init__(self, updater: Updater):
        self.updater = updater

        schedule.every().hour.at(":00").do(self.tag_active)

        x = threading.Thread(target=self.pending, args=(1,))
        x.start()

    def pending(self, *args, **cargs):
        while True:
            schedule.run_pending()
            time.sleep(1)

    def get_string_by_duration(self, duration):
        hours = floor(duration) if duration > 0 else ceil(duration)
        minutes = floor((abs(duration) % 1) * 60)
        seconds = floor((((abs(duration) % 1) * 60) % 1) * 60)

        return "{} часов {} минут {} секунд".format(hours, minutes, seconds)

    def tag_active(self):
        active_users = DB.get_active_users()

        if len(active_users) > 0:

            endings = ["ов", "", "а", "а", "а", "ов", "ов", "ов", "ов", "ов"]

            string = "🟢 *{} участник{} чата сейчас онлайн:*\n\n".format(len(active_users),
                                                                        endings[len(active_users) % 10])
            data_now = datetime.datetime.now()

            for user in active_users:
                data_start = datetime.datetime.strptime(user['start_time'], '%Y-%m-%d %H:%M:%S')
                duration = (data_now - data_start).seconds / 3600

                string += "🔸@{} \- *{}* \(_{}_\)\n".format(user['username'].replace("_", "\_"), user['name'],
                                                            self.get_string_by_duration(duration))

            self.updater.bot.send_message(
                chat_id=-1001156172516,
                text=string,
                parse_mode="MarkdownV2"
            )
