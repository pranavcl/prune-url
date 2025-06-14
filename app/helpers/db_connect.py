from os import environ
from logging import Logger
from psycopg2 import connect
from traceback import print_exc

# Connect to database

def db_connect(logger: Logger):
    db_host = environ.get("DB_HOST", "localhost")
    db_port = environ.get("DB_PORT", 5432)
    db_name = environ.get("DB_NAME", "pruneurl")
    db_user = environ.get("DB_USER", "postgres")

    conn = None

    try:
        logger.info(f"⏳ Attempting to connect to database `{db_name}` on {db_host}:{db_port} with user `{db_user}`")
        conn = connect(
            host=db_host,
            port=db_port,
            dbname = db_name,
            user = db_user,
            password = environ.get("DB_PASS")
        )
        logger.info(f"✅ Successfully connected to database")
    except Exception:
        logger.error(print_exc())
        logger.error(f"⛔ Failed to connect to database `{db_name}` on {db_host}:{db_port} with user `{db_user}`")
        exit()

    cur = conn.cursor()

    # Create required tables

    try:
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
        records = cur.fetchall()
        
        if ("links",) not in records:
            cur.execute("CREATE TABLE links (short_url varchar, redirect varchar, visits int)")
            conn.commit()
            logger.info("✅ Created required table(s)")
        else:
            logger.info("✅ Required tables already exist")
    except Exception:
        logger.error(print_exc())
        logger.error(f"⛔ Failed to create required table(s)")
        exit()

    return (conn, cur)