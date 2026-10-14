"""Synthetic rendering tests; not evidence of real-house facts or visual acceptance."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from run import png, sha

spec = importlib.util.spec_from_file_location('board', Path(__file__).resolve().parents[1] / 'scripts/build_storyboard.py')
board = importlib.util.module_from_spec(spec)
spec.loader.exec_module(board)


class RendererTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.p = Path(self.tmp.name)
        for f in ['source.png', 'floor.png']:
            png(self.p / f)
        seg = {'id':'S01','start_s':0,'end_s':4,'reference_image':'source.png','action':'静态','focus':'空间','text':'口播','highlights':[], 'risk':'fixture',
               'visual':{'title':'户型开场','layout':'opening_composite','headline_lines':['测试名称','测试户型'], 'motion':{'kind':'static','label':'静态锚点'}}}
        self.record = {'fixture':True,'plan':{'version':'fixture'},'assets':[{'path':f,'sha256':sha(self.p/f),'origin':'synthetic_fixture'} for f in ['source.png','floor.png']], 'segments':[seg],
                       'scope':{'coverage':['玄关'],'source_namespace':'fixture','duration_s':4,'opening':'开场','ending':'收束','bgm':'无','render_method':'fixture','validation_scope':'synthetic'}}

    def tearDown(self):
        self.tmp.cleanup()

    def render(self):
        (self.p/'record.json').write_text(json.dumps(self.record))
        board.build(self.p/'record.json', self.p/'out.html', self.p/'floor.png')
        return (self.p/'out.html').read_text()

    def test_explicit_story_role_not_coverage_index(self):
        text = self.render()
        self.assertIn('<h2>户型开场</h2>', text)
        self.assertIn('data-preview="opening_composite"', text)
        self.assertIn('class="motion-diagram"', text)

    def test_missing_motion_rejected_without_output(self):
        self.record['segments'][0]['visual'].pop('motion')
        with self.assertRaises(ValueError): self.render()
        self.assertFalse((self.p/'out.html').exists())

    def test_missing_opening_headlines_rejected_without_output(self):
        self.record['segments'][0]['visual']['headline_lines'] = []
        with self.assertRaises(ValueError): self.render()
        self.assertFalse((self.p/'out.html').exists())

    def test_source_only_cannot_supply_opening_layout(self):
        self.record['segments'][0]['visual']['layout'] = 'unknown'
        with self.assertRaises(ValueError): self.render()

    def test_user_text_escaped_and_output_preserved(self):
        self.record['segments'][0]['visual']['headline_lines'][0] = '<script>bad</script>'
        text = self.render()
        self.assertIn('&lt;script&gt;', text)
        self.assertNotIn('<script>bad</script>', text)
        with self.assertRaises(FileExistsError): self.render()
        self.assertEqual((self.p/'out.html').read_text(), text)


if __name__ == '__main__': unittest.main(verbosity=2)
