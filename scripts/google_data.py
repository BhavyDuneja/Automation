"""Google Search Console + GA4 data (both free) via a service account.

Setup: README step 6. In short: Google Cloud project -> enable "Google Search Console API"
+ "Google Analytics Data API" -> service account -> JSON key saved as secrets/google-sa.json
-> add the service-account email as a user in Search Console (Restricted) and GA4 (Viewer).
  GOOGLE_SA_JSON   - key file path (relative to the project root is fine)
  GSC_SITE         - sc-domain:anantasutra.com (Domain property) or https://www.anantasutra.com/ (URL prefix)
  GA4_PROPERTY_ID  - numeric Property ID (GA4 Admin -> Property details), not the G-XXXX measurement ID

    python scripts/google_data.py --check     # verify access, list the properties the key can see
    python scripts/google_data.py --days 28
"""
import argparse
import datetime as dt
from pathlib import Path
from urllib.parse import quote

from common import DATA, ROOT, env, today, write_json

SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly",
          "https://www.googleapis.com/auth/analytics.readonly"]
GSC_API = "https://searchconsole.googleapis.com/webmasters/v3"
GA4_API = "https://analyticsdata.googleapis.com/v1beta"


class ApiError(Exception):
    pass


def authed():
    """Return (authorized session, service-account email)."""
    from google.auth.exceptions import RefreshError
    from google.auth.transport.requests import AuthorizedSession, Request
    from google.oauth2 import service_account

    path = Path(env("GOOGLE_SA_JSON", "secrets/google-sa.json"))
    if not path.is_absolute():
        path = ROOT / path
    if not path.exists():
        raise SystemExit(f"Key file not found: {path}\n"
                         "Create a service-account JSON key and save it there (README step 6).")
    try:
        creds = service_account.Credentials.from_service_account_file(str(path), scopes=SCOPES)
        creds.refresh(Request())
    except ValueError:
        raise SystemExit(f"{path.name} is not a service-account key (an OAuth client file looks similar). "
                         "Download it from IAM & Admin -> Service Accounts -> Keys.")
    except RefreshError as e:
        raise SystemExit(f"Google rejected the key: {e}\nThe key may be deleted or disabled; create a new one.")
    return AuthorizedSession(creds), creds.service_account_email


def ok(r, api, sa):
    """Return the JSON body, or raise ApiError with Google's message and the usual fix."""
    if r.status_code < 400:
        return r.json()
    try:
        msg = r.json()["error"]["message"]
    except Exception:
        msg = r.text[:300]
    if "has not been used" in msg or "is disabled" in msg:
        fix = "enable this API in Google Cloud (APIs & Services -> Library), wait ~5 minutes and retry"
    elif r.status_code != 403:
        fix = "the request itself was rejected (a script bug, not an access problem)"
    elif api == "gsc":
        fix = (f"add {sa} in Search Console -> Settings -> Users and permissions (Restricted) and set GSC_SITE "
               "to the exact property name; --check lists the properties this key can see")
    else:
        fix = (f"add {sa} in GA4 -> Admin -> Property access management (Viewer); GA4_PROPERTY_ID must be "
               "the numeric Property ID, not the G-XXXX measurement ID")
    raise ApiError(f"{api.upper()} {r.status_code}: {msg}\n  fix: {fix}")


def gsc(s, sa, start, end, dimension, limit=50):
    site = quote(env("GSC_SITE"), safe="")
    r = s.post(f"{GSC_API}/sites/{site}/searchAnalytics/query", timeout=60,
               json={"startDate": start, "endDate": end, "dimensions": [dimension], "rowLimit": limit})
    return [{dimension: row["keys"][0], "clicks": row["clicks"], "impressions": row["impressions"],
             "ctr": round(row["ctr"] * 100, 2), "position": round(row["position"], 1)}
            for row in ok(r, "gsc", sa).get("rows", [])]


GA4_METRICS = ("sessions", "totalUsers", "engagementRate", "keyEvents")


def ga4(s, sa, start, end, dimension="sessionDefaultChannelGroup", metrics=GA4_METRICS, limit=50):
    order = ({"dimension": {"dimensionName": "date"}} if dimension == "date"
             else {"metric": {"metricName": metrics[0]}, "desc": True})
    r = s.post(f"{GA4_API}/properties/{env('GA4_PROPERTY_ID')}:runReport", timeout=60, json={
        "dateRanges": [{"startDate": start, "endDate": end}],
        "dimensions": [{"name": dimension}],
        "metrics": [{"name": n} for n in metrics],
        "orderBys": [order], "limit": limit,
    })
    data = ok(r, "ga4", sa)
    names = [m["name"] for m in data.get("metricHeaders", [])]
    return [{dimension: row["dimensionValues"][0]["value"],
             **{n: v["value"] for n, v in zip(names, row["metricValues"])}} for row in data.get("rows", [])]


def check(s, sa):
    print(f"Service account: {sa}")
    try:
        sites = ok(s.get(f"{GSC_API}/sites", timeout=30), "gsc", sa).get("siteEntry", [])
        for site in sites:
            print(f"  Search Console: {site['siteUrl']} ({site['permissionLevel']})")
        if not sites:
            print("  Search Console: no property shared with this account yet")
        if env("GSC_SITE"):
            found = any(site["siteUrl"] == env("GSC_SITE") for site in sites)
            print(f"  GSC_SITE={env('GSC_SITE')} -> {'OK' if found else 'not in the list above: fix .env or add the user'}")
    except ApiError as e:
        print(f"  {e}")
    if not env("GA4_PROPERTY_ID"):
        print("  GA4: GA4_PROPERTY_ID is empty in .env")
        return
    try:
        rows = ga4(s, sa, "7daysAgo", "today")
        print(f"  GA4 property {env('GA4_PROPERTY_ID')}: OK, "
              f"{sum(int(r['sessions']) for r in rows)} sessions in the last 7 days")
    except ApiError as e:
        print(f"  {e}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=28)
    ap.add_argument("--check", action="store_true", help="verify access and list the properties the key can see")
    args = ap.parse_args()
    s, sa = authed()
    if args.check:
        return check(s, sa)

    end = dt.date.today() - dt.timedelta(days=2)  # GSC data lags ~2 days
    start = end - dt.timedelta(days=args.days - 1)
    prev_end = start - dt.timedelta(days=1)
    prev_start = prev_end - dt.timedelta(days=args.days - 1)
    period, previous = (str(start), str(end)), (str(prev_start), str(prev_end))
    out = {"period": period, "previous": previous, "errors": []}

    if env("GSC_SITE"):
        try:
            out["gsc_queries"] = gsc(s, sa, *period, "query")
            out["gsc_pages"] = gsc(s, sa, *period, "page")
            out["gsc_queries_previous"] = gsc(s, sa, *previous, "query")
        except ApiError as e:
            out["errors"].append(str(e))
    if env("GA4_PROPERTY_ID"):
        try:
            out["ga4_channels"] = ga4(s, sa, *period)
            out["ga4_channels_previous"] = ga4(s, sa, *previous)
            out["ga4_landing_pages"] = ga4(s, sa, *period, "landingPage", limit=25)
            out["ga4_countries"] = ga4(s, sa, *period, "country", limit=15)
            out["ga4_daily"] = ga4(s, sa, *period, "date", metrics=("sessions", "totalUsers"), limit=100)
        except ApiError as e:
            out["errors"].append(str(e))

    path = DATA / "google" / f"google-{today()}.json"
    write_json(path, out)
    print(f"saved -> {path.relative_to(DATA.parent)}")
    for q in out.get("gsc_queries", [])[:15]:
        print(f"  {q['query'][:50]:50} clicks={q['clicks']} impr={q['impressions']} pos={q['position']}")
    for c in out.get("ga4_channels", []):
        print(f"  {c['sessionDefaultChannelGroup'][:22]:22} sessions={c['sessions']} "
              f"users={c['totalUsers']} key_events={c['keyEvents']}")
    if out.get("ga4_countries"):
        print("  top countries: " + ", ".join(f"{c['country']} {c['sessions']}" for c in out["ga4_countries"][:6]))
    if out.get("ga4_daily"):
        peak = max(out["ga4_daily"], key=lambda d: int(d["sessions"]))
        print(f"  busiest day: {peak['date']} with {peak['sessions']} sessions")
    for e in out["errors"]:
        print(e)
    if out["errors"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
