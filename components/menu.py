from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackContext, CallbackQueryHandler, Updater
from data.ds import Data
import xml.etree.ElementTree as ET
import re


class Menu:
    def __init__(self, updater: Updater, file_url, command):
        tree = ET.parse(file_url)
        self.root = tree.getroot()

        self.index = 0
        self.index_elements(self.root)

        for child in self.root:
            print(child)
            print(child.get('id'))

        updater.dispatcher.add_handler(CommandHandler(command, self.send))
        updater.dispatcher.add_handler(CallbackQueryHandler(self.on_button_click))

    def index_elements(self, elem):
        elem.set("id", str(self.index))
        self.index += 1
        for child in elem:
            self.index_elements(child)

    def get_state_string(self, state):
        string = ""
        for key in state:
            string = string + key + ":::" + str(state[key]) + "|||"

        if string.endswith('|||'):
            string = string[:-3]

        return string

    def get_state_from_string(self, string):
        if string == "":
            return {}

        state = {}
        for obj in string.split('|||'):
            temp = obj.split(":::")
            state[temp[0]] = temp[1]

        return state

    def send(self, update: Update, context: CallbackContext) -> None:

        if self.root.get('initial_state') is not None:
            state = getattr(self, self.root.get('initial_state'))(update)
        else:
            state = {}

        text = self.root.attrib['text'].replace("\\n", "\n")
        text = re.sub("  +", "", text)
        text = getattr(self, self.root.attrib['format'])(text, update, state)

        keyboard = []

        for child in self.root:
            keyboard.append([InlineKeyboardButton(child.attrib['name'],
                                                  callback_data="go&&&" + child.get('id') + "&&&" +
                                                                self.get_state_string(state))])

        update.message.reply_text(text=text,
                                  parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(keyboard))

    def open_menu(self, id, state, update: Update):
        elem = self.root.find('.//*[@id="{}"]'.format(id)) if id != '0' else self.root

        if elem.tag == "MenuButton":
            text = elem.get('text').replace("\\n", "\n")
            text = re.sub("  +", "", text)
            if elem.get('format') is not None:
                text = getattr(self, elem.attrib['format'])(text, update, state)

            keyboard = []

            for child in elem:
                keyboard.append([InlineKeyboardButton(child.attrib['name'],
                                                      callback_data="go&&&" + child.get('id') + "&&&" + self.get_state_string(state))])
            if id != '0':
                keyboard.append([InlineKeyboardButton("◀️ Назад",
                                                      callback_data="go&&&" + self.root.find(
                                                          './/*[@id="{}"]...'.format(id)).get('id') + "&&&" + self.get_state_string(state))])

            update.callback_query.edit_message_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )

    def on_button_click(self, update: Update, context: CallbackContext):
        query = update.callback_query

        if query.data.startswith('go'):
            info = query.data.split('&&&')
            self.open_menu(info[1], self.get_state_from_string(info[2]), update)
