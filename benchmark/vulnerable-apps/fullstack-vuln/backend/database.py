import sqlite3
from pathlib import Path

from backend.config import DATABASE_PATH


def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def execute_query(conn, sql, params=None):
    cur = conn.cursor()
    if params:
        cur.execute(sql, params)
    else:
        cur.execute(sql)
    return cur


def execute_many(conn, sql, params=None):
    cur = conn.cursor()
    if params:
        cur.executemany(sql, params)
    else:
        cur.execute(sql)
    conn.commit()
    return cur


def fetch_one(conn, sql, params=None):
    cur = execute_query(conn, sql, params)
    row = cur.fetchone()
    return dict(row) if row else None


def fetch_all(conn, sql, params=None):
    cur = execute_query(conn, sql, params)
    return [dict(r) for r in cur.fetchall()]
