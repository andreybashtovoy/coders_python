import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO



def with_connection(func):
    def wrapper(*args, **kwargs):
        con = sqlite3.connect("database.db")
        return_value = func(*args, **kwargs, con=con)
        return return_value

    return wrapper


class DataMethods:

    def __init__(self):
        pass

    @with_connection
    def plot_sleep(self, user_id, con):
        durations = \
        pd.read_sql_query("SELECT * from activities WHERE activity_id=9 and user_id=" + str(user_id),
                          con)['duration']

        sns.set_style("darkgrid")
        sns.set_color_codes()
        sns.distplot(durations, color='y')

        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)

        plt.clf()

        return buf



Data = DataMethods()