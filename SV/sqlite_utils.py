import pandas as pd
import sqlite3
import os


def from_csv_to_sqlite3():
    # load data
    df = pd.read_csv(
        f'{os.path.dirname(os.path.realpath(__file__))}\\Overview.csv')
    # strip whitespace from headers
    df.columns = df.columns.str.strip()
    con = sqlite3.connect("US_STOCKS.db")
    # drop data into database
    df.to_sql("OVERVIEW", con)
    con.close()
