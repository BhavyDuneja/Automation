"""Collect metrics for posts in content/posted/ into data/social/metrics-<date>.json.

Instagram metrics come from the Graph API. LinkedIn post analytics need extra API
approval, so for LinkedIn export the CSV from your page/profile analytics into
data/manual/ and the performance-report skill will read it.

    python scripts/social_insights.py
"""
from common import CONTENT, DATA, env, parse_frontmatter, today, write_json


def main():
    rows, account = [], None
    if env("IG_ACCESS_TOKEN"):
        import instagram
        try:
            account = instagram.account()
        except Exception as e:
            account = {"error": str(e)[:200]}

    for path in sorted((CONTENT / "posted").glob("*.md")):
        meta, body = parse_frontmatter(path.read_text(encoding="utf-8"))
        row = {"file": path.name, "platform": meta.get("platform"), "posted_at": str(meta.get("posted_at")),
               "url": meta.get("post_url"), "pillar": meta.get("pillar"), "hook": body.strip().splitlines()[0][:100] if body.strip() else ""}
        if meta.get("platform") == "instagram" and env("IG_ACCESS_TOKEN"):
            import instagram
            try:
                row["metrics"] = instagram.insights(meta["post_id"])
            except Exception as e:
                row["metrics_error"] = str(e)[:200]
        rows.append(row)

    out = DATA / "social" / f"metrics-{today()}.json"
    write_json(out, {"date": today(), "instagram_account": account, "posts": rows})
    print(f"{len(rows)} posted items; instagram account: {account}")
    print(f"saved -> {out.relative_to(DATA.parent)}")


if __name__ == "__main__":
    main()
