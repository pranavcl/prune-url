import datetime

from jwt import encode
from typing import Any
from flask import render_template, Blueprint, request, make_response
from validators import email
from traceback import print_exc
from app import cur, logger, INTERNAL_SERVER_ERROR_MSG, limiter, jwt_secret_key
from bcrypt import checkpw

login_bp = Blueprint("login", __name__)

GO_BACK = "<br><a href=\"/login\">Go back</a>"

@login_bp.route("/login")
def get_login():
    return render_template("login.html")

@login_bp.route("/login", methods=["POST"])
@limiter.limit("3 per hour")
def post_login():
    email_input = request.form.get("email")
    password = request.form.get("password")

    if not email_input or not password:
        return render_template("message.html", message = f"Please enter all fields.{GO_BACK}"), 400
    
    if len(email_input) < 6 or len(email_input) > 128 or len(password) < 6 or len(password) > 128:
        return render_template("message.html", message = f"Email and password must be between 6 and 128 characters long.{GO_BACK}"), 400

    if not email(email_input):
        return render_template("message.html", message = f"Please enter a valid email address.{GO_BACK}"), 400
    
    email_input = email_input.lower()
    
    try:
        cur.execute("SELECT * FROM users WHERE email = %s", (email_input,))
        records = cur.fetchone()

        if not records:
            return render_template("message.html", message = f"Invalid username or password.{GO_BACK}"), 400
        
        password = password.encode("utf-8")
        password_db = records[1].encode("utf-8")

        if not checkpw(password, password_db):
            return render_template("message.html", message = f"Invalid username or password.{GO_BACK}"), 400
        
        payload: dict[str, Any] = {
            "email": email_input,
            "role": records[2],
            "exp": datetime.datetime.now() + datetime.timedelta(days=14)
        }

        encoded_jwt:bytes = encode(payload, jwt_secret_key, algorithm="HS256")

        response = make_response(render_template("message.html", message = "Logged in successfully.<br><a href=\"/dashboard\">Proceed to dashboard</a>"))
        response.set_cookie("token", str(encoded_jwt))

        return response

    except Exception:
        print_exc()
        logger.error(f"⛔ Failed to login {email_input}!")
        return render_template("message.html", message = INTERNAL_SERVER_ERROR_MSG), 500

