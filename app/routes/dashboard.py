from flask import Blueprint, request, render_template
from app import cur, INTERNAL_SERVER_ERROR_MSG, logger
from app.helpers.check_jwt import check_jwt
from traceback import print_exc
from json import dumps

dashboard_bp = Blueprint("dashboard", __name__)

GO_BACK = "<br><a href=\"/\">Return to home</a>"

@dashboard_bp.route("/dashboard")
def get_dashboard():
    jwt_token = check_jwt(request.cookies.get("token"))

    if jwt_token == "none":
        return render_template("message.html", message = f"You are not logged in.{GO_BACK}"), 401
    
    if jwt_token == "expired":
        return render_template("message.html", message = f"Your token has expired. Please login again.{GO_BACK}"), 401
    
    if jwt_token == "invalid":
        return render_template("message.html", message = f"Your token is invalid. Please login again.{GO_BACK}"), 401
    
    linksUsed=0
    linksLimit=100
    linksData=None
    
    try:
        cur.execute("SELECT * FROM users WHERE email = %s;", (jwt_token["email"],))
        records = cur.fetchone()

        if not records:
            return render_template("message.html", message = INTERNAL_SERVER_ERROR_MSG), 500


        linksUsed=records[3]
        linksLimit=records[4]
    except:
        print_exc()
        logger.error(f"⛔ Failed to fetch users DB")
        return render_template("message.html", message = INTERNAL_SERVER_ERROR_MSG), 500

    
    try:
        cur.execute("SELECT short_url, redirect, visits, created FROM links WHERE made_by = %s;", (jwt_token["email"],))
        linksData = [list(row) for row in cur.fetchmany(100)]
        
        for i in linksData:
            i[3] = str(i[3])
        
        linksData = dumps(linksData)
    except:
        print_exc()
        logger.error(f"⛔ Failed to fetch links DB")
        return render_template("message.html", message = INTERNAL_SERVER_ERROR_MSG), 500


    return render_template("dashboard.html", email=jwt_token["email"], linksUsed=linksUsed, linksLimit=linksLimit, linksData=linksData), 200