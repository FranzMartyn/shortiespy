"""This program contains the routes and starts the server."""

import json  # Everything is stored inside ./data/data.json
import uuid  # For creating the ids at the end of the url

import flask
import requests  # To check whether the URLs actually exist or not


app = flask.Flask(__name__, static_folder="static", template_folder="static")

JSON_FILE = r"data\data.json"
ONE_MINUTE = 60

SITES = ["index", "new", "add", "get"]


def _is_url_valid(url: str) -> bool:
    """Returns True if the URL exists."""
    try:
        is_ok = requests.get(url, timeout=ONE_MINUTE).ok
        if not is_ok:
            return False
    except requests.exceptions.MissingSchema:
        return False
    return True


@app.route("/", methods=["GET"])
def index():
    """The homepage."""
    return flask.redirect(flask.url_for("new"))


@app.route("/new", methods=["GET"])
def new():
    """The site to create a shortened link. The homepage redirects here."""
    return flask.render_template("index.html")


@app.route("/add", methods=["POST"])
def add():
    """This checks if the url exists and generates the shorties link"""
    url = flask.request.form["url"]
    if not _is_url_valid(url):
        return flask.render_template("badurl.html",
                                     link=flask.url_for("new"))

    with open(JSON_FILE, "r", encoding="utf8") as json_file_read:
        all_urls = json.loads(json_file_read.read())

    urls = list(all_urls.keys())
    url_id = ""
    while not url_id or url_id in urls:
        url_id = str(uuid.uuid4())[0:8]

    all_urls[url_id] = url

    with open(JSON_FILE, "w", encoding="utf8") as json_file_write:
        json.dump(all_urls, json_file_write)

    OPEN_URL_IN_ANOTHER_TAB = True
    return flask.render_template("successful.html",
                                 shortie=flask.url_for(
                                     "get",
                                     urlid=url_id,
                                     _external=OPEN_URL_IN_ANOTHER_TAB))


@app.route("/s/<urlid>", methods=["GET"])
def get(urlid):
    """The endpoint of the shortened links."""
    with open(JSON_FILE, "r", encoding="utf8") as json_file_read:
        all_urls = json.loads(json_file_read.read())
    url = all_urls.get(urlid)

    if not url:
        return flask.render_template("badshortie.html",
                                     link=flask.url_for("new"))
    return flask.redirect(url)

@app.before_request
def check_if_site_exists():
    print("before request")
    print(flask.request.endpoint)
    if not flask.request.endpoint:
        new_site = flask.url_for("new")
        return flask.render_template("badsite.html", link=new_site), 404

if __name__ == "__main__":
    app.run("localhost", 80, debug=False)
