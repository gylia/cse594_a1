# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this app is (A1-2 of the assignment)

A minimal Flask web app for an emotion-labeling study. See [README.md](README.md) for the live link, run instructions, and project structure.

- Participants label 5 tweets, each randomly sampled from a pool of 72 tweets in `data/tweets.json` (12 per emotion, all six covered: anger, fear, joy, love, sadness, surprise).
- The instructions page explains the task, tweets are shown one at a time, and each submission records which participant labeled which tweet with which label.
- `/data` shows every collected row for grading/screenshot purposes. It has no authentication, matching the assignment's "no auth" scope.

## Commands

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python app.py
```
Then open `http://localhost:5000`. There is no build step or test suite; this stays a single-file Flask app with no framework beyond Flask itself.

## Architecture

- **Single-file Flask app** (`app.py`): no blueprints, no app factory. Keep it minimal per the assignment's own scope.
- **Storage: SQLite**, one table:
  `labels(id, participant_id, tweet_id, tweet_text, chosen_label, timestamp)`.
  Each row is one participant's label for one tweet, storing the full tweet text (not just its ID) so a single row is self-contained proof of what was labeled.
- **Tweet pool**: static, loaded once at startup from `data/tweets.json`. Sampled per-participant (5 random tweets each, no replacement), not shown identically to every participant: the random sampling is a graded requirement, not an implementation detail to simplify away.
- **Participant identity**: no auth. A random ID plus the 5 assigned tweet IDs and current progress are stored in a signed session cookie, so a page reload shows the same tweet instead of re-sampling.
- **Deploy target: Render** (free tier). Its filesystem is ephemeral across deploys and restarts: `labels.db` resets when a new deploy runs, since there's no persistent disk attached. Do test-participant runs and take the `/data` screenshot after the last deploy before submission, not before it.
