from components.menu import Menu
from telegram import Update
from telegram.ext import Updater
from data.database import DB
from data.ds import Data


class Rating(Menu):
    def __init__(self, updater: Updater):
        super().__init__(updater, 'components/rating/rating.xml', 'rating')