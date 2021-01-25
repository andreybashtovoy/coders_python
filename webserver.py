from flask import Flask, request
from time import time
import hmac
import json
from data.database import DB
from telegram.ext import Updater

app = Flask(__name__)

SECRET_KEY = b'23a1179dc7491d991e8d840b11555a70eaa7c53a'


@app.route("/", methods=['POST', 'GET'])
def hello():
    if request.method == 'POST':
        cur_time = int(time())

        form = json.loads(list(request.form.to_dict().keys())[0])
        print(form)

        obj = {
            "orderReference": form['orderReference'],
            "status": "accept",
            "time": cur_time
        }

        signature_string = ";".join([
            obj["orderReference"],
            obj['status'],
            str(obj['time'])
        ])

        obj['signature'] = hmac.new(SECRET_KEY,
                                            msg=signature_string.encode(),
                                            digestmod='MD5').hexdigest()

        if form['transactionStatus'] == "Approved":
            DB.confirm_purchase(obj["orderReference"])

            purchase = DB.get_purchase_by_reference(obj["orderReference"])

            f = open('bot_data.json')
            json_object = json.load(f)

            updater = Updater(json_object["token"])

            updater.bot.send_message(
                chat_id=purchase['chat_id'],
                text="*Premium в этом чате был успешно продлен на месяц* 😊",
                parse_mode="Markdown"
            )

        return json.dumps(obj)

    else:
        print(request.form.to_dict())
        return "Hello World!"


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=7000, debug=True)
