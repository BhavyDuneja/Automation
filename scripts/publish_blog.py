"""Publish approved blog drafts from content/blog/ to the website (Supabase blog_posts table).

In .env:
  SUPABASE_URL          https://<project>.supabase.co
  SUPABASE_SERVICE_KEY  service-role key (Supabase -> Project settings -> API). Server-side only.

A draft publishes when `status: approved` and `publish_at` (IST) has come. Frontmatter it uses:
  title, slug, meta_description, category, tags, publish_at: 2026-10-13 08:00, status
The markdown body (no H1: the site prints the title itself) becomes the post's HTML.

    python scripts/publish_blog.py --check      # can we reach blog_posts?
    python scripts/publish_blog.py --dry-run
    python scripts/publish_blog.py              # Task Scheduler: publish everything due
"""
import argparse
import math
import re

import markdown

from common import CONTENT, dump_frontmatter, env, log, now_ist, parse_frontmatter, session
from publish_queue import scheduled_time

BLOG = CONTENT / "blog"
SITE = "https://www.anantasutra.com"


def configured():
    return bool(env("SUPABASE_URL") and env("SUPABASE_SERVICE_KEY"))


def endpoint(query=""):
    base, key = env("SUPABASE_URL", required=True).rstrip("/"), env("SUPABASE_SERVICE_KEY", required=True)
    return f"{base}/rest/v1/blog_posts{query}", {"apikey": key, "Authorization": f"Bearer {key}",
                                                 "Content-Type": "application/json"}


def publish_time(meta):
    try:
        return scheduled_time({"scheduled_at": meta.get("publish_at")})
    except ValueError:
        return None


def problems(meta, body):
    """Reasons an article can't be approved yet."""
    found = [f"missing {k}" for k in ("title", "slug", "meta_description", "publish_at") if not meta.get(k)]
    if meta.get("publish_at") and not publish_time(meta):
        found.append("publish_at is not a date like 2026-10-13 08:00")
    if "[ADD:" in body:
        found.append("fill the [ADD: ...] placeholders")
    if re.search(r"(?m)^# ", body):
        found.append("remove the H1 from the body (the site prints the title)")
    if len(body.split()) < 500:
        found.append("too short for an article (under 500 words)")
    return found


def row(meta, body):
    html = markdown.markdown(body, extensions=["tables", "fenced_code", "sane_lists"])
    words = len(re.sub(r"<[^>]+>", " ", html).split())
    return {
        "id": f"as-{meta['slug']}", "title": meta["title"], "slug": meta["slug"],
        "excerpt": meta.get("excerpt") or meta["meta_description"], "content": html,
        "date": publish_time(meta).date().isoformat(), "read_time": f"{max(1, math.ceil(words / 200))} min read",
        "category": meta.get("category") or "Hiring", "tags": [str(t) for t in meta.get("tags") or []],
        "featured": False, "status": "published", "meta_description": meta["meta_description"],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if not configured():
        if args.check:
            raise SystemExit("Add SUPABASE_URL and SUPABASE_SERVICE_KEY to .env (README: Daily articles)")
        return  # not set up yet: approved articles simply wait
    s = session()
    if args.check:
        url, headers = endpoint("?select=slug,status,date&order=date.desc&limit=3")
        r = s.get(url, headers=headers, timeout=30)
        print(f"blog_posts: HTTP {r.status_code}", r.json() if r.ok else r.text[:300])
        return
    for path in sorted(BLOG.glob("*.md")):
        meta, body = parse_frontmatter(path.read_text(encoding="utf-8"))
        when = publish_time(meta)
        if meta.get("status") != "approved" or not when or when > now_ist():
            continue
        blockers = problems(meta, body)
        if args.dry_run:
            print(f"WOULD PUBLISH {path.name} -> {SITE}/blog/{meta.get('slug')}" + (f" (blocked: {blockers})" if blockers else ""))
            continue
        if blockers:
            meta.update(status="failed", error="; ".join(blockers))
        else:
            url, headers = endpoint("?on_conflict=slug")
            r = s.post(url, json=row(meta, body), timeout=60,
                       headers={**headers, "Prefer": "resolution=merge-duplicates,return=minimal"})
            if r.status_code >= 400:
                meta.update(status="failed", error=f"Supabase {r.status_code}: {r.text[:300]}")
            else:
                meta.update(status="published", published_at=now_ist().isoformat(timespec="minutes"),
                            url=f"{SITE}/blog/{meta['slug']}")
        path.write_text(dump_frontmatter(meta, body), encoding="utf-8")
        log("blog", f"{meta['status'].upper()} {path.name} {meta.get('url') or meta.get('error', '')}")


if __name__ == "__main__":
    main()
