"""Fit a wrap PNG under the 700,000-byte cap without touching alpha, gaps, or dimensions.

Lossless optimisation first; if the file is still too large, the colors of the visible pixels are
reduced step by step (most frequent exact colors are kept exactly, no dithering) until it fits.
The cap is a hard limit: this tool keeps reducing until the file is under it.
"""
import argparse
import io
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[1]
CAP = 700_000
LADDER = (256, 192, 128, 96, 64, 48, 32, 24, 16, 12, 8, 6, 4)


def encode(rgba):
    buffer = io.BytesIO()
    Image.fromarray(rgba).save(buffer, 'PNG', optimize=True, compress_level=9)
    return buffer.getvalue()


def reduce_colors(rgba, original, colors):
    """Quantize the RGB of visible pixels to `colors`; alpha and gap pixels come from `original`."""
    support = original[:, :, 3] > 0
    rgb = np.ascontiguousarray(rgba[:, :, :3])
    quant = Image.fromarray(rgb).quantize(colors=colors, method=Image.Quantize.MEDIANCUT,
                                          dither=Image.Dither.NONE)
    palette = np.array(quant.getpalette()[:3 * colors], dtype=int).reshape(-1, 3)
    visible = rgb[support].reshape(-1, 3)
    unique, counts = np.unique(visible, axis=0, return_counts=True)
    used = set()
    for color in unique[np.argsort(-counts)[:max(1, colors // 4)]]:  # keep flat/brand colors exact
        _, order = cKDTree(palette).query(color, k=min(len(palette), len(used) + 1))
        order = np.atleast_1d(order)
        free = [i for i in order if i not in used]
        if free:
            palette[free[0]] = color
            used.add(free[0])
    _, index = cKDTree(palette).query(visible)
    out = rgba.copy()
    out[support, :3] = palette[index]
    out[~support] = original[~support]
    out[:, :, 3] = original[:, :, 3]
    return out


def fit_to_cap(rgba, original, cap=CAP):
    """Return (rgba, info) with len(PNG bytes) < cap, alpha and gap pixels identical to `original`."""
    data = encode(rgba)
    info = {'initial_bytes': len(data), 'reduced': False, 'colors': None, 'steps': []}
    final = rgba
    if len(data) >= cap:
        info['reduced'] = True
        for colors in LADDER:
            candidate = reduce_colors(rgba, original, colors)
            data = encode(candidate)
            info['steps'].append([colors, len(data)])
            if len(data) < cap:
                final, info['colors'] = candidate, colors
                break
        else:
            raise ValueError(f'Could not get under {cap} bytes even at {LADDER[-1]} colors')
    info['final_bytes'] = len(data)
    return final, info


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--template', type=Path, default=ROOT / 'assets/modely-2025-premium-template.png')
    args = parser.parse_args()
    original = np.array(Image.open(args.template).convert('RGBA'))
    rgba = np.array(Image.open(args.input).convert('RGBA'))
    if rgba.shape != original.shape:
        parser.exit(1, f'Image must be exactly {original.shape[1]}x{original.shape[0]}\n')
    final, info = fit_to_cap(rgba, original)
    Image.fromarray(final).save(args.output, optimize=True, compress_level=9)
    print(f"{info['initial_bytes']} -> {info['final_bytes']} bytes"
          + (f", reduced to {info['colors']} colors" if info['reduced'] else ', lossless'))
    subprocess.run([sys.executable, str(ROOT / 'scripts/check_wrap.py'), str(args.output),
                    '--template', str(args.template)], check=True)


if __name__ == '__main__':
    main()
