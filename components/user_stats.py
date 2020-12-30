from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackContext, CallbackQueryHandler, Updater
from data.ds import Data
from data.database import DB
from components.separated_stats import SeparatedStats
import os


class UserStats:
    def __init__(self, updater: Updater):
        updater.dispatcher.add_handler(CommandHandler('stats', self.stats))
        updater.dispatcher.add_handler(CommandHandler('test', self.hello))
        updater.dispatcher.add_handler(CommandHandler('get_chat_id', self.get_chat_id))
        updater.dispatcher.add_handler(CommandHandler('restart', self.restart))
        updater.dispatcher.add_handler(CallbackQueryHandler(self.on_button_click))
        self.__updater = updater
        self.__separated_stats = SeparatedStats(updater)

    def get_message_text(self, user):
        active_task = DB.get_active_task_user(user[0])
        task_icon = "🟢" if active_task[1] else "🔴"

        return("*📊 Статистика пользователя* _"+user[3].replace("_"," ")+"_\n\n" +
                                  task_icon +" У пользователя активно занятие \"_" + active_task[0] + "_\" (" + active_task[2] + ")\n\n" +
                                  "⏱ *Время с пользой*\n" +
                                  "За сегодня: " + DB.get_user_useful_time_today(user[0]) + "\n" +
                                  "За неделю: " + DB.get_user_useful_time_week(user[0]) + "\n" +
                                  "За месяц: " + DB.get_user_useful_time_month(user[0]) + "\n" +
                                  "За все время: " + DB.get_user_useful_time_all(user[0]) + "\n")

    def get_message_keyboard(self, user_id):
        keyboard = [
            [
                InlineKeyboardButton("📅 Полезное время по дням", callback_data="all_tasks_by_days " + str(user_id))
            ],
            [
                InlineKeyboardButton("🧩 Статистика всем занятиям", callback_data="🔴ф")
            ],
            [
                InlineKeyboardButton("🛌 Стастика сна", callback_data="sleep "+str(user_id))
            ],
            [
                InlineKeyboardButton("🤹‍♂️ Статистика по каждому занятию отдельно", callback_data="separated_stats")
            ],
            [
                InlineKeyboardButton("🔄 Обновить", callback_data="update_message " + str(user_id))
            ]
        ]

        return InlineKeyboardMarkup(keyboard)

    def stats(self, update: Update, context: CallbackContext) -> None:

        if update.message.reply_to_message is None:
            text = update.message.text.split()
            if len(text) > 1 and text[1][0] == '@':
                user_data = DB.get_by_username(text[1][1:])
                if user_data is None:
                    return
            else:
                user_data = DB.get_by_username(update.message.from_user.username)

                if user_data is None:
                    return
        else:
            print(update.message.reply_to_message.from_user.username)
            user_data = DB.get_by_username(update.message.reply_to_message.from_user.username)
            print(user_data)
            if user_data is None:
                return
        DB.get_user_useful_time(user_data['user_id'], 'week')
        update.message.reply_text(text=self.get_message_text(user_data),
                                  parse_mode="Markdown",
                                  reply_markup=self.get_message_keyboard(user_data['user_id']))

    def sleep_stats(self, update: Update, context: CallbackContext, user_id):
        user_data = DB.get_user_by_id(user_id)

        text = "🛌 *Статистика сна пользователя* "+user_data[3].replace("_"," ")+"\n\n" \
               "⏱ Средняя продолжительность _9 часов 5 минут ± 1 часов 3 минут_\n" \
               "🧿 Среднее время подъема: _9:43 ± 0 часов 14 минут_\n" \
               "💤 Среднее время начала сна: _00:15 +- 1 часов 38 минут_"

        keyboard = [
            [
                InlineKeyboardButton("🧮 Распределение продолжительности сна", callback_data="sleep_dist " + str(user_id))
            ],
            [
                InlineKeyboardButton("📊 Продолжительность сна по дням",
                                     callback_data="sleep_bar " + str(user_id))
            ],
            [
                InlineKeyboardButton("◀️ Назад", callback_data="update_message " + str(user_id))
            ]
        ]


        update.callback_query.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    def resend_main_message(self, update: Update, context: CallbackContext, user_id):
        user_data = DB.get_user_by_id(user_id)
        context.bot.send_message(
            text=self.get_message_text(user_data),
            chat_id=update.effective_chat.id,
            reply_to_message_id=update.callback_query.message.reply_to_message.message_id,
            reply_markup=self.get_message_keyboard(user_id),
            parse_mode="Markdown"
        )
        update.callback_query.message.delete()

    def update_main_message(self, update: Update, context: CallbackContext, user_id):
        user_data = DB.get_user_by_id(user_id)
        update.callback_query.edit_message_text(
            text=self.get_message_text(user_data),
            reply_markup=self.get_message_keyboard(user_id),
            parse_mode="Markdown"
        )

    def hello(self, update: Update, context: CallbackContext) -> None:
        #context.bot.send_photo(update.effective_chat.id, Data.plot_sleep(update.effective_user.id))
        context.bot.send_photo(update.effective_chat.id, Data.plot_time_with_benefit(update.effective_user.id))

    def get_chat_id(self, update: Update, context: CallbackContext) -> None:
        update.message.reply_text(update.effective_chat.id)

    def edit_message_with_plot(self, update: Update, context: CallbackContext, user_id, plot):
        keyboard = [
            [
                InlineKeyboardButton("◀️ Назад", callback_data="back_to_main " + str(user_id))
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_photo(
            chat_id=update.effective_chat.id,
            reply_to_message_id=update.callback_query.message.reply_to_message.message_id,
            photo=plot,
            reply_markup=reply_markup
        )

        update.callback_query.message.delete()

    def on_button_click(self, update: Update, context):
        query = update.callback_query

        if query.data == "🔴":
            context.bot.send_dice(update.effective_chat.id)

        elif query.data == 'separated_stats':
            self.__separated_stats.show_separated_stats(update)

        elif query.data.startswith('all_tasks_by_days'):
            user_id = int(query.data.split()[1])
            self.edit_message_with_plot(update, context, user_id, Data.plot_time_with_benefit(user_id))

        elif query.data.startswith('back_to_main'):
            user_id = int(query.data.split()[1])
            self.resend_main_message(update, context, user_id)

        elif query.data.startswith('update_message'):
            user_id = int(query.data.split()[1])
            self.update_main_message(update, context, user_id)

        elif query.data.startswith('sleep'):
            user_id = int(query.data.split()[1])
            self.sleep_stats(update, context, user_id)

    # query.delete_message()

    def restart(self, update: Update, context):
        update.message.reply_text("До связи")
        os._exit(0)