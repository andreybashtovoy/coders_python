import schedule
import time
import threading
from telegram.ext import Updater, CommandHandler
from data.database import DB
import datetime
from math import floor, ceil
from telegram.error import Unauthorized


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
        chats = DB.get_all_chats()

        for chat in chats:

            active_users = DB.get_chat_active_users(chat['chat_id'])

            if len(active_users) > 0:

                endings = ["ов", "", "а", "а", "а", "ов", "ов", "ов", "ов", "ов"]

                string = "🟢 *{} участник{} чата сейчас онлайн:*\n\n".format(len(active_users),
                                                                             endings[len(active_users) % 10])
                data_now = datetime.datetime.now()

                all_ranks = DB.get_all_ranks()

                for user in active_users:
                    data_start = datetime.datetime.strptime(user['start_time'], '%Y-%m-%d %H:%M:%S')
                    duration = (data_now - data_start).seconds / 3600

                    if user['username'] != "None":

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

                    hours = DB._get_user_useful_time(user['user_id'], 'all')['time']

                    rank = all_ranks[0]['name']

                    for obj in all_ranks:
                        if obj['min_hours'] <= hours:
                            rank = obj['name']
                        else:
                            break

                    string += "🔸{} \[`{}`\] \- *{}* \(_{}_\)\n".format(username, rank, user['name'],
                                                               self.get_string_by_duration(duration))

                string += "\n`Выключить/включить теги \- ` /toggle\_tag"

                try:

                    self.updater.bot.send_message(
                        chat_id=chat['chat_id'],
                        #chat_id=-1001243947001,
                        text=string,
                        parse_mode="MarkdownV2"
                    )

                except Exception as e:
                    print(e.message)

    def tag_all(self):

        chats = DB.get_all_chats()

        for chat in chats:
            users = DB.get_chat_users(chat['chat_id'])
            all_ranks = DB.get_all_ranks()

            durations = dict()
            ranks = dict()

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

                if user['username'] != "None":
                    username = ("@" + user['username'].replace("_", "\_"))
                    username = username.replace(".", "\.")
                else:
                    username = "[{}](tg://user?id={})".format(user['user_id'], user['user_id'])

                durations[username] = duration

                hours = DB._get_user_useful_time(user['user_id'], 'all')['time']

                rank = all_ranks[0]['name']

                for obj in all_ranks:
                    if obj['min_hours'] <= hours:
                        rank = obj['name']
                    else:
                        break

                ranks[username] = rank

            durations = dict(sorted(durations.items(), key=lambda item: item[1], reverse=True))

            string = "🧮 *Итоги дня*\n\n"

            i = 0

            emoji = ['🔹', '🔸']

            for name in durations:
                string += "%s%s \- _%s_ \(Звание *%s*\)\n" % (emoji[i % 2],
                                                                                name,
                                                                               self.get_string_by_duration(durations[name]),
                                                                               ranks[name])
                i+=1

            try:

                self.updater.bot.send_message(
                    chat_id=chat['chat_id'],
                    text=string,
                    parse_mode="MarkdownV2"
                )

            except Exception as e:
                print(e.message)
