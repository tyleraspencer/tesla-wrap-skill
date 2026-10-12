"""Render JSON artwork through the immutable Model Y 2025 Premium masks."""
import argparse
import hashlib
import json
import math
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageColor, ImageDraw, ImageFont
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from fit_size import CAP, fit_to_cap  # noqa: E402


class Renderer:
    def __init__(self, config, config_dir, scale=4, strict=False):
        if type(scale) is not int or not 1 <= scale <= 8:
            raise ValueError('Scale must be an integer from 1 to 8')
        self.config, self.config_dir, self.scale = config, Path(config_dir), scale
        self.template_path = ROOT / 'assets/modely-2025-premium-template.png'
        self.geometry = json.loads((ROOT / 'references/panel-map.json').read_text())
        if hashlib.sha256(self.template_path.read_bytes()).hexdigest() != self.geometry['sha256']:
            raise ValueError('Template fingerprint changed; remap before rendering')
        self.original = np.array(Image.open(self.template_path).convert('RGBA'))
        self.ids = np.array(Image.open(ROOT / 'assets/modely-2025-premium-panel-ids.png'))
        if self.ids.shape != (1024, 1024) or not np.array_equal(self.ids > 0, self.original[:, :, 3] > 0):
            raise ValueError('ID map support differs from template')
        if set(np.unique(self.ids)) != set(range(21)):
            raise ValueError('ID map must contain exactly panels 1 through 20 and gaps')
        for panel in self.geometry['panels']:
            yy, xx = np.where(self.ids == panel['id'])
            bounds = [int(xx.min()), int(yy.min()), int(xx.max() + 1), int(yy.max() + 1)]
            if len(xx) != panel['support_pixels'] or bounds != panel['bounds_xyxy_exclusive']:
                raise ValueError(f"ID map geometry differs for panel {panel['id']}")
        self.baselines = {}
        self.records = {p['id']: {**p, 'layers': []} for p in self.geometry['panels']}
        self.fonts_used, self.wordmarks, self.warnings, self.strict = set(), [], [], strict
        self.size_fit = None
        self._coverage, self.current_panels = False, []

    def color(self, value):
        value = self.config.get('colors', {}).get(value, value)
        return ImageColor.getrgb(value)

    def asset(self, value):
        path = Path(value)
        return path if path.is_absolute() else self.config_dir / path

    def baseline(self, side):
        if side not in self.baselines:
            # Fit the original straight outer door segment, before the rear wheel arch.
            pair = [7, 11] if side == 'left' else [8, 12]
            xs, ys = [], []
            for y in range(380, 690):
                x = np.where(np.isin(self.ids[y], pair))[0]
                if len(x):
                    ys.append(y)
                    xs.append(x.min() if side == 'left' else x.max())
            slope, intercept = np.polyfit(ys, xs, 1)
            self.baselines[side] = {
                'x_per_y': float(slope), 'intercept': float(intercept),
                'anchors': [[float(slope * y + intercept), y] for y in [380, 689]],
                'fit_segment_y': [380, 689],
            }
        return self.baselines[side]

    def point(self, point, space):
        if space == 'atlas':
            return tuple(point)
        # Door coordinates: u = atlas y (nose toward tail), v = distance inward
        # from the shared outer baseline. This is a placement frame, not UV/3D.
        u, v = point
        side = space.removeprefix('door_')
        fit = self.baseline(side)
        sign = 1 if side == 'left' else -1
        return (fit['x_per_y'] * u + fit['intercept'] + sign * v, u)

    def scaled(self, points, space):
        return [tuple(round(v * self.scale) for v in self.point(p, space)) for p in points]

    def angle(self, op, space):
        if space == 'atlas':
            return float(op.get('angle', 0))
        side = space.removeprefix('door_')
        slope = self.baseline(side)['x_per_y']
        base = -math.degrees(math.atan2(1, slope)) if side == 'left' else -math.degrees(math.atan2(-1, -slope))
        return base + float(op.get('angle', 0))

    def paste_asset(self, canvas, asset, op, space):
        # Fit within requested box without stretching official marks or glyphs.
        width, height = op['size']
        if width <= 0 or height <= 0:
            raise ValueError('Asset size must be positive')
        if op.get('fit') == 'stretch':
            asset = asset.resize((max(1, round(width * self.scale)), max(1, round(height * self.scale))), Image.Resampling.LANCZOS)
        else:
            ratio = min(width * self.scale / asset.width, height * self.scale / asset.height)
            asset = asset.resize((max(1, round(asset.width * ratio)), max(1, round(asset.height * ratio))), Image.Resampling.LANCZOS)
        asset = asset.rotate(self.angle(op, space), Image.Resampling.BICUBIC, expand=True)
        if self._coverage:
            white = Image.new('L', asset.size, 255)
            asset = Image.merge('RGBA', (white, white, white, asset.getchannel('A')))
        x, y = self.point(op['center'], space)
        canvas.paste(asset, (round(x * self.scale - asset.width / 2), round(y * self.scale - asset.height / 2)), asset)

    def resolve_font(self, value):
        # A font may be one path or a list of fallbacks; use the first that exists.
        for candidate in (value if isinstance(value, list) else [value]):
            path = self.asset(candidate)
            if path.is_file():
                self.fonts_used.add(str(path))
                return path
        raise ValueError(f'No font found in: {value}')

    def check_placement(self, layer):
        # Advisory: report text, images, and wordmarks whose ink (3 px margin) leaves the layer's
        # panels, e.g. letters cut by a seam. Never blocks a design unless strict=True.
        inside = np.isin(self.ids, layer['panels'])
        self.current_panels = layer['panels']
        space = layer.get('space', 'atlas')
        for op in layer['operations']:
            if op['kind'] not in ('text', 'image', 'wordmark') or op.get('allow_clip'):
                continue
            canvas = Image.new('RGB', (1024 * self.scale, 1024 * self.scale), (0, 0, 0))
            self._coverage = True
            try:
                self.draw(canvas, {**op, 'color': '#FFFFFF'}, space)
            finally:
                self._coverage = False
            ink = np.array(canvas.convert('L').resize((1024, 1024), Image.Resampling.BOX)) > 5
            bad = int((ndimage.binary_dilation(ink, iterations=3) & ~inside).sum())
            if bad:
                label = op.get('text') or op.get('file') or op['kind']
                message = (f"{op['kind']} '{label}' reaches outside panels {layer['panels']} by {bad} px "
                           '(crosses a seam or panel edge; it is clipped by the original masks)')
                if self.strict:
                    raise ValueError(message)
                self.warnings.append(message)

    def wordmark(self, canvas, op, space):
        # Door-pair text on the shared baseline, rotated per side and never mirrored.
        # seam "avoid" (default): letter gaps sized so the door seam falls inside one gap.
        # seam "ignore": natural font spacing (plus optional tracking px), centred on the seam;
        # the placement check then only warns if a letter is cut.
        if space not in ('door_left', 'door_right'):
            raise ValueError('wordmark needs a door_left or door_right layer')
        mode = op.get('seam', 'avoid')
        if mode not in ('avoid', 'ignore'):
            raise ValueError('wordmark seam must be "avoid" or "ignore"')
        side = space.removeprefix('door_')
        pair = [7, 11] if side == 'left' else [8, 12]
        if sorted(self.current_panels) != pair:
            raise ValueError(f'wordmark layer must target exactly panels {pair}')
        fit = self.baseline(side)
        slope, intercept = fit['x_per_y'], fit['intercept']
        norm = math.hypot(slope, 1)
        d = np.array((slope, 1)) / norm if side == 'left' else np.array((-slope, -1)) / norm
        n = np.array((1, -slope)) / norm if side == 'left' else np.array((-1, slope)) / norm
        rows = np.where(np.isin(self.ids, pair).any(axis=1))[0]
        ymid = (rows.min() + rows.max()) / 2
        origin = np.array((slope * ymid + intercept, ymid)) + float(op.get('inset', 64)) * n
        cap, margin, big = float(op.get('cap_height', 58)), 6, 8
        font_path = str(self.resolve_font(op['font']))
        probe = ImageFont.truetype(font_path, 200)
        flat = probe.getbbox('H')
        font = ImageFont.truetype(font_path, max(8, round(cap * big * 200 / (flat[3] - flat[1]))))
        text = op['text']
        if not text.replace(' ', ''):
            raise ValueError('Text must contain visible glyphs')

        def at(p):
            x, y = int(round(p[0])), int(round(p[1]))
            return int(self.ids[y, x]) if 0 <= x < 1024 and 0 <= y < 1024 else -1
        seam = [u for v in np.arange(0, cap + 1, 2) for u in np.arange(-250, 250, 1.0)
                if at(origin + u * d + v * n) == 0
                and {at(origin + (u - 6) * d + v * n), at(origin + (u + 6) * d + v * n)} == set(pair)]
        if not seam:
            raise ValueError('Could not locate the door seam along the baseline')
        umin, umax = min(seam), max(seam)
        centre = (umin + umax) / 2
        sc, pad = self.scale, 20

        def to_canvas(strip, u0):
            data = (big * d[0] / sc, big * d[1] / sc, big * (-origin[0] * d[0] - origin[1] * d[1] - u0) + pad,
                    -big * n[0] / sc, -big * n[1] / sc, big * (cap + origin[0] * n[0] + origin[1] * n[1]) + pad)
            return strip.transform(canvas.size, Image.AFFINE, data, resample=Image.BICUBIC)

        info = {'text': text, 'side': side, 'mode': mode, 'cap_height': cap, 'inset': float(op.get('inset', 64)),
                'seam_extent_along_text': [umin, umax]}
        if mode == 'ignore':
            tracking = float(op.get('tracking', 0))
            total = font.getlength(text) / big + tracking * (len(text) - 1)
            strip = Image.new('L', (int(total * big) + 2 * pad + 40, int(cap * big * 1.5) + 2 * pad), 0)
            drawer = ImageDraw.Draw(strip)
            for index, ch in enumerate(text):
                x = font.getlength(text[:index]) + tracking * big * index
                drawer.text((pad + x, pad + cap * big), ch, font=font, fill=255, anchor='ls')
            mask = to_canvas(strip, centre - total / 2)
            info['tracking'] = tracking
        else:
            glyphs = []
            for ch in text.replace(' ', ''):
                m = Image.new('L', (int(cap * big * 3), int(cap * big * 3)), 0)
                ImageDraw.Draw(m).text((20, 20), ch, font=font, fill=255)
                if m.getbbox() is None:
                    raise ValueError(f'Glyph {ch!r} has no visible pixels')
                glyphs.append(m.crop(m.getbbox()))
            if len(glyphs) < 2:
                raise ValueError('seam "avoid" needs at least two letters; use seam "ignore"')
            gap = max(umax - umin + 2 * margin, float(op.get('min_gap', 16)))
            widths = [g.width / big for g in glyphs]
            starts, u = [], 0.0
            for w in widths:
                starts.append(u)
                u += w + gap
            total = u - gap
            inside = np.isin(self.ids, pair)
            order = sorted(range(1, len(glyphs)), key=lambda k: abs(starts[k] - gap / 2 - total / 2))
            choice = None
            for k in order:
                strip = Image.new('L', (int(total * big) + 2 * pad, int(cap * big) + 2 * pad), 0)
                for g, start in zip(glyphs, starts):
                    strip.paste(g, (int(start * big) + pad, pad + int(cap * big) - g.height))
                mask = to_canvas(strip, centre - (starts[k] - gap / 2))
                ink = np.array(mask.resize((1024, 1024), Image.Resampling.BOX)) > 5
                if not (ndimage.binary_dilation(ink, iterations=3) & ~inside).any():
                    choice = (k, mask)
                    break
            if choice is None:
                # Never refuse: fall back to the most balanced split and report that it is clipped.
                k = order[0]
                strip = Image.new('L', (int(total * big) + 2 * pad, int(cap * big) + 2 * pad), 0)
                for g, start in zip(glyphs, starts):
                    strip.paste(g, (int(start * big) + pad, pad + int(cap * big) - g.height))
                choice = (k, to_canvas(strip, centre - (starts[k] - gap / 2)))
                if not self._coverage:
                    self.warnings.append(f"wordmark '{text}' could not clear the {side} door seam with letter gaps; "
                                         'it is clipped by the masks. Try a smaller cap_height/inset or seam "ignore"')
            k, mask = choice
            info.update({'seam_after_letter': k, 'gap_px': round(gap, 1)})
        canvas.paste(self.color(op.get('color', '#FFFFFF')), (0, 0), mask)
        if not self._coverage:
            self.wordmarks.append(info)

    def draw(self, canvas, op, space):
        draw = ImageDraw.Draw(canvas)
        kind = op['kind']
        color = self.color(op.get('color', '#FFFFFF'))
        if kind == 'fill':
            draw.rectangle((0, 0, canvas.width, canvas.height), fill=color)
        elif kind in ['polygon', 'rect']:
            if kind == 'rect':
                x0, y0, x1, y1 = op['box']
                points = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
            else:
                points = op['points']
            draw.polygon(self.scaled(points, space), fill=color)
        elif kind == 'line':
            draw.line(self.scaled(op['points'], space), fill=color,
                      width=max(1, round(op['width'] * self.scale)), joint='curve')
        elif kind == 'stars':
            # Original decorative geometry; never use stars to recreate a brand mark.
            for center in op['centers']:
                x, y = self.point(center, space)
                orientation = float(op.get('angle', 0)) if space == 'atlas' else self.angle(op, space)
                points = []
                for k in range(10):
                    a = math.radians(-90 - orientation + k * 36)
                    r = op['radius'] * (1 if k % 2 == 0 else .38196601125)
                    points.append((x + math.cos(a) * r, y + math.sin(a) * r))
                draw.polygon(self.scaled(points, 'atlas'), fill=color)
        elif kind == 'text':
            font = ImageFont.truetype(str(self.resolve_font(op['font'])), round(op['font_size'] * self.scale))
            stroke = round(float(op.get('stroke_width', 0)) * self.scale)
            bbox = font.getbbox(op['text'], stroke_width=stroke)
            if bbox[2] <= bbox[0] or bbox[3] <= bbox[1]:
                raise ValueError('Text must contain visible glyphs')
            asset = Image.new('RGBA', (bbox[2] - bbox[0] + 2 * self.scale, bbox[3] - bbox[1] + 2 * self.scale))
            ImageDraw.Draw(asset).text((self.scale - bbox[0], self.scale - bbox[1]), op['text'], font=font,
                                       fill=(*color, 255), stroke_width=stroke,
                                       stroke_fill=(*self.color(op.get('stroke_color', '#000000')), 255))
            self.paste_asset(canvas, asset, op, space)
        elif kind == 'ellipse':
            x0, y0, x1, y1 = op['box']
            cx, cy, rx, ry = (x0 + x1) / 2, (y0 + y1) / 2, abs(x1 - x0) / 2, abs(y1 - y0) / 2
            ring = [(cx + rx * math.cos(2 * math.pi * k / 180), cy + ry * math.sin(2 * math.pi * k / 180)) for k in range(180)]
            draw.polygon(self.scaled(ring, space), fill=color)
        elif kind == 'gradient':
            if space != 'atlas':
                raise ValueError('gradient uses atlas coordinates')
            x0, y0, x1, y1 = op.get('box', [0, 0, 1024, 1024])
            stops = sorted((float(t), np.array(self.color(c), float)) for t, c in op['stops'])
            theta = math.radians(float(op.get('angle', 0)))
            ux, uy = math.cos(theta), math.sin(theta)
            corners = [(x0, y0), (x1, y0), (x0, y1), (x1, y1)]
            proj = [cx * ux + cy * uy for cx, cy in corners]
            lo, hi = min(proj), max(proj)
            yy, xx = np.mgrid[0:canvas.height, 0:canvas.width]
            t = np.clip(((xx + .5) / self.scale * ux + (yy + .5) / self.scale * uy - lo) / max(hi - lo, 1e-9), 0, 1)
            out = np.zeros(t.shape + (3,))
            for ch in range(3):
                out[:, :, ch] = np.interp(t, [a for a, _ in stops], [c[ch] for _, c in stops])
            layer_img = Image.fromarray(out.round().astype(np.uint8))
            region = Image.new('L', canvas.size, 0)
            ImageDraw.Draw(region).rectangle((round(x0 * self.scale), round(y0 * self.scale),
                                              round(x1 * self.scale) - 1, round(y1 * self.scale) - 1), fill=255)
            canvas.paste(layer_img, (0, 0), region)
        elif kind == 'wordmark':
            self.wordmark(canvas, op, space)
        elif kind == 'image':
            with Image.open(self.asset(op['file'])) as source:
                asset = source.convert('RGBA')
            self.paste_asset(canvas, asset, op, space)
        else:
            raise ValueError(f'Unknown operation: {kind}')

    def render(self):
        if self.config.get('version') != 1:
            raise ValueError('Design version must be 1')
        if set(self.config.get('panel_notes', {})) != {str(p) for p in range(1, 21)}:
            raise ValueError('Provide panel_notes for all 20 panels (axes, artwork, confidence)')
        base = self.color(self.config['base'])
        # Store only changed panels to avoid allocating twenty supersampled canvases.
        result = self.original.copy()
        result[self.ids > 0, :3] = base
        layers = self.config.get('layers', [])
        for index, layer in enumerate(layers):
            panels = layer['panels']
            if not panels or any(type(p) is not int or p not in self.records for p in panels):
                raise ValueError('Each layer must target known panel IDs')
            space = layer.get('space', 'atlas')
            if space not in ['atlas', 'door_left', 'door_right']:
                raise ValueError(f'Unknown coordinate space: {space}')
            if space == 'door_left' and not set(panels) <= {3, 7, 11, 13}:
                raise ValueError('Left door frame is restricted to the left side panels')
            if space == 'door_right' and not set(panels) <= {4, 8, 12, 14}:
                raise ValueError('Right door frame is restricted to the right side panels')
            operations = layer['operations']
            if set(panels) & {9, 10, 17} and any(o['kind'] in ['text', 'image', 'stars', 'wordmark'] for o in operations):
                self.warnings.append(f'Directional art on mirror cap/spoiler panels {sorted(set(panels) & {9, 10, 17})}: '
                                     'orientation evidence is limited (see seam-adjacency.md); verify on the car')
            self.check_placement(layer)
            for panel in panels:
                self.records[panel]['layers'].append({'index': index, 'space': space, 'operations': operations})
        # Group panels sharing the same layer stack; render once at high resolution
        # and downsample once. Never resample previously downsampled artwork.
        groups = {}
        for panel, record in self.records.items():
            stack = tuple(item['index'] for item in record['layers'])
            groups.setdefault(stack, []).append(panel)
        for stack, panels in groups.items():
            if not stack:
                continue
            canvas = Image.new('RGB', (1024 * self.scale, 1024 * self.scale), base)
            for index in stack:
                layer = layers[index]
                self.current_panels = layer['panels']
                for op in layer['operations']:
                    self.draw(canvas, op, layer.get('space', 'atlas'))
            artwork = np.array(canvas.resize((1024, 1024), Image.Resampling.LANCZOS))
            mask = np.isin(self.ids, panels)
            result[mask, :3] = artwork[mask]
        # Alpha and transparent RGB are copied from the immutable source after all art.
        result[:, :, 3] = self.original[:, :, 3]
        result[self.ids == 0] = self.original[self.ids == 0]
        return Image.fromarray(result)

    def save(self, output, manifest):
        output, manifest = Path(output), Path(manifest)
        if ROOT == output.resolve() or ROOT in output.resolve().parents or ROOT == manifest.resolve() or ROOT in manifest.resolve().parents:
            raise ValueError('Keep output and manifest outside the immutable skill directory')
        if output.resolve() == manifest.resolve():
            raise ValueError('PNG and manifest paths must differ')
        if output.suffix.lower() != '.png' or not re.fullmatch(r'[A-Za-z0-9_ -]{1,30}', output.stem):
            raise ValueError('Use a PNG filename with 1–30 allowed characters')
        output.parent.mkdir(parents=True, exist_ok=True)
        image = self.render()
        # Hard limit: never write a file at or over the byte cap; reduce colors until it fits.
        fitted, self.size_fit = fit_to_cap(np.array(image), self.original)
        if self.size_fit['reduced']:
            self.warnings.append(f"PNG was {self.size_fit['initial_bytes']} bytes (cap {CAP}); reduced to "
                                 f"{self.size_fit['colors']} colors, alpha and gaps untouched")
        image = Image.fromarray(fitted)
        image.save(output, optimize=True, compress_level=9)
        if output.stat().st_size >= CAP:
            raise ValueError('Saved PNG is not under the byte cap')
        with Image.open(output) as saved:
            if not np.array_equal(np.array(saved.convert('RGBA')), np.array(image)):
                raise ValueError('Saved pixels differ from render')
        # Fail rather than quantize or silently degrade the design to meet the cap.
        subprocess.run([sys.executable, str(ROOT / 'scripts/check_wrap.py'), str(output),
                        '--template', str(self.template_path)], check=True)
        for panel, record in self.records.items():
            record['placement'] = self.config['panel_notes'][str(panel)]
        manifest.parent.mkdir(parents=True, exist_ok=True)
        manifest.write_text(json.dumps({
            'template_sha256': self.geometry['sha256'], 'sources': self.config.get('sources', []),
            'fonts_used': sorted(self.fonts_used), 'wordmarks': self.wordmarks, 'warnings': self.warnings, 'size_fit': self.size_fit,
            'panels': list(self.records.values()), 'door_baselines': self.baselines,
            'audits': {'pixel_geometry': 'PASS exact source alpha and gaps',
                       'panel_geometry': 'PASS pinned areas/bounds and bundled connected-component check',
                       'saved_file': 'PASS decoded equality and bundled validator',
                       'artwork_orientation': 'PENDING manual native/enlarged inspection'},
            'limits': 'Fitted 2D axes do not establish exact on-car seam correspondence or 3D appearance.',
        }, indent=2) + '\n')
        return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('design', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--scale', type=int, default=4)
    parser.add_argument('--strict-placement', action='store_true',
                        help='fail instead of warn when text/images/wordmarks leave their panels')
    args = parser.parse_args()
    try:
        config = json.loads(args.design.read_text())
        renderer = Renderer(config, args.design.resolve().parent, args.scale, args.strict_placement)
        renderer.save(args.output, args.manifest)
        for warning in renderer.warnings:
            print(f'WARNING: {warning}', file=sys.stderr)
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as exc:
        parser.exit(1, f'Render failed: {exc}\n')


if __name__ == '__main__':
    main()
