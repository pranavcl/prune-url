import datetime

from flask import render_template, Blueprint, request
from flask_mail import Mail, Message
from app import cur, logger, INTERNAL_SERVER_ERROR_MSG, conn, limiter, app
from os import environ
from bcrypt import gensalt, hashpw
from secrets import token_bytes
from traceback import print_exc
from validators import email

forgot_password_bp = Blueprint("forgot_password", __name__)

SUCCESS_MSG = "If an account with that email exists, a password reset link has been sent."
GO_BACK = "<br><a href=\"/\">Return to home</a>"

@forgot_password_bp.route("/forgot-password")
def get_forgot_password():
    return render_template("forgot-password.html")

@forgot_password_bp.route("/forgot-password", methods=["POST"])
@limiter.limit("3 per hour")
def post_forgot_password():
    email_input = request.form.get("email")

    if not email_input:
        return f"You did not enter an email address.{GO_BACK}", 400
    
    if len(email_input) < 6 or len(email_input) > 128:
        return f"Email address must be between 6 and 128 characters in length.{GO_BACK}", 400

    if not email(email_input):
        return f"Please enter a valid email address.{GO_BACK}", 400
    
    email_input = email_input.lower()
    
    token = None
    hashedToken = None
    expires = None

    try:
        cur.execute("SELECT * FROM users WHERE email = %s", (email_input,))
        records = cur.fetchone()

        if not records:
            return f"{SUCCESS_MSG}{GO_BACK}", 200
        
        token = token_bytes(16).hex()
        hashedToken = hashpw(token.encode("utf-8"), gensalt())
        expires = datetime.datetime.now() + datetime.timedelta(hours=1)
    except Exception:
        print_exc()
        logger.error(f"⛔ Failed to fetch users")
        return INTERNAL_SERVER_ERROR_MSG, 500
    
    url = f"{environ.get("BASE_URL", "http://localhost:2000")}/reset-password?email={email_input}&token={token}"

    try:
        cur.execute("DELETE FROM reset_password WHERE email = %s;", (email_input,))
        cur.execute("INSERT INTO reset_password VALUES (%s, %s, %s)", (email_input, hashedToken.decode("utf-8"), expires))
        conn.commit()
        logger.info(f"🔄 Password reset requested for {email_input}")

        # ONLY FOR DEBUGGING: comment in production
        print(url) 
    except:
        print_exc()
        logger.error(f"⛔ Failed to store reset token")
        return INTERNAL_SERVER_ERROR_MSG, 500
    
    # Implement sending mail

    if not environ.get("MAIL_SERVER") or not environ.get("MAIL_PORT") or not environ.get("MAIL_USERNAME") or not environ.get("MAIL_PASSWORD"):
        return f"This server is not configured to send emails. Please contact your server administrator.{GO_BACK}", 500
    
    try:
        mail = Mail()
        app.config.update( #type: ignore
            MAIL_SERVER=environ.get("MAIL_SERVER"),
            MAIL_PORT=environ.get("MAIL_PORT"),
            MAIL_USE_TLS=True,
            MAIL_USERNAME=environ.get("MAIL_USERNAME"),
            MAIL_PASSWORD=environ.get("MAIL_PASSWORD"),
            MAIL_DEFAULT_SENDER=environ.get("MAIL_USERNAME")
        )
        mail.init_app(app)

        msg = Message(
            subject="Password Reset",
            recipients=[email_input],
            body=f"You requested a password reset. Click the link below to reset your password:\n\n{url}\n\nIf you did not request this, please ignore this email."
        )
        mail.send(msg)
    except Exception:
        print_exc()
        logger.error(f"⛔ Failed to send reset password link")
        return INTERNAL_SERVER_ERROR_MSG, 500

    return f"{SUCCESS_MSG}{GO_BACK}", 200