import pymysql
import os


db_user = os.environ.get('aws_db_user')
db_pass = os.environ.get('aws_db_pass')
db_endp = os.environ.get('aws_db_endpoint')



db = pymysql.connect(f'{db_endp}',f'{db_user}',f'{db_pass}','flaskfinance')
cursor = db.cursor()

query = "LOAD DATA LOCAL INFILE '/home/ubuntu/financials-downloader-bot/Overview.csv'INTO TABLE financetest COLUMNS TERMINATED BY ',' LINES TERMINATED BY '\n' IGNORE 1 LINES;"

cursor.execute(query)

cursor.close()
db.close()


