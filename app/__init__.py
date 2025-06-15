# Imports

from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from dotenv import load_dotenv
from os import environ
from logging import basicConfig, getLogger, INFO

from app.helpers.db_connect import db_connect

# Load environment variables from .env file

load_dotenv()

# Python logger

basicConfig()
logger = getLogger(__name__)
logger.setLevel(INFO)

if not environ.get("DB_PASS"):
    logger.error(f"⛔ You have not set the DB_PASS variable in your .env file (password for user {environ.get("DB_USER", "postgres")})")
    exit()

if not environ.get("SECRET_KEY"):
    logger.error(f"⛔ You have not set the SECRET_KEY variable in your .env file (required for issuing JWTs)")
    exit()

conn, cur = db_connect(logger) # Connect to database

INTERNAL_SERVER_ERROR_MSG = "An internal server error occured while trying to process your request<br><a href=\"/\">Return to home</a>"
jwt_secret_key: str = environ.get("SECRET_KEY", "")

# Create Flask app

app = Flask(__name__)

# Rate Limiter

limiter = Limiter(
    get_remote_address, # Limit by IP
    app=app,
    storage_uri=f"{environ.get("REDIS", "redis://localhost:11211")}",
    in_memory_fallback_enabled=True
    #storage_options={"socket_connect_timeout": 30},
    #strategy="fixed-window", # or "moving-window" or "sliding-window-counter"
    )

# Route everything

from app.routes.root import root_bp
from app.routes.prune import prune_bp
from app.routes.login import login_bp
from app.routes.register import register_bp
from app.routes.forgot_password import forgot_password_bp
from app.routes.reset_password import reset_password_bp
from app.routes.dashboard import dashboard_bp
from app.routes.logout import logout_bp

app.register_blueprint(root_bp)
app.register_blueprint(prune_bp)
app.register_blueprint(login_bp)
app.register_blueprint(register_bp)
app.register_blueprint(forgot_password_bp)
app.register_blueprint(reset_password_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(logout_bp)