"""Render branded carousel slides (1080x1350 PNG) for queued drafts that have `slides` but no images yet.

A draft lists its slides in the frontmatter; the first one is the hook, and a standard CTA slide is added
to Instagram carousels unless the last slide is marked `cta: true`:

    slides:
      - kicker: Hiring sutra          # optional small label on the first slide
        title: A shortlist is not the same as vetting.
        body: Here is how to tell them apart.
      - title: Shortlisting matches a CV to a job description
        body: Fast and useful. It tells you who *might* fit.

Instagram posts get every slide as a carousel (`images`); `format: single-image` posts and LinkedIn
posts get only the first slide (`image`). Rendering uses Playwright's own Chromium (Hindi and emoji
render correctly). One-time setup: python -m playwright install --only-shell chromium

    python scripts/make_visuals.py                 # all drafts with slides and no images
    python scripts/make_visuals.py --file 2026-10-12-instagram-x.md --force
"""
import argparse
import base64
import html
import re
from pathlib import Path

from common import CONTENT, ROOT, dump_frontmatter, parse_frontmatter

QUEUE = CONTENT / "queue"
MEDIA = CONTENT / "media"
BRAND = CONTENT / "brand"
W, H = 1080, 1350
CTA = {"title": "Want 2-3 vetted experts to interview?",
       "body": "Book a free 30-minute consultation. Pay the salary plus one transparent fee.", "cta": True}


def data_uri(path, mime):
    return f"data:{mime};base64,{base64.b64encode(Path(path).read_bytes()).decode()}"


def rich(text):
    """Escape, then allow **bold** and *italic*."""
    text = html.escape(str(text or ""))
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    return re.sub(r"\*(.+?)\*", r"<em>\1</em>", text).replace("\n", "<br>")


def fit(text, sizes):
    """Pick a font size from (max_chars, px) pairs so long lines still fit."""
    length = len(str(text or ""))
    return next((px for limit, px in sizes if length <= limit), sizes[-1][1])


CSS = """
@font-face{font-family:Inter;src:url(%(inter)s)}
@font-face{font-family:Playfair;src:url(%(playfair)s)}
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:%(w)dpx;height:%(h)dpx;overflow:hidden}
body{font-family:Inter,'Nirmala UI','Segoe UI Emoji',sans-serif;color:#e8e6f0;
 background:radial-gradient(circle at 85%% 8%%,rgba(106,61,232,.38),transparent 46%%),
 radial-gradient(circle at 10%% 95%%,rgba(232,163,23,.16),transparent 40%%),linear-gradient(160deg,#0A0A0F,#12122a);
 display:flex;flex-direction:column;padding:72px 80px}
header{display:flex;align-items:center;justify-content:space-between}
.brand{display:flex;align-items:center;gap:18px;font-family:Playfair,serif;font-size:34px;letter-spacing:.5px}
.brand img{width:64px;height:64px}.count{font-size:26px;color:#8b89a0}
.rule{height:4px;width:120px;background:linear-gradient(90deg,#E8A317,#FFB800);border-radius:4px;margin:44px 0 0}
main{flex:1;display:flex;flex-direction:column;justify-content:center;gap:34px}
.kicker{font-size:30px;letter-spacing:4px;text-transform:uppercase;color:#E8A317;font-weight:600}
h1{font-family:Playfair,'Nirmala UI',serif;font-weight:700;line-height:1.15}
.num{font-family:Playfair,serif;font-size:132px;line-height:1;color:#E8A317;opacity:.9}
h2{font-weight:700;line-height:1.18}
p{color:#c9c6d8;line-height:1.45}
em{color:#FFB800;font-style:normal}strong{color:#fff}
.button{align-self:flex-start;background:#E8A317;color:#0A0A0F;font-weight:700;font-size:34px;padding:22px 40px;border-radius:999px}
.url{font-size:30px;color:#8b89a0}
footer{display:flex;justify-content:space-between;align-items:center;font-size:26px;color:#8b89a0;border-top:1px solid #1e1e3a;padding-top:28px}
"""


def slide_html(slide, index, total, assets):
    title, body = slide.get("title", ""), slide.get("body", "")
    if index == 0:
        inner = (f'<div class="kicker">{rich(slide["kicker"])}</div>' if slide.get("kicker") else "") + \
                f'<h1 style="font-size:{fit(title, [(12, 150), (40, 96), (70, 84), (110, 70), (999, 58)])}px">{rich(title)}</h1>' + \
                (f'<p style="font-size:{fit(body, [(90, 40), (999, 34)])}px">{rich(body)}</p>' if body else "")
        corner = "Swipe &rarr;" if total > 1 else "anantasutra.com"
    elif slide.get("cta"):
        inner = f'<h1 style="font-size:{fit(title, [(50, 80), (90, 68), (999, 56)])}px">{rich(title)}</h1>' + \
                (f'<p style="font-size:36px">{rich(body)}</p>' if body else "") + \
                '<div class="button">Book a free consultation</div><div class="url">anantasutra.com/contact</div>'
        corner = "anantasutra.com"
    else:
        inner = f'<div class="num">{index:02d}</div>' + \
                f'<h2 style="font-size:{fit(title, [(45, 62), (80, 54), (999, 46)])}px">{rich(title)}</h2>' + \
                (f'<p style="font-size:{fit(body, [(120, 38), (220, 33), (999, 29)])}px">{rich(body)}</p>' if body else "")
        corner = "Swipe &rarr;" if index < total - 1 else "anantasutra.com"
    count = f"{index + 1} / {total}" if total > 1 else ""
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS % assets}</style></head><body>
<header><div class="brand"><img src="{assets['logo']}" alt="">AnantaSutra</div><div class="count">{count}</div></header>
<div class="rule"></div><main>{inner}</main>
<footer><span>@anantasutra</span><span>{corner}</span></footer></body></html>"""


def render(pages, outs):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
        for html_text, out in zip(pages, outs):
            page.set_content(html_text)
            page.evaluate("document.fonts.ready.then(() => true)")
            page.screenshot(path=str(out))
        browser.close()


def make(path, force=False):
    meta, body = parse_frontmatter(path.read_text(encoding="utf-8"))
    slides = [s if isinstance(s, dict) else {"title": str(s)} for s in meta.get("slides") or []]
    if not slides or meta.get("status") != "draft" or ((meta.get("images") or meta.get("image")) and not force):
        return None
    carousel = meta.get("platform") == "instagram" and meta.get("format") != "single-image"
    if not carousel:
        slides = slides[:1]
    elif not slides[-1].get("cta"):
        slides.append(CTA)
    assets = {"w": W, "h": H, "logo": data_uri(BRAND / "logo.png", "image/png"),
              "inter": data_uri(BRAND / "fonts" / "Inter.ttf", "font/ttf"),
              "playfair": data_uri(BRAND / "fonts" / "PlayfairDisplay.ttf", "font/ttf")}
    MEDIA.mkdir(parents=True, exist_ok=True)
    outs = [MEDIA / f"{path.stem}-{i + 1}.png" for i in range(len(slides))]
    render([slide_html(s, i, len(slides), assets) for i, s in enumerate(slides)], outs)
    files = [o.relative_to(ROOT).as_posix() for o in outs]
    if carousel:
        meta["images"], meta["image"] = files, ""
    else:
        meta["image"], meta["images"] = files[0], []
    if not meta.get("alt_text"):
        meta["alt_text"] = " / ".join(re.sub(r"\*", "", str(s.get("title", ""))) for s in slides)[:300]
    path.write_text(dump_frontmatter(meta, body), encoding="utf-8")
    return files


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", help="one queue file name")
    ap.add_argument("--force", action="store_true", help="re-render even if images are already set")
    args = ap.parse_args()
    targets = [QUEUE / Path(args.file).name] if args.file else sorted(QUEUE.glob("*.md"))
    for path in targets:
        try:
            files = make(path, args.force)
        except Exception as e:
            print(f"FAILED {path.name}: {e}")
            continue
        if files:
            print(f"{path.name}: {len(files)} slide(s) -> {', '.join(files)}")


if __name__ == "__main__":
    main()
