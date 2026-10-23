"""Review snapshot must reject missing current voiceover/risk before host submit."""
import importlib.util
import json
from pathlib import Path
import sys
import unittest
import run as fixtures

SCRIPTS=Path(__file__).resolve().parents[1]/'scripts'
sys.path.insert(0,str(SCRIPTS))
from storyboard.render import load, render_html
spec=importlib.util.spec_from_file_location('approval_snapshot',SCRIPTS/'approval/snapshot.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.f=fixtures.GateTests();self.f.setUp();self.path=self.f.root/'record.json'
        self.f.record['presentation'].update(mode='linked_document',document_path='plan_v1.md')
        self.save()
    def tearDown(self):self.f.tearDown()
    def save(self):self.path.write_text(json.dumps(self.f.record,ensure_ascii=False))
    def test_full_script_can_be_submitted_without_local_approval(self):
        self.f.record['status']='DRAFT';self.f.record['approval']={};self.save()
        result=module.snapshot(self.path)
        self.assertTrue(result['review_passed']);self.assertFalse(result['host_user_approved'])
    def test_current_voiceover_and_risk_must_be_presented_not_just_action(self):
        for field in ['text','risk','music']:
            original=self.f.record['segments'][0][field]
            self.f.record['segments'][0][field]='not in current script body '+field;self.save()
            with self.subTest(field=field),self.assertRaisesRegex(ValueError,'card_content_not_in_plan'):
                module.snapshot(self.path)
            self.f.record['segments'][0][field]=original
    def html_document(self):
        self.f.record['presentation']['document_path']='script.html'
        self.f.record['assets'].append({'path':'floorplan.png','sha256':fixtures.sha(self.f.root/'overview.png'),'role':'floorplan','origin':'actual_source'})
        (self.f.root/'floorplan.png').write_bytes((self.f.root/'overview.png').read_bytes())
        for seg in self.f.record['segments']:
            seg['visual']={'title':seg['id'],'layout':'source_reference','motion':{'kind':'static','label':'静态'}}
        self.save()
        checked,images=load(self.path,'floorplan.png')
        source=render_html(checked,images,'floorplan.png')
        path=self.f.root/'script.html'
        def render(transform=lambda text:text):
            path.write_text(transform(source))
            entry={'path':'script.html','sha256':fixtures.sha(path),'role':'integrated_review_source'}
            self.f.record['assets']=[a for a in self.f.record['assets'] if a['path']!='script.html']+[entry]
            self.save()
        render();return render
    def test_html_requires_canonical_visible_chapters(self):
        render=self.html_document();module.snapshot(self.path)
        for transform in [lambda s:s.replace('<p>核证字幕</p>',''),lambda s:s.replace('<p>已披露</p>',''),
                          lambda s:s.replace('<p>已批准素材库BGM</p>',''),lambda s:s.replace('<p>核证字幕</p>','<p hidden>核证字幕</p>'),
                          lambda s:s.replace('<p>核证字幕</p>','<template>核证字幕</template>')]:
            render(transform)
            with self.assertRaisesRegex(ValueError,'differs from the standard renderer'):module.snapshot(self.path)
    def test_operational_settings_do_not_change_content_fingerprint(self):
        before=module.snapshot(self.path)
        self.f.record['scope'].update(output_dir='take02',render_config={'dpr':2,'renderer':'test','width':720,'height':1280,'fov_axis':'vertical','fov_deg':85.57})
        self.save();self.assertEqual(module.snapshot(self.path)['fingerprint'],before['fingerprint'])
    def test_changed_script_bytes_change_snapshot_even_with_updated_sha(self):
        before=module.snapshot(self.path);body=self.f.root/'plan_v1.md'
        body.write_text(body.read_text()+'\n新增承诺')
        self.f.record['plan']['sha256']=fixtures.sha(body);self.save()
        self.assertNotEqual(module.snapshot(self.path)['fingerprint'],before['fingerprint'])


if __name__=='__main__':unittest.main(verbosity=2)
