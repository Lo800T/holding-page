"""Inline every asset into one self-contained index.html.

    python3 build.py

Reads index.template.html plus ../assets/* and writes ../index.html, plus
../index-paged.html: the same page with paged.html added, which shows one
section per screen on phones.
Needs Pillow only (for the small hero avatars).
"""
import base64
import io
import os
import re

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "..", "assets")
MARKETING = os.path.join(HERE, "..", "..", "active-marketing-assets")
OUT = os.path.join(HERE, "..", "index.html")
OUT_PAGED = os.path.join(HERE, "..", "index-paged.html")


def data_uri(path, mime):
    with open(path, "rb") as f:
        return f"data:{mime};base64," + base64.b64encode(f.read()).decode("ascii")


def avatar_uri(path, size=80):
    im = Image.open(path).convert("RGB")
    w, h = im.size
    s = min(w, h)
    im = im.crop(((w - s) // 2, int((h - s) * 0.35), (w - s) // 2 + s, int((h - s) * 0.35) + s))
    im = im.resize((size, size), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=84, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


def inline_svg(path):
    with open(path, encoding="utf-8") as f:
        svg = f.read().strip()
    return svg.replace("<svg ", '<svg aria-hidden="true" focusable="false" shape-rendering="crispEdges" ', 1)


def hero_image():
    """Reuse the London skyline hero from the current site so the brand look carries over."""
    with open(os.path.join(MARKETING, "current-site-index.html"), encoding="utf-8") as f:
        html = f.read()
    m = re.search(r'\.hero-city\s*\{[^}]*?url\("(data:image/jpeg;base64,[A-Za-z0-9+/=]+)"\)', html, re.S)
    if not m:
        raise SystemExit("hero image not found in current-site-index.html")
    return m.group(1)


subs = {
    "{{FONT_MONTSERRAT}}": data_uri(os.path.join(ASSETS, "montserrat-latin.woff2"), "font/woff2"),
    "{{HERO_IMG}}": hero_image(),
    "{{CESAR_IMG}}": data_uri(os.path.join(ASSETS, "cesar-portrait.webp"), "image/webp"),
    "{{JAY_IMG}}": data_uri(os.path.join(ASSETS, "jay-portrait.webp"), "image/webp"),
    "{{CESAR_AVATAR}}": avatar_uri(os.path.join(ASSETS, "cesar-square.jpg")),
    "{{JAY_AVATAR}}": avatar_uri(os.path.join(ASSETS, "jay-square.jpg")),
    "{{QR_CESAR}}": inline_svg(os.path.join(ASSETS, "qr-cesar-vcard.svg")),
    "{{QR_JAY}}": inline_svg(os.path.join(ASSETS, "qr-jay-vcard.svg")),
    "{{QR_SITE}}": inline_svg(os.path.join(ASSETS, "qr-website.svg")),
    "{{VCF_CESAR}}": data_uri(os.path.join(ASSETS, "Cesar-Sepulveda.vcf"), "text/vcard"),
    "{{VCF_JAY}}": data_uri(os.path.join(ASSETS, "Jay-Cartwright.vcf"), "text/vcard"),
}

with open(os.path.join(HERE, "index.template.html"), encoding="utf-8") as f:
    html = f.read()
for k, v in subs.items():
    if k not in html:
        raise SystemExit(f"placeholder {k} missing from template")
    html = html.replace(k, v)
left = re.findall(r"\{\{[A-Z_]+\}\}", html)
if left:
    raise SystemExit(f"unreplaced placeholders: {left}")
with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)
print(f"wrote {os.path.relpath(OUT, HERE)}  ({len(html) / 1024:.0f} KB)")

with open(os.path.join(HERE, "paged.html"), encoding="utf-8") as f:
    paged = f.read()
if html.count("</body>") != 1:
    raise SystemExit("expected exactly one </body> in the template")
paged_html = html.replace("</body>", paged + "\n</body>", 1)
with open(OUT_PAGED, "w", encoding="utf-8") as f:
    f.write(paged_html)
print(f"wrote {os.path.relpath(OUT_PAGED, HERE)}  ({len(paged_html) / 1024:.0f} KB, paged on phones)")
