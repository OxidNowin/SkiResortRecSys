# - *- coding: utf- 8 - *-
import psycopg
from config import DB_NAME, HOST, PASSWORD, USER


def create_tables():
    commands = (
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id SERIAL PRIMARY KEY,
            tg_id INTEGER UNIQUE NOT NULL,
            tg_username VARCHAR(255),
            name VARCHAR(255)            
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS finding (
            finding_id SERIAL PRIMARY KEY,
            user_id INTEGER,
            estimate INTEGER,
            response_time REAL,
            is_closed_question BOOLEAN NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE ON UPDATE CASCADE
        )
        """,
    )
    with psycopg.connect(user=USER, password=PASSWORD, host=HOST, dbname=DB_NAME) as conn:
        with conn.cursor() as cur:
            for com in commands:
                cur.execute(com)
            conn.commit()
