from flask import Flask, request
from time import time
import hmac
import json
from data.database import DB

app = Flask(__name__)

SECRET_KEY = b'23a1179dc7491d991e8d840b11555a70eaa7c53a'


@app.route("/", methods=['POST', 'GET'])
def hello():
    if request.method == 'POST':
        cur_time = int(time())

        obj = {
            "orderReference": request.form['orderReference'],
            "status": "accept",
            "time": cur_time
        }

        signature_string = ";".join([
            obj["orderReference"],
            obj['status'],
            str(obj['time'])
        ])

        obj['merchantSignature'] = hmac.new(SECRET_KEY,
                                            msg=signature_string.encode(),
                                            digestmod='MD5').hexdigest()

        DB.confirm_purchase(obj["orderReference"])

        return json.dumps(obj)

    else:
        print(request.form.to_dict())
        return "Hello World!"


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=7000, debug=True)
