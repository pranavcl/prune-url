import validators

from flask import Blueprint, request
from html import escape
from traceback import print_exc
from os import environ

from app import limiter, conn, cur, logger, INTERNAL_SERVER_ERROR_MSG
from app.helpers.utils import gen_random_string

prune_bp = Blueprint("prune", __name__)

# POST /prune

@prune_bp.route("/prune", methods=["POST"])
@limiter.limit("20 per hour")
def prune_url():
    url: str = escape(request.form.get("url") or "")

    if not url:
        return "No URL provided<br><a href=\"/\">Return to home</a>", 400
    
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    if not validators.url(url):
        return "Invalid URL<br><a href=\"/\">Return to home</a>", 400

    random_string = gen_random_string(5, cur, logger)

    if not random_string:
        return INTERNAL_SERVER_ERROR_MSG, 500

    try:
        cur.execute("INSERT INTO links VALUES (%s, %s, %s)", (random_string, url, 0))

        conn.commit()
    except Exception:
        logger.error(print_exc())
        logger.error("⛔ Failed to insert link into DB")
        return INTERNAL_SERVER_ERROR_MSG, 500

    full_url = f"{environ.get("BASE_URL", "http://localhost")}:{environ.get("PORT", 2000)}/{random_string}" 
    logger.info(f"🔗 Redirect created: {full_url} -> {url}")

    return f"Here\'s your pruned URL:<br><a target=\"_blank\" href=\"{full_url}\">{full_url}</a><br><br><a href=\"/\">Return to home</a>", 200

@prune_bp.route("/prune", methods=["GET"])
def error():
    return "Send a POST request to this endpoint<br><a href=\"/\">Return to home</a>"
