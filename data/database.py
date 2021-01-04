import sqlite3
from math import floor, ceil
import json
import datetime

f = open('bot_data.json')
json_object = json.load(f)


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def with_connection(func):
    def wrapper(*args, **kwargs):
        con = sqlite3.connect(json_object['database'] if 'database' in json_object else "./data/database.db")
        con.row_factory = dict_factory
        cur = con.cursor()
        return_value = func(*args, **kwargs, cur=cur)
        con.commit()
        con.close()
        return return_value

    return wrapper


class DataBase:
    def __init__(self):
        pass

    def __hours_to_str(self, fcho):

        time_user = fcho['time']

        if fcho['time'] is not None and fcho['duration'] is not None:

            data_now = datetime.datetime.now()

            data_start = datetime.datetime.strptime(fcho['start_time'], '%Y-%m-%d %H:%M:%S')

            diff = (data_now - data_start).seconds / 3600
            time_user = time_user + diff


        elif fcho['time'] is None:
            return " 0 часов 0 минут 0 секунд"

        hours = floor(time_user) if time_user > 0 else floor(time_user)
        minutes = floor((time_user % 1) * 60)
        seconds = floor((((time_user % 1) * 60) % 1) * 60)

        return " _" + str(hours) + "_ часов _" + str(minutes) + "_ минут _" + str(seconds) + "_ секунд"

    @with_connection
    def get_by_username(self, username, cur):
        cur.execute("SELECT * FROM users WHERE username='" + username + "'")
        return cur.fetchone()

    @with_connection
    def get_user_by_id(self, id, cur):
        cur.execute("SELECT * FROM users WHERE user_id=" + str(id))
        return cur.fetchone()

    @with_connection
    def get_all_activity_names(self, cur):
        cur.execute("SELECT * FROM activity_names")
        return cur.fetchall()

    @with_connection
    def get_user_useful_time(self, user_id, period, cur):

        if period == 'week':
            period_sql = "AND a.start_time > DATE('now', 'localtime', 'weekday 1', '-7 days');"
        elif period == 'month':
            period_sql = "AND a.start_time > DATE('now', 'localtime', 'start of month');"
        elif period == 'today':
            period_sql = "AND a.start_time > DATE('now', 'localtime');"
        else:
            period_sql = ";"

        cur.execute(
            "SELECT SUM(a.duration) AS time, ac.duration, ac.start_time FROM (SELECT * FROM activities WHERE user_id=" + str(
                user_id) + ") a " +
            "INNER JOIN activity_names an ON a.activity_id=an.id LEFT JOIN (SELECT * FROM activities WHERE duration=0) ac ON ac.user_id=a.user_id " +
            "AND an.id = ac.activity_id WHERE an.challenge=1 " + period_sql)

        fcho = cur.fetchone()

        time = self.__hours_to_str(fcho)

        return time

    @with_connection
    def get_active_task_user(self, user_id, cur):
        cur.execute("SELECT an.name, a.start_time, a.activity_id  FROM (SELECT * FROM activities WHERE user_id=" + str(
            user_id) + " AND duration=0) a " +
                    "INNER JOIN activity_names an ON a.activity_id=an.id " +
                    "INNER JOIN users u ON u.user_id=a.user_id")

        fcho = cur.fetchone()

        user_task_time_in_date = ({
            'time': 0,
            'start_time': fcho['start_time'],
            'duration': 0})
        time = self.__hours_to_str(user_task_time_in_date)

        return {
            'name': fcho['name'],
            'active': True if fcho['activity_id'] != 0 else False,
            'time': time
        }

    @with_connection
    def get_rating(self, period, cur):
        condition = ""

        if period == "month":
            condition = "AND p.start_time > DATE('now', 'localtime', 'start of month')"
        elif period == "week":
            condition = "AND p.start_time > DATE('now', 'localtime', 'weekday 1', '-7 days')"
        elif period == "day":
            condition = "AND p.start_time > DATE('now', 'localtime')"

        cur.execute(
            "SELECT main.*, act.challenge FROM (SELECT p.user_id,u.username,SUM(p.duration) AS sum, a.activity_id AS current_activity, " +
            "a.start_time AS current_start_time " +
            "FROM activities p " +
            "JOIN activity_names an on p.activity_id = an.id " +
            "JOIN users u on p.user_id = u.user_id " +
            "JOIN (SELECT * FROM activities WHERE duration=0) a on p.user_id = a.user_id " +
            "WHERE an.challenge = 1 " + condition +
            "GROUP BY p.user_id) main " +
            "JOIN activity_names act ON main.current_activity = act.id;")

        return cur.fetchall()

    @with_connection
    def count_user_activities(self, user_id, cur):
        cur.execute("SELECT main.*, act.name FROM (SELECT activity_id, COUNT(*) as count FROM activities " +
                    "WHERE user_id=" + str(user_id) + " AND activity_id != 0 " +
                    "GROUP BY activity_id " +
                    "ORDER BY count desc) main " +
                    "JOIN activity_names act ON main.activity_id = act.id")

        return cur.fetchall()

    @with_connection
    def get_active_activity(self, user_id, cur):
        cur.execute(
            "SELECT main.*, an.name FROM (SELECT * FROM activities WHERE duration=0 AND user_id=" + str(user_id) +
            ") main JOIN activity_names an ON main.activity_id = an.id")
        return cur.fetchone()

    @with_connection
    def start_activity(self, user_id, name, duration, cur):
        cur.execute("UPDATE activities SET duration=" + str(duration) + " WHERE duration=0 AND user_id=" + str(user_id) + ";")
        cur.execute("INSERT INTO activities(user_id, activity_id) VALUES(" + str(user_id) + ", (SELECT id FROM " +
                    "activity_names WHERE " +
                    "name='" + name + "'));")


DB = DataBase()
