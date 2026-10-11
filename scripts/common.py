"""Shared helpers for the marketing scripts: paths, .env loading, HTTP, frontmatter."""
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path

import requests
import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
CONTEXT = ROOT / "context"
CONTENT = ROOT / "content"
REPORTS = ROOT / "reports"

USER_AGENT = "Mozilla/5.0 (compatible; AnantaSutraMarketingBot/1.0; +https://anantasutra.com)"

# Windows consoles default to cp1252; force UTF-8 so Hindi text and emoji print safely.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")


def load_env():
    """Load KEY=VALUE pairs from ROOT/.env without overriding real environment variables."""
    path = ROOT / ".env"
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_env()


def set_env_value(key, value, path=None):
    """Create or replace KEY=value in .env, keeping every other line (used to save refreshed tokens)."""
    path = Path(path or ROOT / ".env")
    lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    for i, line in enumerate(lines):
        if not line.lstrip().startswith("#") and line.split("=", 1)[0].strip() == key:
            lines[i] = f"{key}={value}"
            break
    else:
        lines.append(f"{key}={value}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    os.environ[key] = value


def env(key, default=None, required=False):
    value = os.environ.get(key, default)
    if required and not value:
        sys.exit(f"Missing {key} in .env (see .env.example)")
    return value


IST = dt.timezone(dt.timedelta(hours=5, minutes=30), "IST")


def now_ist():
    """Current India time (naive). Dates and post schedules are IST whatever timezone this PC is set to."""
    return dt.datetime.now(IST).replace(tzinfo=None, microsecond=0)


def today():
    return now_ist().date().isoformat()


SECRET_RE = re.compile(r"((?:access_token|key|token)=)[^&\s'\"]+", re.I)


def redact(text):
    """Hide tokens/keys that appear in URLs before text reaches a log or the console."""
    return SECRET_RE.sub(r"\1***", str(text))


class _Session(requests.Session):
    """requests.Session whose connection errors don't leak query-string secrets."""

    def request(self, *args, **kwargs):
        try:
            return super().request(*args, **kwargs)
        except requests.RequestException as e:
            raise requests.RequestException(redact(e)) from None


def session():
    s = _Session()
    s.headers.update({"User-Agent": USER_AGENT, "Accept-Language": "en-IN,en;q=0.9"})
    return s


def read_json(path, default=None):
    path = Path(path)
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")


def read_yaml(path, default=None):
    path = Path(path)
    if not path.exists():
        return default
    return yaml.safe_load(path.read_text(encoding="utf-8")) or default


FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", re.S)


def parse_frontmatter(text):
    """Split a markdown file into (frontmatter dict, body)."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    return yaml.safe_load(m.group(1)) or {}, m.group(2)


def dump_frontmatter(meta, body):
    fm = yaml.safe_dump(meta, sort_keys=False, allow_unicode=True).strip()
    return f"---\n{fm}\n---\n{body}"


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60] or "item"


def log(name, message):
    path = DATA / "logs" / f"{name}.log"
    path.parent.mkdir(parents=True, exist_ok=True)
    line = f"{now_ist().isoformat()} {redact(message)}"
    with path.open("a", encoding="utf-8") as f:
        f.write(line + "\n")
    print(line)
