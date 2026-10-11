"""Local marketing dashboard: KPIs, the posting queue with approve buttons, market intel and reports.

    python scripts/dashboard.py              # then open http://localhost:8765
    python scripts/dashboard.py --port 8800

Runs on this PC only (127.0.0.1) and reads the files the scripts and skills write. Approving a post
here is your own explicit approval; the same checks as /social-schedule apply. Pages use no
JavaScript, and every change is a POST carrying a token that is new on each start.
"""
import argparse
import csv
import datetime as dt
import html
import mimetypes
import re
import secrets
from collections import Counter
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, urlparse

import markdown

from common import CONTENT, DATA, REPORTS, ROOT, dump_frontmatter, now_ist, parse_frontmatter, read_json
from publish_blog import BLOG, configured as blog_publishing_configured, problems as blog_problems, publish_time
from publish_queue import POSTED, QUEUE, scheduled_time

TOKEN = secrets.token_urlsafe(16)
READABLE = ("reports/", "content/", "email/", "context/", "data/intel/")
MEDIA = CONTENT / "media"
e = html.escape


# ---------- data ----------

def latest(folder, pattern):
    files = sorted(Path(folder).glob(pattern))
    return files[-1] if files else None


def website():
    path = latest(DATA / "google", "google-*.json")
    g = read_json(path, {}) if path else {}
    channels = g.get("ga4_channels", [])
    countries = {c["country"]: int(c["sessions"]) for c in g.get("ga4_countries", [])}
    queries = g.get("gsc_queries", [])
    # Page rows include clicks from anonymised queries, so their totals are closer to the real figure.
    totals = g.get("gsc_pages") or queries
    return {
        "period": " to ".join(g.get("period", [])),
        "sessions": sum(int(c["sessions"]) for c in channels),
        "singapore": countries.get("Singapore", 0),
        "leads": sum(int(float(c.get("keyEvents", 0))) for c in channels),
        "clicks": sum(r["clicks"] for r in totals),
        "impressions": sum(r["impressions"] for r in totals),
        "queries": queries[:8],
        "daily": [(d["date"], int(d["sessions"])) for d in g.get("ga4_daily", [])],
    }


def aeo():
    path = DATA / "aeo" / "visibility.csv"
    rows = list(csv.DictReader(path.open(encoding="utf-8"))) if path.exists() else []
    if not rows:
        return None
    last = max(r["date"] for r in rows)
    current = [r for r in rows if r["date"] == last]
    cited = sum(r["anantasutra_cited"].strip().lower() in ("yes", "true", "1") for r in current)
    return {"date": last, "cited": cited, "prompts": len(current)}


def seo():
    path = latest(DATA / "seo", "audit-anantasutra.com-*.json")
    if not path:
        return None
    audit = read_json(path, {})
    severity = Counter(i["severity"] for p in audit.get("pages", []) for i in p.get("issues", []))
    return {"date": audit.get("date"), "pages": len(audit.get("pages", [])), **severity}


def when_of(meta):
    try:
        return scheduled_time(meta)
    except ValueError:
        return None


def problems(meta, body):
    """Reasons a post can't be approved yet (same rules as /social-schedule)."""
    found = []
    if "[ADD:" in f"{body}\n{meta.get('first_comment') or ''}":
        found.append("fill the [ADD: ...] placeholders")
    if str(meta.get("review") or "").strip().upper().startswith("FIX"):
        found.append("brand review says FIX")
    when = when_of(meta)
    if not when or when <= now_ist():
        found.append("scheduled time has passed, move it first")
    local = meta.get("images") or ([meta["image"]] if meta.get("image") else [])
    missing = [p for p in local if not (ROOT / p).exists()]
    if missing:
        found.append("image not found: " + ", ".join(missing))
    if meta.get("platform") == "instagram" and not (meta.get("image_url") or local):
        found.append("Instagram needs an image")
    return found


def posts():
    items = []
    for folder, posted in ((QUEUE, False), (POSTED, True)):
        for path in sorted(folder.glob("*.md")):
            meta, body = parse_frontmatter(path.read_text(encoding="utf-8"))
            hook = next((line.strip() for line in body.splitlines() if line.strip()), "")
            items.append({"name": path.name, "path": path, "meta": meta, "body": body, "when": when_of(meta),
                          "hook": hook[:110], "problems": [] if posted else problems(meta, body)})
    return items


def blogs():
    items = []
    for path in sorted(BLOG.glob("*.md"), reverse=True):
        meta, body = parse_frontmatter(path.read_text(encoding="utf-8"))
        items.append({"name": path.name, "path": path, "meta": meta, "body": body, "when": publish_time(meta),
                      "problems": blog_problems(meta, body) if meta.get("status") == "draft" else []})
    return items


def needs_you(items, articles=()):
    todo = []
    for art in articles:
        status = art["meta"].get("status")
        if status == "draft":
            todo.append(f"Read article {art['name']}" + (f" ({'; '.join(art['problems'])})" if art["problems"] else ": ready to approve"))
        elif status == "failed":
            todo.append(f"Article failed to publish: {art['name']}: {str(art['meta'].get('error', ''))[:140]}")
    if any(a["meta"].get("status") == "approved" for a in articles) and not blog_publishing_configured():
        todo.append("Approved articles are waiting: add SUPABASE_URL and SUPABASE_SERVICE_KEY to .env to publish them")
    for it in items:
        status, name = it["meta"].get("status"), it["name"]
        if status == "draft":
            todo.append(f"Review {name}" + (f" ({'; '.join(it['problems'])})" if it["problems"] else ": ready to approve"))
        elif status == "failed":
            todo.append(f"Failed: {name}: {str(it['meta'].get('error', ''))[:140]}")
        if it["meta"].get("first_comment_error"):
            todo.append(f"Add the first comment by hand under {name}")
    channels = (ROOT / "context" / "channels.md").read_text(encoding="utf-8")
    renew = re.search(r"token_renew_by:\s*(\d{4}-\d{2}-\d{2})", channels)
    if renew and (dt.date.fromisoformat(renew.group(1)) - now_ist().date()).days <= 10:
        todo.append(f"Renew the LinkedIn token by {renew.group(1)}")
    return todo


def calendar():
    path = CONTENT / "calendar.md"
    rows = []
    for line in (path.read_text(encoding="utf-8").splitlines() if path.exists() else []):
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 7 and re.match(r"\d{4}-\d{2}-\d{2}", cells[0]):
            rows.append(cells)
    today = now_ist().date().isoformat()
    return Counter(r[6] for r in rows), [r for r in rows if r[0][:10] >= today][:8]


def newest_section(path):
    """Last '## ' section of a running log."""
    if not path.exists():
        return ""
    parts = re.split(r"(?m)^(?=## )", path.read_text(encoding="utf-8"))
    return parts[-1] if len(parts) > 1 else ""


def report_files():
    files = [p for folder in (REPORTS, ROOT / "email") if folder.exists() for p in folder.rglob("*.md")]
    files = [p for p in files if "daily" not in p.parts]
    return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)


def set_status(path, status, check=problems):
    """Approve a post or article, or move it back to draft; refuses when the approval checks fail."""
    meta, body = parse_frontmatter(path.read_text(encoding="utf-8"))
    if status == "approved":
        blockers = check(meta, body)
        if blockers:
            return "Not approved: " + "; ".join(blockers)
        meta.update(status="approved", approved_at=now_ist().isoformat(timespec="minutes"), approved_via="dashboard")
    else:
        meta["status"] = "draft"
        meta.pop("approved_at", None)
        meta.pop("approved_via", None)
    path.write_text(dump_frontmatter(meta, body), encoding="utf-8")
    return f"{path.name}: {meta['status']}"


# ---------- html ----------

CSS = """
:root{--bg:#f6f7f9;--card:#fff;--ink:#16181d;--muted:#667085;--line:#e4e7ec;--accent:#6d28d9;--ok:#067647;--warn:#b54708;--bad:#b42318}
@media (prefers-color-scheme:dark){:root{--bg:#0f1115;--card:#171a21;--ink:#e7e9ee;--muted:#98a2b3;--line:#2a2f3a;--accent:#a78bfa;--ok:#47cd89;--warn:#fdb022;--bad:#f97066}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,Segoe UI,sans-serif}
main{max-width:1180px;margin:0 auto;padding:20px 16px 60px}a{color:var(--accent)}h1{font-size:22px;margin:0}
h2{font-size:16px;margin:28px 0 10px}header{display:flex;justify-content:space-between;align-items:baseline;gap:12px;flex-wrap:wrap}
.muted{color:var(--muted)}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px;margin-top:16px}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 16px}
.kpi b{display:block;font-size:26px;line-height:1.2}.kpi span{font-size:13px;color:var(--muted)}
table{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--line);border-radius:12px;overflow:hidden}
th,td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top;font-size:14px}th{color:var(--muted);font-weight:600}
.pill{display:inline-block;padding:1px 8px;border-radius:99px;font-size:12px;border:1px solid var(--line)}
.approved,.posted{color:var(--ok)}.draft{color:var(--warn)}.failed{color:var(--bad)}
.chart rect{fill:var(--accent);opacity:.8}.chart{width:100%;height:120px}
button{font:inherit;padding:6px 14px;border-radius:8px;border:1px solid var(--accent);background:var(--accent);color:#fff;cursor:pointer}
button.ghost{background:transparent;color:var(--accent)}.flash{padding:10px 14px;border-radius:10px;background:var(--card);border:1px solid var(--accent);margin-top:14px}
.md{overflow-x:auto}.md table{margin:10px 0}pre.post{white-space:pre-wrap;font:15px/1.6 system-ui,Segoe UI,sans-serif;margin:0}
ul{margin:6px 0;padding-left:20px}.cols{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:16px}
img.preview{max-width:320px;border-radius:8px;border:1px solid var(--line)}
"""


def page(title, body):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(title)}</title>
<style>{CSS}</style></head><body><main>{body}</main></body></html>"""


def md(text):
    return f'<div class="md">{markdown.markdown(text, extensions=["tables", "fenced_code", "sane_lists"])}</div>'


def kpi(value, label):
    return f'<div class="card kpi"><b>{e(str(value))}</b><span>{e(label)}</span></div>'


def bars(daily, width=640, height=120):
    if not daily:
        return '<p class="muted">No daily data yet.</p>'
    top, step = max(v for _, v in daily) or 1, width / len(daily)
    rects = "".join(
        f'<rect x="{i * step:.1f}" y="{height - v / top * height:.1f}" width="{max(step - 2, 1):.1f}" '
        f'height="{v / top * height:.1f}"><title>{d[:4]}-{d[4:6]}-{d[6:]}: {v} sessions</title></rect>'
        for i, (d, v) in enumerate(daily))
    return f'<svg class="chart" viewBox="0 0 {width} {height}" preserveAspectRatio="none" role="img" aria-label="Daily sessions">{rects}</svg>'


def view_link(path, label=None):
    rel = path.relative_to(ROOT).as_posix()
    return f'<a href="/view?path={quote(rel)}">{e(label or rel)}</a>'


def overview(flash=""):
    w, a, s, items, articles = website(), aeo(), seo(), posts(), blogs()
    statuses = Counter(it["meta"].get("status", "?") for it in items)
    cal_counts, upcoming = calendar()
    daily_report = latest(REPORTS / "daily", "*.md")
    alerts = REPORTS / "alerts.md"
    parts = [f'<header><h1>AnantaSutra Marketing</h1><span class="muted">IST {now_ist():%a %d %b, %H:%M}'
             f'{" · last daily run " + daily_report.stem if daily_report else ""}</span></header>']
    if flash:
        parts.append(f'<div class="flash">{e(flash)}</div>')
    human = w["sessions"] - w["singapore"]
    parts.append('<div class="grid">'
                 + kpi(w["sessions"], f"website sessions ({w['period'] or 'no data'})")
                 + kpi(human, "without Singapore bot traffic")
                 + kpi(w["leads"], "leads tracked (GA4 key events)")
                 + kpi(f"{w['clicks']} / {w['impressions']}", "Google clicks / impressions")
                 + kpi(f"{a['cited']}/{a['prompts']}" if a else "-", f"AI-search answers citing you{' (' + a['date'] + ')' if a else ''}")
                 + kpi(f"{s.get('critical', 0) + s.get('high', 0)}" if s else "-", f"critical + high SEO issues{' (' + str(s['date']) + ')' if s else ''}")
                 + kpi(statuses.get("posted", 0), "posts published")
                 + kpi(f"{statuses.get('approved', 0)} / {statuses.get('draft', 0)}", "approved / waiting for you")
                 + "</div>")
    parts.append(f'<h2>Daily website sessions</h2><div class="card">{bars(w["daily"])}</div>')

    todo = needs_you(items, articles)
    parts.append("<h2>Needs you</h2>" + (
        '<div class="card"><ul>' + "".join(f"<li>{e(t)}</li>" for t in todo) + "</ul></div>" if todo
        else '<div class="card muted">Nothing right now.</div>'))

    rows = "".join(
        f'<tr><td>{e(it["when"].strftime("%a %d %b %H:%M")) if it["when"] else "-"}</td>'
        f'<td>{e(str(it["meta"].get("platform", "")))}</td>'
        f'<td><span class="pill {e(str(it["meta"].get("status", "")))}">{e(str(it["meta"].get("status", "")))}</span></td>'
        f'<td>{e(it["hook"])}</td><td><a href="/post?f={quote(it["name"])}">open</a></td></tr>'
        for it in sorted(items, key=lambda i: i["when"] or dt.datetime.max))
    parts.append('<h2>Posts (times in IST)</h2><table><tr><th>When</th><th>Where</th><th>Status</th><th>Hook</th><th></th></tr>'
                 + (rows or '<tr><td colspan="5" class="muted">Queue is empty.</td></tr>') + "</table>")

    market = md(newest_section(DATA / "intel" / "log.md") or "_No intel yet._")
    alert_lines = alerts.read_text(encoding="utf-8").strip().splitlines()[-6:] if alerts.exists() else []
    parts.append('<div class="cols"><div><h2>Market today</h2><div class="card">' + market
                 + ("<b>Alerts</b>" + md("\n".join(alert_lines)) if alert_lines else "") + "</div></div>"
                 + '<div><h2>Latest daily summary</h2><div class="card">'
                 + (md(daily_report.read_text(encoding="utf-8")) if daily_report else '<span class="muted">No daily run yet.</span>')
                 + "</div></div></div>")

    queries = "".join(f'<tr><td>{e(q["query"])}</td><td>{q["clicks"]}</td><td>{q["impressions"]}</td><td>{q["position"]}</td></tr>'
                      for q in w["queries"])
    upcoming_rows = "".join(f"<tr><td>{e(r[0])}</td><td>{e(r[1])}</td><td>{e(r[3][:90])}</td><td>{e(r[6])}</td></tr>" for r in upcoming)
    parts.append('<div class="cols"><div><h2>Top Google searches</h2><table><tr><th>Query</th><th>Clicks</th><th>Impr.</th><th>Pos.</th></tr>'
                 + (queries or '<tr><td colspan="4" class="muted">No data.</td></tr>') + "</table></div>"
                 + '<div><h2>Campaign calendar</h2><p class="muted">' + e(", ".join(f"{k}: {v}" for k, v in cal_counts.items()))
                 + '</p><table><tr><th>Date</th><th>Where</th><th>Topic</th><th>Status</th></tr>'
                 + (upcoming_rows or '<tr><td colspan="4" class="muted">Nothing planned.</td></tr>') + "</table></div></div>")

    article_rows = "".join(
        f'<tr><td>{e(a_["when"].strftime("%a %d %b %H:%M")) if a_["when"] else "-"}</td>'
        f'<td><span class="pill {e(str(a_["meta"].get("status", "")))}">{e(str(a_["meta"].get("status", "")))}</span></td>'
        f'<td>{e(str(a_["meta"].get("title", a_["name"])))}</td><td><a href="/blog?f={quote(a_["name"])}">open</a></td></tr>'
        for a_ in articles)
    parts.append('<h2>Blog articles (publish time in IST)</h2><table><tr><th>Publish</th><th>Status</th><th>Title</th><th></th></tr>'
                 + (article_rows or '<tr><td colspan="4" class="muted">No articles yet.</td></tr>') + "</table>")

    parts.append('<h2>Reports</h2><div class="card"><ul>' + "".join(
        f'<li>{view_link(p)} <span class="muted">{dt.datetime.fromtimestamp(p.stat().st_mtime):%d %b}</span></li>'
        for p in report_files()) + "</ul></div>")
    return page("AnantaSutra Marketing", "".join(parts))


def post_page(name, flash=""):
    path = QUEUE / Path(name).name
    if not path.exists():
        path = POSTED / Path(name).name
    if not path.exists():
        return None
    meta, body = parse_frontmatter(path.read_text(encoding="utf-8"))
    status, queued = meta.get("status", ""), path.parent == QUEUE
    blockers = problems(meta, body) if queued else []
    when = when_of(meta)
    images = meta.get("images") or ([meta["image"]] if meta.get("image") else [])
    previews = "".join(f'<img class="preview" src="/media?f={quote(Path(p).name)}" alt="">' for p in images if (ROOT / p).exists())
    form = ""
    if queued and status == "draft" and not blockers:
        form = action_form(path.name, "approved", "Approve: publish at the scheduled time")
    elif queued and status == "approved":
        form = action_form(path.name, "draft", "Move back to draft", ghost=True)
    details = "".join(f"<tr><th>{e(k)}</th><td>{e(str(meta.get(k)))}</td></tr>"
                      for k in ("platform", "pillar", "audience", "format", "review", "post_url", "error") if meta.get(k))
    body_html = [
        '<p><a href="/">&larr; Dashboard</a></p>',
        f'<div class="flash">{e(flash)}</div>' if flash else "",
        f'<h1>{e(path.name)}</h1><p><span class="pill {e(status)}">{e(status)}</span> '
        f'<span class="muted">{e(when.strftime("%A %d %B %Y, %H:%M IST")) if when else "no time set"}</span> · '
        f'<a href="vscode://file/{quote(path.as_posix())}">edit in VS Code</a></p>',
        f'<h2>Post text</h2><div class="card"><pre class="post">{e(body.strip())}</pre></div>',
        f'<h2>First comment</h2><div class="card"><pre class="post">{e(str(meta["first_comment"]))}</pre></div>' if meta.get("first_comment") else "",
        f'<h2>Image</h2><div class="card">{previews}</div>' if previews else "",
        f'<h2>Visual brief</h2><div class="card"><pre class="post">{e(str(meta["visual_brief"]))}</pre></div>' if meta.get("visual_brief") else "",
        f"<h2>Details</h2><table>{details}</table>" if details else "",
        ('<h2>Before it can be approved</h2><div class="card"><ul>' + "".join(f"<li>{e(b)}</li>" for b in blockers) + "</ul></div>") if blockers else "",
        f'<p style="margin-top:20px">{form}</p>',
    ]
    return page(path.name, "".join(body_html))


def action_form(name, status, label, ghost=False, kind="post"):
    return (f'<form method="post" action="/{kind}"><input type="hidden" name="f" value="{e(name)}">'
            f'<input type="hidden" name="status" value="{status}"><input type="hidden" name="token" value="{TOKEN}">'
            f'<button{" class=ghost" if ghost else ""}>{e(label)}</button></form>')


def blog_page(name, flash=""):
    path = BLOG / Path(name).name
    if not path.exists():
        return None
    meta, body = parse_frontmatter(path.read_text(encoding="utf-8"))
    status, when = meta.get("status", ""), publish_time(meta)
    blockers = blog_problems(meta, body) if status == "draft" else []
    form = ""
    if status == "draft" and not blockers:
        form = action_form(path.name, "approved", "Approve: publish on the website at the publish time", kind="blog")
    elif status == "approved":
        form = action_form(path.name, "draft", "Move back to draft", ghost=True, kind="blog")
    details = "".join(f"<tr><th>{e(k)}</th><td>{e(str(meta.get(k)))}</td></tr>" for k in
                      ("slug", "meta_description", "category", "tags", "primary_keyword", "topic_reason", "sources", "url", "error")
                      if meta.get(k))
    parts = [
        '<p><a href="/">&larr; Dashboard</a></p>',
        f'<div class="flash">{e(flash)}</div>' if flash else "",
        f'<h1>{e(str(meta.get("title", path.name)))}</h1><p><span class="pill {e(status)}">{e(status)}</span> '
        f'<span class="muted">{e(when.strftime("%A %d %B %Y, %H:%M IST")) if when else "no publish time"}</span> · '
        f'<a href="vscode://file/{quote(path.as_posix())}">edit in VS Code</a></p>',
        f"<h2>Details</h2><table>{details}</table>" if details else "",
        ('<h2>Before it can be approved</h2><div class="card"><ul>' + "".join(f"<li>{e(b)}</li>" for b in blockers) + "</ul></div>") if blockers else "",
        f'<p style="margin-top:16px">{form}</p>',
        f'<h2>Article</h2><div class="card">{md(body)}</div>',
    ]
    return page(str(meta.get("title", path.name)), "".join(parts))


def view_page(rel):
    rel = rel.replace("\\", "/").lstrip("/")
    path = (ROOT / rel).resolve()
    if not rel.startswith(READABLE) or ROOT.resolve() not in path.parents or path.suffix not in (".md", ".csv", ".txt") \
            or not path.exists():
        return None
    text = path.read_text(encoding="utf-8")
    content = md(text) if path.suffix == ".md" else f'<pre class="post">{e(text)}</pre>'
    return page(path.name, f'<p><a href="/">&larr; Dashboard</a></p><h1>{e(rel)}</h1><div class="card">{content}</div>')


# ---------- server ----------

class Handler(BaseHTTPRequestHandler):
    port = 8765

    def send(self, code, body=b"", ctype="text/html; charset=utf-8", location=None):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'unsafe-inline'; img-src 'self'; script-src 'none'; form-action 'self'")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Cache-Control", "no-store")
        if location:
            self.send_header("Location", location)
        self.end_headers()
        self.wfile.write(body)

    def local_only(self):
        # Blocks DNS-rebinding: only accept requests addressed to this machine by name or loopback IP.
        if self.headers.get("Host") not in (f"localhost:{self.port}", f"127.0.0.1:{self.port}"):
            self.send(403, b"Forbidden")
            return False
        return True

    def do_GET(self):
        if not self.local_only():
            return
        url = urlparse(self.path)
        query = {k: v[0] for k, v in parse_qs(url.query).items()}
        if url.path == "/":
            return self.send(200, overview(query.get("msg", "")).encode())
        if url.path == "/post":
            html_page = post_page(query.get("f", ""), query.get("msg", ""))
            return self.send(200, html_page.encode()) if html_page else self.send(404, b"Not found")
        if url.path == "/blog":
            html_page = blog_page(query.get("f", ""), query.get("msg", ""))
            return self.send(200, html_page.encode()) if html_page else self.send(404, b"Not found")
        if url.path == "/view":
            html_page = view_page(query.get("path", ""))
            return self.send(200, html_page.encode()) if html_page else self.send(404, b"Not found")
        if url.path == "/media":
            path = MEDIA / Path(query.get("f", "")).name
            ctype = mimetypes.guess_type(path.name)[0] or ""
            if path.exists() and ctype.startswith("image/"):
                return self.send(200, path.read_bytes(), ctype)
        self.send(404, b"Not found")

    def do_POST(self):
        if not self.local_only():
            return
        length = min(int(self.headers.get("Content-Length") or 0), 10_000)
        form = {k: v[0] for k, v in parse_qs(self.rfile.read(length).decode()).items()}
        origin = self.headers.get("Origin")
        if form.get("token") != TOKEN or (origin and origin not in (f"http://localhost:{self.port}", f"http://127.0.0.1:{self.port}")):
            return self.send(403, b"Forbidden: reload the dashboard and try again")
        folder, check = {"/post": (QUEUE, problems), "/blog": (BLOG, blog_problems)}.get(self.path, (None, None))
        path = folder / Path(form.get("f", "")).name if folder else None
        if not path or not path.exists() or form.get("status") not in ("approved", "draft"):
            return self.send(400, b"Bad request")
        message = set_status(path, form["status"], check)
        self.send(303, location=f"{self.path}?f={quote(path.name)}&msg={quote(message)}")

    def log_message(self, *args):  # quiet: runs without a console under pythonw
        pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8765)
    args = ap.parse_args()
    Handler.port = args.port
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"Dashboard: http://localhost:{args.port}  (Ctrl+C to stop)")
    server.serve_forever()


if __name__ == "__main__":
    main()
