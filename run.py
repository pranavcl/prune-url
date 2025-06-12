import flask
from dotenv import load_dotenv
import os
import random
import string
import validators

load_dotenv()

app = flask.Flask(__name__)

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
    print(f"🛫 Redirecting {os.environ.get("BASE_URL", "http://localhost")}:{os.environ.get("PORT", 2000)}/{link} -> {urlMaps[link].link} ({urlMaps[link].visits} visits)")

    return flask.redirect(urlMaps[link].link)

@app.route("/prune", methods=["POST"])
def prune_url():
    url = flask.request.form.get("url")

    if not url:
        return "No URL provided<br><a href=\"/\">Return to home</a>", 400
    
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    if not validators.url(url):
        return "Invalid URL<br><a href=\"/\">Return to home</a>", 400

    bytes = 0
    while True:
        bytes = "".join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=5)) # 916 million possibilities!
        if bytes not in urlMaps:
            break

    urlMaps[bytes] = LinkRedirect(url)

    full_url = f"{os.environ.get("BASE_URL", "http://localhost")}:{os.environ.get("PORT", 2000)}/{bytes}" 

    print(f"🔗 Redirect created: {full_url} -> {url}")

    return f"Here\'s your pruned URL:<br><a target=\"_blank\" href=\"{full_url}\">{full_url}</a><br><br><a href=\"/\">Return to home</a>", 200

@app.route("/prune", methods=["GET"])
def error():
    return "Send a POST request to this endpoint<br><a href=\"/\">Return to home</a>"

if __name__ == "__main__":
    print(f"✅ Server started on port {os.environ.get("PORT", 2000)}")
    from waitress import serve
    serve(app, host="127.0.0.1", port=os.environ.get("PORT", 2000))