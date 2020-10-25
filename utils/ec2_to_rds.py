
import pymysql
import os


db_user = os.environ.get('aws_db_user')
db_pass = os.environ.get('aws_db_pass')
db_endp = os.environ.get('aws_db_endpoint')



db = pymysql.connect(f'{db_endp}',f'{db_user}',f'{db_pass}','flaskfinance')
cursor = db.cursor()

query = "CREATE TABLE financetest (no int(5), ticker varchar(10) primary key, company varchar(200),sector varchar(90), industry varchar(250),country varchar(30), market_cap float(25), p_e float(8), price float(8), change_ float(8), volume int(10));"
cursor.execute(query)

cursor.close()
db.close()

print("/home/ubuntu/financials-downloader-bot/downloads/Overview_2020-10-15.csv")
