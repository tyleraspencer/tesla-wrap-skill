"""Check saved Tesla PNG constraints and exact template geometry."""
import argparse
import hashlib
import json
import re
from pathlib import Path
from PIL import Image
import numpy as np
from scipy import ndimage


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('png', type=Path)
    parser.add_argument('--template', type=Path, required=True)
    args = parser.parse_args()
    path = args.png
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads((root / 'references/panel-map.json').read_text())
    if hashlib.sha256(args.template.read_bytes()).hexdigest() != manifest['sha256']:
        parser.exit(1, 'Template fingerprint differs from pinned official original; remap before use.\n')
    errors = []
    size = path.stat().st_size
    if size >= 700_000:
        errors.append(f'Must be under 700,000 bytes; got {size}')
    if path.suffix.lower() != '.png':
        errors.append('Filename must end in .png')
    if not re.fullmatch(r'[A-Za-z0-9_ -]{1,30}', path.stem):
        errors.append('Invalid filename stem: use allowed characters, 1–30 characters')
    with Image.open(path) as im:
        im.load()
        dims = im.size
        if im.format != 'PNG':
            errors.append('File content is not PNG')
        if dims != (1024, 1024):
            errors.append(f'Must be exactly 1024x1024; got {dims}')
        rgba = np.array(im.convert('RGBA'))
        alpha = rgba[:, :, 3]
    if args.template:
        with Image.open(args.template) as template:
            if dims != template.size:
                errors.append(f'Dimensions {dims} differ from template {template.size}')
            else:
                reference_rgba = np.array(template.convert('RGBA'))
                reference = reference_rgba[:, :, 3]
                if not np.array_equal(rgba[reference == 0], reference_rgba[reference == 0]):
                    errors.append('Fully transparent gap pixels changed')
                if np.all(reference == 255):
                    errors.append('Template lacks a transparent panel mask; obtain the original RGBA PNG')
                else:
                    # Check 1: canvas dimensions above. Check 2: every alpha value,
                    # including partially transparent antialiased boundaries.
                    changed = int(np.count_nonzero(alpha != reference))
                    if changed:
                        errors.append(f'Panel edge/alpha differences: {changed} pixels (must be 0)')
                    # Check 3: panel support and transparent gaps at every pixel.
                    support = alpha > 0
                    expected = reference > 0
                    outside = int(np.count_nonzero(support & ~expected))
                    missing = int(np.count_nonzero(expected & ~support))
                    if outside or missing:
                        errors.append(f'Gap/silhouette differences: {outside} outside, {missing} missing pixels')
                    # Check 4: independent connected panel labels, areas and bounds.
                    panels, count = ndimage.label(alpha > 127)
                    original, original_count = ndimage.label(reference > 127)
                    if count != original_count or not np.array_equal(panels, original):
                        errors.append(f'Panel positions/areas/bounds differ; counts {count}/{original_count}')
    if errors:
        parser.exit(1, '\n'.join(errors) + '\n')
    print(f'PASS: {path.name}, {dims[0]}x{dims[1]}, {size} bytes')
    print(f'Geometry PASS: exact alpha, silhouettes/gaps, and all {count} panel positions/areas/bounds; 0 differences')


if __name__ == '__main__':
    main()
