from flask import Blueprint, request, render_template
from app import cur, INTERNAL_SERVER_ERROR_MSG, logger
from app.helpers.check_jwt import check_jwt
from traceback import print_exc

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
    
    linksUsed=0
    linksLimit=100
    linksData=None
    
    try:
        cur.execute("SELECT * FROM users WHERE email = %s;", (jwt_token["email"],))
        records = cur.fetchone()

        if not records:
            return INTERNAL_SERVER_ERROR_MSG, 500

        linksUsed=records[3]
        linksLimit=records[4]
    except:
        print_exc()
        logger.error(f"⛔ Failed to fetch users DB")
        return INTERNAL_SERVER_ERROR_MSG, 500
    
    try:
        cur.execute("SELECT * FROM links WHERE made_by = %s;", (jwt_token["email"],))
        linksData = cur.fetchmany(100)
    except:
        print_exc()
        logger.error(f"⛔ Failed to fetch links DB")
        return INTERNAL_SERVER_ERROR_MSG, 500

    return render_template("dashboard.html", email=jwt_token["email"], linksUsed=linksUsed, linksLimit=linksLimit, linksData=linksData), 200