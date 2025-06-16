from flask import Blueprint, request, render_template
from app.helpers.check_jwt import check_jwt
from traceback import print_exc
from app import links_length, logger, INTERNAL_SERVER_ERROR_MSG, cur, conn

delete_bp = Blueprint("delete", __name__)

GO_BACK = "<br><a href=\"/\">Return to home</a>"

@delete_bp.route("/delete/<string:link>", methods=["POST"])
def delete_delete(link: str):
    jwt_token = check_jwt(request.cookies.get("token"))

    if jwt_token == "none":
        return render_template("message.html", message = f"You are not logged in.{GO_BACK}"), 401
    
    if jwt_token == "expired":
        return render_template("message.html", message = f"Your token has expired. Please login again.{GO_BACK}"), 401
    
    if jwt_token == "invalid":
        return render_template("message.html", message = f"Your token is invalid. Please login again.{GO_BACK}"), 401
    
    if not link:
        return render_template("message.html", message = f"No link supplied.{GO_BACK}"), 400
    
    if len(link) != links_length:
        return render_template("message.html", message = f"Invalid link.{GO_BACK}"), 400
    
    try:
        cur.execute("SELECT * FROM links WHERE short_url = %s AND made_by = %s;", (link, jwt_token["email"]))
        records = cur.fetchall()

        if not records:
            return render_template("message.html", message = f"Link not found.{GO_BACK}"), 400

        cur.execute("DELETE FROM links WHERE short_url = %s AND made_by = %s;", (link, jwt_token["email"]))        
        cur.execute("UPDATE users SET links_made = links_made - 1 WHERE email = %s;", (jwt_token["email"],))
        conn.commit()
    except Exception:
        print_exc()
        logger.error("⛔ Failed to delete link")
        return render_template("message.html", message = INTERNAL_SERVER_ERROR_MSG), 500


    return render_template("message.html", message = "Link successfully deleted.{GO_BACK}")