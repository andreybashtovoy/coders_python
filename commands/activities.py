from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import CommandHandler, CallbackContext, CallbackQueryHandler, Updater, MessageHandler, Filters
from data.database import DB
import datetime
from math import floor, ceil


class Activities:
    def __init__(self, updater: Updater):
        updater.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, self.on_message))
        updater.dispatcher.add_handler(CommandHandler('keyboard', self.send_keyboard_to_all))

    def get_keyboard_list_by_names(self, names):
        keyboard = list()
        i = 0

        for name in names:
            if i % 2 == 0:
                keyboard.append([KeyboardButton(text=name)])
            else:
                keyboard[i // 2].append(KeyboardButton(text=name))
            i += 1

        keyboard.insert(0, [
            KeyboardButton(text="⏯"),
            KeyboardButton(text="⏹"),
            KeyboardButton(text="🔄")
        ])

        return keyboard

    def send_keyboard_to_all(self, update: Update, context: CallbackContext):
        activity_names = DB.get_all_activity_names()

        names = []

        for activity in activity_names:
            if activity['id'] != 0:
                names.append(activity['name'])

        keyboard = self.get_keyboard_list_by_names(names)

        update.message.reply_text(text="ok",
                                  reply_markup=ReplyKeyboardMarkup(keyboard))

    def get_user_keyboard(self, user_id):
        activity_names = DB.get_all_activity_names()

        names = []

        counted = DB.count_user_activities(user_id)

        for obj in counted:
            names.append(obj['name'])

        for activity in activity_names:
            if activity['name'] not in names and activity['id'] != 0:
                names.append(activity['name'])

        keyboard = self.get_keyboard_list_by_names(names)

        return ReplyKeyboardMarkup(keyboard, selective=True)

    def get_string_by_duration(self, duration):
        hours = floor(duration) if duration > 0 else floor(duration)
        minutes = floor((duration % 1) * 60)
        seconds = floor((((duration % 1) * 60) % 1) * 60)

        return "{} часов {} минут {} секунд".format(hours, minutes, seconds)

    def on_message(self, update: Update, context: CallbackContext):
        activity_names = DB.get_all_activity_names()

        name = update.message.text

        names = [activity['name'] for activity in activity_names]

        if update.message.text == "⏹":
            name = activity_names[0]['name']

        if name in names:
            stopped_activity = self.start_activity(update.message.from_user.id, name)

            if stopped_activity is not None and stopped_activity['id'] != 0:
                update.message.reply_text(
                    text="✅ Занятие завершено ({})\n\n⏱ Продолжительность: {}.".format(
                        stopped_activity['name'],
                        self.get_string_by_duration(stopped_activity['duration'])
                    ),
                    parse_mode="Markdown"
                )

            if name != activity_names[0]['name']:
                update.message.reply_text(
                    text="🧾 Ты начал занятие \"{}\".".format(name),
                    reply_markup=self.get_user_keyboard(update.message.from_user.id))

    def start_activity(self, user_id, name):
        active_activity = DB.get_active_activity(user_id)

        stopped_activity = None
        
        duration = 0

        if active_activity is not None:
            data_now = datetime.datetime.now()
            data_start = datetime.datetime.strptime(active_activity['start_time'], '%Y-%m-%d %H:%M:%S')
            duration = (data_now - data_start).seconds / 3600

            stopped_activity = active_activity
            stopped_activity['duration'] = duration
        
        DB.start_activity(user_id, name, duration)
        
        return stopped_activity



