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

ROOT = Path(__file__).resolve().parents[1]


class Renderer:
    def __init__(self, config, config_dir, scale=4):
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
        ratio = min(width * self.scale / asset.width, height * self.scale / asset.height)
        asset = asset.resize((max(1, round(asset.width * ratio)), max(1, round(asset.height * ratio))), Image.Resampling.LANCZOS)
        asset = asset.rotate(self.angle(op, space), Image.Resampling.BICUBIC, expand=True)
        x, y = self.point(op['center'], space)
        canvas.paste(asset, (round(x * self.scale - asset.width / 2), round(y * self.scale - asset.height / 2)), asset)

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
            font = ImageFont.truetype(str(self.asset(op['font'])), round(op['font_size'] * self.scale))
            bbox = font.getbbox(op['text'])
            if bbox[2] <= bbox[0] or bbox[3] <= bbox[1]:
                raise ValueError('Text must contain visible glyphs')
            asset = Image.new('RGBA', (bbox[2] - bbox[0] + 2 * self.scale, bbox[3] - bbox[1] + 2 * self.scale))
            ImageDraw.Draw(asset).text((self.scale - bbox[0], self.scale - bbox[1]), op['text'], font=font, fill=(*color, 255))
            self.paste_asset(canvas, asset, op, space)
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
            if set(panels) & {9, 10, 17} and any(o['kind'] in ['text', 'image', 'stars'] for o in operations):
                raise ValueError('Mirror caps and spoiler permit nondirectional fills/accents only')
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
        image.save(output, optimize=True, compress_level=9)
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
    args = parser.parse_args()
    try:
        config = json.loads(args.design.read_text())
        Renderer(config, args.design.resolve().parent, args.scale).save(args.output, args.manifest)
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as exc:
        parser.exit(1, f'Render failed: {exc}\n')


if __name__ == '__main__':
    main()
