from flask import Blueprint, request, render_template
from app import links_length, logger, INTERNAL_SERVER_ERROR_MSG, cur, conn
from traceback import print_exc
from app.helpers.check_jwt import check_jwt
from os import environ

delete_link_bp = Blueprint("delete_link", __name__)

GO_BACK = "<br><a href=\"/\">Return to home</a>"

@delete_link_bp.route("/delete-link", methods=["POST"])
def post_delete_link():
    jwt_token = check_jwt(request.cookies.get("token"))

    if jwt_token == "none":
        return render_template("message.html", message = f"You are not logged in.{GO_BACK}"), 401
    
    if jwt_token == "expired":
        return render_template("message.html", message = f"Your token has expired. Please login again.{GO_BACK}"), 401
    
    if jwt_token == "invalid":
        return render_template("message.html", message = f"Your token is invalid. Please login again.{GO_BACK}"), 401
    
    if jwt_token["role"] != "admin":
        return render_template("message.html", message = f"You do not have permission to perform this action.{GO_BACK}"), 401

    link = request.form.get("delete_link")

    if not link:
        return render_template("message.html", message=f"Please enter a link to delete.{GO_BACK}"), 400
    
    if '/' in link:
        link = link.split('/').pop()

    if len(link) != links_length:
        return render_template("message.html", message=f"Link must be exactly {links_length} characters in length.{GO_BACK}"), 400
    
    try:
        cur.execute("SELECT * FROM links WHERE short_url = %s;", (link,))
        records = cur.fetchone()

        if not records:
            return render_template("message.html", message=f"Link does not exist.{GO_BACK}"), 400

        cur.execute("DELETE FROM links WHERE short_url = %s;", (link,))
        cur.execute("UPDATE users SET links_made = links_made - 1 WHERE email = %s;", (records[0],))
        conn.commit()
        logger.info(f"⛓️‍💥 Redirect destroyed: {environ.get("BASE_URL", "http://localhost:2000")}/{link} -> {records[2]}")
    except Exception:
        print_exc()
        logger.error("⛔ Failed to delete link!")
        return render_template("message.html", message=INTERNAL_SERVER_ERROR_MSG), 500

    return render_template("message.html", message = f"Link successfully deleted.{GO_BACK}")