import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import json
import datetime
from math import floor
from data.database import DB

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
            sns.set()
            sns.set_palette("colorblind")
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

        range_ = pd.date_range(end=pd.to_datetime("today").strftime("%m/%d/%y"), periods=21)

        indicies = pd.Series(range_).apply(lambda x: pd.Timestamp(x).strftime("%m-%d-%y"))

        indicies = np.intersect1d(indicies, grouped.index)


        ax = grouped.loc[indicies].plot(kind='bar', figsize=(10, 10))
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
        activities = pd.read_sql_query("SELECT * from activities a JOIN activity_names an ON a.activity_id=an.id WHERE an.challenge=1 AND a.user_id="+str(user_id), con)
        # activities = activities.merge(self.activity_names[['id', 'challenge', 'name']], left_on="activity_id", right_on="id",
        #                               how="inner")

        activities['date'] = activities.start_time.apply(lambda x: pd.Timestamp(x).strftime("%m-%d-%y"))

        grouped = activities[~activities.activity_id.isin([0, 9])].groupby(by=["date", "name"]).duration.sum()

        range_ = pd.date_range(end=pd.to_datetime("today").strftime("%m/%d/%y"), periods=14)

        indicies = pd.Series(range_).apply(lambda x: pd.Timestamp(x).strftime("%m-%d-%y"))

        sns.set()
        ax = grouped.loc[indicies, :].unstack().plot(kind='bar', figsize=(10, 10), stacked=True)
        ax.set_xlabel('Дата')
        ax.set_ylabel('Время с пользой (часов)')
        ax.set_title('Время с пользой по дням пользователя %s' % (DB.get_user_by_id(user_id)['username']))

    @plot_and_return
    @with_connection
    def plot_all_time(self, user_id, con):
        activities = pd.read_sql_query(
            "SELECT * from activities a JOIN activity_names an ON a.activity_id=an.id WHERE a.user_id=" + str(
                user_id), con)

        activities['date'] = activities.start_time.apply(lambda x: pd.Timestamp(x).strftime("%m-%d-%y"))

        grouped = activities[~activities.activity_id.isin([0, 9])].groupby(by=["date", "name"]).duration.sum()

        range_ = pd.date_range(end=pd.to_datetime("today").strftime("%m/%d/%y"), periods=14)

        indicies = pd.Series(range_).apply(lambda x: pd.Timestamp(x).strftime("%m-%d-%y"))

        sns.set()
        ax = grouped.loc[indicies, :].unstack().plot(kind='bar', figsize=(10, 10), stacked=True)
        ax.set_xlabel('Дата')
        ax.set_ylabel('Время (часов)')
        ax.set_title('Все занятия пользователя %s' % (DB.get_user_by_id(user_id)['username']))

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
            return "?", "?"

        mean = ":".join(self.seconds_to_str(activities.duration.mean() * 60 * 60))
        std = ":".join(self.seconds_to_str(activities.duration.std() * 60 * 60))

        return mean, std

    @with_connection
    def get_average_sleep_start_time(self, user_id, con):
        activities = pd.read_sql_query("SELECT * from activities WHERE activity_id=9 AND user_id=" + str(user_id), con)

        if activities.shape[0] == 0:
            return "?", "?"

        seconds = activities.start_time.apply(self.to_seconds)
        time = seconds[~seconds.between(60 * 60 * 6, 60 * 60 * 19)]

        if len(time) == 0:
            return "?", "?"

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
            return "?", "?"

        seconds = activities.apply(get_seconds, axis=1)

        time = seconds[seconds.between(60 * 60 * 5, 60 * 60 * 14)]

        if len(time) == 0:
            return "?", "?"


        mean = ":".join(self.seconds_to_str(time.mean()))
        std = ":".join(self.seconds_to_str(np.std(time)))

        return mean, std

    def legend_positions(self, df, y):
        """ Calculate position of labels to the right in plot... """
        positions = {}
        for column in y:
            positions[column] = df[column].values[-1] - 0.5

        def push():
            """
            ...by puting them to the last y value and
            pushing until no overlap
            """
            collisions = 0
            for column1, value1 in positions.items():
                for column2, value2 in positions.items():
                    if column1 != column2:
                        dist = abs(value1 - value2)
                        if dist < 2.5:
                            collisions += 1
                            if value1 < value2:
                                positions[column1] -= .1
                                positions[column2] += .1
                            else:
                                positions[column1] += .1
                                positions[column2] -= .1
                            return True

        while True:
            pushed = push()
            if not pushed:
                break

        return positions

    @plot_and_return
    @with_connection
    def plot_rating(self, state, chat_id, con):
        data = pd.read_sql("SELECT act.*, an.name, an.challenge, u.username FROM activities act "
                           "JOIN activity_names an ON act.activity_id=an.id "
                           "JOIN users u ON act.user_id=u.user_id "
                           "WHERE act.user_id IN "
                            "(SELECT u.user_id FROM users_chats uc "
                            "JOIN users u on uc.user_id = u.user_id "
                            "WHERE uc.chat_id=%s)" % chat_id, con)
        data['date'] = data.start_time.apply(lambda x: pd.Timestamp(x).strftime("%m-%d-%y"))
        grouped = data[data.challenge == 1].groupby(by=['date', 'username']).duration.sum()
        df = pd.DataFrame(grouped).reset_index()
        df['date'] = df.date.apply(pd.to_datetime)

        tod = datetime.datetime.now()
        d = datetime.timedelta(days=int(state['days']))
        a = tod - d


        df = df[df.date >= a.strftime('%Y-%m-%d')].set_index(['date', 'username']).unstack().fillna(0).cumsum()
        days = (df.index[-1:] - df.index[0]).days[0]
        df.reset_index(inplace=True)

        x = 'date'

        row = df.iloc[-1:].T

        y = list(row[row.columns[0]].iloc[1:].sort_values(ascending=False)[:int(state['members'])].index.droplevel())
        cols = list(df.columns.droplevel())
        cols[0] = 'date'
        df.columns = cols

        positions = self.legend_positions(df, y)

        cmap = plt.cm.get_cmap('Dark2', len(y))

        fig, ax = plt.subplots(1, 1, figsize=(11, 8))
        fig.subplots_adjust(left=.1, right=.83, bottom=0.2, top=.94)

        for i, (column, position) in enumerate(positions.items()):
            # Get a color
            color = cmap(float(i) / len(positions))
            # Plot each line separatly so we can be explicit about color
            df.plot(x=x, y=column, linewidth=3, legend=False, ax=ax, color=color)

            # Add the text to the right
            plt.text(
                df[x][df[column].last_valid_index()] + pd.Timedelta("1 days"),
                position, column, fontsize=12,
                color=color  # Same color as line
            )
        ax.set_ylabel('Часов с пользой')
        ax.set_xlabel('Дата')
        # Add percent signs
        # ax.set_yticklabels(['{:3.0f}%'.format(x) for x in ax.get_yticks()])
        ax.set_title("Изменение рейтинга участников чата со временем")
        # sns.despine()


Data = DataMethods()