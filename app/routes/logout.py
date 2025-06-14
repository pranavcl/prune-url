from flask import Blueprint, make_response

logout_bp = Blueprint("logout", __name__)

@logout_bp.route("/logout")
def get_logout():
    response = make_response("Logged out successfully.<br><a href=\"/\">Return to home</a>")
    response.delete_cookie("token")

    return response