import random
from string import ascii_uppercase, ascii_lowercase, digits
from traceback import print_exc
from psycopg2 import extensions
from logging import Logger

def gen_random_string(n: int, cur: extensions.cursor, logger: Logger):
    random_string = ""
    while True:
        random_string = "".join(random.choices(ascii_uppercase + ascii_lowercase + digits, k=n))

        records = None
        try:
            cur.execute("SELECT * FROM links WHERE short_url = %s", (random_string,))
            records = cur.fetchall()
        except Exception:
            logger.error(print_exc())
            logger.error("⛔ Failed to fetch links from DB")
            return None

        if not records:
            break

    return random_string