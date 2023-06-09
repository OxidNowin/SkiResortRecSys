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


async def add_finding(tg_id, estimate, time, is_closed_question):
    async with await psycopg.AsyncConnection.connect(user=USER, password=PASSWORD, host=HOST, dbname=DB_NAME) as aconn:
        async with aconn.cursor() as cur:
            await cur.execute('SELECT user_id FROM users where tg_id = %s', (tg_id,))
            user_id = await cur.fetchone()
            await cur.execute('INSERT INTO finding (user_id, estimate, response_time, is_closed_question) '
                              'VALUES (%s, %s, %s, %s)',
                              (user_id[0], estimate, time, is_closed_question))
            await aconn.commit()
