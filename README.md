# Emotion Labeling Task (CSE 594 HAI, Assignment 1, A1-2)

A minimal Flask + SQLite web app where participants label 5 randomly sampled
tweets with one of six emotions (anger, fear, joy, love, sadness, surprise).

**Live link (preferred):** https://gylia.pythonanywhere.com
**View collected data:** https://gylia.pythonanywhere.com/data

This link stays up continuously with no cold start, and collected data
persists across reloads. It is scheduled to expire on **Saturday, October
10, 2026** (PythonAnywhere's free tier requires a monthly login to keep a
site active); it can be renewed by logging in and extending it, but that
will not be done for the purposes of this assignment.

**Backup link:** https://cse594-a1.onrender.com (see limitations below)

## How it works

- `data/tweets.json` holds a pool of 72 tweets (12 per emotion), sourced from
  the [`dair-ai/emotion`](https://huggingface.co/datasets/dair-ai/emotion)
  dataset. Each tweet has a local `id`, its `text`, and its ground-truth
  `emotion` (the ground truth is not shown to participants).
- On `/start`, a participant is assigned a random 8-character ID and 5
  tweets are sampled without replacement from the pool. This assignment is
  stored in a signed session cookie, so reloading a page mid-task shows the
  same tweet rather than reshuffling.
- Each submitted label is written as one row to a `labels` table in SQLite
  (`labels.db`), with columns `id, participant_id, tweet_id, tweet_text,
  chosen_label, timestamp`. Storing the tweet text directly (not just its
  ID) means each row is self-contained: no need to cross-reference
  `data/tweets.json` to see what was labeled.
- `/data` renders every row in that table as an HTML table. It has no
  authentication (matching the assignment's "no auth" scope) and isn't
  linked from the participant-facing pages.

## Running it locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Then open http://localhost:5000. A `labels.db` SQLite file is created
automatically in the project root on first run.

## Deployment

**Primary: [PythonAnywhere](https://www.pythonanywhere.com)** (free "Beginner"
tier), source at `/home/gylia/cse594_a1`, deployed as a manually-configured
WSGI web app rather than through `Procfile`/`gunicorn`. No cold start, data
persists across reloads. Redeploying a code change means `git pull` inside
the PythonAnywhere console, then clicking Reload on the Web tab (no
git-push auto-deploy).

**Backup: [Render](https://render.com)** as a free Web Service:
- **Build command:** `pip install -r requirements.txt`
- **Start command:** `gunicorn app:app`
- **Environment variable:** `SECRET_KEY` (used to sign session cookies)

Free Web Services on Render sleep after about 15 minutes of no traffic and
have no persistent disk. Effect: **any previously collected labels are lost**
whenever the instance sleeps and wakes back up, or whenever a new deploy
runs. A participant opening the link after an idle period will also hit a
~30 second loading screen first, which can look like the link is broken if
they don't wait it out. This is why PythonAnywhere is the preferred link.

## Project structure

```
app.py                  Flask app: routes, DB access, session-based sampling
data/tweets.json        The 72-tweet pool (id, text, emotion)
templates/               instructions.html, label.html, done.html, data.html
static/style.css        Shared styling
requirements.txt, Procfile   Dependencies and Render start command
```
