import sqlite3


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

    @with_connection
    def get_by_username(self, username, cur):
        cur.execute("SELECT * FROM users WHERE username='"+username+"'")
        return cur.fetchone()

    @with_connection
    def get_all_activities(self, cur):
        cur.execute("SELECT * FROM activity_names")
        return cur.fetchall()

DB = DataBase()