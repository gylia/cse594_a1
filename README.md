# Emotion Labeling Task (CSE 594 HAI, Assignment 1, A1-2)

A minimal Flask + SQLite web app where participants label 5 randomly sampled
tweets with one of six emotions (anger, fear, joy, love, sadness, surprise).

**Live link:** https://cse594-a1.onrender.com
**View collected data:** https://cse594-a1.onrender.com/data

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

Deployed on [Render](https://render.com) as a free Web Service:
- **Build command:** `pip install -r requirements.txt`
- **Start command:** `gunicorn app:app`
- **Environment variable:** `SECRET_KEY` (used to sign session cookies)

## Known limitations of the free Render tier

Free Web Services on Render sleep after about 15 minutes of no traffic, and
also have no persistent disk attached. Two things follow from this:

**The link can appear broken on the first visit after it has been idle.**
Waking a sleeping instance can take 30-60+ seconds, and the very first
request during that window sometimes times out or shows an error page
instead of waiting it out. In practice this has happened: a participant
opened the link while the instance was asleep, saw it fail to load, and it
only came back after a retry. If you (or a participant) see this, wait a
few seconds and reload the page. Once the instance is awake, it responds
normally until it goes idle again.

**Collected data resets on redeploys and on spin-down/wake cycles.**
With no persistent disk, `labels.db` is recreated empty both when a new
deploy runs and when the instance restarts after sleeping. Only the rows in
the `labels` table are affected, not the app's code or correctness: once
awake, the labeling flow and `/data` page work exactly as before.

If long-term persistence or more reliable uptime were needed, the fix would
be a paid Render plan (no spin-down, persistent disk) and/or swapping SQLite
for a hosted database with its own free tier (for example Render's own
Postgres, Supabase, or Neon). Neither was necessary for this assignment's
scope.

## Project structure

```
app.py                  Flask app: routes, DB access, session-based sampling
data/tweets.json        The 72-tweet pool (id, text, emotion)
templates/               instructions.html, label.html, done.html, data.html
static/style.css        Shared styling
requirements.txt, Procfile   Dependencies and Render start command
```
