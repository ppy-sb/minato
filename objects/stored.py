import aiomysql
from aiomysql import Connection, DictCursor, Pool
from contextlib import asynccontextmanager


import config

pool: Pool = None


@asynccontextmanager
async def db_context():
    global pool
    try:
        conn: Connection = await pool.acquire()
        cur: DictCursor = await conn.cursor(DictCursor)
        yield conn, cur
    finally:
        await cur.close()
        await pool.release(conn)


async def create_pool():
    global pool
    if pool is not None:
        return
    pool = await aiomysql.create_pool(
        host=config.mysql_host,
        port=3306,
        user=config.mysql_user,
        password=config.mysql_password,
        db=config.mysql_dbname,
        charset="utf8",
        autocommit=True,
    )
