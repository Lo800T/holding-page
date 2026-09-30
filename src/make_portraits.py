"""Crop the directors' studio photos into the portrait, avatar and vCard images.

    python3 make_portraits.py

Reads ../assets/source-photos/*.png and writes the crops to ../assets/.
Needs Pillow only. Run make_contacts.py afterwards so the vCards pick up the new photos.
"""
import os

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "..", "assets")

# Pupil centres (x, y) in each source photo, measured with macOS Vision face landmarks.
# Every crop is scaled and positioned from these so both heads match in size and eye line.
PEOPLE = {
    "jay": ("jay.png", (608.5, 485.4), (722.9, 486.1)),
    "cesar": ("cesar.png", (353.0, 294.6), (426.2, 289.7)),
}


def crop(im, left, right, eye_gap, eye_line, size):
    """Square crop where the pupil gap is `eye_gap` of the width and the eyes sit `eye_line` from the top."""
    gap = ((right[0] - left[0]) ** 2 + (right[1] - left[1]) ** 2) ** 0.5
    side = gap / eye_gap
    cx, cy = (left[0] + right[0]) / 2, (left[1] + right[1]) / 2
    box = (cx - side / 2, cy - eye_line * side, cx + side / 2, cy + (1 - eye_line) * side)
    if box[0] < 0 or box[1] < 0 or box[2] > im.width or box[3] > im.height:
        raise SystemExit(f"crop {tuple(round(v) for v in box)} falls outside the {im.size} photo")
    return im.crop(tuple(round(v) for v in box)).resize((size, size), Image.LANCZOS)


for key, (name, lp, rp) in PEOPLE.items():
    im = Image.open(os.path.join(ASSETS, "source-photos", name)).convert("RGB")
    crop(im, lp, rp, 0.15, 0.43, 360).save(os.path.join(ASSETS, f"{key}-portrait.webp"), quality=86, method=6)
    crop(im, lp, rp, 0.22, 0.50, 240).save(os.path.join(ASSETS, f"{key}-square.jpg"), quality=88)
    crop(im, lp, rp, 0.19, 0.42, 200).save(os.path.join(ASSETS, f"{key}-vcard.jpg"), quality=80, optimize=True)
    print(key, "portrait, avatar and vCard crops written")
