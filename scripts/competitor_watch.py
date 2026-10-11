"""Daily competitor monitor (free replacement for Similarweb/Ahrefs change tracking).

For every competitor in context/competitors.yaml it snapshots the tracked pages
(title, meta, headings, body text) and the sitemap, compares with the previous
snapshot and writes only the *changes* to data/intel/changes-<date>.json, so the
analysis step reads a small diff instead of whole websites.

    python scripts/competitor_watch.py
    python scripts/competitor_watch.py --only uplers
"""
import argparse
import difflib
import hashlib
import time
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from common import CONTEXT, DATA, read_json, read_yaml, session, slugify, today, write_json
from site_audit import sitemap_urls

MAX_DIFF_LINES = 40


def snapshot_page(s, url):
    try:
        r = s.get(url, timeout=25)
    except Exception as e:
        return {"url": url, "error": str(e)[:150]}
    if r.status_code != 200:
        return {"url": url, "error": f"HTTP {r.status_code}"}
    soup = BeautifulSoup(r.text, "html.parser")
    desc = soup.find("meta", attrs={"name": "description"})
    snap = {
        "url": url,
        "title": soup.title.get_text(strip=True) if soup.title else "",
        "meta_description": (desc.get("content") or "").strip() if desc else "",
        "h1": [h.get_text(" ", strip=True) for h in soup.find_all("h1")],
        "h2": [h.get_text(" ", strip=True) for h in soup.find_all("h2")][:25],
    }
    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()
    lines = [l.strip() for l in soup.get_text("\n").splitlines()]
    snap["text"] = [l for l in lines if len(l) > 2][:600]
    snap["hash"] = hashlib.sha1("\n".join(snap["text"]).encode()).hexdigest()
    return snap


def diff_page(old, new):
    if not old or "error" in old or "error" in new:
        return None
    if old.get("hash") == new.get("hash"):
        return None
    change = {"url": new["url"]}
    for field in ("title", "meta_description", "h1"):
        if old.get(field) != new.get(field):
            change[field] = {"before": old.get(field), "after": new.get(field)}
    added_h2 = [h for h in new["h2"] if h not in old.get("h2", [])]
    removed_h2 = [h for h in old.get("h2", []) if h not in new["h2"]]
    if added_h2 or removed_h2:
        change["h2"] = {"added": added_h2, "removed": removed_h2}
    text_diff = [l for l in difflib.unified_diff(old.get("text", []), new["text"], lineterm="", n=0)
                 if l[:1] in "+-" and not l.startswith(("+++", "---"))]
    change["text_diff"] = text_diff[:MAX_DIFF_LINES]
    change["text_diff_truncated"] = len(text_diff) > MAX_DIFF_LINES
    return change


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="slug of a single competitor")
    args = ap.parse_args()

    config = read_yaml(CONTEXT / "competitors.yaml", {})
    competitors = [c for c in config.get("competitors", []) if c.get("track", True)]
    if args.only:
        competitors = [c for c in competitors if slugify(c["name"]) == args.only]
    s = session()
    summary = {"date": today(), "competitors": []}

    for comp in competitors:
        slug = slugify(comp["name"])
        base = comp["domain"].rstrip("/")
        if not base.startswith("http"):
            base = "https://" + base
        folder = DATA / "competitors" / slug
        # Diff against the last snapshot from an earlier day, so a second run on the same day keeps today's diff.
        latest = read_json(folder / "latest.json", {})
        if latest and latest.get("date") != today():
            write_json(folder / "previous.json", latest)
        previous = read_json(folder / "previous.json", {})
        first_run = not previous

        pages = {}
        for path in comp.get("pages", ["/"]):
            url = urljoin(base + "/", path.lstrip("/"))
            pages[url] = snapshot_page(s, url)
            time.sleep(0.5)

        sm_url = comp.get("sitemap") or base + "/sitemap.xml"
        urls = sorted(set(sitemap_urls(s, sm_url)))
        old_urls = set(previous.get("sitemap", []))

        entry = {"name": comp["name"], "first_run": first_run, "page_changes": [], "errors": []}
        for url, snap in pages.items():
            if "error" in snap:
                entry["errors"].append(f"{url}: {snap['error']}")
                continue
            ch = diff_page(previous.get("pages", {}).get(url), snap)
            if ch:
                entry["page_changes"].append(ch)
        if urls and old_urls:
            entry["new_urls"] = [u for u in urls if u not in old_urls][:50]
            entry["removed_urls"] = sorted(old_urls - set(urls))[:50]
        entry["sitemap_size"] = len(urls)
        if first_run:
            entry["baseline"] = {u: {"title": p.get("title"), "h1": p.get("h1"), "h2": p.get("h2", [])[:10]}
                                 for u, p in pages.items() if "error" not in p}

        write_json(folder / "latest.json", {"date": today(), "pages": pages, "sitemap": urls})
        write_json(folder / "history" / f"{today()}.json", entry)
        summary["competitors"].append(entry)

    out = DATA / "intel" / f"changes-{today()}.json"
    if args.only:
        # Merge into today's full run instead of replacing it.
        done = {e["name"] for e in summary["competitors"]}
        earlier = read_json(out, {}).get("competitors", [])
        summary["competitors"] = [e for e in earlier if e["name"] not in done] + summary["competitors"]
    write_json(out, summary)
    for e in summary["competitors"]:
        status = "baseline captured" if e["first_run"] else (
            f"{len(e['page_changes'])} page changes, {len(e.get('new_urls', []))} new URLs")
        print(f"- {e['name']}: {status}" + (f"; errors: {e['errors']}" if e["errors"] else ""))
    print(f"saved -> {out.relative_to(DATA.parent)}")


if __name__ == "__main__":
    main()
