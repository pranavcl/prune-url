import flask
import flask_limiter
import redis

from dotenv import load_dotenv
import os
import random
import string
import validators
import logging
import html

load_dotenv()

app = flask.Flask(__name__)
limiter = flask_limiter.Limiter(
    flask_limiter.util.get_remote_address, 
    app=app,
    storage_uri=f"{os.environ.get("REDIS", "redis://localhost:11211")}",
    #storage_options={"socket_connect_timeout": 30},
    #strategy="fixed-window", # or "moving-window" or "sliding-window-counter"
    )

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

urlMaps = dict()

class LinkRedirect:
    def __init__(self, link):
        self.link = link
        self.visits = 0

@app.route("/")
def serve_index():
    return flask.render_template("index.html")

@app.route("/<string:link>")
def redirect(link):
    if link not in urlMaps:
        return "Requested URL was not found<br><a href=\"/\">Return to home</a>", 404
    
    urlMaps[link].visits += 1
    logger.info(f"🛫 Redirecting {os.environ.get("BASE_URL", "http://localhost")}:{os.environ.get("PORT", 2000)}/{link} -> {urlMaps[link].link} ({urlMaps[link].visits} visits)")

    #return flask.redirect(urlMaps[link].link)
    return flask.render_template("redirect_warning.html", target_url=urlMaps[link].link)

def gen_random_string(n):
    random_string = ""
    while True:
        random_string = "".join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=n))
        if bytes not in urlMaps:
            break

    return random_string

@app.route("/prune", methods=["POST"])
@limiter.limit("20 per hour")
def prune_url():
    url = html.escape(flask.request.form.get("url"))

    if not url:
        return "No URL provided<br><a href=\"/\">Return to home</a>", 400
    
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    if not validators.url(url):
        return "Invalid URL<br><a href=\"/\">Return to home</a>", 400

    random_string = gen_random_string(5)
    urlMaps[random_string] = LinkRedirect(url)

    full_url = f"{os.environ.get("BASE_URL", "http://localhost")}:{os.environ.get("PORT", 2000)}/{random_string}" 

    logger.info(f"🔗 Redirect created: {full_url} -> {url}")

    return f"Here\'s your pruned URL:<br><a target=\"_blank\" href=\"{full_url}\">{full_url}</a><br><br><a href=\"/\">Return to home</a>", 200

@app.route("/prune", methods=["GET"])
def error():
    return "Send a POST request to this endpoint<br><a href=\"/\">Return to home</a>"

if __name__ == "__main__":
    logger.info(f"✅ Server started on port {os.environ.get("PORT", 2000)}")
    from waitress import serve
    serve(app, host="127.0.0.1", port=os.environ.get("PORT", 2000))