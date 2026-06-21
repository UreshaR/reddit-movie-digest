# Reddit Movie Digest (r/movies, last 2 days)

## Setup
```bash
pip install -r requirements.txt
export GROQ_API_KEY="your_groq_key_here"   # get one at console.groq.com/keys
```
**Note:** the key that was hardcoded in the old `grok_client.py` is exposed in
your uploaded zip. Rotate/revoke it at console.groq.com/keys, then use the
new key as above.

## What changed vs your original code
- Replaced the Playwright browser scraper with Reddit's public JSON API
  (`reddit_collector.py`). No login, no flaky DOM scraping, and it gives you
  an exact `created_utc` timestamp per post so the "last 2 days" filter is
  exact (not approximate via scrolling/guessing).
- `summarize_movies.py` is the new main script — it's what you asked for:
  for every post from the last 48 hours, it asks the LLM for the film name
  + a short description, using the post + its top comments as context.
- `grok_client.py` -> `llm_client.py`: switched to Groq (matches your `gsk_`
  key), reads the key from an environment variable instead of being
  hardcoded in source.
- `ask_reddit.py` (optional semantic Q&A over embeddings) kept as a bonus,
  also switched to Groq.

## Run order
```bash
# 1. Collect last 2 days of posts + comments from r/movies
python3 reddit_collector.py
# -> reddit_posts_with_comments.json

# 2. Get film name + description per post (the main deliverable)
python3 summarize_movies.py
# -> movie_digest.json + printed list

# --- Optional: semantic search over comments ---
python3 clean_data.py            # -> documents.json
python3 create_embeddings.py     # -> documents_store.json
python3 build_faiss_index.py     # -> reddit.index
python3 ask_reddit.py            # interactive Q&A
```

## Adjusting
- Change subreddit or window: edit `SUBREDDIT` / `HOURS_WINDOW` at the top
  of `reddit_collector.py`.
- Change LLM model: edit `MODEL` in `llm_client.py` (any Groq-hosted model,
  e.g. `llama-3.3-70b-versatile`, `mixtral-8x7b-32768`).
