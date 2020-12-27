import sqlite3
from math import floor, ceil
import json
import datetime

f = open('bot_data.json')
json_object = json.load(f)

def with_connection(func):
    def wrapper(*args, **kwargs):
        con = sqlite3.connect(json_object['database'] if 'database' in json_object else "./data/database.db")
        cur = con.cursor()
        return_value = func(*args, **kwargs, cur=cur)
        con.close()
        return return_value

    return wrapper



class DataBase:
    def __init__(self):
        pass

    def __hours_to_str(self, fcho):

        time_user = fcho[0]

        if fcho[0] is not None and fcho[1] is not None:

            data_now = datetime.datetime.now()
            data_start = datetime.datetime.strptime(fcho[2], '%Y-%m-%d %H:%M:%S')
            diff = (data_now - data_start).seconds / 3600
            time_user = time_user + diff


        elif fcho[0] is None:
            return " _0_ часов _0_ минут"

        hours = floor(time_user) if time_user > 0 else floor(time_user)
        minutes = floor((time_user % 1) * 60)
        seconds = floor((((time_user % 1) * 60) % 1) * 60)

        return " _"+str(hours) + "_ часов _" + str(minutes) + "_ минут _" +  str(seconds) + "_ секунд"



    @with_connection
    def get_by_username(self, username, cur):
        cur.execute("SELECT * FROM users WHERE username='"+username+"'")
        return cur.fetchone()

    @with_connection
    def get_user_by_id(self, id, cur):
        cur.execute("SELECT * FROM users WHERE user_id="+str(id))
        return cur.fetchone()

    @with_connection
    def get_all_activities_names(self, cur):
        cur.execute("SELECT * FROM activity_names")
        return cur.fetchall()

    @with_connection
    def get_user_useful_time_today(self, user_id, cur):
        cur.execute("SELECT SUM(a.duration) AS time, ac.duration, ac.start_time FROM (SELECT * FROM activities WHERE user_id=" + str(user_id) + ") a INNER JOIN activity_names an ON a.activity_id=an.id LEFT JOIN (SELECT * FROM activities WHERE duration=0) ac ON ac.user_id=a.user_id AND an.id = ac.activity_id WHERE an.challenge=1 AND a.start_time > DATE('now', 'localtime');")

        fcho = cur.fetchone()

        time = self.__hours_to_str(fcho)

        if time:
            return time
        return '0'


    @with_connection
    def get_user_useful_time_week(self, user_id, cur):

        cur.execute("SELECT SUM(a.duration) AS time, ac.duration, ac.start_time FROM (SELECT * FROM activities WHERE user_id=" + str(user_id) + ") a INNER JOIN activity_names an ON a.activity_id=an.id LEFT JOIN (SELECT * FROM activities WHERE duration=0) ac ON ac.user_id=a.user_id AND an.id = ac.activity_id  WHERE an.challenge=1 AND a.start_time > DATE('now', 'localtime', 'weekday 1', '-7 days')")

        fcho = cur.fetchone()

        time = self.__hours_to_str(fcho)

        return time


    @with_connection
    def get_user_useful_time_month(self, user_id, cur):
        cur.execute("SELECT SUM(a.duration) AS time, ac.duration, ac.start_time FROM (SELECT * FROM activities WHERE user_id=" + str(user_id) + ") a INNER JOIN activity_names an ON a.activity_id=an.id LEFT JOIN (SELECT * FROM activities WHERE duration=0) ac ON ac.user_id=a.user_id AND an.id = ac.activity_id WHERE an.challenge=1 AND a.start_time > DATE('now', 'localtime', 'start of month')")

        fcho = cur.fetchone()

        time = self.__hours_to_str(fcho)

        return time

    @with_connection
    def get_user_useful_time_all(self, user_id, cur):
        cur.execute("SELECT SUM(a.duration) AS time, ac.duration, ac.start_time FROM (SELECT * FROM activities WHERE user_id=" + str(user_id) + ") a "
                    "INNER JOIN activity_names an ON a.activity_id=an.id LEFT JOIN (SELECT * FROM activities WHERE duration=0) ac ON ac.user_id=a.user_id AND an.id = ac.activity_id " +
                    "WHERE an.challenge=1;")

        fcho = cur.fetchone()

        time = self.__hours_to_str(fcho)

        return time

    @with_connection
    def get_active_task_user(self, user_id, cur):
        cur.execute("SELECT an.name, a.start_time, a.activity_id FROM (SELECT * FROM activities WHERE user_id=" + str(user_id) + " AND duration=0) a " +
                    "INNER JOIN activity_names an ON a.activity_id=an.id " +
                    "INNER JOIN users u ON u.user_id=a.user_id")

        fcho = cur.fetchone()

        user_task_time_in_date = (0, 0, fcho[1])
        time = self.__hours_to_str(user_task_time_in_date)

        return [fcho[0],  True if fcho[2] != 0 else False, time]

DB = DataBase()