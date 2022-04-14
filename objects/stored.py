import pymysql
from pymysql import cursors
from pymysql.cursors import DictCursor

import config

db = pymysql.connect(host=config.mysql_host,
                     user=config.mysql_user,
                     password=config.mysql_password,
                     database=config.mysql_dbname)


def new_cursor() -> DictCursor:
    return db.cursor(cursors.DictCursor)
