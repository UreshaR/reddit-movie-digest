# Reddit Movie Digest (r/movies, last 2 days)

Scrapes r/movies for posts + comments from the last 2 days, then uses an
LLM (Groq) to identify the film name and a short description for each post,
and exports the result as a PDF.

## Setup

```powershell
pip install -r requirements.txt
python -m playwright install chromium
```

Create a `.env` file in the project root (not committed to git). On
Windows, avoid `Out-File` for this since it can add a BOM that breaks
parsing — use:

```powershell
[System.IO.File]::WriteAllLines("$pwd\.env", "GROQ_API_KEY=your_groq_key_here")
```

Get a key at https://console.groq.com/keys.

Verify it loads correctly:
```powershell
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(repr(os.environ.get('GROQ_API_KEY')))"
```
This should print your key, not `None`.

## Run order

```powershell
python webscrapping.py        # scrapes last 2 days -> reddit_posts_with_comments.json
python summarize_movies.py    # film name + description -> movie_digest.json
python generate_pdf.py        # formatted report -> movie_digest.pdf
```

That's the entire core pipeline.

## Optional (not required)
- `reddit_collector.py` — an alternate scraper using Reddit's public JSON
  API instead of Playwright. Currently blocked by Reddit (403), kept here
  only as a reference/fallback if that changes.
- `clean_data.py`, `create_embeddings.py`, `build_faiss_index.py`,
  `ask_reddit.py` — builds a semantic search index over the scraped
  comments so you can ask free-form questions (e.g. "what are people
  saying about Scooby-Doo?"). Not needed for the film digest output.

## Adjusting
- Change subreddit or time window: edit `SUBREDDIT_URL` / `HOURS_WINDOW`
  at the top of `webscrapping.py`.
- Change LLM model: edit `MODEL` in `llm_client.py` (any Groq-hosted model,
  e.g. `llama-3.3-70b-versatile`).
- Change PDF styling: edit the style definitions near the top of
  `generate_pdf.py` (fonts, colors, margins).

## Security note
Never commit your `.env` file or hardcode API keys in source. `.gitignore`
already excludes `.env`, `venv/`, and generated JSON/PDF output files. If
a key is ever pasted into a chat, screenshot, or commit history, treat it
as compromised and revoke it at console.groq.com/keys immediately.