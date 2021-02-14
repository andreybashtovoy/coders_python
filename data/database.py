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

        if fcho['time'] is not None and fcho['start_time'] is not None:

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
    def _get_user_useful_time(self, user_id, period, cur):

        if period == 'week':
            period_sql = "AND a.start_time > DATE('now', 'localtime', 'weekday 1', '-7 days')"
        elif period == 'month':
            period_sql = "AND a.start_time > DATE('now', 'localtime', 'start of month')"
        elif period == 'today':
            period_sql = "AND a.start_time > DATE('now', 'localtime')"
        else:
            period_sql = ""

        cur.execute(
            "SELECT s.time, active.start_time FROM "
            "("
            "SELECT IFNULL(SUM(a.duration), 0) as time, a.user_id FROM activities a "
            "JOIN activity_names an ON a.activity_id = an.id "
            "WHERE a.user_id=%d AND an.challenge=1 %s "
            ") s "
            "LEFT JOIN (SELECT * FROM activities a JOIN "
            "activity_names n on a.activity_id = n.id WHERE a.duration=0 AND n.challenge=1) active "
            "ON s.user_id=active.user_id" % (user_id, period_sql))

        return cur.fetchone()

    def get_user_useful_time(self, user_id, period):
        return self.__hours_to_str(self._get_user_useful_time(user_id, period))

    def get_today_user_useful_time(self, user_id):
        return self._get_user_useful_time(user_id, "today")

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
    def get_rating(self, period, chat_id, cur):
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
            "JOIN activity_names act ON main.current_activity = act.id "
            "WHERE main.user_id IN ("
            "SELECT user_id FROM users_chats uc "
            "WHERE uc.chat_id=%s)" % chat_id)

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
    def start_activity(self, user_id, name, duration, project_id, chat_id, delay, cur):
        activity_names = self.get_user_accessible_activities(user_id, chat_id)

        activity_id = None

        for obj in activity_names:
            if obj['name'] == name:
                activity_id = obj['id']
                break

        cur.execute(
            "UPDATE activities SET duration=" + str(duration) + " WHERE duration=0 AND user_id=" + str(user_id) + ";")
        cur.execute("INSERT INTO activities(user_id, activity_id, project_id, start_time) VALUES(" + str(user_id) +
                    ", " + str(activity_id) + ", " + (str(project_id) if project_id is not None else "NULL") + ", DATETIME('now','localtime','-"+ str(delay) +" minutes'));")

    @with_connection
    def get_activity_by_name(self, name, cur):
        cur.execute("SELECT * FROM activity_names WHERE name='%s'" % name)
        return cur.fetchone()

    def get_user_activity_by_name(self, name, user_id, chat_id):
        activity_names = self.get_user_accessible_activities(user_id, chat_id)

        for obj in activity_names:
            if obj['name'] == name:
                return obj

    @with_connection
    def get_activity_by_id(self, id, cur):
        cur.execute("SELECT * FROM activity_names WHERE id=%d" % int(id))
        return cur.fetchone()

    @with_connection
    def add_activity(self, user_id, activity_id, duration, project_id, cur):
        cur.execute("INSERT INTO activities(user_id, activity_id, duration, project_id, start_time) VALUES(" + str(user_id) + ","
                    + str(activity_id) + "," + str(duration) + ", " + (str(project_id) if project_id is not None else "NULL") +
                    ", DATETIME('now','localtime','-" + str(duration if duration > 0 else 0) + " hours') );")

    @with_connection
    def get_active_users(self, cur):
        cur.execute("SELECT active.start_time, u.user_id, u.username, u.day, u.tag, act.id, act.name FROM "
                    "(SELECT * FROM activities WHERE duration = 0) active "
                    "JOIN users u ON active.user_id = u.user_id "
                    "JOIN activity_names act ON active.activity_id = act.id "
                    "WHERE active.activity_id NOT IN(0, 9)")

        return cur.fetchall()

    @with_connection
    def get_all_users(self, cur):
        cur.execute("SELECT * FROM users")
        return cur.fetchall()

    @with_connection
    def get_all_ranks(self, cur):
        cur.execute("SELECT * FROM rank")
        return cur.fetchall()

    @with_connection
    def set_user_day(self, user_id, day, cur):
        cur.execute("UPDATE users SET day=%d WHERE user_id=%d" % (day, user_id))

    @with_connection
    def disable_tag(self, user_id, cur):
        cur.execute("UPDATE users SET tag=0 WHERE user_id=" + str(user_id))

    @with_connection
    def enable_tag(self, user_id, cur):
        cur.execute("UPDATE users SET tag=1 WHERE user_id=" + str(user_id))

    @with_connection
    def get_user_projects_by_activity_id(self, user_id, activity_id, cur):
        cur.execute("SELECT * FROM projects WHERE user_id=%s AND activity_id=%s "
                    "ORDER BY id DESC" % (user_id, activity_id))
        return cur.fetchall()

    @with_connection
    def get_project_by_name(self, user_id, activity_id, name, cur):
        cur.execute("SELECT * FROM projects WHERE user_id=%s AND activity_id=%s AND name='%s'" %
                    (user_id, activity_id, name))
        return cur.fetchone()

    @with_connection
    def set_user_dialog_state(self, user_id, state, cur):
        cur.execute("UPDATE users SET dialog_state='%s', dialog_start_time=DATETIME('now', 'localtime') "
                    "WHERE user_id=%s" % (state, user_id))

    @with_connection
    def get_user_dialog_state(self, user_id, cur):
        cur.execute("SELECT * FROM users WHERE user_id=%d AND "
                    "dialog_start_time IS NOT NULL AND "
                    "dialog_start_time>DATETIME('now', 'localtime', '-1 minute')" % user_id)
        return cur.fetchone()

    @with_connection
    def create_project(self, user_id, activity_id, name, cur):
        cur.execute("INSERT INTO projects(user_id, activity_id, name) "
                    "VALUES (%s, %s, '%s')" % (user_id, activity_id, name))
        cur.execute("SELECT * FROM projects WHERE id=(SELECT MAX(id) FROM projects)")
        return cur.fetchone()

    @with_connection
    def get_project_by_id(self, id, cur):
        cur.execute("SELECT * FROM projects WHERE id=%d" % int(id))
        return cur.fetchone()

    @with_connection
    def get_project_time(self, project_id, cur):
        cur.execute("SELECT IFNULL(SUM(duration), 0) AS duration FROM activities WHERE project_id=%s" % project_id)
        return cur.fetchone()

    @with_connection
    def activate_project(self, project_id, user_id, activity_id, cur):
        cur.execute("UPDATE projects SET active=0 WHERE user_id=%s AND activity_id=%s" % (user_id, activity_id))
        cur.execute("UPDATE projects SET active=1 WHERE id=%s" % project_id)

    @with_connection
    def stop_project(self, project_id, cur):
        cur.execute("UPDATE projects SET active=0 WHERE id=%s" % project_id)

    @with_connection
    def remove_project(self, project_id, cur):
        cur.execute("DELETE FROM projects WHERE id=%s" % project_id)

    @with_connection
    def get_active_project(self, user_id, name, cur):
        cur.execute(("SELECT * FROM projects WHERE user_id=%s AND active=1 AND activity_id=(SELECT id FROM " +
                    "activity_names WHERE " +
                    "name='%s')") %
                    (user_id, name))
        return cur.fetchone()

    @with_connection
    def get_chat_by_id(self, chat_id, cur):
        cur.execute('SELECT * FROM chats WHERE chat_id=%s' % str(chat_id))
        return cur.fetchone()

    @with_connection
    def update_user_and_chat(self, user, chat, cur):
        obj = self.get_user_by_id(user.id)

        if obj is None:
            cur.execute("INSERT INTO users(user_id, username) VALUES(%d, '%s')" % (user.id, user.username))
        else:
            cur.execute("UPDATE users SET username='%s' WHERE user_id=%d" % (user.username, user.id))

        cur.execute("REPLACE INTO chats(chat_id, name) VALUES (%d, '%s')" %
                    (chat.id, chat.title if chat.title is not None else chat.username))

        cur.execute("REPLACE INTO users_chats(chat_id, user_id) VALUES (%d, %d)" % (chat.id, user.id))

    @with_connection
    def get_user_personal_activities(self, user_id, cur):
        cur.execute('SELECT * FROM activity_names WHERE owner=' + str(user_id))
        return cur.fetchall()

    @with_connection
    def create_activity(self, user_id, name, cur):
        cur.execute("INSERT INTO activity_names(name, owner) "
                    "VALUES ('%s', %s)" % (name, user_id))
        cur.execute("SELECT * FROM activity_names WHERE id=(SELECT MAX(id) FROM activity_names)")
        return cur.fetchone()

    @with_connection
    def remove_activity(self, activity_id, cur):
        cur.execute("DELETE FROM activity_names WHERE id=" + str(activity_id))

    @with_connection
    def set_activity_access(self, activity_id, access, cur):
        cur.execute("UPDATE activity_names SET access=%d WHERE id=%s" % (access, activity_id))

    @with_connection
    def set_activity_challenge(self, activity_id, challenge, cur):
        cur.execute("UPDATE activity_names SET challenge=%d WHERE id=%s" % (challenge, activity_id))

    @with_connection
    def get_user_accessible_activities(self, user_id, chat_id, cur):
        cur.execute("SELECT * FROM activity_names WHERE access=0 OR "
                    "(access=1 AND owner=%s) OR "
                    "id IN (SELECT an.id FROM users_chats uc "
                    "JOIN activity_names an ON an.owner=uc.user_id "
                    "WHERE an.access=2 AND uc.chat_id=%s)" % (user_id, chat_id))
        return cur.fetchall()

    @with_connection
    def get_all_chats(self, cur):
        cur.execute("SELECT * FROM chats")
        return cur.fetchall()

    @with_connection
    def get_chat_active_users(self, chat_id, cur):
        cur.execute("SELECT * FROM users_chats uc "
                    "JOIN "
                    "("
                    "SELECT active.start_time, u.user_id, u.username, u.day, u.tag, act.id, act.name FROM "
                    "(SELECT * FROM activities WHERE duration = 0) active "
                    "JOIN users u ON active.user_id = u.user_id "
                    "JOIN activity_names act ON active.activity_id = act.id "
                    "WHERE active.activity_id NOT IN(0, 9) "
                    ") all_active ON uc.user_id=all_active.user_id "
                    "WHERE uc.chat_id=%s;" % chat_id)
        return cur.fetchall()

    @with_connection
    def get_chat_users(self, chat_id, cur):
        cur.execute("SELECT * FROM users_chats uc "
                    "JOIN users u on uc.user_id = u.user_id "
                    "WHERE uc.chat_id=%s;" % chat_id)
        return cur.fetchall()

    @with_connection
    def get_user_activities_by_day(self, user_id, day, cur):
        cur.execute(("SELECT main.sum, an.name as activity_name, an.challenge,"
                    "p.name as project_name, main.start_time FROM ("
                    "SELECT SUM(duration) as sum, start_time, activity_id, project_id "
                    "FROM activities "
                    "WHERE start_time < DATE('now', 'localtime', '%d days') "
                    "AND start_time > DATE('now', 'localtime', '%d days') "
                    "AND user_id = %s "
                    "and activity_id != 0 "
                    "GROUP BY activity_id, project_id "
                    ") main "
                    "JOIN activity_names an ON main.activity_id = an.id "
                    "LEFT JOIN projects p ON main.project_id = p.id "
                    "ORDER BY sum DESC") % (int(day)+1, int(day), user_id))
        return cur.fetchall()

    @with_connection
    def get_chat_active_days(self, chat_id, cur):
        cur.execute("SELECT MIN(start_time) as min FROM activities WHERE user_id IN "
                    "(SELECT u.user_id FROM users_chats uc "
                    "JOIN users u on uc.user_id = u.user_id "
                    "WHERE uc.chat_id=%s)" % chat_id)

        date = datetime.datetime.strptime(cur.fetchone()['min'], '%Y-%m-%d %H:%M:%S').date()
        now = datetime.datetime.now().date()

        return (now - date).days + 1

    @with_connection
    def has_user_activities(self, user_id, cur):
        cur.execute("SELECT COUNT(*) as count FROM activities WHERE duration!=0 AND user_id=%s;" % user_id)
        return cur.fetchone()['count'] != 0

    @with_connection
    def has_chat_activities(self, chat_id, cur):
        cur.execute("SELECT COUNT(*) as count FROM activities a "
                    "JOIN activity_names an on an.id = a.activity_id "
                    "WHERE a.user_id IN "
                    "(SELECT user_id FROM users_chats WHERE chat_id=%s) AND "
                    "an.challenge = 1 AND a.duration > 0 "
                    "AND a.start_time < DATE('now', 'localtime')" % chat_id)
        return cur.fetchone()['count'] != 0

    @with_connection
    def get_purchase_by_reference(self, reference, cur):
        cur.execute("SELECT * FROM purchases WHERE reference='%s'" % reference)
        return cur.fetchone()

    @with_connection
    def add_purchase(self, reference, chat_id, vkh, cur):
        cur.execute("INSERT INTO purchases(reference, chat_id, vkh) VALUES('%s', %s, '%s')" % (reference, chat_id, vkh))

    @with_connection
    def confirm_purchase(self, reference, cur):
        cur.execute("UPDATE chats SET premium_expiration=DATETIME('now', 'localtime', '+1 month') "
                    "WHERE premium_expiration < DATETIME('now', 'localtime')")
        cur.execute("UPDATE chats SET premium_expiration=DATETIME(premium_expiration, '+1 month'), is_free=0 "
                    "WHERE chat_id=(SELECT chat_id FROM purchases WHERE reference='%s')" % reference)
        cur.execute("UPDATE purchases SET paid=1 WHERE reference='%s'" % reference)

    @with_connection
    def reset_user_activities(self, user_id, cur):
        cur.execute("UPDATE activities SET reset_user_id=user_id, user_id=NULL WHERE user_id = %s;" % user_id)

    @with_connection
    def restore_user_activities(self, user_id, cur):
        cur.execute("UPDATE activities SET user_id=reset_user_id WHERE reset_user_id = %s;" % user_id)

    @with_connection
    def get_user_projects(self, user_id, cur):
        cur.execute("SELECT * FROM projects WHERE user_id=%s" % user_id)
        return cur.fetchall()

    @with_connection
    def get_last_projects(self, user_id, cur):
        cur.execute("SELECT DISTINCT p.id, p.name FROM activities a "
                    "JOIN projects p on p.id = a.project_id "
                    "WHERE a.user_id=%s ORDER BY a.id DESC" % user_id)
        return cur.fetchall()

    @with_connection
    def get_activity_by_project_id(self, project_id, cur):
        cur.execute("SELECT * FROM activity_names "
                    "WHERE id=(SELECT activity_id FROM projects WHERE id=%s)" % project_id)
        return cur.fetchone()

DB = DataBase()
