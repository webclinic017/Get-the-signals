#!/usr/bin/env python3

import pymysql
import os


db_user = os.environ.get('aws_db_user')
db_pass = os.environ.get('aws_db_pass')
db_endp = os.environ.get('aws_db_endpoint')



db = pymysql.connect(f'{db_endp}',f'{db_user}',f'{db_pass}','flaskfinance')
cursor = db.cursor()

query = "CREATE TABLE financetest (no INT(5), ticker VARCHAR(10) PRIMARY KEY, company VARCHAR(200),\
sector VARCHAR(90), industry VARCHAR(250),country VARCHAR(30), market_cap FLOAT(25) DEFAULT NULL,\
p_e FLOAT(8) DEFAULT NULL,price FLOAT(8), change_ FLOAT(8), volume INT(10));"
cursor.execute(query)

cursor.close()
db.close()

print("/home/ubuntu/financials-downloader-bot/downloads/Overview_2020-10-15.csv")
