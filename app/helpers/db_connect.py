from os import environ
from logging import Logger
from psycopg2 import connect
from traceback import print_exc
from bcrypt import hashpw, gensalt

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

        if ("links",) in records and ("users",) in records and ("reset_password",) in records:
            logger.info("✅ Required tables already exist")
            return (conn, cur)
        
        if ("links",) not in records:
            cur.execute("CREATE TABLE links (made_by varchar, short_url varchar, redirect varchar, visits int, created timestamp);")
            conn.commit()
            logger.info("✅ Created links table")

        if ("users",) not in records:
            cur.execute("CREATE TABLE users (email varchar, password varchar, role varchar, links_made int, links_limit int, created timestamp, total_views int);")

            logger.info("ℹ️ You can login to the admin panel with the email `a@a.com`")

            if not environ.get("ADMIN_PASS"):
                logger.info(f"⚠️ No ADMIN_PASS environment variable set, using default password `admin1`. You should change this in your .env file.")

            admin_password= environ.get("ADMIN_PASS", "admin1")
            hashed_admin_password = hashpw(admin_password.encode('utf-8'), gensalt()).decode('utf-8')

            cur.execute(f"INSERT INTO users VALUES ('a@a.com', {environ.get("ADMIN_PASS", f"'{hashed_admin_password}'")}, 'admin', 0, 2147483646, NOW(), 0);")
            conn.commit()
            logger.info("✅ Created users table")

        if ("reset_password",) not in records:
            cur.execute("CREATE TABLE reset_password (email varchar, hashed_token varchar, expires timestamp);")
            conn.commit()
            logger.info("✅ Created reset_password table")
    except Exception:
        logger.error(print_exc())
        logger.error(f"⛔ Failed to create required table(s)")
        exit()

    return (conn, cur)