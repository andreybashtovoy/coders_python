from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import CommandHandler, CallbackContext, CallbackQueryHandler, Updater

from data.ds import Data
import xml.etree.ElementTree as ET
import re
from data.ds import Data
from data.database import DB
from datetime import datetime

class Menu:
    def __init__(self, updater: Updater, file_url, command=None):
        tree = ET.parse(file_url)
        self.root = tree.getroot()
        self.command = command

        self.index = 0
        self.index_elements(self.root)

        if command is not None:
            updater.dispatcher.add_handler(CommandHandler(command, self.send))

    def index_elements(self, elem):
        elem.set("id", str(self.index))
        self.index += 1
        for child in elem:
            self.index_elements(child)

    def get_state_string(self, state):
        string = ""
        for key in state:
            string = string + key + "^" + str(state[key]) + "|"

        if string.endswith('|'):
            string = string[:-1]

        return string

    def get_state_from_string(self, string):
        if string == "":
            return {}

        state = {}
        for obj in string.split('|'):
            temp = obj.split("^")
            state[temp[0]] = temp[1]

        return state

    def send(self, update: Update, context: CallbackContext) -> None:

        if self.root.get('initial_state') is not None:
            state = getattr(self, self.root.get('initial_state'))(update)
        else:
            state = {}

        menu_id = '0'

        if self.root.tag == "SwitchMenu":
            state['opened_menu'] = '1'
            menu_id = '1'

        self.open_menu(menu_id, state, update, context, send=True)

    def action_callback(self, elem_id, state, update: Update, context: CallbackContext) -> bool:
        if elem_id == "c":
            return getattr(self, "check")(update, state)
        elif elem_id == "custom":
            return getattr(self, "action_custom_callback")(update, state)
        elif elem_id.startswith("_"):
            return getattr(self, "action_custom_callback")(update, state, elem_id[1:])

        elem = self.root.find('.//*[@id="{}"]'.format(elem_id))
        if elem.get('callback') is not None:
            return getattr(self, elem.get('callback'))(update, state)

        return True

    def open_menu(self, id, state, update: Update, context=None, resend=False, send=False):
        elem = self.root.find('.//*[@id="{}"]'.format(id)) if id != '0' else self.root

        def get_text(e):
            text = None

            if e.get('text') is not None:
                text = e.get('text').replace("\\n", "\n")
                text = re.sub("  +", "", text)
                if e.get('format') is not None:
                    text = getattr(self, e.attrib['format'])(text, update, state)

            return text

        def send_message(message_text, message_keyboard, img=None):
            if message_text is not None:
                message_text = message_text.replace("(", "\(")
                message_text = message_text.replace(")", "\)")
                message_text = message_text.replace(".", "\.")
                message_text = message_text.replace("-", "\-")

            if send:
                if img is not None:
                    update.message.reply_photo(
                        caption=message_text,
                        photo=img,
                        parse_mode="MarkdownV2",
                        reply_markup=InlineKeyboardMarkup(message_keyboard),
                        quote=True
                    )
                else:
                    update.message.reply_text(
                        text=message_text,
                        parse_mode="MarkdownV2",
                        reply_markup=InlineKeyboardMarkup(message_keyboard),
                        quote=True
                    )
            elif resend:

                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    reply_to_message_id=update.callback_query.message.reply_to_message.message_id,
                    text=message_text,
                    reply_markup=InlineKeyboardMarkup(message_keyboard),
                    parse_mode="MarkdownV2"
                )

                update.callback_query.message.delete()
            else:

                if img is not None:
                    if update.callback_query.message.text is None:
                        update.callback_query.message.edit_media(
                            InputMediaPhoto(
                                media=img,
                                caption=message_text,
                                parse_mode="MarkdownV2"
                            ),
                            reply_markup=InlineKeyboardMarkup(message_keyboard)
                        )
                    else:
                        update.callback_query.message.reply_to_message.reply_photo(
                            caption=message_text,
                            photo=img,
                            parse_mode="MarkdownV2",
                            reply_markup=InlineKeyboardMarkup(message_keyboard),
                            quote=True
                        )
                        update.callback_query.message.delete()
                else:
                    if update.callback_query.message.text is not None:
                        update.callback_query.edit_message_text(
                            text=message_text,
                            reply_markup=InlineKeyboardMarkup(message_keyboard),
                            parse_mode="MarkdownV2"
                        )
                    else:
                        update.callback_query.message.reply_to_message.reply_text(
                            text=message_text,
                            reply_markup=InlineKeyboardMarkup(message_keyboard),
                            parse_mode="MarkdownV2",
                            quote=True
                        )
                        update.callback_query.message.delete()

        def get_button(child, parent, state, row_child=None):
            if child is None:
                if 'action' in row_child:
                    new_state = getattr(self, row_child['action'])(state.copy(), update, row_child['name'])
                else:
                    new_state = state

                if 'callback' in row_child:
                    if row_child['callback'] == True:
                        callback = 'custom'
                    else:
                        callback = '_' + str(row_child['callback'])
                else:
                    callback = 'c'

                return InlineKeyboardButton(row_child['name'],
                                            callback_data="action&" + parent.get(
                                                'id') + "&" + self.get_state_string(new_state) + '&' + callback)
            elif child.tag == "SwitchButton":
                return InlineKeyboardButton(child.attrib['name'],
                                            callback_data="switch&" + child.get(
                                                'id') + "&" + self.get_state_string(state))
            elif child.tag == "ActionButton":
                if child.get('is_hidden') is not None:
                    is_hidden = getattr(self, child.get('is_hidden'))(state.copy(), update)
                    if is_hidden:
                        return None

                if child.get('action') is not None:
                    new_state = getattr(self, child.get('action'))(state.copy(), update)
                else:
                    new_state = state

                prevent_edit = ""

                #if state == new_state:
                #    prevent_edit = "&1"

                url = None

                if child.get('wayforpay_url') is not None:
                    url = getattr(self, child.get('wayforpay_url'))(state.copy(), update)

                return InlineKeyboardButton(child.attrib['name'],
                                            url=url,
                                            callback_data="action&" + parent.get(
                                                'id') + "&" + self.get_state_string(new_state) + "&" + child.get('id') + prevent_edit)

            else:
                return InlineKeyboardButton(child.attrib['name'],
                                            callback_data="go&" + child.get(
                                                'id') + "&" + self.get_state_string(state))

        if elem.tag == "SwitchButton":
            text = get_text(elem)
            keyboard = []

            parent = self.root.find('.//*[@id="{}"]...'.format(state['opened_menu']))

            for child in parent:
                keyboard.append([get_button(child, parent, state)])

            if parent.get('update_button') is not None:
                keyboard.append([InlineKeyboardButton("🔄 Обновить",
                                                      callback_data="switch&" + state[
                                                          'opened_menu'] + "&" + self.get_state_string(state))])

            send_message(text, keyboard)

        if elem.tag == "MenuButton":
            text = get_text(elem)
            keyboard = []

            img = None

            if elem.get('image') is not None:
                img = getattr(Data, elem.get('image'))(state, update.effective_chat.id)

            for child in elem:
                if child.tag == 'Row':
                    keyboard.append(
                        [get_button(row_child, elem, state) for row_child in child]
                    )

                    def remove_all_occurrences(list_obj, value):
                        while value in list_obj:
                            list_obj.remove(value)

                    remove_all_occurrences(keyboard[len(keyboard) - 1], None)

                    if [] in keyboard:
                        keyboard.remove([])
                elif child.tag == "CustomButtons":
                    buttons = getattr(self, child.get('init'))(state.copy(), update)

                    for row in buttons:
                        keyboard.append([get_button(None, elem, state, row_child) for row_child in row])
                else:
                    button = get_button(child, elem, state)

                    if button is not None:
                        keyboard.append([button])

            if elem.get('update_button') is not None:
                keyboard.append([InlineKeyboardButton("🔄 Обновить",
                                                      callback_data="go&" + elem.get(
                                                          'id') + "&" + self.get_state_string(state))])

            if id != '0':
                keyboard.append([InlineKeyboardButton("◀️ Назад",
                                                      callback_data="go&" + self.root.find(
                                                          './/*[@id="{}"]...'.format(id)).get(
                                                          'id') + "&" + self.get_state_string(state))])

            send_message(text, keyboard, img)
        elif elem.tag == "PlotButton":
            keyboard = [
                [
                    InlineKeyboardButton("◀️ Назад", callback_data="go&" + self.root.find(
                        './/*[@id="{}"]...'.format(id)).get('id') + "&" +
                                                                   self.get_state_string(state))
                ]
            ]

            plot = getattr(Data, elem.attrib['plot'])(state['user_id'])
            caption = None

            if elem.get('not_premium_image') is not None:
                chat = DB.get_chat_by_id(update.effective_chat.id)

                now = datetime.now()
                expiration = datetime.strptime(chat['premium_expiration'], '%Y-%m-%d %H:%M:%S')

                if now > expiration:
                    plot = open(elem.get('not_premium_image'), 'rb')
                    if elem.get("not_premium_text") is not None:
                        caption = elem.get('not_premium_text').replace("\\n", "\n")
                        caption = re.sub("  +", "", caption)


            reply_markup = InlineKeyboardMarkup(keyboard)
            # context.bot.send_photo(
            #     chat_id=update.effective_chat.id,
            #     reply_to_message_id=update.callback_query.message.reply_to_message.message_id,
            #     photo=plot,
            #     reply_markup=reply_markup,
            #     caption=caption,
            #     parse_mode="Markdown"
            # )
            #
            # update.callback_query.message.delete()

            send_message(caption, keyboard, plot)

    def on_button_click(self, update: Update, context: CallbackContext):
        query = update.callback_query

        if query.data.startswith('go'):
            info = query.data.split('&')
            self.open_menu(info[1], self.get_state_from_string(info[2]), update, context)
        elif query.data.startswith('back_resend'):
            info = query.data.split('&')
            self.open_menu(info[1], self.get_state_from_string(info[2]), update, context, resend=True)
        elif query.data.startswith("switch"):
            info = query.data.split('&')
            state = self.get_state_from_string(info[2])
            state['opened_menu'] = info[1]
            self.open_menu(info[1], state, update, context)
        elif query.data.startswith("action"):
            info = query.data.split('&')

            state = self.get_state_from_string(info[2])

            allow_open = True

            if len(info) >= 4:
                allow_open = self.action_callback(info[3], state, update, context)

            if len(info) != 5 and allow_open:
                self.open_menu(info[1], state, update, context)
