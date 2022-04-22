import aiomysql
from aiomysql import Connection, DictCursor, Pool

import config

pool: Pool


async def new_cursor():
    conn: Connection = await pool.acquire()
    cur: DictCursor = await conn.cursor(DictCursor)
    return conn, cur


async def create_pool():
    global pool
    pool = await aiomysql.create_pool(host=config.mysql_host, port=3306,
                                      user=config.mysql_user, password=config.mysql_password,
                                      db=config.mysql_dbname, charset='utf8')


async def release_conn(conn):
    await pool.release(conn)
