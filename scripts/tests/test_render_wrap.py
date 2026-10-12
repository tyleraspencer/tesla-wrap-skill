"""Regression checks for mask preservation, layering, and placement constraints."""
import copy
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from render_wrap import Renderer, ROOT


def design():
    return {'version': 1, 'base': '#002147', 'panel_notes': {
        str(p): {'artwork': 'test', 'axes': 'nondirectional', 'confidence': '2D'}
        for p in range(1, 21)}, 'layers': []}


class RendererTests(unittest.TestCase):
    def test_masks_and_layer_scope(self):
        c = design()
        c['layers'] = [{'panels': [2], 'operations': [{'kind': 'fill', 'color': '#BB133E'}]},
                       {'panels': [20], 'operations': [{'kind': 'fill', 'color': '#FFFFFF'}]}]
        r = Renderer(c, '.', scale=1)
        a = np.array(r.render())
        self.assertTrue(np.array_equal(a[:, :, 3], r.original[:, :, 3]))
        self.assertTrue(np.array_equal(a[r.ids == 0], r.original[r.ids == 0]))
        self.assertTrue(np.all(a[r.ids == 2, :3] == [187, 19, 62]))
        self.assertTrue(np.all(a[r.ids == 20, :3] == [255, 255, 255]))
        self.assertTrue(np.all(a[r.ids == 7, :3] == [0, 33, 71]))

    def test_ordered_layers_downsample_once(self):
        c = design()
        ops = [{'kind': 'polygon', 'color': '#FFFFFF', 'points': [[420,140],[575,170],[480,290]]},
               {'kind': 'rect', 'color': '#BB133E', 'box': [450,190,490,230]}]
        c['layers'] = [{'panels': [2], 'operations': [op]} for op in ops]
        combined = copy.deepcopy(c)
        combined['layers'] = [{'panels': [2], 'operations': ops}]
        self.assertTrue(np.array_equal(np.array(Renderer(c, '.', 2).render()),
                                       np.array(Renderer(combined, '.', 2).render())))

    def test_unresolved_directional_art_rejected(self):
        for p in [9, 10, 17]:
            c = design()
            c['layers'] = [{'panels': [p], 'operations': [{'kind': 'stars', 'centers': [[500,500]], 'radius': 10}]}]
            with self.assertRaisesRegex(ValueError, 'nondirectional'):
                Renderer(c, '.', 1).render()

    def test_door_frame_and_wrong_side(self):
        r = Renderer(design(), '.', 1)
        for side in ['left', 'right']:
            outer = r.point([500, 0], 'door_' + side)
            inward = r.point([500, 25], 'door_' + side)
            self.assertEqual(outer[1], 500)
            self.assertEqual(round(inward[0] - outer[0]), 25 if side == 'left' else -25)
        c = design()
        c['layers'] = [{'panels': [8], 'space': 'door_left', 'operations': []}]
        with self.assertRaisesRegex(ValueError, 'Left door'):
            Renderer(c, '.', 1).render()

    def test_relative_image_alpha_and_aspect_ratio(self):
        with tempfile.TemporaryDirectory() as folder:
            Image.new('RGBA', (40, 20), (255, 255, 255, 128)).save(Path(folder) / 'mark.png')
            c = design()
            c['layers'] = [{'panels': [2], 'operations': [{'kind':'image', 'file':'mark.png',
                          'center':[510,220], 'size':[100,100]}]}]
            r = Renderer(c, folder, 1)
            a = np.array(r.render())
            self.assertTrue(np.all(a[220,510,:3] == [128,144,163]))
            self.assertTrue(np.all(a[180,510,:3] == [0,33,71]))  # aspect ratio remains 2:1
            self.assertTrue(np.array_equal(a[:,:,3], r.original[:,:,3]))

    def test_fail_incomplete_manifest_and_protected_output(self):
        c = design(); del c['panel_notes']['20']
        with self.assertRaisesRegex(ValueError, 'all 20'):
            Renderer(c, '.', 1).render()
        with self.assertRaisesRegex(ValueError, 'immutable skill'):
            Renderer(design(), '.', 1).save(ROOT/'assets/Overwrite.png', '/tmp/manifest.json')

    def test_saved_file_validator(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder)/'Regression.png'; manifest = Path(folder)/'placement.json'
            r = Renderer(design(), '.', 1)
            r.save(output, manifest)
            self.assertTrue(output.is_file() and manifest.is_file())
            self.assertLess(output.stat().st_size, 1_000_000)


FONTS = ['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', '/System/Library/Fonts/Supplemental/Arial Bold.ttf',
         '/Library/Fonts/Arial Bold.ttf', 'C:/Windows/Fonts/arialbd.ttf']


class PlacementTests(unittest.TestCase):
    def test_font_fallback_list_and_missing_font(self):
        r = Renderer(design(), '.', 1)
        self.assertTrue(r.resolve_font(['/no/such/font.ttf'] + FONTS).is_file())
        with self.assertRaisesRegex(ValueError, 'No font found'):
            r.resolve_font(['/no/such/font.ttf'])

    def test_text_crossing_seam_rejected_unless_allowed(self):
        c = design()
        op = {'kind': 'text', 'text': 'USA', 'font': FONTS, 'font_size': 80, 'color': '#FFFFFF',
              'center': [150, 580], 'size': [150, 60], 'angle': -90}
        c['layers'] = [{'panels': [7, 11], 'operations': [op]}]
        with self.assertRaisesRegex(ValueError, 'reaches outside panels'):
            Renderer(c, '.', 1).render()
        c['layers'][0]['operations'] = [{**op, 'allow_clip': True}]
        Renderer(c, '.', 1).render()

    def test_wordmark_clears_seam_on_both_sides(self):
        for pair, space in (([7, 11], 'door_left'), ([8, 12], 'door_right')):
            c = design()
            c['layers'] = [{'panels': pair, 'space': space, 'operations': [
                {'kind': 'wordmark', 'text': 'PLUGS', 'font': FONTS, 'color': '#FFFFFF'}]}]
            r = Renderer(c, '.', 2)
            a = np.array(r.render())
            ink = np.all(a[:, :, :3] == 255, axis=2) & (r.ids > 0)
            self.assertGreater(int(ink.sum()), 3000)
            self.assertTrue(np.isin(r.ids[ink], pair).all())
            self.assertTrue(np.array_equal(a[:, :, 3], r.original[:, :, 3]))
            self.assertEqual(len(r.wordmarks), 1)
            self.assertEqual(r.wordmarks[0]['side'], space.removeprefix('door_'))

    def test_wordmark_scope_rules(self):
        c = design()
        c['layers'] = [{'panels': [7], 'space': 'door_left', 'operations': [
            {'kind': 'wordmark', 'text': 'AB', 'font': FONTS}]}]
        with self.assertRaisesRegex(ValueError, 'exactly panels'):
            Renderer(c, '.', 1).render()
        c['layers'] = [{'panels': [10], 'operations': [{'kind': 'wordmark', 'text': 'AB', 'font': FONTS}]}]
        with self.assertRaisesRegex(ValueError, 'nondirectional'):
            Renderer(c, '.', 1).render()


if __name__ == '__main__':
    unittest.main()
