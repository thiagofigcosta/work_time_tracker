import errno
import os
import sqlite3
from pathlib import Path

wtt_dir = os.path.join(str(Path.home()), ".wtt")
if not os.path.exists(wtt_dir):
    try:
        os.makedirs(wtt_dir)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise e

DATABASE_PATH = os.getenv('DATABASE_NAME', os.path.join(wtt_dir, 'wtt_records.db'))


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def get_db_conn():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = dict_factory
    return conn


def execute_query(query, params=None, fetch=False):
    conn = get_db_conn()
    return execute_query_with_conn(conn, query, params=params, fetch=fetch, close_conn=True)


def execute_query_with_conn(conn, query, params=None, fetch=False, close_conn=True):
    if params is None:
        params = tuple([])
    cur = conn.cursor()
    results = None
    if fetch:
        results = cur.execute(query, params).fetchall()
    else:
        cur.execute(query, params)
    conn.commit()
    cur.close()
    if close_conn:
        conn.close()
    if fetch:
        return results


def build_database():
    conn = get_db_conn()
    # DEFAULT DATETIME('now', 'UTC') does not work on DEFAULT
    create_profile_table = """
        CREATE TABLE IF NOT EXISTS profiles(
            "uuid" UUID PRIMARY KEY,
            "first_name" VARCHAR(50) NOT NULL,
            "last_name" VARCHAR(50) NOT NULL,
            "company" VARCHAR(50) NOT NULL,
            "working_location" VARCHAR(50) NOT NULL,
            "start_date" DATE NOT NULL,
            "daily_office_hours" INT NOT NULL,
            "required_lunch_time" INT NOT NULL,
            "auto_insert_lunch_time" INT NOT NULL,
            "max_allowed_extra_hours" INT NOT NULL,
            "latest_working_hour" TIME NOT NULL DEFAULT '22:00:00', 
            "min_hours_between_working_days" INT NOT NULL DEFAULT 11, 
            "initial_extra_hours_balance" INT NOT NULL DEFAULT 0,
            "default_timezone" VARCHAR(30) NOT NULL DEFAULT 'America/Sao_Paulo',
            "created_at_utc" DATETIME DEFAULT CURRENT_TIMESTAMP,
            "updated_at_utc" DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """

    create_holidays_table = """
            CREATE TABLE IF NOT EXISTS holidays(
                "uuid" UUID PRIMARY KEY,
                "description" VARCHAR(100) NULL,
                "date" DATE NOT NULL,
                "location" VARCHAR(50) NOT NULL,
                "working_hours" INT NOT NULL DEFAULT 0,
                "repeats_every_year" BOOL DEFAULT True
            );
            """

    create_time_cards_table = """
                CREATE TABLE IF NOT EXISTS time_cards(
                    "uuid" UUID PRIMARY KEY,
                    "profile_uuid" UUID NOT NULL,
                    "event_timestamp_utc" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    "insertion_method" VARCHAR(30) DEFAULT 'manual'
                );
                """

    create_absences_table = """
                CREATE TABLE IF NOT EXISTS absences(
                    "uuid" UUID PRIMARY KEY,
                    "profile_uuid" UUID NOT NULL,
                    "date" DATE NOT NULL,
                    "description" VARCHAR(300) NULL
                );
                """
    execute_query_with_conn(conn, create_profile_table, close_conn=False)
    execute_query_with_conn(conn, create_holidays_table, close_conn=False)
    execute_query_with_conn(conn, create_time_cards_table, close_conn=False)
    execute_query_with_conn(conn, create_absences_table, close_conn=True)


build_database()
