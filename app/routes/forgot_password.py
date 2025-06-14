from flask import render_template, Blueprint

forgot_password_bp = Blueprint("forgot_password", __name__)

@forgot_password_bp.route("/forgot-password")
def get_forgot_password():
    return render_template("forgot-password.html")