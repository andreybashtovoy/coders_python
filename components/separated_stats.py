from telegram import InlineKeyboardButton, Update, CallbackQuery, InlineKeyboardMarkup
from telegram.ext import CallbackContext

# keyboard pattern with calllback_data that represents id
keyboard = [
    [
        InlineKeyboardButton('Sport', callback_data='test1')
    ],
    [
        InlineKeyboardButton('Code', callback_data='test2')
    ],
    [
        InlineKeyboardButton('Music', callback_data='test3')
    ]
]


# shows multiple buttons to look at detailed information about tasks
def show_separated_stats(update: Update, context: CallbackContext) -> None:
    query = update.callback_query

    update.callback_query.edit_message_text(
                                           "📝 *Статистика занятий по отдельности*\n\n"
                                           "⚡️Ваше самое времязатратное занятие - \"Спорт\"\n\n"
                                           "✋*Нажмите на любую из кнопок ниже для просмотра детальной статистики*",
                                           parse_mode='Markdown')

    update.callback_query.edit_message_reply_markup(InlineKeyboardMarkup(keyboard))
