import pymysql
import os


db_user = os.environ.get('aws_db_user')
db_pass = os.environ.get('aws_db_pass')
db_endp = os.environ.get('aws_db_endpoint')



db = pymysql.connect(f'{db_endp}',f'{db_user}',f'{db_pass}','flaskfinance')
cursor = db.cursor()

query = "LOAD DATA LOCAL INFILE 'Overview.csv'\
        INTO TABLE financetest\
        COLUMNS TERMINATED BY ','\
        OPTIONALLY ENCLOSED BY '"'\
        ESCAPED BY '"'\
        LINES TERMINATED BY '\n'\
        IGNORE 1 LINES\
        (no, ticker, company, sector, industry, country, @market_cap, @p_e, price, change_, volume)\
        SET\
        market_cap = NULLIF(@market_cap,''),\
        p_e = NULLIF(@p_e,'');"

cursor.execute(query)

cursor.close()
db.close()


