"""Generate a calibration wrap: a position-coded texture for reading seam continuity on the car.

Every panel pixel encodes its own canvas position so screenshots from the Tesla app's
3D preview reveal which template regions meet at each on-car seam:
  R = canvas x, G = canvas y, B = panel ID.
Overlaid are 32 px grid lines, coordinate labels every 128 px, and one large ID label per
panel with a canvas-up arrow. The output keeps the template's alpha byte-for-byte.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
FONTS = ['/System/Library/Fonts/Helvetica.ttc', '/System/Library/Fonts/Supplemental/Arial Bold.ttf',
         '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf']


def font(size):
    for path in FONTS:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def label(draw, xy, text, size, anchor='mm'):
    draw.text(xy, text, font=font(size), fill=(255, 255, 255, 255), anchor=anchor,
              stroke_width=max(1, size // 8), stroke_fill=(0, 0, 0, 255))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--template', type=Path, default=ROOT / 'assets/modely-2025-premium-template.png')
    parser.add_argument('--ids', type=Path, default=ROOT / 'assets/modely-2025-premium-panel-ids.png')
    parser.add_argument('--out', type=Path, default=ROOT / 'calibration/Calibration_Grid.png')
    args = parser.parse_args()

    manifest = json.loads((ROOT / 'references/panel-map.json').read_text())
    if hashlib.sha256(args.template.read_bytes()).hexdigest() != manifest['sha256']:
        parser.exit(1, 'Template fingerprint differs from pinned official original.\n')

    template = np.array(Image.open(args.template).convert('RGBA'))
    ids = np.array(Image.open(args.ids).convert('L'))
    alpha = template[:, :, 3]
    h, w = alpha.shape
    yy, xx = np.mgrid[0:h, 0:w]

    rgb = np.zeros((h, w, 3), np.uint8)
    rgb[:, :, 0] = (xx * 255 // (w - 1)).astype(np.uint8)
    rgb[:, :, 1] = (yy * 255 // (h - 1)).astype(np.uint8)
    rgb[:, :, 2] = np.clip(ids.astype(int) * 12, 0, 255).astype(np.uint8)

    # Grid: thin dark line every 32 px, heavier every 128 px.
    minor = (xx % 32 == 0) | (yy % 32 == 0)
    major = (xx % 128 < 2) | (yy % 128 < 2)
    rgb[minor] = (rgb[minor] * 0.45).astype(np.uint8)
    rgb[major] = 0

    img = Image.fromarray(np.dstack([rgb, alpha]))
    draw = ImageDraw.Draw(img)

    # Coordinate labels at every 128 px crossing that sits well inside a panel.
    inside = ndimage.distance_transform_edt(ids > 0)
    for gy in range(128, h, 128):
        for gx in range(128, w, 128):
            if inside[gy, gx] > 22:
                label(draw, (gx + 3, gy + 3), f'{gx},{gy}', 11, anchor='la')

    # One ID + canvas-up arrow per panel, at its deepest interior point.
    for panel in manifest['panels']:
        pid = panel['id']
        mask = ids == pid
        depth = ndimage.distance_transform_edt(mask)
        cy, cx = np.unravel_index(np.argmax(depth), depth.shape)
        radius = depth[cy, cx]
        size = int(np.clip(radius * 1.1, 14, 56))
        label(draw, (cx, cy), str(pid), size)
        ah = max(6, size // 2)
        top = cy - size // 2 - 3
        if radius > 18:
            draw.polygon([(cx, top - ah), (cx - ah // 2, top), (cx + ah // 2, top)],
                         fill=(255, 255, 0, 255), outline=(0, 0, 0, 255))

    out = np.array(img)
    out[alpha == 0] = template[alpha == 0]  # gap pixels stay exactly as the template has them
    out[:, :, 3] = alpha
    args.out.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(out).save(args.out, optimize=True)
    print(f'wrote {args.out} ({args.out.stat().st_size} bytes)')


if __name__ == '__main__':
    main()
