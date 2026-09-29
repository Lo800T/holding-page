"""Build vCards (with embedded photo) and QR codes for the website and business cards.

Run with any Python that has `segno` installed:  python make_contacts.py
Outputs go to ../assets/
"""
import base64
import os
import re

import segno

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "..", "assets")
SITE = "https://assettracingadvisory.com"

PEOPLE = {
    "cesar": {
        "first": "Cesar", "last": "Sepulveda",
        "title": "Co-founder & Director",
        "email": "cesar@assettracingadvisory.com",
        "mobile": "+44 7732 054924",
        "linkedin": "https://www.linkedin.com/in/cesar-sepulveda-447a0119/",
    },
    "jay": {
        "first": "Jay", "last": "Cartwright",
        "title": "Co-founder & Director",
        "email": "jay@assettracingadvisory.com",
        "mobile": "+44 7545 847475",
        "linkedin": "https://www.linkedin.com/in/jay-cartwright/",
    },
}


def fold(line):
    """vCard 3.0 line folding: max 75 octets, continuation lines start with a space."""
    out, cur = [], line
    while len(cur.encode("utf-8")) > 75:
        cut = 75 if not out else 74
        out.append(cur[:cut])
        cur = cur[cut:]
    out.append(cur)
    return "\r\n ".join(out)


def vcard(p, photo_b64=None):
    lines = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        f"N:{p['last']};{p['first']};;;",
        f"FN:{p['first']} {p['last']}",
        "ORG:Asset Tracing Advisory Limited",
        f"TITLE:{p['title']}",
        f"TEL;TYPE=CELL,VOICE:{p['mobile']}",
        "TEL;TYPE=WORK,VOICE:+44 20 7164 0332",
        f"EMAIL;TYPE=INTERNET,WORK:{p['email']}",
        f"URL:{SITE}",
        "ADR;TYPE=WORK:;;45 Albemarle Street;London;;W1S 4JL;United Kingdom",
        f"X-SOCIALPROFILE;TYPE=linkedin:{p['linkedin']}",
    ]
    if photo_b64:
        lines.append("PHOTO;ENCODING=b;TYPE=JPEG:" + photo_b64)
    lines.append("END:VCARD")
    return "\r\n".join(fold(l) for l in lines) + "\r\n"


def vcard_qr(p):
    """Lean vCard for QR codes: fewer fields keeps the code small enough to scan off a screen."""
    return "\n".join([
        "BEGIN:VCARD",
        "VERSION:3.0",
        f"N:{p['last']};{p['first']}",
        f"FN:{p['first']} {p['last']}",
        "ORG:Asset Tracing Advisory",
        f"TITLE:{p['title']}",
        f"TEL;TYPE=CELL:{p['mobile'].replace(' ', '')}",
        "TEL;TYPE=WORK:+442071640332",
        f"EMAIL:{p['email']}",
        f"URL:{SITE}",
        f"URL:{p['linkedin'].rstrip('/')}",
        "END:VCARD",
    ])


def qr_svg(data, path, error="m"):
    qr = segno.make(data, error=error, boost_error=False, micro=False)
    qr.save(path, kind="svg", scale=1, border=2, dark="#021821", light="#ffffff",
            xmldecl=False, svgns=True, omitsize=True, nl=False)
    return qr.version


for key, p in PEOPLE.items():
    with open(os.path.join(ASSETS, f"{key}-vcard.jpg"), "rb") as f:
        photo = base64.b64encode(f.read()).decode("ascii")
    with open(os.path.join(ASSETS, f"{p['first']}-{p['last']}.vcf"), "w", newline="") as f:
        f.write(vcard(p, photo))
    v = qr_svg(vcard_qr(p), os.path.join(ASSETS, f"qr-{key}-vcard.svg"), error="l")
    print(key, "vcard QR version", v)

v = qr_svg(SITE, os.path.join(ASSETS, "qr-website.svg"))
print("website QR version", v)
# high-resolution PNG of the website QR for business-card print
segno.make(SITE, error="q").save(os.path.join(ASSETS, "qr-website-print.png"), scale=30, border=4,
                                  dark="#021821", light="#ffffff")
