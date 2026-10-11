"""Google PageSpeed Insights (free) - Lighthouse scores, Core Web Vitals, top fixes.

    python scripts/pagespeed.py                      # SITE_URL, mobile + desktop
    python scripts/pagespeed.py --url https://anantasutra.com/services --strategy mobile

A free API key (PAGESPEED_API_KEY in .env) raises the rate limit; it works without one too.
"""
import argparse

from common import DATA, env, redact, session, today, write_json

API = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
CATEGORIES = ["performance", "seo", "accessibility", "best-practices"]


def fail(r):
    """Exit with Google's message and the usual fix; never prints the request URL (it holds the key)."""
    try:
        msg = r.json()["error"]["message"]
    except Exception:
        msg = r.text[:200]
    if r.status_code == 429:
        hint = ("Quota hit: add a free PAGESPEED_API_KEY to .env "
                "(https://developers.google.com/speed/docs/insights/v5/get-started).")
    elif "REFERRER" in r.text:
        hint = ("This API key only allows browser referrers. Google Cloud -> APIs & Services -> Credentials -> the key "
                "-> Application restrictions: None (keep its API restriction to the PageSpeed Insights API).")
    else:
        hint = ""
    raise SystemExit(f"PageSpeed {r.status_code}: {redact(msg)}\n{hint}".strip())


def run(s, url, strategy):
    params = [("url", url), ("strategy", strategy)] + [("category", c) for c in CATEGORIES]
    key = env("PAGESPEED_API_KEY")
    if key:
        params.append(("key", key))
    r = s.get(API, params=params, timeout=120)
    if r.status_code >= 400:
        fail(r)
    data = r.json()
    lh = data["lighthouseResult"]
    audits = lh["audits"]
    field = data.get("loadingExperience", {}).get("metrics", {})
    opportunities = sorted(
        (a for a in audits.values()
         if a.get("details", {}).get("type") == "opportunity" and (a.get("score") or 1) < 0.9),
        key=lambda a: a.get("details", {}).get("overallSavingsMs", 0), reverse=True)
    failed_seo = [audits[ref["id"]]["title"] for ref in lh["categories"]["seo"]["auditRefs"]
                  if audits.get(ref["id"], {}).get("score") == 0]
    return {
        "url": url, "strategy": strategy,
        "scores": {c: round((lh["categories"][c]["score"] or 0) * 100) for c in CATEGORIES},
        "lab": {k: audits[k]["displayValue"] for k in
                ["largest-contentful-paint", "cumulative-layout-shift", "total-blocking-time", "first-contentful-paint", "speed-index"]
                if k in audits and "displayValue" in audits[k]},
        "field_cwv": {k: v.get("category") for k, v in field.items()} or "no field data (low traffic)",
        "top_opportunities": [{"title": a["title"], "savings_ms": a["details"].get("overallSavingsMs")} for a in opportunities[:6]],
        "failed_seo_audits": failed_seo,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default=env("SITE_URL", "https://anantasutra.com"))
    ap.add_argument("--strategy", choices=["mobile", "desktop", "both"], default="both")
    args = ap.parse_args()
    s = session()
    strategies = ["mobile", "desktop"] if args.strategy == "both" else [args.strategy]
    results = [run(s, args.url, st) for st in strategies]
    out = DATA / "seo" / f"pagespeed-{today()}.json"
    write_json(out, results)
    for res in results:
        print(f"[{res['strategy']}] {res['url']} scores={res['scores']}")
        print(f"  lab={res['lab']}")
        print(f"  field={res['field_cwv']}")
        for o in res["top_opportunities"]:
            print(f"  fix: {o['title']} (~{o['savings_ms']} ms)")
        if res["failed_seo_audits"]:
            print(f"  failed SEO checks: {res['failed_seo_audits']}")
    print(f"saved -> {out.relative_to(DATA.parent)}")


if __name__ == "__main__":
    main()
