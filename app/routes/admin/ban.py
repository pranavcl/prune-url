from flask import Blueprint, request, render_template
from app import logger, INTERNAL_SERVER_ERROR_MSG, cur, conn
from traceback import print_exc
from app.helpers.check_jwt import check_jwt
from validators import email

ban_bp = Blueprint("ban", __name__)

GO_BACK = "<br><a href=\"/\">Return to home</a>"

@ban_bp.route("/ban", methods=["POST"])
def post_ban():
    jwt_token = check_jwt(request.cookies.get("token"))

    if jwt_token == "none":
        return render_template("message.html", message = f"You are not logged in.{GO_BACK}"), 401
    
    if jwt_token == "expired":
        return render_template("message.html", message = f"Your token has expired. Please login again.{GO_BACK}"), 401
    
    if jwt_token == "invalid":
        return render_template("message.html", message = f"Your token is invalid. Please login again.{GO_BACK}"), 401
    
    if jwt_token["role"] != "admin":
        return render_template("message.html", message = f"You do not have permission to perform this action.{GO_BACK}"), 401

    email_input = request.form.get("ban_email")

    if not email_input:
        return render_template("message.html", message=f"Please enter an email address.{GO_BACK}"), 400
    
    if len(email_input) < 6 or len(email_input) > 128:
        return render_template("message.html", message=f"Email address must be between 6 and 128 characters in length.{GO_BACK}"), 400
    
    if not email(email_input):
        return render_template("message.html", message=f"Please enter a valid email address.{GO_BACK}"), 400
    
    email_input = email_input.lower()
    
    try:
        cur.execute("SELECT * FROM users WHERE email = %s;", (email_input,))
        records = cur.fetchone()
        if not records:
            return render_template("message.html", message=f"No user found with email {email_input}.{GO_BACK}"), 404

        cur.execute("DELETE FROM users WHERE email = %s;", (email_input,))
        cur.execute("DELETE FROM links WHERE made_by = %s;", (email_input,))
        conn.commit()

        logger.info(f"⚖️ {email_input} has been banned")
    except Exception:
        print_exc()
        logger.error(f"⛔ Failed to ban {email_input}")
        return render_template("message.html", message=INTERNAL_SERVER_ERROR_MSG), 500

    return render_template("message.html", message=f"{email_input} has been banned.{GO_BACK}"), 200