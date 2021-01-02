import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import json
import datetime
from math import floor

f = open('bot_data.json')
json_object = json.load(f)


class DataMethods:

    def with_connection(func):
        def wrapper(*args, **kwargs):
            con = sqlite3.connect(json_object['database'] if 'database' in json_object else "./data/database.db")
            return_value = func(*args, **kwargs, con=con)
            return return_value

        return wrapper

    def plot_and_return(func):
        def wrapper(*args, **kwargs):
            func(*args, **kwargs)
            buf = BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)

            plt.clf()

            return buf

        return wrapper

    @with_connection
    def __init__(self, con):
        self.users = pd.read_sql_query("SELECT * from users", con)
        self.activity_names = pd.read_sql_query("SELECT * from activity_names", con)

    @plot_and_return
    @with_connection
    def plot_sleep(self, user_id, con):
        activities = pd.read_sql_query("SELECT * from activities WHERE activity_id=9 AND user_id="+str(user_id), con)
        activities['date'] = activities.start_time.apply(lambda x: (pd.Timestamp(x) + pd.Timedelta("3 hours")).strftime("%m-%d-%y"))

        grouped = activities.groupby(by=["date"]).duration.sum()

        range_ = pd.date_range(end=pd.to_datetime("today").strftime("%m/%d/%y"), periods=7)

        indicies = pd.Series(range_).apply(lambda x: pd.Timestamp(x).strftime("%m-%d-%y"))

        indicies = np.intersect1d(indicies, grouped.index)

        sns.set()
        ax = grouped.loc[indicies].plot(kind='bar', figsize=(10, 7))
        ax.set_xlabel('Дата')
        ax.set_ylabel('Продолжительность сна (Часов)')
        ax.set_title('Продолжительность сна по дням')

    @plot_and_return
    @with_connection
    def plot_sleep_dist(self, user_id, con):
        activities = pd.read_sql_query("SELECT * from activities WHERE activity_id=9 AND user_id="+str(user_id), con)
        activities['date'] = activities.start_time.apply(
            lambda x: (pd.Timestamp(x) + pd.Timedelta("3 hours")).strftime("%m-%d-%y"))

        grouped = activities.groupby(by=["date"]).duration.sum()

        sns.set()
        ax = sns.distplot(grouped)
        ax.set_xlabel('Продолжительность сна')
        ax.set_title('Распределение продолжительности сна')

    @plot_and_return
    @with_connection
    def plot_time_with_benefit(self, user_id, con):
        activities = pd.read_sql_query("SELECT * from activities WHERE user_id="+str(user_id), con)
        activities = activities.merge(self.activity_names[['id', 'challenge', 'name']], left_on="activity_id", right_on="id",
                                      how="inner")

        activities['date'] = activities.start_time.apply(lambda x: pd.Timestamp(x).strftime("%m-%d-%y"))

        grouped = activities[~activities.activity_id.isin([0, 9])].groupby(by=["date", "name"]).duration.sum()

        range_ = pd.date_range(end=pd.to_datetime("today").strftime("%m/%d/%y"), periods=21)

        indicies = pd.Series(range_).apply(lambda x: pd.Timestamp(x).strftime("%m-%d-%y"))

        sns.set()
        ax = grouped.loc[indicies, :].unstack().plot(kind='bar', figsize=(10, 7), stacked=True)
        ax.set_xlabel('Дата')
        ax.set_ylabel('Время с пользой (часов)')
        ax.set_title('Время с пользой пользователя по дням')

    def to_seconds(self, x):
        val = pd.to_datetime(x).time()
        seconds = int(datetime.timedelta(hours=val.hour, minutes=val.minute, seconds=val.second).total_seconds())
        if seconds > 60 * 60 * 21:
            seconds = seconds - 60 * 60 * 24

        return seconds

    def seconds_to_str(self, seconds):
        hours = floor(seconds / 60 / 60)
        minutes = floor(seconds / 60) - floor(seconds / 60 / 60) * 60

        hours_str = str(hours) if len(str(hours)) == 2 else "0" + str(hours)
        minutes_str = str(minutes) if len(str(minutes)) == 2 else "0" + str(minutes)
        return hours_str, minutes_str

    @with_connection
    def get_average_sleep_duration(self, user_id, con):
        activities = pd.read_sql_query("SELECT * from activities WHERE activity_id=9 AND user_id=" + str(user_id), con)

        if activities.shape[0] == 0:
            return "ХЗ", "ХЗ"

        mean = ":".join(self.seconds_to_str(activities.duration.mean() * 60 * 60))
        std = ":".join(self.seconds_to_str(activities.duration.std() * 60 * 60))

        return mean, std

    @with_connection
    def get_average_sleep_start_time(self, user_id, con):
        activities = pd.read_sql_query("SELECT * from activities WHERE activity_id=9 AND user_id=" + str(user_id), con)

        if activities.shape[0] == 0:
            return "ХЗ", "ХЗ"

        seconds = activities.start_time.apply(self.to_seconds)
        time = seconds[~seconds.between(60 * 60 * 6, 60 * 60 * 19)]

        mean = ":".join(self.seconds_to_str(time.mean()))
        std = ":".join(self.seconds_to_str(np.std(time)))

        return mean, std

    @with_connection
    def get_average_wake_up_time(self, user_id, con):
        activities = pd.read_sql_query("SELECT * from activities WHERE activity_id=9 AND user_id=" + str(user_id), con)

        def get_seconds(row):
            sec = self.to_seconds(row.start_time) + row.duration*60*60
            sec = sec % (60 * 60 * 24)
            return sec

        if activities.shape[0] == 0:
            return "ХЗ", "ХЗ"

        seconds = activities.apply(get_seconds, axis=1)

        time = seconds[seconds.between(60 * 60 * 5, 60 * 60 * 14)]


        mean = ":".join(self.seconds_to_str(time.mean()))
        std = ":".join(self.seconds_to_str(np.std(time)))

        return mean, std




Data = DataMethods()