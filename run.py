# Imports

from flask import Flask, render_template, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

import traceback

from dotenv import load_dotenv
import os
import random
import string
import validators
import logging
import html

import psycopg2

# Load environment variables from .env file

os.environ.pop("DB_PASS", None)
load_dotenv()

# Python logger

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if not os.environ.get("DB_PASS"):
    logger.error(f"⛔ You have not set the DB_PASS variable in your .env file (password for user {os.environ.get("DB_USER", "postgres")})")
    exit()

# Connect to database

db_host = os.environ.get("DB_HOST", "localhost")
db_port = os.environ.get("DB_PORT", 5432)
db_name = os.environ.get("DB_NAME", "pruneurl")
db_user = os.environ.get("DB_USER", "postgres")

conn = None

try:
    logger.info(f"⏳ Attempting to connect to database `{db_name}` on {db_host}:{db_port} with user `{db_user}`")
    conn = psycopg2.connect(
        host=db_host,
        port=db_port,
        dbname = db_name,
        user = db_user,
        password = os.environ.get("DB_PASS")
    )
    logger.info(f"✅ Successfully connected to database")
except Exception:
    logger.error(traceback.print_exc())
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
except:
    logger.error(traceback.print_exc())
    logger.error(f"⛔ Failed to create required table(s)")
    exit()

# Create Flask app

app = Flask(__name__)

# Rate Limiter

limiter = Limiter(
    get_remote_address, # Limit by IP
    app=app,
    storage_uri=f"{os.environ.get("REDIS", "redis://localhost:11211")}",
    in_memory_fallback_enabled=True
    #storage_options={"socket_connect_timeout": 30},
    #strategy="fixed-window", # or "moving-window" or "sliding-window-counter"
    )

internal_server_error_msg = "An internal server error occured while trying to process your request<br><a href=\"/\">Return to home</a>"

# Helper Functions

def gen_random_string(n: int):
    random_string = ""
    while True:
        random_string = "".join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=n))

        records = None
        try:
            cur.execute("SELECT * FROM links WHERE short_url = %s", (random_string,))
            records = cur.fetchall()
        except:
            logger.error(traceback.print_exc())
            logger.error("⛔ Failed to fetch links from DB")
            return None

        if not records:
            break

    return random_string

# GET /

@app.route("/")
def serve_index():
    return render_template("index.html")

# GET /:link

@app.route("/<string:link>")
def redirect(link: str):
    records = None

    try:
        cur.execute("SELECT * FROM links WHERE short_url = %s", (link,))
        records = cur.fetchone()
    except:
        logger.error(traceback.print_exc())
        logger.error("⛔ Failed to fetch links from DB")
        return internal_server_error_msg, 500

    if not records:
        return internal_server_error_msg, 500

    if link != records[0]:
        return "Requested URL was not found<br><a href=\"/\">Return to home</a>", 404
    
    try:
        cur.execute("UPDATE links SET visits = visits + 1 WHERE short_url = %s", (link,))
    except:
        logger.error(traceback.print_exc())
        logger.error(f"⛔ Failed to increment visits value for {os.environ.get("BASE_URL", "http://localhost")}:{os.environ.get("PORT", 2000)}/{link}")
        return internal_server_error_msg, 500

    logger.info(f"🛫 Redirecting {os.environ.get("BASE_URL", "http://localhost")}:{os.environ.get("PORT", 2000)}/{link} -> {records[1]} ({records[2]} visits)")

    return render_template("redirect_warning.html", target_url=records[1])

# POST /prune

@app.route("/prune", methods=["POST"])
@limiter.limit("20 per hour")
def prune_url():
    url: str = html.escape(request.form.get("url") or "")

    if not url:
        return "No URL provided<br><a href=\"/\">Return to home</a>", 400
    
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    if not validators.url(url):
        return "Invalid URL<br><a href=\"/\">Return to home</a>", 400

    random_string = gen_random_string(5)

    if not random_string:
        return internal_server_error_msg, 500

    try:
        cur.execute("INSERT INTO links VALUES (%s, %s, %s)", (random_string, url, 0))
        if conn is None:
            raise Exception

        conn.commit()
    except:
        logger.error(traceback.print_exc())
        logger.error("⛔ Failed to insert link into DB")
        return internal_server_error_msg, 500

    full_url = f"{os.environ.get("BASE_URL", "http://localhost")}:{os.environ.get("PORT", 2000)}/{random_string}" 
    logger.info(f"🔗 Redirect created: {full_url} -> {url}")

    return f"Here\'s your pruned URL:<br><a target=\"_blank\" href=\"{full_url}\">{full_url}</a><br><br><a href=\"/\">Return to home</a>", 200

# GET /prune

@app.route("/prune", methods=["GET"])
def error():
    return "Send a POST request to this endpoint<br><a href=\"/\">Return to home</a>"

# Start up the server

if __name__ == "__main__":
    logger.info(f"✅ Server started on port {os.environ.get("PORT", 2000)}")
    from waitress import serve
    serve(app, host="127.0.0.1", port=os.environ.get("PORT", 2000))