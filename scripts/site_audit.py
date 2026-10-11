"""Crawl a site and record on-page, technical and AI-crawler SEO signals.

Free replacement for the paid SEO-tool crawl. Writes data/seo/audit-<domain>-<date>.json
and prints a compact summary.

    python scripts/site_audit.py                       # SITE_URL from .env
    python scripts/site_audit.py --url https://x.com --max-pages 10
"""
import argparse
import json
import time
import xml.etree.ElementTree as ET
from collections import Counter
from urllib.parse import urljoin, urldefrag, urlparse

from bs4 import BeautifulSoup

from common import DATA, env, session, today, write_json

AI_BOTS = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot",
           "PerplexityBot", "Google-Extended", "Applebot-Extended", "CCBot", "Bytespider"]
SKIP_EXT = (".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".pdf", ".zip", ".mp4", ".css", ".js", ".ico", ".xml")


def parse_robots(text):
    """Return {user-agent-lowercase: [disallow paths]} and sitemap URLs."""
    groups, sitemaps, current, last_was_agent = {}, [], [], False
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if ":" not in line:
            continue
        key, value = (p.strip() for p in line.split(":", 1))
        key = key.lower()
        if key == "user-agent":
            if not last_was_agent:
                current = []
            current.append(value.lower())
            groups.setdefault(value.lower(), [])
            last_was_agent = True
            continue
        last_was_agent = False
        if key == "disallow" and value:
            for agent in current:
                groups[agent].append(value)
        elif key == "sitemap":
            sitemaps.append(value)
    return groups, sitemaps


def ai_bot_access(groups):
    result = {}
    for bot in AI_BOTS:
        rules = groups.get(bot.lower())
        if rules is None:
            rules = groups.get("*", [])
            source = "*"
        else:
            source = bot
        result[bot] = "BLOCKED" if "/" in rules else (f"allowed except {', '.join(rules)}" if rules else "allowed")
        result[bot] += f" (via {source})"
    return result


def sitemap_urls(s, url, depth=0):
    if depth > 2:
        return []
    try:
        r = s.get(url, timeout=20)
        if r.status_code != 200:
            return []
        root = ET.fromstring(r.content)
    except Exception:
        return []
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    if root.tag.endswith("sitemapindex"):
        urls = []
        for loc in root.findall("sm:sitemap/sm:loc", ns):
            urls += sitemap_urls(s, loc.text.strip(), depth + 1)
        return urls
    return [loc.text.strip() for loc in root.findall("sm:url/sm:loc", ns)]


def same_site(url, host):
    return urlparse(url).netloc.replace("www.", "") == host.replace("www.", "")


def analyse_page(url, r, host):
    soup = BeautifulSoup(r.text, "html.parser")
    title = (soup.title.string or "").strip() if soup.title and soup.title.string else ""
    desc_tag = soup.find("meta", attrs={"name": "description"})
    desc = (desc_tag.get("content") or "").strip() if desc_tag else ""
    robots_tag = soup.find("meta", attrs={"name": "robots"})
    canonical = soup.find("link", rel="canonical")
    h1s = [h.get_text(" ", strip=True) for h in soup.find_all("h1")]
    h2s = [h.get_text(" ", strip=True) for h in soup.find_all("h2")]
    imgs = soup.find_all("img")
    no_alt = [i.get("src", "")[:80] for i in imgs if not (i.get("alt") or "").strip()]
    jsonld_types = []
    for tag in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(tag.string or "{}")
        except Exception:
            jsonld_types.append("INVALID_JSON")
            continue
        items = data if isinstance(data, list) else data.get("@graph", [data])
        for item in items:
            if isinstance(item, dict) and item.get("@type"):
                t = item["@type"]
                jsonld_types += t if isinstance(t, list) else [t]
    links = []
    for a in soup.find_all("a", href=True):
        href = urldefrag(urljoin(url, a["href"]))[0]
        if href.startswith("http"):
            links.append(href)
    internal = sorted({l for l in links if same_site(l, host)})
    has_og = bool(soup.find("meta", property="og:title"))
    for tag in soup(["script", "style", "noscript", "nav", "footer", "header"]):
        tag.decompose()
    words = len(soup.get_text(" ", strip=True).split())

    page = {
        "url": url, "status": r.status_code, "load_ms": int(r.elapsed.total_seconds() * 1000),
        "title": title, "title_len": len(title), "meta_description": desc, "desc_len": len(desc),
        "h1": h1s, "h2_count": len(h2s), "h2": h2s[:12], "word_count": words,
        "canonical": canonical.get("href") if canonical else None,
        "meta_robots": robots_tag.get("content") if robots_tag else None,
        "images": len(imgs), "images_missing_alt": len(no_alt), "missing_alt_samples": no_alt[:5],
        "schema_types": sorted(set(jsonld_types)),
        "og_title": has_og,
        "internal_links": len(internal), "external_links": len(set(links)) - len(internal),
    }
    issues = []
    if not title:
        issues.append(("critical", "Missing <title>"))
    elif not 30 <= len(title) <= 60:
        issues.append(("medium", f"Title length {len(title)} (aim 30-60)"))
    if not desc:
        issues.append(("high", "Missing meta description"))
    elif not 70 <= len(desc) <= 160:
        issues.append(("low", f"Meta description length {len(desc)} (aim 70-160)"))
    if len(h1s) == 0:
        issues.append(("high", "No H1"))
    elif len(h1s) > 1:
        issues.append(("medium", f"{len(h1s)} H1 tags"))
    if not page["canonical"]:
        issues.append(("medium", "No canonical tag"))
    if page["meta_robots"] and "noindex" in page["meta_robots"].lower():
        issues.append(("critical", "Page is noindex"))
    if no_alt:
        issues.append(("medium", f"{len(no_alt)} images without alt text"))
    if words < 300:
        issues.append(("low", f"Thin content: {words} words"))
    if not page["schema_types"]:
        issues.append(("medium", "No JSON-LD structured data"))
    if not page["og_title"]:
        issues.append(("low", "No Open Graph tags (social previews)"))
    if page["load_ms"] > 2000:
        issues.append(("medium", f"Slow server response {page['load_ms']} ms"))
    page["issues"] = [{"severity": s, "issue": i} for s, i in issues]
    return page, internal


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default=env("SITE_URL", "https://anantasutra.com"))
    ap.add_argument("--max-pages", type=int, default=40)
    ap.add_argument("--check-links", action="store_true", help="HEAD-check every internal link found")
    args = ap.parse_args()

    base = args.url.rstrip("/")
    host = urlparse(base).netloc
    s = session()
    report = {"site": base, "date": today(), "site_checks": {}, "pages": []}

    robots = s.get(base + "/robots.txt", timeout=15)
    groups, sm_list = parse_robots(robots.text) if robots.status_code == 200 else ({}, [])
    llms = s.get(base + "/llms.txt", timeout=15)
    https_redirect = s.get(base.replace("https://", "http://"), timeout=15, allow_redirects=True)
    report["site_checks"] = {
        "robots_txt": robots.status_code == 200,
        "sitemaps_declared": sm_list,
        "llms_txt": llms.status_code == 200 and "html" not in llms.headers.get("content-type", ""),
        "http_redirects_to_https": https_redirect.url.startswith("https://"),
        "ai_crawler_access": ai_bot_access(groups),
    }

    queue = sitemap_urls(s, sm_list[0]) if sm_list else sitemap_urls(s, base + "/sitemap.xml")
    report["site_checks"]["sitemap_url_count"] = len(queue)
    if not queue:
        queue = [base + "/"]
    seen, all_internal = set(), set()
    while queue and len(report["pages"]) < args.max_pages:
        url = queue.pop(0)
        if url in seen or url.lower().endswith(SKIP_EXT):
            continue
        seen.add(url)
        try:
            r = s.get(url, timeout=20)
        except Exception as e:
            report["pages"].append({"url": url, "status": "error", "issues": [{"severity": "critical", "issue": str(e)[:120]}]})
            continue
        if "html" not in r.headers.get("content-type", ""):
            continue
        page, internal = analyse_page(r.url, r, host)
        report["pages"].append(page)
        all_internal.update(internal)
        queue += [l for l in internal if l not in seen and l not in queue]
        time.sleep(0.3)

    if args.check_links:
        broken = []
        for link in sorted(all_internal - seen)[:150]:
            try:
                code = s.head(link, timeout=10, allow_redirects=True).status_code
            except Exception:
                code = "error"
            if code != 200:
                broken.append({"url": link, "status": code})
        report["site_checks"]["broken_internal_links"] = broken

    pages = [p for p in report["pages"] if isinstance(p.get("status"), int)]
    titles = Counter(p["title"] for p in pages if p.get("title"))
    descs = Counter(p["meta_description"] for p in pages if p.get("meta_description"))
    report["site_checks"]["duplicate_titles"] = [t for t, c in titles.items() if c > 1]
    report["site_checks"]["duplicate_descriptions"] = [d[:80] for d, c in descs.items() if c > 1]
    report["site_checks"]["non_200_pages"] = [{"url": p["url"], "status": p["status"]} for p in report["pages"] if p.get("status") != 200]

    out = DATA / "seo" / f"audit-{host.replace('www.', '')}-{today()}.json"
    write_json(out, report)

    sev = Counter(i["severity"] for p in report["pages"] for i in p.get("issues", []))
    print(f"Audited {len(report['pages'])} pages of {base} -> {out.relative_to(DATA.parent)}")
    print("Site checks:", json.dumps({k: v for k, v in report["site_checks"].items() if k != "ai_crawler_access"}, ensure_ascii=False))
    print("AI crawler access:", json.dumps(report["site_checks"]["ai_crawler_access"]))
    print("Issue counts:", dict(sev))
    for p in report["pages"]:
        if p.get("issues"):
            print(f"- {p['url']}: " + "; ".join(f"[{i['severity']}] {i['issue']}" for i in p["issues"]))


if __name__ == "__main__":
    main()
