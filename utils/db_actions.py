# - *- coding: utf- 8 - *-
import psycopg

from config import DB_NAME, HOST, PASSWORD, USER


async def is_user(tg_id):
    async with await psycopg.AsyncConnection.connect(user=USER, password=PASSWORD, host=HOST, dbname=DB_NAME) as aconn:
        async with aconn.cursor() as cur:
            await cur.execute('SELECT user_id FROM users WHERE tg_id = %s', (tg_id,))
            user_id = await cur.fetchone()
            return user_id


async def add_user(tg_id, username):
    async with await psycopg.AsyncConnection.connect(user=USER, password=PASSWORD, host=HOST, dbname=DB_NAME) as aconn:
        async with aconn.cursor() as cur:
            await cur.execute('INSERT INTO users (tg_id, tg_username) VALUES (%s, %s)', (tg_id, username))
            await aconn.commit()
