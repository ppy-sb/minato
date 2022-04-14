import pymysql
from pymysql import cursors

import config

db = pymysql.connect(host=config.mysql_host,
                     user=config.mysql_user,
                     password=config.mysql_password,
                     database=config.mysql_dbname)
db_cursor = db.cursor(cursors.DictCursor)
