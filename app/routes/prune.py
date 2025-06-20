import datetime

from validators import url
from flask import Blueprint, request, render_template
from html import escape
from traceback import print_exc
from os import environ

from app import limiter, conn, cur, logger, INTERNAL_SERVER_ERROR_MSG, links_length
from app.helpers.utils import gen_random_string
from app.helpers.check_jwt import check_jwt

prune_bp = Blueprint("prune", __name__)

GO_BACK = "<br><a href=\"/\">Return to home</a>"

# POST /prune

@prune_bp.route("/prune", methods=["POST"])
@limiter.limit("20 per hour")
def prune_url():
    jwt_token = check_jwt(request.cookies.get("token"))

    if jwt_token == "none":
        return render_template("message.html", message = f"You are not logged in.{GO_BACK}"), 401
    
    if jwt_token == "expired":
        return render_template("message.html", message = f"Your token has expired. Please login again.{GO_BACK}"), 401
    
    if jwt_token == "invalid":
        return render_template("message.html", message = f"Your token is invalid. Please login again.{GO_BACK}"), 401

    url_input: str = escape(request.form.get("url") or "")

    if not url_input:
        return render_template("message.html", message = f"No URL provided.{GO_BACK}"), 400
    
    if not url_input.startswith("http://") and not url_input.startswith("https://"):
        url_input = "https://" + url_input

    if not url(url_input):
        return render_template("message.html", message = f"Invalid URL.{GO_BACK}"), 400

    random_string = gen_random_string(links_length, cur, logger)

    if not random_string:
        return render_template("message.html", message = INTERNAL_SERVER_ERROR_MSG), 500

    try:
        cur.execute("SELECT * FROM users WHERE email = %s", (jwt_token["email"],))
        records = cur.fetchone()

        if records is None:
            return render_template("message.html", message = INTERNAL_SERVER_ERROR_MSG), 500

        
        if records[3] >= records[4]:
            return render_template("message.html", message = f"You have ran out of link slots!{GO_BACK}"), 400
        
        cur.execute("UPDATE users SET links_made = links_made + 1 WHERE email = %s", (jwt_token["email"],))
        conn.commit()

        cur.execute("INSERT INTO links VALUES (%s, %s, %s, 0, %s)", (jwt_token["email"], random_string, url_input, str(datetime.datetime.now())))
        conn.commit()
    except Exception:
        logger.error(print_exc())
        logger.error("⛔ Failed to insert link into DB")
        return render_template("message.html", message = INTERNAL_SERVER_ERROR_MSG), 500

    full_url = f"{environ.get("BASE_URL", "http://localhost:2000")}/{random_string}" 
    logger.info(f"🔗 Redirect created: {full_url} -> {url_input}")

    return render_template("message.html", message = f"Here\'s your pruned URL:<br><a target=\"_blank\" href=\"{full_url}\">{full_url}</a><br>{GO_BACK}"), 200

@prune_bp.route("/prune", methods=["GET"])
def error():
    return render_template("message.html", message = f"Send a POST request to this endpoint.{GO_BACK}")
