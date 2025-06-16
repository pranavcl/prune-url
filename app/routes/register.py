import datetime

from flask import render_template, Blueprint, request
from app import conn, cur, logger, limiter, INTERNAL_SERVER_ERROR_MSG
from validators import email
from traceback import print_exc
from bcrypt import gensalt, hashpw

register_bp = Blueprint("register", __name__)

GO_BACK = "<br><a href=\"/register\">Go back</a>"

@register_bp.route("/register")
def get_register():
    return render_template("register.html")

@register_bp.route("/register", methods=["POST"])
@limiter.limit("5 per day")
def post_register():
    email_input = request.form.get("email")
    password = request.form.get("password")
    repeat_password = request.form.get("repeat-password")

    if not email_input or not password or not repeat_password:
        return render_template("message.html", message = f"Please enter all fields.{GO_BACK}"), 400
    
    if len(email_input) < 6 or len(email_input) > 128 or len(password) < 6 or len(password) > 128 or len(repeat_password) < 6 or len(repeat_password) > 128:
        return render_template("message.html", message = f"Email and password must be between 6 and 128 characters long.{GO_BACK}"), 400

    if password != repeat_password:
        return render_template("message.html", message = f"Passwords don't match.{GO_BACK}"), 400

    if not email(email_input):
        return render_template("message.html", message = f"Please enter a valid email address.{GO_BACK}"), 400
    
    email_input = email_input.lower()

    try:
        cur.execute("SELECT * FROM users WHERE email=%s", (email_input,))
        records = cur.fetchone()

        if records:
            return render_template("message.html", message = f"Email address is already registered.{GO_BACK}"), 400
    except Exception:
        print_exc()
        logger.error(f"⛔ Failed to fetch users")
        return render_template("message.html", message = INTERNAL_SERVER_ERROR_MSG), 500

    
    # Put stuff in postgres

    try:
        salt = gensalt()
        password = password.encode("utf-8")
        hashedPassword = hashpw(password, salt).decode("utf-8")

        cur.execute("INSERT INTO users VALUES (%s, %s, 'user', 0, 100, %s)", (email_input, hashedPassword, str(datetime.datetime.now())))
        conn.commit()
        logger.info(f"✨ New user registered with email {email_input}")
        return render_template("message.html", message = "Account registered successfully! You can login now.<br><a href=\"/\">Return to home</a>")
    except Exception:
        print_exc()
        logger.error(f"⛔ Registration of {email_input} failed!")
        return render_template("message.html", message = INTERNAL_SERVER_ERROR_MSG), 500
