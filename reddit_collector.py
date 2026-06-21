"""
Collects posts (and their top comments) from a subreddit, restricted to
the last N hours (default 48h = 2 days), using Reddit's public JSON API.

No login, no Playwright/browser needed. Reddit's read-only JSON endpoints
(<subreddit>/new.json, <permalink>.json) work without auth for public
subreddits, you just need a real User-Agent string.
"""

import json
import time
import requests

SUBREDDIT = "movies"
HOURS_WINDOW = 48          # collect everything posted in the last 2 days
MAX_PAGES = 10              # safety cap on pagination (100 posts/page)
COMMENTS_PER_POST = 25
REQUEST_DELAY = 1.5         # be polite to Reddit's API

HEADERS = {
    "User-Agent": "movie-digest-bot/1.0 (by u/your_username)"
}


def fetch_recent_posts(subreddit=SUBREDDIT, hours=HOURS_WINDOW):
    """Page through /new.json until posts fall outside the time window."""
    cutoff = time.time() - hours * 3600
    posts = []
    after = None

    for _ in range(MAX_PAGES):
        url = f"https://www.reddit.com/r/{subreddit}/new.json"
        params = {"limit": 100}
        if after:
            params["after"] = after

        resp = requests.get(url, headers=HEADERS, params=params, timeout=20)
        resp.raise_for_status()
        data = resp.json()

        children = data["data"]["children"]
        if not children:
            break

        stop = False
        for child in children:
            p = child["data"]
            created = p["created_utc"]

            if created < cutoff:
                # new.json is sorted newest-first, so once we're past
                # the cutoff every later post is older too.
                stop = True
                break

            posts.append({
                "id": p["id"],
                "title": p["title"],
                "url": "https://www.reddit.com" + p["permalink"],
                "selftext": p.get("selftext", ""),
                "score": p.get("score", 0),
                "num_comments": p.get("num_comments", 0),
                "created_utc": created,
            })

        if stop:
            break

        after = data["data"].get("after")
        if not after:
            break

        time.sleep(REQUEST_DELAY)

    return posts


def fetch_comments(permalink_url, limit=COMMENTS_PER_POST):
    """Pull top-level comment bodies for a post via its .json endpoint."""
    resp = requests.get(
        permalink_url.rstrip("/") + ".json",
        headers=HEADERS,
        params={"limit": limit, "depth": 1, "sort": "top"},
        timeout=20,
    )
    resp.raise_for_status()
    data = resp.json()

    comments = []
    if len(data) < 2:
        return comments

    for child in data[1]["data"]["children"]:
        if child["kind"] != "t1":
            continue
        body = child["data"].get("body", "").strip()
        if body and body not in ("[deleted]", "[removed]"):
            comments.append(body)
        if len(comments) >= limit:
            break

    return comments


def collect(subreddit=SUBREDDIT, hours=HOURS_WINDOW):
    print(f"Fetching posts from r/{subreddit} in the last {hours}h...")
    posts = fetch_recent_posts(subreddit, hours)
    print(f"Found {len(posts)} posts in window.")

    results = []
    for i, post in enumerate(posts, start=1):
        print(f"[{i}/{len(posts)}] {post['title'][:70]}")
        try:
            comments = fetch_comments(post["url"])
        except Exception as e:
            print("  comment fetch error:", e)
            comments = []

        post["comments"] = comments
        results.append(post)
        time.sleep(REQUEST_DELAY)

    return results


if __name__ == "__main__":
    data = collect()
    with open("reddit_posts_with_comments.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\nSaved {len(data)} posts to reddit_posts_with_comments.json")
