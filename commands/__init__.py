from telegram import InlineKeyboardButton, Update, CallbackQuery, InlineKeyboardMarkup
from telegram.ext import CallbackContext, Updater, CommandHandler
from data.database import DB
import os

class CommandHandlers:
    def __init__(self, updater: Updater):
        self.__updater = updater
        updater.dispatcher.add_handler(CommandHandler('restart', self.restart))
        updater.dispatcher.add_handler(CommandHandler('get_chat_id', self.get_chat_id))
        updater.dispatcher.add_handler(CommandHandler('disable_tag', self.disable_tag))
        updater.dispatcher.add_handler(CommandHandler('enable_tag', self.enable_tag))


    def restart(self, update: Update, context):
        update.message.reply_text("До связи")
        os._exit(0)

    def get_chat_id(self, update: Update, context: CallbackContext):
        update.message.reply_text(update.effective_chat.id)

    def disable_tag(self, update: Update, context: CallbackContext):
        DB.disable_tag(update.message.from_user.id)
        update.message.reply_text("*Ок\. Вернуть теги можешь командой:*\n"
                                  "/enable\_tag", parse_mode="MarkdownV2")

    def enable_tag(self, update: Update, context: CallbackContext):
        DB.enable_tag(update.message.from_user.id)
        update.message.reply_text("*Ок\. Отключить теги можешь командой:*\n"
                                  "/disable\_tag", parse_mode="MarkdownV2")
