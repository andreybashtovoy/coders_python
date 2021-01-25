from components.menu import Menu
from telegram import Update
from telegram.ext import Updater
from data.database import DB
from math import floor, ceil
from datetime import datetime, timedelta
import requests
import random
import string
from time import time
import hmac
import json


class Chat(Menu):
    def __init__(self, updater: Updater):
        super().__init__(updater, 'components/chat/chat.xml', 'chat')

    def initial_state(self, update: Update):
        order = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

        return {
            "order": order
        }

    def get_url(self, state, update: Update):
        purchase = DB.get_purchase_by_reference(state['order'])

        if purchase is None:
            date = int(time())

            url = 'https://secure.wayforpay.com/pay?behavior=offline'
            myobj = {
                'merchantAccount': '34_89_218_42',
                'merchantDomainName': 'https://t.me/timeplayer_bot',
                'merchantTransactionSecureType': 'AUTO',
                'orderReference': state['order'],
                'orderDate': date,
                'amount': 1,
                'currency': 'UAH',
                'productName': ['TimePlayer Premium'],
                'productCount': [1],
                'productPrice': [1],
                'serviceUrl': 'http://34.89.218.42:7000/'
            }

            signature_string = ';'.join([myobj['merchantAccount'],
                                         myobj['merchantDomainName'],
                                         myobj['orderReference'],
                                         str(date),
                                         str(myobj['amount']),
                                         myobj['currency'],
                                         myobj['productName'][0],
                                         str(myobj['productCount'][0]),
                                         str(myobj['productPrice'][0])
                                         ])

            myobj['merchantSignature'] = hmac.new(b'23a1179dc7491d991e8d840b11555a70eaa7c53a',
                                                  msg=signature_string.encode(),
                                                  digestmod='MD5').hexdigest()

            x = requests.post(url, data=myobj)

            vkh = json.loads(x.text)['url'].split('=')[1]
            DB.add_purchase(state['order'], update.effective_chat.id, vkh)
            return "https://secure.wayforpay.com/page?vkh=" + vkh
        else:
            return "https://secure.wayforpay.com/page?vkh=" + purchase['vkh']


    def text_format(self, message_text, update: Update, state):
        chat = DB.get_chat_by_id(update.effective_chat.id)

        now = datetime.now()

        expiration = datetime.strptime(chat['premium_expiration'], '%Y-%m-%d %H:%M:%S')

        left = ""

        if expiration > now:
            days = (expiration - now).days
            if chat['is_free']:
                left = "\n\nДо конца пробного периода осталось %s дней." % days
            else:
                left = "\n\nДо следующего платежа осталось %s дней." % days

        return message_text.format(
            emodji="❌" if now > expiration else "🌟",
            active="не " if now > expiration else "",
            left=left
        )
