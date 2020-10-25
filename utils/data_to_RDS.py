import pymysql
import os


db_user = os.environ.get('aws_db_user')
db_pass = os.environ.get('aws_db_pass')
db_endp = os.environ.get('aws_db_endpoint')



db = pymysql.connect(host=f'{db_endp}',user=f'{db_user}',password=f'{db_pass}',database='flaskfinance',local_infile=True)
cursor = db.cursor()

query = """
LOAD DATA LOCAL INFILE 'Overview.csv'
INTO TABLE financetest
COLUMNS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
ESCAPED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES\
(no, ticker, company, sector, industry, country, market_cap, p_e, price, change_, volume);
"""
cursor.execute(query)
cursor.execute("UPDATE financetest SET market_cap = NULLIF(market_cap, ''), p_e = NULLIF(p_e, '');")
db.commit()
cursor.close()
db.close()


