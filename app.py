import functools
import json
import os
import random
import secrets
import sqlite3
import uuid
from datetime import datetime, timezone

from flask import Flask, Response, g, redirect, render_template, request, session, url_for

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "labels.db")
TWEETS_PATH = os.path.join(BASE_DIR, "data", "tweets.json")
TWEETS_PER_PARTICIPANT = 5
EMOTIONS = ["anger", "fear", "joy", "love", "sadness", "surprise"]

DATA_USERNAME = os.environ.get("DATA_USERNAME", "admin")
DATA_PASSWORD = os.environ.get("DATA_PASSWORD", "changeme")

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")


def require_data_auth(view):
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        auth = request.authorization
        valid = (
            auth is not None
            and secrets.compare_digest(auth.username, DATA_USERNAME)
            and secrets.compare_digest(auth.password, DATA_PASSWORD)
        )
        if not valid:
            return Response(
                "Authentication required.",
                401,
                {"WWW-Authenticate": 'Basic realm="Collected data"'},
            )
        return view(*args, **kwargs)

    return wrapped

with open(TWEETS_PATH, encoding="utf-8") as f:
    TWEETS = json.load(f)
TWEETS_BY_ID = {t["id"]: t for t in TWEETS}


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DB_PATH)
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS labels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            participant_id TEXT NOT NULL,
            tweet_id INTEGER NOT NULL,
            tweet_text TEXT NOT NULL,
            chosen_label TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
        """
    )
    db.commit()
    db.close()


@app.route("/")
def instructions():
    return render_template("instructions.html")


@app.route("/start")
def start():
    session["participant_id"] = uuid.uuid4().hex[:8]
    session["assigned_ids"] = random.sample(list(TWEETS_BY_ID.keys()), TWEETS_PER_PARTICIPANT)
    session["current_index"] = 0
    return redirect(url_for("label"))


@app.route("/label", methods=["GET", "POST"])
def label():
    if "assigned_ids" not in session:
        return redirect(url_for("instructions"))

    assigned_ids = session["assigned_ids"]
    index = session["current_index"]

    if request.method == "POST":
        chosen_label = request.form.get("emotion")
        if chosen_label not in EMOTIONS:
            return redirect(url_for("label"))

        tweet_id = assigned_ids[index]
        tweet = TWEETS_BY_ID[tweet_id]

        db = get_db()
        db.execute(
            "INSERT INTO labels (participant_id, tweet_id, tweet_text, chosen_label, timestamp) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                session["participant_id"],
                tweet_id,
                tweet["text"],
                chosen_label,
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        db.commit()

        session["current_index"] = index + 1
        return redirect(url_for("label"))

    if index >= TWEETS_PER_PARTICIPANT:
        return redirect(url_for("done"))

    tweet = TWEETS_BY_ID[assigned_ids[index]]
    return render_template(
        "label.html",
        tweet=tweet,
        emotions=EMOTIONS,
        current=index + 1,
        total=TWEETS_PER_PARTICIPANT,
    )


@app.route("/done")
def done():
    if "assigned_ids" not in session or session.get("current_index", 0) < TWEETS_PER_PARTICIPANT:
        return redirect(url_for("instructions"))
    participant_id = session["participant_id"]
    session.clear()
    return render_template("done.html", participant_id=participant_id)


@app.route("/data")
@require_data_auth
def data():
    db = get_db()
    rows = db.execute(
        "SELECT id, participant_id, tweet_id, tweet_text, chosen_label, timestamp "
        "FROM labels ORDER BY id DESC"
    ).fetchall()
    return render_template("data.html", rows=rows)


init_db()

if __name__ == "__main__":
    app.run(debug=True)
