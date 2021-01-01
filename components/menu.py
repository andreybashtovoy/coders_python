from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackContext, CallbackQueryHandler, Updater
from data.ds import Data
import xml.etree.ElementTree as ET


# for child in root:
#     print(child.tag, child.attrib)
#     for child1 in child:
#         print(child1.tag, child1.attrib)


class Menu:
    def __init__(self, updater: Updater, file_url, command):
        tree = ET.parse(file_url)
        self.root = tree.getroot()

        updater.dispatcher.add_handler(CommandHandler(command, self.send))

    def send(self, update: Update, context: CallbackContext) -> None:
        pass
