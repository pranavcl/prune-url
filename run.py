from app import app, logger
from os import environ

# Start up the server

if __name__ == "__main__":
    logger.info(f"✅ Server started on port {environ.get("PORT", 2000)}")
    from waitress import serve
    serve(app, host="127.0.0.1", port=environ.get("PORT", 2000))