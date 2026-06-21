# """
# Reads reddit_posts_with_comments.json (already filtered to the last 48h
# by reddit_collector.py), and for each post asks Groq:
#   - what film(s) the post + comments are about
#   - a short description / takeaway based on what people are saying

# Outputs movie_digest.json + a printed summary.
# """

# import json
# import time
# from llm_client import ask_groq

# INPUT_FILE = "reddit_posts_with_comments.json"
# OUTPUT_FILE = "movie_digest.json"

# PROMPT_TEMPLATE = """You are reading a Reddit post from r/movies and its top comments.

# Post title: {title}
# Post body: {selftext}

# Top comments:
# {comments}

# Based ONLY on the above, respond in this exact format and nothing else:
# Film: <film name, or "N/A" if no specific film is identifiable>
# Description: <one or two sentence summary of what this post/comments are about, in your own words>
# """


# def build_prompt(post):
#     comments = post.get("comments", [])
#     comments_text = "\n".join(f"- {c}" for c in comments[:15]) or "(no comments)"
#     return PROMPT_TEMPLATE.format(
#         title=post["title"],
#         selftext=post.get("selftext", "")[:1000] or "(no body text)",
#         comments=comments_text,
#     )


# def parse_response(text):
#     film, description = "N/A", ""
#     for line in text.splitlines():
#         line = line.strip()
#         if line.lower().startswith("film:"):
#             film = line.split(":", 1)[1].strip()
#         elif line.lower().startswith("description:"):
#             description = line.split(":", 1)[1].strip()
#     return film, description


# def main():
#     with open(INPUT_FILE, "r", encoding="utf-8") as f:
#         posts = json.load(f)

#     print(f"Summarizing {len(posts)} posts from the last 2 days...")

#     digest = []
#     for i, post in enumerate(posts, start=1):
#         print(f"[{i}/{len(posts)}] {post['title'][:70]}")
#         prompt = build_prompt(post)

#         try:
#             raw = ask_groq(prompt)
#             film, description = parse_response(raw)
#         except Exception as e:
#             print("  LLM error:", e)
#             film, description = "N/A", ""

#         digest.append({
#             "film": film,
#             "description": description,
#             "post_title": post["title"],
#             "url": post["url"],
#         })

#         time.sleep(1)

#     with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
#         json.dump(digest, f, indent=2, ensure_ascii=False)

#     print(f"\nSaved digest to {OUTPUT_FILE}\n")
#     print("===== MOVIE DIGEST (last 2 days, r/movies) =====\n")
#     for entry in digest:
#         if entry["film"] == "N/A":
#             continue
#         print(f"{entry['film']}")
#         print(f"  {entry['description']}")
#         print(f"  source: {entry['url']}\n")


# if __name__ == "__main__":
#     main()


"""
Reads reddit_posts_with_comments.json (already filtered to the last 48h
by reddit_collector.py), and for each post asks Groq:
  - what film(s) the post + comments are about
  - a short description / takeaway based on what people are saying

Outputs movie_digest.json + a printed summary.
"""

import json
import time
from llm_client import ask_groq

INPUT_FILE = "reddit_posts_with_comments.json"
OUTPUT_FILE = "movie_digest.json"

PROMPT_TEMPLATE = """You are reading a Reddit post from r/movies and its top comments.

Post title: {title}
Post body: {selftext}

Top comments:
{comments}

Identify the film being discussed. The post TITLE very often already
contains the film name (sometimes with year/director, e.g.
"Crouching Tiger, Hidden Dragon (2000, dir. Ang Lee)") - use that if present,
even if the comments wander into other topics. Only use "N/A" if the post is
truly not about any specific identifiable film (e.g. general industry news,
finance/legal news, or a discussion with no single named film).

Respond in this exact format and nothing else:
Film: <film name, or "N/A" only if truly no film is identifiable>
Description: <one or two sentence summary of what this post/comments are about, in your own words>
"""


def build_prompt(post):
    comments = post.get("comments", [])
    comments_text = "\n".join(f"- {c}" for c in comments[:15]) or "(no comments)"
    return PROMPT_TEMPLATE.format(
        title=post["title"],
        selftext=post.get("selftext", "")[:1000] or "(no body text)",
        comments=comments_text,
    )


def guess_film_from_title(title):
    """Fallback: many r/movies titles already contain the film name,
    often followed by a year/director in parentheses or a separator.
    e.g. 'Crouching Tiger, Hidden Dragon (2000, dir. Ang Lee) - ...'
    e.g. 'Scooby-Doo (2002) | Dir: Raja Gosnell | ...'

    Returns None if no clear film-title pattern is found (rather than
    guessing the whole sentence is a film name).
    """
    import re

    match = re.split(r"\s*\(\d{4}", title)
    had_year = len(match) > 1
    candidate = match[0].strip()

    had_sep = False
    for sep in [" | ", " - ", ": "]:
        if sep in candidate:
            candidate = candidate.split(sep)[0].strip()
            had_sep = True
            break

    # Only trust this as a film name if we actually found a year-in-parens
    # or a clear separator - otherwise it's probably just a regular
    # sentence/question, not "Title (year) - description" format.
    if not (had_year or had_sep):
        return None

    return candidate if candidate else None


def parse_response(text, fallback_title=None):
    film, description = "N/A", ""
    for line in text.splitlines():
        line = line.strip()
        if line.lower().startswith("film:"):
            film = line.split(":", 1)[1].strip()
        elif line.lower().startswith("description:"):
            description = line.split(":", 1)[1].strip()

    if film in ("N/A", "", None) and fallback_title:
        guess = guess_film_from_title(fallback_title)
        if guess:
            film = guess

    return film, description


def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        posts = json.load(f)

    print(f"Summarizing {len(posts)} posts from the last 2 days...")

    digest = []
    for i, post in enumerate(posts, start=1):
        print(f"[{i}/{len(posts)}] {post['title'][:70]}")
        prompt = build_prompt(post)

        try:
            raw = ask_groq(prompt)
            film, description = parse_response(raw, fallback_title=post["title"])
        except Exception as e:
            print("  LLM error:", e)
            film, description = "N/A", ""

        digest.append({
            "film": film,
            "description": description,
            "post_title": post["title"],
            "url": post["url"],
        })

        time.sleep(1)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(digest, f, indent=2, ensure_ascii=False)

    print(f"\nSaved digest to {OUTPUT_FILE}\n")
    print("===== MOVIE DIGEST (last 2 days, r/movies) =====\n")
    for entry in digest:
        if entry["film"] == "N/A":
            continue
        print(f"{entry['film']}")
        print(f"  {entry['description']}")
        print(f"  source: {entry['url']}\n")


if __name__ == "__main__":
    main()