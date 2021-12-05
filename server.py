from datetime import datetime, timedelta

from flask import Flask, request, render_template
from time import time
import hmac
import json
from data.database import DB

app = Flask(__name__)


@app.route("/", methods=['POST', 'GET'])
def hello():
    return "Hello world"


colors = ["#57385c", "#a75265", "#ec7263", "#febe7e"]


@app.route('/activities/<int:user_id>', methods=['POST', 'GET'])
def get_activities(user_id: int):
    activities = DB.get_all_user_activities(user_id)
    results = []
    for activity in activities:
        if activity['activity_id'] is None:
            continue

        if activity['activity_id'] != 0:
            start_dt = datetime.strptime(activity['start_time'], '%Y-%m-%d %H:%M:%S')
            end_dt = start_dt + timedelta(hours=activity['duration'])

            project = ""

            if activity['project_name'] is not None:
                project = f" ({activity['project_name']})"

            results.append({
                "start": start_dt.strftime('%Y-%m-%dT%H:%M:%S'),
                "end": end_dt.strftime('%Y-%m-%dT%H:%M:%S'),
                "title": f"{activity['activity_name']}{project}",
                "color": colors[activity['activity_id'] % len(colors)]
            })

    print(results)

    return render_template("index.html", data=results)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80, debug=True)
