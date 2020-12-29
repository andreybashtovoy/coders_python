import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import json

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
        durations = \
        pd.read_sql_query("SELECT * from activities WHERE activity_id=9 and user_id=" + str(user_id),
                          con)['duration']

        sns.set_style("darkgrid")
        sns.set_color_codes()
        sns.distplot(durations, color='y')

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




Data = DataMethods()