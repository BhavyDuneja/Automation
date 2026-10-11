"""LinkedIn posting via the official REST Posts API (free).

Setup (one time, see README):
  LINKEDIN_ACCESS_TOKEN  - OAuth token. Personal profile: scopes openid profile w_member_social.
                           Company page: w_organization_social (needs Community Management API access).
  LINKEDIN_AUTHOR_URN    - optional. Empty = post as the token owner (looked up from the token).
                           Company page: urn:li:organization:<id>
  LINKEDIN_API_VERSION   - optional YYYYMM. Empty = automatic; versions LinkedIn reports as inactive
                           are skipped by trying the previous monthly versions.

    python scripts/linkedin.py whoami          # token check: name, person URN, working API version
    python scripts/linkedin.py post "text" [--image path.png]
"""
import argparse
import datetime as dt
import re
from pathlib import Path
from urllib.parse import quote

from common import env, session

API = "https://api.linkedin.com/rest"
# Characters LinkedIn's "little text" format treats as markup; unescaped they truncate posts.
RESERVED = re.compile(r"([\\|{}@\[\]()<>#*_~])")
HASHTAG = re.compile(r"(?<![\w\\])#(\w+)")
_working_version = None


def token():
    return env("LINKEDIN_ACCESS_TOKEN", required=True)


def candidate_versions():
    """Last working / configured version first, then the previous 8 monthly versions (each lives ~1 year)."""
    month = dt.date.today().replace(day=1)
    recent = []
    for _ in range(8):
        month = (month - dt.timedelta(days=1)).replace(day=1)
        recent.append(month.strftime("%Y%m"))
    first = [v for v in (_working_version, env("LINKEDIN_API_VERSION")) if v]
    return list(dict.fromkeys(first + recent))


def rest(s, method, path, **kwargs):
    """Call a versioned REST endpoint, skipping versions LinkedIn says are not active."""
    global _working_version
    for version in candidate_versions():
        headers = {"Authorization": f"Bearer {token()}", "LinkedIn-Version": version,
                   "X-Restli-Protocol-Version": "2.0.0"}
        r = s.request(method, f"{API}/{path}", headers=headers, timeout=60, **kwargs)
        if r.status_code != 426 and "NONEXISTENT_VERSION" not in r.text:
            _working_version = version
            return r
    raise RuntimeError(f"LinkedIn rejected every API version tried: {r.text[:300]}")


def me(s):
    """(name, person URN) of the token's owner; needs the openid + profile scopes."""
    r = s.get("https://api.linkedin.com/v2/userinfo", headers={"Authorization": f"Bearer {token()}"}, timeout=30)
    if r.status_code == 401:
        raise RuntimeError("LinkedIn token expired or invalid (401): generate a new one (README step 4)")
    if r.status_code == 403:
        raise RuntimeError("Token lacks the openid/profile scopes: regenerate it with openid profile "
                           "w_member_social, or set LINKEDIN_AUTHOR_URN in .env")
    r.raise_for_status()
    info = r.json()
    return info.get("name"), f"urn:li:person:{info['sub']}"


def author(s):
    return env("LINKEDIN_AUTHOR_URN") or me(s)[1]


def to_little_text(text):
    """Escape reserved characters but keep #hashtags clickable."""
    tags = []

    def keep(m):
        tags.append(m.group(1))
        return f"\x00{len(tags) - 1}\x00"

    text = HASHTAG.sub(keep, text)
    text = RESERVED.sub(r"\\\1", text)
    return re.sub("\x00(\\d+)\x00", lambda m: "{hashtag|\\#|" + tags[int(m.group(1))] + "}", text)


def upload_image(s, owner, path):
    r = rest(s, "POST", "images?action=initializeUpload", json={"initializeUploadRequest": {"owner": owner}})
    r.raise_for_status()
    value = r.json()["value"]
    up = s.put(value["uploadUrl"], data=Path(path).read_bytes(),
               headers={"Authorization": f"Bearer {token()}"}, timeout=120)
    up.raise_for_status()
    return value["image"]


def post(text, image=None, alt_text=""):
    """Publish a post; returns (post_urn, url)."""
    s = session()
    owner = author(s)
    body = {
        "author": owner,
        "commentary": to_little_text(text),
        "visibility": "PUBLIC",
        "distribution": {"feedDistribution": "MAIN_FEED", "targetEntities": [], "thirdPartyDistributionChannels": []},
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False,
    }
    if image:
        body["content"] = {"media": {"id": upload_image(s, owner, image), "altText": alt_text[:300]}}
    r = rest(s, "POST", "posts", json=body)
    if r.status_code >= 400:
        raise RuntimeError(f"LinkedIn {r.status_code}: {r.text[:400]}")
    urn = r.headers.get("x-restli-id", "")
    return urn, f"https://www.linkedin.com/feed/update/{urn}/"


def comment(post_urn, text):
    """Comment as the author under a post (used for 'link in comments'); returns the comment id."""
    s = session()
    r = rest(s, "POST", f"socialActions/{quote(post_urn, safe='')}/comments",
             json={"actor": author(s), "object": post_urn, "message": {"text": text}})
    if r.status_code >= 400:
        raise RuntimeError(f"LinkedIn comment {r.status_code}: {r.text[:300]}")
    return r.headers.get("x-restli-id", "")


def whoami():
    s = session()
    name, urn = me(s)
    print(f"name={name}  person URN={urn}")
    if env("LINKEDIN_AUTHOR_URN") and env("LINKEDIN_AUTHOR_URN") != urn:
        print(f"posts go to LINKEDIN_AUTHOR_URN={env('LINKEDIN_AUTHOR_URN')}")
    # Harmless read to find an API version LinkedIn accepts; a 403 only means the token has no read scope.
    r = rest(s, "GET", "posts", params={"q": "author", "author": urn, "count": 1})
    print(f"API version {_working_version} accepted (HTTP {r.status_code})")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("whoami")
    p = sub.add_parser("post")
    p.add_argument("text")
    p.add_argument("--image")
    args = ap.parse_args()
    if args.cmd == "whoami":
        whoami()
    else:
        print(post(args.text, args.image))
