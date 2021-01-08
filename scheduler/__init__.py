import schedule
import time
import threading
from telegram.ext import Updater, CommandHandler
from data.database import DB
import datetime
from math import floor, ceil


class Scheduler:
    def __init__(self, updater: Updater):
        self.updater = updater

        schedule.every().hour.at(":00").do(self.tag_active)
        schedule.every().day.at("23:55").do(self.tag_all)

        #updater.dispatcher.add_handler(CommandHandler('test', self.tag_active))

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

    def tag_active(self, *args, **afqwe):
        active_users = DB.get_active_users()

        if len(active_users) > 0:

            endings = ["ов", "", "а", "а", "а", "ов", "ов", "ов", "ов", "ов"]

            string = "🟢 *{} участник{} чата сейчас онлайн:*\n\n".format(len(active_users),
                                                                         endings[len(active_users) % 10])
            data_now = datetime.datetime.now()

            all_ranks = DB.get_all_ranks()

            for user in active_users:
                data_start = datetime.datetime.strptime(user['start_time'], '%Y-%m-%d %H:%M:%S')
                duration = (data_now - data_start).seconds / 3600

                if user['username'] != "":

                    if user['tag']:
                        username = ("@" + user['username'].replace("_", "\_"))
                        username = username.replace(".", "\.")
                    else:
                        username = ("`" + user['username'].replace("_", "\_") + "`")
                else:
                    if user['tag']:
                        username = "[{}](tg://user?id={})".format(user['user_id'], user['user_id'])
                    else:
                        username = str(user['user_id'])

                rank = all_ranks[0]['name']

                for obj in all_ranks:
                    if obj['min_days'] <= user['day']:
                        rank = obj['name']
                    else:
                        break

                string += "🔸{} \[`{}`\] \- *{}* \(_{}_\)\n".format(username, rank, user['name'],
                                                           self.get_string_by_duration(duration))

            string += "\n`Не тегать меня - ` /disable\_tag"

            self.updater.bot.send_message(
                chat_id=-1001156172516,
                #chat_id=-1001243947001,
                text=string,
                parse_mode="MarkdownV2"
            )

    def tag_all(self):
        users = DB.get_all_users()
        all_ranks = DB.get_all_ranks()

        durations = dict()
        ranks = dict()
        days = dict()

        for user in users:
            obj = DB.get_today_user_useful_time(user['user_id'])

            now = datetime.datetime.now()

            if obj['time'] is not None:
                duration = float(obj['time'])

                if obj['start_time'] is not None:
                    data_start = datetime.datetime.strptime(obj['start_time'], '%Y-%m-%d %H:%M:%S')

                    diff = (now - data_start).seconds / 3600
                    duration = duration + diff
            else:
                duration = 0

            if user['username'] != "":
                username = ("@" + user['username'].replace("_", "\_"))
                username = username.replace(".", "\.")
            else:
                username = "[{}](tg://user?id={})".format(user['user_id'], user['user_id'])

            durations[username] = duration

            if duration >= 2:
                day = int(user['day']) + 1
            else:
                day = 0

            DB.set_user_day(user['user_id'], day)

            days[username] = day

            rank = all_ranks[0]['name']

            for obj in all_ranks:
                if obj['min_days'] <= day:
                    rank = obj['name']
                else:
                    break

            ranks[username] = rank

        durations = dict(sorted(durations.items(), key=lambda item: item[1], reverse=True))

        string = "🧮 *Итоги дня*\n\n"

        i = 0

        emoji = ['🔹', '🔸']

        for name in durations:
            string += "%s%s \- _%s_ \(*%d* дней подряд, звание *%s*\)\n" % (emoji[i % 2],
                                                                            name,
                                                                           self.get_string_by_duration(durations[name]),
                                                                           days[name],
                                                                           ranks[name])
            i+=1

        self.updater.bot.send_message(
            chat_id=-1001156172516,
            text=string,
            parse_mode="MarkdownV2"
        )
