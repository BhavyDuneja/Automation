"""Instagram posting + insights via the official API with Instagram Login (free).

Needs an Instagram professional (Business/Creator) account and a Meta app left in Development mode with that
account as an Instagram Tester; no App Review is needed for your own account. In .env:
  IG_ACCESS_TOKEN  - long-lived token from the app dashboard (API setup with Instagram login)
  IG_USER_ID       - optional; looked up from the token when empty
  IMGBB_API_KEY    - free key from https://api.imgbb.com. Instagram only accepts public JPEG URLs, so local
                     images are converted to JPEG and hosted there (auto-deleted after 7 days)
  IG_GRAPH_HOST / IG_API_VERSION - defaults graph.instagram.com / v23.0

    python scripts/instagram.py whoami
    python scripts/instagram.py post "caption" --image content/media/a.png [--image content/media/b.png ...]
    python scripts/instagram.py insights <media_id>
    python scripts/instagram.py refresh      # renew the 60-day token (publish_queue.py also does this weekly)
"""
import argparse
import base64
import datetime as dt
import io
import time
from pathlib import Path

from common import DATA, ROOT, env, now_ist, read_json, session, set_env_value, write_json

TOKEN_STATE = DATA / "social" / "ig_token.json"
_user_id = None


def base():
    return f"https://{env('IG_GRAPH_HOST', 'graph.instagram.com')}/{env('IG_API_VERSION', 'v23.0')}"


def call(s, method, path, **params):
    params["access_token"] = env("IG_ACCESS_TOKEN", required=True)
    r = s.request(method, f"{base()}/{path}", params=params if method == "GET" else None,
                  data=params if method == "POST" else None, timeout=60)
    if r.status_code >= 400:
        raise RuntimeError(f"Instagram {r.status_code}: {r.text[:400]}")
    return r.json()


def configured_user_id():
    """IG_USER_ID from .env if it is a numeric account id (a username there is ignored)."""
    value = (env("IG_USER_ID") or "").strip()
    return value if value.isdigit() else None


def user_id(s):
    global _user_id
    _user_id = _user_id or configured_user_id() or call(s, "GET", "me", fields="user_id")["user_id"]
    return _user_id


def to_jpeg(path):
    """JPEG bytes for any image; transparent areas become white."""
    from PIL import Image
    img = Image.open(path)
    if img.format == "JPEG":
        return Path(path).read_bytes()
    if img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGBA")
        flat = Image.new("RGB", img.size, "white")
        flat.paste(img, mask=img.split()[-1])
        img = flat
    else:
        img = img.convert("RGB")
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=92)
    return buf.getvalue()


def host_image(path):
    """Upload a local image to ImgBB as JPEG (deleted after 7 days) and return its public URL."""
    key = env("IMGBB_API_KEY")
    if not key:
        raise RuntimeError("Local images need IMGBB_API_KEY in .env (free at https://api.imgbb.com), "
                           "or set image_url to a public JPEG URL")
    r = session().post("https://api.imgbb.com/1/upload", params={"key": key, "expiration": 7 * 86400},
                       data={"image": base64.b64encode(to_jpeg(path)).decode(), "name": Path(path).stem},
                       timeout=120)
    if r.status_code >= 400:
        raise RuntimeError(f"ImgBB {r.status_code}: {r.text[:300]}")
    return r.json()["data"]["url"]


def queue_images(meta):
    """Public image URLs for a queue item: `image_url` (str or list) as given, else local `images`/`image` hosted."""
    urls = meta.get("image_url") or []
    urls = [u for u in ([urls] if isinstance(urls, str) else urls) if u]
    if urls:
        return urls
    local = meta.get("images") or ([meta["image"]] if meta.get("image") else [])
    return [host_image(ROOT / p) for p in local]


def wait_ready(s, container):
    for _ in range(40):
        status = call(s, "GET", container, fields="status_code").get("status_code")
        if status == "FINISHED":
            return
        if status in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"Instagram container {container} {status}")
        time.sleep(3)
    raise RuntimeError(f"Instagram container {container} not ready after 2 minutes")


def post(caption, image_urls):
    """Publish one image, or a carousel of 2-10; returns (media_id, permalink)."""
    if isinstance(image_urls, str):
        image_urls = [image_urls]
    if not image_urls or not all(u.startswith("https://") for u in image_urls):
        raise ValueError("Instagram needs public https image URLs")
    if len(image_urls) > 10:
        raise ValueError("Instagram carousels take at most 10 images")
    s = session()
    ig = user_id(s)
    if len(image_urls) == 1:
        container = call(s, "POST", f"{ig}/media", image_url=image_urls[0], caption=caption)["id"]
    else:
        children = [call(s, "POST", f"{ig}/media", image_url=u, is_carousel_item="true")["id"] for u in image_urls]
        for child in children:
            wait_ready(s, child)
        container = call(s, "POST", f"{ig}/media", media_type="CAROUSEL", children=",".join(children),
                         caption=caption)["id"]
    wait_ready(s, container)
    media_id = call(s, "POST", f"{ig}/media_publish", creation_id=container)["id"]
    permalink = call(s, "GET", media_id, fields="permalink").get("permalink", "")
    return media_id, permalink


def refresh_token():
    """Swap the long-lived token for a fresh 60-day one and save it to .env; returns the new expiry."""
    r = session().get("https://graph.instagram.com/refresh_access_token", timeout=60, params={
        "grant_type": "ig_refresh_token", "access_token": env("IG_ACCESS_TOKEN", required=True)})
    if r.status_code >= 400:
        raise RuntimeError(f"Instagram token refresh {r.status_code}: {r.text[:300]}")
    data = r.json()
    set_env_value("IG_ACCESS_TOKEN", data["access_token"])
    expires = now_ist() + dt.timedelta(seconds=int(data.get("expires_in", 0)))
    write_json(TOKEN_STATE, {"refreshed": now_ist().isoformat(), "expires": expires.isoformat()})
    return expires


def maybe_refresh(every_days=7):
    """Refresh at most weekly (retry daily after a failure); returns a note to log, or None."""
    if not env("IG_ACCESS_TOKEN") or env("IG_GRAPH_HOST", "graph.instagram.com") != "graph.instagram.com":
        return None
    state, now = read_json(TOKEN_STATE, {}), now_ist()

    def older_than(key, days):
        return not state.get(key) or now - dt.datetime.fromisoformat(state[key]) >= dt.timedelta(days=days)

    if not (older_than("refreshed", every_days) and older_than("attempted", 1)):
        return None
    try:
        return f"token refreshed, valid until {refresh_token():%Y-%m-%d}"
    except Exception as e:  # a token younger than 24h can't be refreshed yet; try again tomorrow
        write_json(TOKEN_STATE, {**state, "attempted": now.isoformat(), "error": str(e)[:300]})
        return f"token refresh failed: {e}"


def insights(media_id):
    s = session()
    # Metric names change between API versions; fall back to a smaller set if rejected.
    for metrics in ("reach,likes,comments,saved,shares,views,total_interactions", "reach,likes,comments,saved"):
        try:
            data = call(s, "GET", f"{media_id}/insights", metric=metrics)["data"]
            return {d["name"]: d["values"][0]["value"] for d in data}
        except RuntimeError as e:
            last = e
    raise last


def account():
    s = session()
    return call(s, "GET", user_id(s), fields="username,followers_count,media_count")


def whoami():
    me = call(session(), "GET", "me", fields="user_id,username,account_type,followers_count,media_count")
    print(me)
    if env("IG_USER_ID") and not configured_user_id():
        print(f"note: IG_USER_ID in .env ({env('IG_USER_ID')}) isn't a numeric id, so it's ignored; "
              f"posts use the token's user_id {me.get('user_id')}")
    elif configured_user_id() and configured_user_id() != me.get("user_id"):
        print(f"note: IG_USER_ID in .env ({configured_user_id()}) differs from the token's user_id")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("whoami")
    sub.add_parser("refresh")
    p = sub.add_parser("post")
    p.add_argument("caption")
    p.add_argument("--image", action="append", default=[], help="local file (needs IMGBB_API_KEY); repeat for a carousel")
    p.add_argument("--image-url", action="append", default=[], help="public JPEG URL; repeat for a carousel")
    i = sub.add_parser("insights")
    i.add_argument("media_id")
    args = ap.parse_args()
    if args.cmd == "whoami":
        whoami()
    elif args.cmd == "refresh":
        print(f"token valid until {refresh_token():%Y-%m-%d}")
    elif args.cmd == "post":
        print(post(args.caption, args.image_url + [host_image(ROOT / path) for path in args.image]))
    else:
        print(insights(args.media_id))
