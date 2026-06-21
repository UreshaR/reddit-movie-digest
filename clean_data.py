import json

with open("reddit_posts_with_comments.json", "r", encoding="utf-8") as f:
    posts = json.load(f)

documents = []

for post in posts:
    title = post["title"]
    url = post["url"]
    post_id = post.get("id", url)
    created_utc = post.get("created_utc")

    # Include the post title + body itself as a document so the LLM has
    # context even for posts with no/short comments.
    intro_text = title
    if post.get("selftext"):
        intro_text += ". " + post["selftext"].strip()

    if len(intro_text) >= 20:
        documents.append({
            "text": intro_text,
            "metadata": {
                "post_id": post_id,
                "title": title,
                "url": url,
                "created_utc": created_utc,
                "type": "post",
            },
        })

    for comment in post.get("comments", []):
        comment = comment.strip()
        if len(comment) < 20:
            continue

        documents.append({
            "text": comment,
            "metadata": {
                "post_id": post_id,
                "title": title,
                "url": url,
                "created_utc": created_utc,
                "type": "comment",
            },
        })

with open("documents.json", "w", encoding="utf-8") as f:
    json.dump(documents, f, indent=2, ensure_ascii=False)

print("Documents created:", len(documents))
