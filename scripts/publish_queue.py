"""Publish approved, due posts from content/queue/ (runs from Task Scheduler, no AI usage).

Each queue file is markdown with frontmatter, body = the post text:

    ---
    platform: linkedin            # linkedin | instagram
    status: approved              # draft -> approved (by you) -> posted | failed
    scheduled_at: 2026-10-12 09:30   # always IST, whatever timezone the PC is in
    image: content/media/x.png    # local file: LinkedIn uploads it, Instagram gets it hosted via ImgBB
    images: [content/media/a.png, content/media/b.png]   # Instagram carousel, 2-10 files in order
    image_url: https://...        # optional public JPEG URL instead of a local file (Instagram)
    alt_text: ...
    first_comment: Full guide: https://...   # LinkedIn: added as a comment right after posting
    ---
    Post text...

Every link in the post or first_comment must answer 200 before posting; otherwise the item is held
(status: failed, with the reason) so a post never points at a page that isn't live yet.

    python scripts/publish_queue.py            # publish everything due
    python scripts/publish_queue.py --dry-run  # show what would be published
    python scripts/publish_queue.py --list     # show the whole queue
"""
import argparse
import datetime as dt
import re

from common import CONTENT, IST, ROOT, dump_frontmatter, env, log, now_ist, parse_frontmatter, session

QUEUE = CONTENT / "queue"
POSTED = CONTENT / "posted"
URL_RE = re.compile(r"https?://[^\s)\"'<>]+")


def dead_links(text):
    """URLs in the text that don't answer 200 (e.g. a blog post that isn't published yet)."""
    s, dead = session(), []
    for url in dict.fromkeys(URL_RE.findall(text or "")):
        try:
            live = s.get(url, timeout=20, allow_redirects=True).status_code == 200
        except Exception:
            live = False
        if not live:
            dead.append(url)
    return dead


def load_queue():
    items = []
    for path in sorted(QUEUE.glob("*.md")):
        meta, body = parse_frontmatter(path.read_text(encoding="utf-8"))
        items.append((path, meta, body))
    return items


def due(meta):
    when = meta.get("scheduled_at")
    if not when:
        return False
    if isinstance(when, str):
        when = dt.datetime.fromisoformat(when.strip())
    elif isinstance(when, dt.date) and not isinstance(when, dt.datetime):
        when = dt.datetime.combine(when, dt.time(9, 0))
    if when.tzinfo:
        when = when.astimezone(IST).replace(tzinfo=None)
    return when <= now_ist()


def publish(meta, body):
    text = body.strip()
    if meta["platform"] == "linkedin":
        import linkedin
        image = meta.get("image")
        return linkedin.post(text, str(ROOT / image) if image else None, meta.get("alt_text", ""))
    if meta["platform"] == "instagram":
        import instagram
        return instagram.post(text, instagram.queue_images(meta))
    raise ValueError(f"unknown platform {meta.get('platform')}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()
    items = load_queue()

    if args.list:
        for path, meta, body in items:
            print(f"{meta.get('status', '?'):9} {str(meta.get('scheduled_at', '-')):17} {meta.get('platform', '?'):10} {path.name}")
        return

    if not args.dry_run and env("IG_ACCESS_TOKEN"):
        import instagram
        note = instagram.maybe_refresh()
        if note:
            log("publisher", f"instagram {note}")

    for path, meta, body in items:
        if meta.get("status") != "approved" or not due(meta):
            continue
        dead = dead_links(f"{body}\n{meta.get('first_comment') or ''}")
        if args.dry_run:
            links = f"NOT LIVE: {', '.join(dead)}" if dead else "all links live"
            print(f"WOULD POST {meta['platform']}: {path.name} ({links})\n{body.strip()[:300]}\n")
            continue
        if dead:
            meta.update(status="failed", error=f"link not live yet: {', '.join(dead)}. "
                                                "Publish the page, then set status back to approved.")
            path.write_text(dump_frontmatter(meta, body), encoding="utf-8")
            log("publisher", f"HELD {path.name}: link not live {dead}")
            continue
        try:
            post_id, url = publish(meta, body)
            meta.update(status="posted", posted_at=now_ist().isoformat(), post_id=post_id, post_url=url)
            note = ""
            if meta.get("first_comment") and meta["platform"] == "linkedin":
                import linkedin
                try:
                    linkedin.comment(post_id, meta["first_comment"])
                    meta["first_comment_posted"] = True
                except Exception as e:  # the post is live; the comment can be added by hand
                    meta["first_comment_error"] = str(e)[:300]
                    note = f" (first comment FAILED, add it by hand: {e})"
            POSTED.mkdir(parents=True, exist_ok=True)
            (POSTED / path.name).write_text(dump_frontmatter(meta, body), encoding="utf-8")
            path.unlink()
            log("publisher", f"posted {meta['platform']} {path.name} -> {url}{note}")
        except Exception as e:
            meta.update(status="failed", error=str(e)[:500])
            path.write_text(dump_frontmatter(meta, body), encoding="utf-8")
            log("publisher", f"FAILED {path.name}: {e}")


if __name__ == "__main__":
    main()
