from playwright.sync_api import sync_playwright
from datetime import datetime, timezone, timedelta
import json
import time

SUBREDDIT_URL = "https://www.reddit.com/r/movies/"
HOURS_WINDOW = 48          # last 2 days
MAX_SCROLLS = 15           # scroll more to make sure we cover 2 days of posts
COMMENTS_PER_POST = 20


def parse_timestamp(ts_str):
    """shreddit-post's created-timestamp attribute is ISO 8601, e.g.
    '2026-06-20T14:32:01.000Z'."""
    if not ts_str:
        return None
    try:
        return datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
    except ValueError:
        return None


def get_post_links(page, cutoff):
    posts = page.query_selector_all("shreddit-post")

    post_data = []

    for post in posts:
        try:
            title = post.get_attribute("post-title")
            permalink = post.get_attribute("permalink")
            created_raw = post.get_attribute("created-timestamp")
            score = post.get_attribute("score")

            created_dt = parse_timestamp(created_raw)

            if not (title and permalink):
                continue

            # Skip posts outside the 2-day window. If we can't read the
            # timestamp at all, keep the post rather than silently drop it.
            if created_dt and created_dt < cutoff:
                continue

            post_data.append({
                "title": title,
                "url": "https://www.reddit.com" + permalink,
                "created_utc": created_dt.timestamp() if created_dt else None,
                "created_iso": created_raw,
                "score": score,
            })

        except Exception as e:
            print("Post extraction error:", e)

    return post_data


def extract_comments(page, limit=COMMENTS_PER_POST):
    comments = []

    comment_elements = page.locator("shreddit-comment")
    comment_count = comment_elements.count()

    for i in range(comment_count):
        try:
            comment = comment_elements.nth(i)
            paragraphs = comment.locator("p")

            text_parts = []
            for j in range(paragraphs.count()):
                txt = paragraphs.nth(j).inner_text().strip()
                if txt:
                    text_parts.append(txt)

            comment_text = " ".join(text_parts)

            if comment_text:
                comments.append(comment_text)

            if len(comments) >= limit:
                break

        except Exception:
            pass

    return comments


def scrape_reddit():
    cutoff = datetime.now(timezone.utc) - timedelta(hours=HOURS_WINDOW)
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        print(f"Opening subreddit (collecting posts from last {HOURS_WINDOW}h)...")
        page.goto(SUBREDDIT_URL, timeout=60000)
        page.wait_for_timeout(8000)

        seen_titles = set()
        post_data = []

        # Keep scrolling and collecting until we stop finding NEW posts
        # within the window, or hit the scroll cap.
        for scroll_i in range(MAX_SCROLLS):
            page.mouse.wheel(0, 4000)
            page.wait_for_timeout(2000)

            current = get_post_links(page, cutoff)
            new_count = 0
            for p_ in current:
                if p_["title"] not in seen_titles:
                    seen_titles.add(p_["title"])
                    post_data.append(p_)
                    new_count += 1

            print(f"  scroll {scroll_i + 1}: {len(post_data)} posts in window so far")

            if new_count == 0 and scroll_i > 3:
                # Nothing new in last few scrolls, likely scrolled past
                # the 2-day window or hit the end of the feed.
                break

        print("Posts collected (within window):", len(post_data))

        for idx, post in enumerate(post_data, start=1):
            print(f"\n[{idx}/{len(post_data)}] {post['title']}")

            try:
                page.goto(post["url"], timeout=60000)
                page.wait_for_timeout(8000)

                for _ in range(5):
                    page.mouse.wheel(0, 5000)
                    page.wait_for_timeout(1500)

                comments = extract_comments(page)
                print("Comments found:", len(comments))

                results.append({
                    "title": post["title"],
                    "url": post["url"],
                    "created_utc": post["created_utc"],
                    "created_iso": post["created_iso"],
                    "score": post["score"],
                    "comments": comments,
                })

                time.sleep(2)

            except Exception as e:
                print("Error:", e)

        browser.close()

    return results


if __name__ == "__main__":
    data = scrape_reddit()

    with open("reddit_posts_with_comments.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\nSaved {len(data)} posts to reddit_posts_with_comments.json")
