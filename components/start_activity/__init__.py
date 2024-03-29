from components.menu import Menu
from telegram import Update, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackContext
from data.database import DB
import datetime
from math import ceil, floor


class StartActivity(Menu):
    IN_PAGE = 4

    def __init__(self, updater: Updater):
        super().__init__(updater, 'components/start_activity/start_activity.xml')
        updater.dispatcher.add_handler(CommandHandler('stop', self.stop))
        updater.dispatcher.add_handler(CommandHandler('start', self.start))
        updater.dispatcher.add_handler(CommandHandler('s', self.start))

    def initial_state(self, update: Update):
        temp = update.message.text.split(" ")

        dur = "0"
        q = ""

        if len(temp) > 1:
            if temp[1].isdigit():
                dur = temp[1]
            else:
                q = temp[1]

        return {
            "u_id": update.message.from_user.id,
            "page": "1",
            "a": "0",
            "dur": dur,
            "q": q
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
            activities = DB.get_user_activity_by_query(update.effective_user.id, update.effective_chat.id, temp[1])
            if len(activities) == 1:
                activity_name = activities[0]['name']

                self.start_activity(
                    update.effective_user.id,
                    activity_name,
                    update,
                    edit=False
                )
                return

        chat = DB.get_chat_by_id(update.effective_chat.id)

        if chat is None:
            keyboard = [
                [
                    KeyboardButton(text="/help"),
                    KeyboardButton(text="/start")
                ]
            ]

            markup = ReplyKeyboardMarkup(
                keyboard=keyboard,
                one_time_keyboard=True,
                resize_keyboard=True
            )

            update.message.reply_text(
                text="👋 *Привет!*\n\n"
                     "Я помогу тебе контролировать все твои занятия в течении дня и "
                     "существенно улучшить твою продуктивность.\n\n"
                     "📄 *Как пользоваться ботом* - /help\n"
                     "▶️ *Выбрать и начать занятие* - /start",
                parse_mode="Markdown"
            )

            # update.message.reply_text(
            #     text="🌟 Поздравляю! Для этого чата было начислено *30 дней* бесплатного *Premium*.\n\n"
            #          "_Узнать возможности Premium и продлить его можно в меню_ /chat",
            #     parse_mode="Markdown"
            # )
        else:
            self.send(update, context)

        DB.update_user_and_chat(update.message.from_user, update.effective_chat)

    def get_activity_buttons(self, state, update: Update):

        def get_keyboard_by_names(names):
            keyboard = list()
            i = 0

            for name in names:
                button = {
                    "name": name,
                    "action": "select_activity",
                    "callback": True
                }

                if i % 2 == 0:
                    keyboard.append([button])
                else:
                    keyboard[i // 2].append(button)
                i += 1

            return keyboard

        if state['q'] == "":
            activity_names = DB.get_user_accessible_activities(state['u_id'], update.effective_chat.id)

            names = []

            counted = DB.get_last_activities(state['u_id'])

            for obj in counted:
                if obj['name'] in [x['name'] for x in activity_names]:
                    names.append(obj['name'])

            for activity in activity_names:
                if activity['name'] not in names and activity['id'] != 0:
                    names.append(activity['name'])
        else:
            names = [obj['name'] for obj in
                     DB.get_user_activity_by_query(update.effective_user.id, update.effective_chat.id, state['q'])]

            if 'Ничего' in names:
                names.remove('Ничего')

        i = self.IN_PAGE * (int(state['page']) - 1)

        return get_keyboard_by_names(names[i:i + 4])

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
        if state['q'] == "":
            length = len(DB.get_user_accessible_activities(state['u_id'], update.effective_chat.id)) - 1
        else:
            names = [obj['name'] for obj in
                     DB.get_user_activity_by_query(update.effective_user.id, update.effective_chat.id, state['q'])]

            if 'Ничего' in names:
                names.remove('Ничего')

            length = len(names)

        page_count = ceil(length / self.IN_PAGE)

        if page_count <= int(state['page']):
            return True
        return False

    def select_activity(self, state, update: Update, name):
        activity = DB.get_activity_by_name(name)
        state['a'] = activity['id']
        return state

    def get_string_by_duration(self, duration):
        hours = floor(duration) if duration > 0 else ceil(duration)
        minutes = floor((abs(duration) % 1) * 60)
        seconds = floor((((abs(duration) % 1) * 60) % 1) * 60)

        return "{} часов {} минут {} секунд".format(hours, minutes, seconds)

    def stop(self, update: Update, context: CallbackContext):
        msg = update.message.text.split()

        if len(msg) > 1:
            if len(msg) > 1 and msg[1].isnumeric() and 0 < int(msg[1]) < 1000:
                self.start_activity(update.message.from_user.id, "Ничего", update, penalty=int(msg[1]), edit=False)
            else:
                update.message.reply_text(
                    "Штраф должен быть в промежутке от 0 до 1000 минут.",
                    parse_mode="Markdown")
        else:
            self.start_activity(update.message.from_user.id, "Ничего", update, edit=False)

    def start_activity(self, user_id, name, update: Update, penalty=0, edit=True, delay=0, project=None):
        active_activity = DB.get_active_activity(user_id)

        stopped_activity = None

        duration = 0

        if active_activity is not None:
            data_now = datetime.datetime.now()
            data_start = datetime.datetime.strptime(active_activity['start_time'], '%Y-%m-%d %H:%M:%S')
            duration = (data_now - data_start).seconds / 3600 - penalty / 60

            stopped_activity = active_activity
            stopped_activity['duration'] = duration

        if project is None:
            project = DB.get_active_project(user_id, name)

        if project is not None:
            DB.start_activity(user_id, name, duration, project['id'], update.effective_chat.id, delay)
        else:
            DB.start_activity(user_id, name, duration, None, update.effective_chat.id, delay)

        if stopped_activity is not None and stopped_activity['activity_id'] != 0:
            if edit and update:
                func = update.callback_query.message.reply_to_message.reply_text
            else:
                func = update.message.reply_text

            ac_name = stopped_activity['name'].replace("_", "\_")
            ac_name = ac_name.replace("(", "\(")
            ac_name = ac_name.replace(")", "\)")
            ac_name = ac_name.replace("-", "\-")
            ac_name = ac_name.replace(".", "\.")

            project_string = ""

            if stopped_activity['project_id'] is not None:
                stopped_project = DB.get_project_by_id(stopped_activity['project_id'])

                pr_name = stopped_project['name'].replace("_", "\_")
                pr_name = pr_name.replace("(", "\(")
                pr_name = pr_name.replace(")", "\)")
                pr_name = pr_name.replace(".", "\.")
                pr_name = pr_name.replace("-", "\-")

                project_string = "📂 *Проект:* _%s_\n" % pr_name

            day_activities = DB.get_user_activities_by_day(user_id, 0)

            sum_duration = 0

            for activity in day_activities:
                if activity['activity_id'] == stopped_activity['activity_id']:
                    if any(
                            [stopped_activity['project_id'] is None,
                             stopped_activity['project_id'] == activity['project_id']]
                    ):
                        sum_duration += activity['sum']

            func(
                text="✅ Занятие завершено \({}\)\n{}\n⏱ Продолжительность: {}\.\n😎 Всего за сутки: {}\.".format(
                    ac_name,
                    project_string,
                    self.get_string_by_duration(stopped_activity['duration']),
                    self.get_string_by_duration(sum_duration),
                ),
                parse_mode="MarkdownV2"
            )

        if name != "Ничего":
            string = ""

            if project is not None:
                pr_name = project['name'].replace("_", "\_")
                pr_name = pr_name.replace("(", "\(")
                pr_name = pr_name.replace(")", "\)")
                pr_name = pr_name.replace(".", "\.")
                pr_name = pr_name.replace("-", "\-")

                string = "\n📂 *Проект:* _%s_" % pr_name

            ac_name = name.replace("_", "\_")
            ac_name = ac_name.replace("(", "\(")
            ac_name = ac_name.replace(")", "\)")
            ac_name = ac_name.replace("-", "\-")
            ac_name = ac_name.replace(".", "\.")

            delay_str = ""

            if delay > 0:
                delay_str = "\n\n⏱ \+%s мин\." % delay

            text = "🧾 Ты начал занятие \"{}\"\.{}{}\n\n⏹ Остановить: /stop".format(ac_name, string, delay_str)

            if update.callback_query is not None:
                update.callback_query.message.edit_text(
                    text=text,
                    parse_mode="MarkdownV2"
                )
            else:
                update.effective_message.reply_text(
                    text=text,
                    parse_mode="MarkdownV2"
                )

    def action_custom_callback(self, update: Update, state):
        if update.callback_query is not None and update.callback_query.from_user.id != int(state['u_id']):
            update.callback_query.answer(text="Меню было вызвано другим пользователем.", show_alert=True)
            return False

        name = DB.get_activity_by_id(int(state['a']))['name']

        self.start_activity(state['u_id'], name, update, delay=int(state['dur']))

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
