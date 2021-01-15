from components.menu import Menu
from telegram import Update
from telegram.ext import Updater


class Help(Menu):
    def __init__(self, updater: Updater):
        super().__init__(updater, 'components/help/help.xml', 'help')
