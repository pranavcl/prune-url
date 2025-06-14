from flask import Blueprint, render_template, redirect, request
from os import environ
from app import logger, cur, INTERNAL_SERVER_ERROR_MSG
from traceback import print_exc
from app.helpers.check_jwt import check_jwt

root_bp = Blueprint("root", __name__)

@root_bp.route("/")
def serve_index():
    jwt_token = request.cookies.get("token")

    if type(check_jwt(jwt_token)) != str:
        return redirect("/dashboard")

    return render_template("index.html")

# GET /:link

@root_bp.route("/<string:link>")
def redirect_link(link: str):
    records = None

    try:
        cur.execute("SELECT * FROM links WHERE short_url = %s", (link,))
        records = cur.fetchone()
    except Exception:
        logger.error(print_exc())
        logger.error("⛔ Failed to fetch links from DB")
        return INTERNAL_SERVER_ERROR_MSG, 500

    if not records:
        return INTERNAL_SERVER_ERROR_MSG, 500

    if link != records[0]:
        return "Requested URL was not found<br><a href=\"/\">Return to home</a>", 404
    
    try:
        cur.execute("UPDATE links SET visits = visits + 1 WHERE short_url = %s", (link,))
    except Exception:
        logger.error(print_exc())
        logger.error(f"⛔ Failed to increment visits value for {environ.get("BASE_URL", "http://localhost")}:{environ.get("PORT", 2000)}/{link}")
        return INTERNAL_SERVER_ERROR_MSG, 500

    logger.info(f"🛫 Redirecting {environ.get("BASE_URL", "http://localhost")}:{environ.get("PORT", 2000)}/{link} -> {records[1]} ({records[2]} visits)")

    return render_template("redirect_warning.html", target_url=records[1])
