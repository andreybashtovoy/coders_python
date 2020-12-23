import sqlite3
from math import floor, ceil

def with_connection(func):
    def wrapper(*args, **kwargs):
        con = sqlite3.connect("./data/database.db")
        cur = con.cursor()
        return_value = func(*args, **kwargs, cur=cur)
        con.close()
        return return_value

    return wrapper



class DataBase:
    def __init__(self):
        pass

    def hours_to_str(self, hours_user):
        hours = floor(hours_user) if hours_user > 0 else ceil(hours_user)
        # minutes = round((hours_user % 1) * 60)
        return str(hours) # + ':' + str(minutes)

    @with_connection
    def get_by_username(self, username, cur):
        cur.execute("SELECT * FROM users WHERE username='"+username+"'")
        return cur.fetchone()

    @with_connection
    def get_all_activities_names(self, cur):
        cur.execute("SELECT * FROM activity_names")
        return cur.fetchall()

    @with_connection
    def get_user_useful_time_today(self, user_id, cur):
        cur.execute(
            "SELECT SUM(a.duration) AS time FROM (SELECT * FROM activities WHERE user_id="+str(user_id)+") a INNER JOIN activity_names an ON a.activity_id=an.id WHERE an.challenge=1 AND a.start_time > DATE('now', 'localtime', '-1 days')")

        return self.hours_to_str(cur.fetchone()[0])

    @with_connection
    def get_user_useful_time_week(self, user_id, cur):
        cur.execute("SELECT SUM(a.duration) AS time FROM (SELECT * FROM activities WHERE user_id="+str(user_id)+") a "
                    "INNER JOIN activity_names an ON a.activity_id=an.id  WHERE an.challenge=1 "
                    "AND a.start_time > DATE('now', 'localtime', 'weekday 1', '-7 days')")

        return self.hours_to_str(cur.fetchone()[0])

    @with_connection
    def get_user_useful_time_month(self, user_id, cur):
        cur.execute("SELECT SUM(a.duration) AS time FROM (SELECT * FROM activities WHERE user_id="+str(user_id)+") a "
                    "INNER JOIN activity_names an ON a.activity_id=an.id  WHERE an.challenge=1 "
                    "AND a.start_time > DATE('now', 'localtime', 'start of month')")

        return self.hours_to_str(cur.fetchone()[0])

    @with_connection
    def get_user_useful_time_all(self, user_id, cur):
        cur.execute("SELECT SUM(a.duration) AS time FROM (SELECT * FROM activities WHERE user_id="+str(user_id)+") a "
                    "INNER JOIN activity_names an ON a.activity_id=an.id WHERE an.challenge=1;")

        return self.hours_to_str(cur.fetchone()[0])



DB = DataBase()