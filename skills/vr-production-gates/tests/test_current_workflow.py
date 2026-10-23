"""Current template -> generated package -> host/CLI contracts. Synthetic only.

These fixtures are not property evidence or human visual acceptance. Runtime tests
reuse this builder to exercise the real host without model-written approval fields.
"""
import copy
import importlib.util
import json
import os
from pathlib import Path
import sys
import subprocess
import tempfile
import unittest

SKILL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL / 'scripts'))
from run import png, sha
from build_script_package import build_package
from check_shooting_plan import check, bundle_digest
spec = importlib.util.spec_from_file_location('current_snapshot', SKILL / 'scripts/approval/snapshot.py')
snapshot_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(snapshot_module)


def fixture(root, prechecked=False):
    root = Path(root); root.mkdir(parents=True, exist_ok=True)
    record = json.loads((SKILL / 'assets/templates/record.json').read_text())
    # Preserve current v3/profile/route contracts. Only fill missing source facts
    # with explicitly synthetic values, never real-house credentials or media.
    record['assets'] = [a for a in record['assets'] if a['role'] not in {'precheck', 'precheck_report'}]
    record['scope'].pop('render_validation', None)
    for asset in record['assets']:
        if asset['path'].endswith('.png'):
            png(root / asset['path']); asset['sha256'] = sha(root / asset['path'])
        elif asset['role'] == 'source':
            asset['path'] = 'source.bin'; (root / asset['path']).write_bytes(b'synthetic source, not a property')
            asset['sha256'] = sha(root / asset['path'])
    png(root / 'floorplan.png')
    record['assets'].append({'path':'floorplan.png','sha256':sha(root/'floorplan.png'),'role':'floorplan','origin':'actual_source'})
    scope = record['scope']
    scope.update(source_namespace='SYNTHETIC-CONTRACT-ONLY', route='0→1→2',
                 opening='合成户型开场', ending='合成室内收束', facts_and_rights='测试输入，不是真实房源，不授权制作')
    scope['render_config']['renderer'] = 'synthetic-contract'
    for seg in record['segments']:
        seg.update(action='正向动作示意', focus='合成主体', text='合成口播'+seg['id'], music='合成配乐说明',
                   risk='仅用于离线契约验证', framing_status='pending')
    route = record['review_route']; route['route'] = scope['route']
    route['nodes'] = [dict(pano_index=i, floorplan_xy=[x,.5], room_id=room, room_evidence='synthetic room label')
                      for i,(x,room) in enumerate(zip([.15,.5,.85],scope['showcase']['space_order']))]
    route['registration'].update(floorplan_sha256=sha(root/'floorplan.png'), rooms=[
        {'id':room,'polygon':[[i/3,0],[(i+1)/3,0],[(i+1)/3,1],[i/3,1]]}
        for i,room in enumerate(scope['showcase']['space_order'])])
    paths = [[0],[0,1],[1],[1,2],[2]]
    route['chapters'] = [dict(id=s['id'], title=s['visual']['title'], start_s=s['start_s'], end_s=s['end_s'],
                              pano_indices=nodes, stop_pano=nodes[-1], motion_kind=s['visual']['motion']['kind'])
                         for s,nodes in zip(record['segments'],paths)]
    route['transitions'] = [dict(from_pano=i,to_pano=i+1,movement='forward',view='转向后正向移动',duration_s=1) for i in range(2)]
    path = root / 'record.json'
    path.write_text(json.dumps(record, ensure_ascii=False))
    build_package(path, root/'generated', 'floorplan.png')
    record['plan'].update(path='generated/剧本正文.md',sha256=sha(root/'generated/剧本正文.md'))
    record['presentation']['document_path'] = 'generated/视频剧本.html'
    scope['storyboard_layout']['source'] = 'generated/视频剧本.html'
    scope['review_route_layout']['source'] = 'generated/视频剧本.html#完整方案板'
    for asset in record['assets']:
        if asset['role'] == 'storyboard_source':
            asset['path'] = 'generated/视频剧本.html'; asset['sha256'] = sha(root/asset['path'])
    layout = dict(schema='vr-storyboard-layout-review/v1', board_sha256=sha(root/'overview.png'),
                  source_sha256=sha(root/'generated/视频剧本.html'),segment_ids=[s['id'] for s in record['segments']],
                  review_basis='synthetic structure fixture, not real visual review')
    layout.update({key:True for key in ['all_images_loaded','no_overflow','reference_structure_matches',
                                      'motion_diagrams_reviewed','opening_composite_reviewed']})
    (root/'layout-review.json').write_text(json.dumps(layout))
    next(a for a in record['assets'] if a['role']=='layout_review')['sha256'] = sha(root/'layout-review.json')
    path.write_text(json.dumps(record,ensure_ascii=False))
    if prechecked:
        add_precheck(path)
    return path


def add_precheck(path):
    path = Path(path); root = path.parent; r = json.loads(path.read_text()); s = r['scope']
    report = {key:copy.deepcopy(s[key]) for key in ['source_namespace','capture_medium','validation_scope',
              'render_method','render_config','continuity_class','route','coverage']}
    report.update(schema='vr-render-precheck/v1',source_sha256={a['path']:a['sha256'] for a in r['assets'] if a['role']=='source'},
                  evidence_kind='continuous_media',complete_interval_reviewed=True,
                  checks={'control':'PASS','playback':'PASS','visual':'PASS'},evidence={})
    for key,name in [('media','precheck.webm'),('review','visual-review.md')]:
        (root/name).write_text('synthetic structure fixture only')
        entry={'path':name,'sha256':sha(root/name)};report['evidence'][key]=entry
        r['assets'].append({**entry,'role':'precheck','origin':'synthetic_fixture'})
    (root/'precheck.json').write_text(json.dumps(report,ensure_ascii=False))
    entry={'path':'precheck.json','sha256':sha(root/'precheck.json')}
    for seg in r['segments']:seg['framing_status']='subject'
    s['render_validation']=entry;r['assets'].append({**entry,'role':'precheck_report','origin':'synthetic_fixture'})
    path.write_text(json.dumps(r,ensure_ascii=False))


class CurrentWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='current-workflow-')
        self.path=fixture(Path(self.tmp.name)/'plan')
    def tearDown(self):self.tmp.cleanup()
    def record(self):return json.loads(self.path.read_text())
    def save(self,r):self.path.write_text(json.dumps(r,ensure_ascii=False))
    def test_shared_confirmation_policy_keeps_negative_and_wrong_version_rejected(self):
        from document_review import approves_current
        for text in ['确认本版脚本，开始制作。','审核通过，现在开始制作。','接受，现在开始']:
            self.assertTrue(approves_current(text,'v1'),text)
        for text in ['确认','同意','先修改，不批准','是否确认脚本？','批准 v0，开始制作','approve script?']:
            self.assertFalse(approves_current(text,'v1'),text)
    def test_confirmation_rejection_is_bounded_and_languages_agree(self):
        values=['审核通过，　开始制作。','审核通过，\u00a0开始制作。','批准'+' '*40+'X',
                '批准'+'，'*40+'X','确认本版脚本，开始制作。','批准v2，开始制作','是否批准？']
        code='import sys,json;sys.path.insert(0,sys.argv[1]);from document_review import approves_current;print(json.dumps([approves_current(s,"v1") for s in json.load(sys.stdin)]))'
        py=subprocess.run([sys.executable,'-c',code,str(SKILL/'scripts')],input=json.dumps(values),
                          capture_output=True,text=True,timeout=3,check=True)
        js='import {approves} from '+json.dumps((SKILL/'scripts/approval/policy.mjs').as_uri())+';let s="";for await(const c of process.stdin)s+=c;console.log(JSON.stringify(JSON.parse(s).map(v=>approves(v,"v1"))));'
        node=subprocess.run(['node','--input-type=module','-e',js],input=json.dumps(values),
                            capture_output=True,text=True,timeout=3,check=True)
        self.assertEqual(json.loads(py.stdout),[True,True,False,False,True,False,False])
        self.assertEqual(json.loads(py.stdout),json.loads(node.stdout))
    def test_host_adapter_rejects_wrong_fingerprint_and_retains_technical_checks(self):
        current=snapshot_module.snapshot(self.path)
        with self.assertRaisesRegex(ValueError,'snapshot changed'):
            snapshot_module.production_check(self.path,{'phase':'capture','fingerprint':'0'*64})
        result=snapshot_module.production_check(self.path,{'phase':'capture','fingerprint':current['fingerprint']})
        self.assertIn('missing_render_validation',result['errors'])
        self.assertNotIn('not_approved',result['errors'])
    def test_confirmation_load_does_not_depend_on_locale(self):
        env={**os.environ,'LC_ALL':'C','PYTHONUTF8':'0','PYTHONCOERCECLOCALE':'0'}
        code='import sys;sys.path.insert(0,sys.argv[1]);from document_review import approves_current;assert approves_current("approve script", "v1")'
        subprocess.run([sys.executable,'-c',code,str(SKILL/'scripts')],env=env,capture_output=True,check=True,timeout=3)
    def test_host_rejects_legacy_presentation_even_with_current_fingerprint(self):
        before=snapshot_module.snapshot(self.path);r=self.record()
        r['presentation']['mode']='rendered_document';self.save(r)
        with self.assertRaisesRegex(ValueError,'linked_document'):snapshot_module.snapshot(self.path)
        with self.assertRaisesRegex(ValueError,'linked_document'):
            snapshot_module.production_check(self.path,{'phase':'capture','fingerprint':before['fingerprint']})
    def test_template_has_no_future_precheck_assets(self):
        template=json.loads((SKILL/'assets/templates/record.json').read_text())
        self.assertFalse([a for a in template['assets'] if a['role'] in {'precheck','precheck_report'}])
        self.assertNotIn('render_validation',template['scope'])
    def test_generated_current_package_submits_without_dynamic_precheck(self):
        r=self.record()
        self.assertEqual(r['schema'],'vr-production-plan/v3')
        self.assertEqual(r['design_system']['version'],'1.3.0')
        self.assertIn('![完整方案板](../overview.png)',(self.path.parent/r['plan']['path']).read_text())
        self.assertTrue(check(self.path,'review',False)['passed'])
        self.assertTrue(snapshot_module.snapshot(self.path)['review_passed'])
    def test_framing_verification_can_complete_after_approval_without_changing_content(self):
        r=self.record()
        for seg in r['segments']:seg['framing_status']='pending'
        self.save(r);before=snapshot_module.snapshot(self.path)
        for seg in r['segments']:seg['framing_status']='subject'
        self.save(r)
        self.assertEqual(snapshot_module.snapshot(self.path)['fingerprint'],before['fingerprint'])
        r['segments'][0]['framing_status']='blank_wall';self.save(r)
        with self.assertRaisesRegex(ValueError,'Blank wall'):snapshot_module.snapshot(self.path)
    def test_precheck_added_after_review_does_not_change_snapshot(self):
        before=snapshot_module.snapshot(self.path)
        add_precheck(self.path)
        self.assertEqual(snapshot_module.snapshot(self.path)['fingerprint'],before['fingerprint'])
    def test_generated_linked_html_uses_same_contract_in_legacy_cli(self):
        add_precheck(self.path); r=self.record();r['status']='SCRIPT_APPROVED_ONCE'
        document=self.path.parent/r['presentation']['document_path']
        reply='确认本版脚本，开始制作。'
        events=[{'id':'shown','message':{'role':'assistant','content':f'[本版脚本]({document})'}},
                {'id':'approved','message':{'role':'user','content':reply}}]
        trace=self.path.parent/'review.jsonl';trace.write_text('\n'.join(json.dumps(e,ensure_ascii=False) for e in events))
        r['presentation'].update(transcript_sha256=sha(trace),assistant_event_id='shown')
        r['approval'].update(user_event_id='approved',explicit_text=reply,plan_sha256=r['plan']['sha256'],bundle_sha256=bundle_digest(r))
        self.save(r)
        result=check(self.path,'capture',False)
        self.assertTrue(result['passed'],result)
    def test_hidden_or_changed_linked_html_is_rejected_by_review_cli(self):
        r=self.record();html=self.path.parent/r['presentation']['document_path']
        html.write_text(html.read_text().replace('合成口播S01','<span hidden>合成口播S01</span>'))
        next(a for a in r['assets'] if a['role']=='storyboard_source')['sha256']=sha(html)
        layout_path=self.path.parent/'layout-review.json';layout=json.loads(layout_path.read_text())
        layout['source_sha256']=sha(html);layout_path.write_text(json.dumps(layout))
        next(a for a in r['assets'] if a['role']=='layout_review')['sha256']=sha(layout_path)
        self.save(r)
        with self.assertRaisesRegex(ValueError,'standard renderer'):check(self.path,'review',False)


if __name__=='__main__':unittest.main(verbosity=2)
