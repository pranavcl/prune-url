import datetime

from flask import Blueprint, render_template, request
from traceback import print_exc
from app import limiter, logger, INTERNAL_SERVER_ERROR_MSG, cur, conn
from bcrypt import hashpw, gensalt, checkpw

reset_password_bp = Blueprint("reset_password", __name__)

RETURN_HOME = "<br><a href=\"/\">Return to home</a>"
GO_BACK = "<br><a href=\"javascript:history.back()\">Go back</a>"

@reset_password_bp.route("/reset-password")
def get_reset_password():
    email_input = request.args.get("email")
    token = request.args.get("token")

    if not email_input or not token:
        return render_template("message.html", message = "Email or token is missing.{RETURN_HOME}"), 400
    
    if len(email_input) < 6 or len(email_input) > 128:
        return render_template("message.html", message = f"Email must be between 6 and 128 characters in length.{RETURN_HOME}"), 400
    
    if len(token) > 128:
        return render_template("message.html", message = f"Token is too long.{RETURN_HOME}"), 400
    
    email_input = email_input.lower()

    return render_template("reset-password.html", email=email_input, token=token)

@reset_password_bp.route("/reset-password", methods=["POST"])
@limiter.limit("5 per day")
def post_reset_password():
    email_input = request.args.get("email")
    token = request.args.get("token")

    password = request.form.get("password")
    confirm_password = request.form.get("confirm-password")

    if not email_input or not token:
        return render_template("message.html", message = f"Email or token is missing.{GO_BACK}"), 400
    
    if len(email_input) < 6 or len(email_input) > 128:
        return render_template("message.html", message = f"Email must be between 6 and 128 characters in length.{GO_BACK}"), 400
    
    if len(token) > 128:
        return render_template("message.html", message = f"Token is too long.{GO_BACK}"), 400
    
    email_input = email_input.lower()
    
    if not password or not confirm_password:
        return render_template("message.html", message = f"Please enter a password.{GO_BACK}"), 400
    
    if password != confirm_password:
        return render_template("message.html", message = f"Passwords must match.{GO_BACK}"), 400
    
    if len(password) < 6 or len(password) > 128:
        return render_template("message.html", message = f"Password must be between 6 and 128 characters in length.{GO_BACK}"), 400
    
    try:
        cur.execute("SELECT * FROM reset_password WHERE email = %s;", (email_input,))
        records = cur.fetchone()
        if not records:
            return render_template("message.html", message = f"Reset password token not found.{RETURN_HOME}"), 404
        
        if datetime.datetime.now() > records[2]:
            return render_template("message.html", message = f"Your password reset link has expired.{RETURN_HOME}"), 400
        
        token_db = records[1].encode("utf-8")
        if not checkpw(token.encode("utf-8"), token_db):
            return render_template("message.html", message = f"Your token is invalid.{RETURN_HOME}"), 400
    except Exception:
        print_exc()
        logger.error(f"⛔ Failed to fetch reset tokens DB")
        return render_template("message.html", message = INTERNAL_SERVER_ERROR_MSG), 500

    try:
        hashedPassword = hashpw(password.encode("utf-8"), gensalt())
        cur.execute("UPDATE users SET password = %s WHERE email = %s;", (hashedPassword.decode("utf-8"),email_input))
        cur.execute("DELETE FROM reset_password WHERE email = %s;", (email_input,))
        conn.commit()
    except Exception:
        print_exc()
        logger.error(f"⛔ Failed to update user password")
        return render_template("message.html", message = INTERNAL_SERVER_ERROR_MSG), 500

    return render_template("message.html", message = f"Password reset successfully.{RETURN_HOME}")