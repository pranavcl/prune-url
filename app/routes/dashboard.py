from flask import Blueprint, request, render_template
from app.helpers.check_jwt import check_jwt

dashboard_bp = Blueprint("dashboard", __name__)

GO_BACK = "<br><a href=\"/\">Return to home</a>"

@dashboard_bp.route("/dashboard")
def get_dashboard():
    jwt_token = check_jwt(request.cookies.get("token"))

    if jwt_token == "none":
        return f"You are not logged in.{GO_BACK}", 401
    
    if jwt_token == "expired":
        return f"Your token has expired. Please login again.{GO_BACK}", 401
    
    if jwt_token == "invalid":
        return f"Your token is invalid. Please login again.{GO_BACK}", 401

    return render_template("dashboard.html", email=jwt_token["email"]), 200