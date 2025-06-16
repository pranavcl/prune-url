from flask import Blueprint, render_template, request
from app import logger, INTERNAL_SERVER_ERROR_MSG, cur
from app.helpers.check_jwt import check_jwt
from traceback import print_exc
from typing import Any
from json import dumps

search_users_bp = Blueprint("search_users", __name__)

GO_BACK = "<br><a href=\"/\">Return to home</a>"

@search_users_bp.route("/search-users")
def get_search_users():
    jwt_token = check_jwt(request.cookies.get("token"))

    if jwt_token == "none":
        return render_template("message.html", message = f"You are not logged in.{GO_BACK}"), 401
    
    if jwt_token == "expired":
        return render_template("message.html", message = f"Your token has expired. Please login again.{GO_BACK}"), 401
    
    if jwt_token == "invalid":
        return render_template("message.html", message = f"Your token is invalid. Please login again.{GO_BACK}"), 401
    
    if jwt_token["role"] != "admin":
        return render_template("message.html", message = f"You do not have permission to perform this action.{GO_BACK}"), 401

    email_regex = request.args.get("search_email")
    page = request.args.get("page")
    sort_by = request.args.get("sort_by")
    sort_order = request.args.get("sort_order")

    # Validate input

    ALLOWED_SORT_BY = {"created", "links_made", "links_limit", "total_views", "email"}
    ALLOWED_SORT_ORDER = {"asc", "desc"}

    sort_by = sort_by if sort_by in ALLOWED_SORT_BY else "created"
    sort_order = sort_order if sort_order in ALLOWED_SORT_ORDER else "asc"

    try:
        if page is not None:
            page = int(page)
        else:
            page = 1
        
        if page < 1:
            page = 1
    except (TypeError, ValueError):
        page = 1

    PAGE_SIZE = 20
    offset = (page - 1) * PAGE_SIZE

    query = "SELECT email, role, links_made, links_limit, created, total_views FROM users"
    params: list[Any] = []

    if email_regex:
        # print(email_regex)
        query += " WHERE email ILIKE %s"
        params.append(f"%{email_regex}%")

    query += f" ORDER BY {sort_by} {sort_order.upper()} LIMIT %s OFFSET %s"
    params.extend([PAGE_SIZE, offset])

    # Get records

    try:
        cur.execute(query, params)
        records = [[str(item) for item in row] for row in cur.fetchall()]
    except Exception:
        print_exc()
        logger.error("⛔ Failed to fetch from users DB")
        return render_template("message.html", message=INTERNAL_SERVER_ERROR_MSG), 500
    
    # Get no. of pages

    count_query = "SELECT COUNT(*) FROM users"
    count_params: list[Any] = []
    total_pages = 0

    if email_regex:
        count_query += " WHERE email ILIKE %s"
        count_params.append(f"%{email_regex}%")

    try:
        cur.execute(count_query, count_params)
        total_users = cur.fetchone()

        if not total_users:
            raise Exception()

        total_pages = (total_users[0] + PAGE_SIZE - 1) // PAGE_SIZE 
    except Exception:
        print_exc()
        logger.error("⛔ Failed to fetch from users DB")
        return render_template("message.html", message=INTERNAL_SERVER_ERROR_MSG), 500

    return render_template("search-users.html", data_users=dumps(records), total_pages=total_pages, current_page=page)