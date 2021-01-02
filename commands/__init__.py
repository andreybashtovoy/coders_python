from telegram import InlineKeyboardButton, Update, CallbackQuery, InlineKeyboardMarkup
from telegram.ext import CallbackContext, Updater, CommandHandler
from data.database import DB
import os

class CommandHandlers:
    def __init__(self, updater: Updater):
        self.__updater = updater
        updater.dispatcher.add_handler(CommandHandler('restart', self.restart))

    def restart(self, update: Update, context):
        update.message.reply_text("До связи")
        os._exit(0)

