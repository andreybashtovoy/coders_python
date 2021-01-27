from components.menu import Menu
from telegram import Update
from telegram.ext import Updater
from data.database import DB


class Reset(Menu):
    def __init__(self, updater: Updater):
        super().__init__(updater, 'components/reset/reset.xml', 'reset')

    def initial_state(self, update: Update):
        return {
            "u_id": str(update.effective_user.id)
        }

    def reset(self, update: Update, state):
        if update.callback_query is not None and update.callback_query.from_user.id != int(state['u_id']):
            update.callback_query.answer(text="Меню было вызвано другим пользователем.", show_alert=True)
            return False

        DB.reset_user_activities(update.effective_user.id)
        update.callback_query.answer(text="Все твои занятия были успешно сброшены.", show_alert=True)

        return False

    def restore(self, update: Update, state):
        if update.callback_query is not None and update.callback_query.from_user.id != int(state['u_id']):
            update.callback_query.answer(text="Меню было вызвано другим пользователем.", show_alert=True)
            return False

        DB.restore_user_activities(update.effective_user.id)
        update.callback_query.answer(text="Все твои занятия были успешно восстановлены.", show_alert=True)

        return False

