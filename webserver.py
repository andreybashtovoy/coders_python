from flask import Flask, request
app = Flask(__name__)


@app.route("/", methods=['POST', 'GET'])
def hello():
    print(request.form.to_dict())
    return "Hello World!"


if __name__ == '__main__':
    app.run(port=7000, debug=True)
