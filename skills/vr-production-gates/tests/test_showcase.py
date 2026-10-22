"""Current three-space choices: semantic failures and real generation CLI.

Synthetic references only; these checks do not certify real-room labels or video
quality. Browser verification of the generated pages is separate.
"""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from storyboard.model import validate
from storyboard.showcase import showcase_options


def candidate(primary='outdoor'):
    record = json.loads((ROOT / 'assets/design-system/examples/valid.json').read_text())
    record['storyboard_title'] = '三空间展示选择 · 合成验证'
    record['scope'].update(showcase={}, route_space_ids=['living_room', 'balcony', 'primary_bedroom'],
                           coverage=['客厅', '阳台', '主卧'])
    if primary == 'indoor':
        record['scope']['showcase'] = {'primary_content': 'indoor', 'selection_source': 'user'}
    # A display chapter belongs to one space. Transition time is not display time.
    for seg, space, mode, title in zip(record['segments'], record['scope']['route_space_ids'],
                                     ['indoor', primary, primary], ['客厅开场', '阳台展示', '主卧收尾']):
        seg.update(space_ids=[space], content_mode=mode)
        seg['visual']['title'] = title
    return record


class ShowcaseTests(unittest.TestCase):
    def test_default_is_outdoor_and_does_not_mutate_input(self):
        record = candidate(); before = copy.deepcopy(record)
        validate(record)
        self.assertEqual(showcase_options(record)['primary_content'], 'outdoor')
        self.assertEqual(showcase_options(record)['transition_speed_multiplier'], 1.5)
        self.assertEqual(record, before)

    def test_explicit_indoor_and_explicit_outdoor(self):
        validate(candidate('indoor'))
        record = candidate(); record['scope']['showcase']['selection_source'] = 'user'
        validate(record)

    def test_other_rooms_rejected_in_route_and_chapters(self):
        for location in ('route', 'chapter'):
            record = candidate()
            if location == 'route': record['scope']['route_space_ids'].append('kitchen')
            else: record['segments'][1]['space_ids'] = ['secondary_bedroom']
            with self.assertRaisesRegex(ValueError, 'space|route'): validate(record)

    def test_wrong_display_order_rejected_even_when_route_labels_are_right(self):
        record = candidate()
        record['segments'][1]['space_ids'], record['segments'][2]['space_ids'] = (
            record['segments'][2]['space_ids'], record['segments'][1]['space_ids'])
        with self.assertRaisesRegex(ValueError, 'order'): validate(record)

    def test_transition_cannot_supply_missing_room_display(self):
        record = candidate(); record['segments'][1]['content_mode'] = 'transition'
        with self.assertRaisesRegex(ValueError, 'display|three'): validate(record)

    def test_normal_forward_return_through_living_room_allowed_as_transition(self):
        record = candidate(); record['scope']['route_space_ids'].insert(2, 'living_room')
        transition = copy.deepcopy(record['segments'][1])
        transition.update(id='S-return', start_s=8, end_s=9, content_mode='transition',
                          space_ids=['balcony', 'living_room', 'primary_bedroom'])
        transition['visual']['title'] = '转向后正向前往主卧'
        record['segments'][2]['start_s'] = 9
        record['segments'].insert(2, transition)
        validate(record)

    def test_route_ends_in_primary_bedroom_without_repeated_detours(self):
        living, balcony, bedroom = ['living_room', 'balcony', 'primary_bedroom']
        for route in ([living, balcony, bedroom, balcony], [living, balcony, bedroom, living],
                      [living, balcony, living, balcony, bedroom]):
            record = candidate(); record['scope']['route_space_ids'] = route
            with self.subTest(route=route), self.assertRaisesRegex(ValueError, 'route'):
                validate(record)

    def test_missing_room_and_multiple_display_space_labels_rejected(self):
        for spaces in ([], ['living_room', 'balcony']):
            record = candidate(); record['segments'][0]['space_ids'] = spaces
            with self.assertRaises(ValueError): validate(record)

    def test_primary_receives_more_display_time_excluding_transitions(self):
        record = candidate(); record['segments'][2]['content_mode'] = 'indoor'
        with self.assertRaisesRegex(ValueError, 'display time'): validate(record)

    def test_default_cannot_silently_be_indoor(self):
        record = candidate('indoor'); record['scope']['showcase']['selection_source'] = 'default'
        with self.assertRaisesRegex(ValueError, 'Default'): validate(record)

    def test_invalid_modes_and_nonfinite_or_unaccelerated_multipliers_rejected(self):
        for value in (True, 1, 0, float('inf'), float('nan')):
            record = candidate(); record['scope']['showcase']['transition_speed_multiplier'] = value
            with self.assertRaises(ValueError): validate(record)
        record = candidate(); record['segments'][0]['content_mode'] = 'outside'
        with self.assertRaises(ValueError): validate(record)

    def test_numeric_route_room_labels_cannot_hide_extra_space(self):
        record = candidate()
        record['design_system']['version'] = '1.1.0'
        record['scope']['route'] = '0→1→2'
        record['review_route'] = {
            'purpose': 'script_review_only', 'included_in_video': False,
            'floorplan': 'floorplan.png', 'route': '0→1→2', 'caption': '合成点位，仅验证结构。',
            'nodes': [{'pano_index': n, 'room_id': space, 'floorplan_xy': [100 + n*100, 400]}
                      for n, space in enumerate(record['scope']['route_space_ids'])],
            'chapters': [dict(id=seg['id'], title=seg['visual']['title'], start_s=seg['start_s'],
                              end_s=seg['end_s'], pano_indices=[0] if n == 0 else [n-1, n],
                              stop_pano=n, motion_kind='pan') for n, seg in enumerate(record['segments'])]}
        validate(record)
        record['review_route']['nodes'][1]['room_id'] = 'kitchen'
        with self.assertRaisesRegex(ValueError, 'space|route'): validate(record)

    def test_template_exposes_current_defaults_and_three_display_spaces(self):
        template = json.loads((ROOT / 'assets/templates/record.json').read_text())
        from storyboard.showcase import validate_showcase
        validate_showcase({**template, 'review_route': None})
        self.assertEqual(showcase_options(template), showcase_options(candidate()))
        self.assertEqual(template['scope']['coverage'], ['客厅', '阳台', '主卧'])

    def test_historical_records_without_showcase_stay_readable(self):
        record = json.loads((ROOT / 'assets/design-system/examples/valid.json').read_text())
        self.assertIsNone(showcase_options(record)); validate(record)


class ShowcaseCLI(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.p = Path(self.tmp.name)
        for name in ('scene.png', 'floorplan.png'):
            (self.p / name).write_bytes((ROOT / 'assets/design-system/examples' / name).read_bytes())

    def tearDown(self): self.tmp.cleanup()

    def generate(self, record, name):
        path = self.p / (name + '.json'); path.write_text(json.dumps(record, ensure_ascii=False))
        out = self.p / name
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/build_script_package.py'),
                                 '--record', str(path), '--floorplan', 'floorplan.png',
                                 '--output-dir', str(out)], capture_output=True, text=True)
        return result, out

    def test_default_and_indoor_reach_both_outputs_and_receipt(self):
        for primary, label in [('outdoor', '室外为主（默认）'), ('indoor', '室内为主（用户选择）')]:
            result, out = self.generate(candidate(primary), primary)
            self.assertEqual(result.returncode, 0, result.stderr)
            html = (out / '视频剧本.html').read_text(); md = (out / '剧本正文.md').read_text()
            receipt = json.loads((out / 'generation.json').read_text())
            for text in (html, md):
                self.assertIn(label, text); self.assertIn('客厅→阳台→主卧', text)
                for title in ('客厅开场', '阳台展示', '主卧收尾'): self.assertIn(title, text)
                self.assertIn('展示内容：', text)
            self.assertEqual(receipt['showcase']['primary_content'], primary)
            self.assertEqual(receipt['board_html_sha256'], hashlib.sha256(html.encode()).hexdigest())
            self.assertEqual(receipt['script_markdown_sha256'], hashlib.sha256(md.encode()).hexdigest())
            self.assertFalse(receipt['capture_authorized'])

    def test_conflicting_choice_fails_before_output(self):
        record = candidate('indoor'); record['scope']['showcase']['selection_source'] = 'default'
        result, out = self.generate(record, 'bad')
        self.assertNotEqual(result.returncode, 0); self.assertFalse(out.exists())


if __name__ == '__main__': unittest.main(verbosity=2)
