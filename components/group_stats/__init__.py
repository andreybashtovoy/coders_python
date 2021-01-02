from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackContext, CallbackQueryHandler
from data.ds import Data


# class UserStats:
#     def __init__(self, updater):
#         updater.dispatcher.add_handler(CommandHandler('stats', self.stats))
#         updater.dispatcher.add_handler(CommandHandler('stats', self.stats))
#         updater.dispatcher.add_handler(CallbackQueryHandler(self.on_button_click))