from telegram import InlineKeyboardButton, Update, CallbackQuery, InlineKeyboardMarkup
from telegram.ext import CallbackContext, Updater, CallbackQueryHandler
from data.database import DB
import components.user_stats


# keyboard pattern with calllback_data that represents id
# keyboard = [
#     [
#         InlineKeyboardButton('Sport', callback_data='test1')
#     ],
#     [
#         InlineKeyboardButton('Code', callback_data='test2')
#     ],
#     [
#         InlineKeyboardButton('Music', callback_data='test3')
#     ]
# ]
class SeparatedStats:
    def __init__(self, updater: Updater):
        self.__updater = updater
        #updater.dispatcher.add_handler(CallbackQueryHandler(self.on_page_button_click))

    # shows multiple buttons to look at detailed information about tasks
    def show_separated_stats(self, update: Update) -> None:

        button_quantity = 3
        activity_names = list()
        for item in DB.get_all_activities():
            activity_names.append(item[2])

        keyboard = list()
        for name in activity_names:
            keyboard.append([InlineKeyboardButton(name, callback_data=str(activity_names.index(name)))])

        page_keyboard = list()
        keyboard.append([InlineKeyboardButton('<-', callback_data='to_page -1'),
                         InlineKeyboardButton('->', callback_data='to_page 1')])
        query = update.callback_query

        update.callback_query.edit_message_text(
            "📝 *Статистика занятий по отдельности*\n\n"
            "⚡️Ваше самое времязатратное занятие - \"Спорт\"\n\n"
            "✋*Нажмите на любую из кнопок ниже для просмотра детальной статистики*",
            parse_mode='Markdown')

        update.callback_query.edit_message_reply_markup(InlineKeyboardMarkup(keyboard))

    def on_page_button_click(self, update: Update):
        query = update.callback_query
        if query.data.startswith('to_page'):
            index = int(query.data.split(' ')[1])
            # self.__load_page_by_index(index)


