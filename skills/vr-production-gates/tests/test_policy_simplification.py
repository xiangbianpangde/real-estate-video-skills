"""Policy regressions: authorized recovery without arbitrary quotas or UI rituals.

Fixtures exercise the real CLI and synthetic approvals, not video quality.
"""
import json
import sys
sys.dont_write_bytecode = True
import unittest
import run as fixtures


class SimplifiedPolicyTests(unittest.TestCase):
    def setUp(self):
        self.f = fixtures.GateTests()
        self.f.setUp()

    def tearDown(self):
        self.f.tearDown()

    def passed(self, phase='review'):
        # Present this changed synthetic variant, rather than testing an old
        # approval against changed content (covered separately by drift tests).
        if hasattr(self.f, 'presented_bundle_sha'):
            del self.f.presented_bundle_sha
        self.f.events[0]['message']['content'][0]['text'] = self.f.body+'\nSHA256: '+self.f.record['plan']['sha256']
        code, result = self.f.run_gate(phase)
        self.assertEqual(code, 0, result)
        return result

    def test_third_local_and_second_full_check_are_not_failures(self):
        self.f.record['exploration'].update(key_prechecks=4, full_route_prechecks=3,
                                           comparisons_by_issue={'framing': 8})
        self.passed()

    def test_exploration_bookkeeping_is_optional(self):
        self.f.record.pop('exploration')
        self.passed()

    def test_explicit_user_exploration_limit_still_applies(self):
        self.f.record['exploration']['limits'] = {'full_route_prechecks': 1}
        self.f.record['exploration']['full_route_prechecks'] = 2
        code, result = self.f.run_gate('review')
        self.assertNotEqual(code, 0)
        self.assertIn('user_exploration_limit_exceeded:full_route_prechecks', result['errors'])

    def test_no_universal_single_capture_attempt(self):
        self.f.record['scope']['max_capture_attempts'] = 3
        self.passed('capture')

    def test_capture_attempt_field_is_optional(self):
        self.f.record['scope'].pop('max_capture_attempts')
        self.passed('capture')

    def test_no_bgm_when_not_requested(self):
        self.f.record['scope']['authorized_actions'].remove('bgm')
        self.f.record['scope'].pop('bgm')
        self.passed('capture')

    def test_requested_bgm_without_permission_is_rejected(self):
        self.f.record['scope']['requested_actions'] = ['capture', 'bgm']
        self.f.record['scope']['authorized_actions'].remove('bgm')
        code, result = self.f.run_gate('capture')
        self.assertNotEqual(code, 0)
        self.assertIn('incomplete_production_scope', result['errors'])

    def test_approval_without_parent_id(self):
        self.f.events[1].pop('parentId')
        self.passed('capture')

    def test_existing_post_directory_can_be_resumed_without_overwriting(self):
        self.f.post_only_record()
        output = self.f.root/'post_v2'
        output.mkdir()
        asset=output/'already-generated.mp3'
        asset.write_bytes(b'preserve this successful asset')
        self.passed('post')
        self.assertEqual(asset.read_bytes(), b'preserve this successful asset')

    def test_optional_telemetry_and_restore_files(self):
        self.f.precheck['evidence'].pop('telemetry')
        self.f.precheck['evidence'].pop('restore')
        self.f.precheck['checks'].pop('state_restore')
        self.f.save_precheck()
        self.passed('capture')

    def test_reported_restore_failure_is_still_rejected(self):
        self.f.precheck['checks']['state_restore'] = 'FAIL'
        self.f.save_precheck()
        code,result=self.f.run_gate('capture')
        self.assertNotEqual(code,0)
        self.assertIn('render_precheck_not_passed:state_restore', result['errors'])

    def test_limitations_need_disclosure_not_a_separate_reference_approval(self):
        self.f.precheck['checks']['visual']='PASS_WITH_LIMITATIONS'
        self.f.precheck['visual_review']={'within_user_criteria':True,'limitations':['公共区']}
        self.f.save_precheck()
        self.passed('capture')

    def test_one_or_three_opening_headlines_and_no_cta(self):
        import sys
        from pathlib import Path
        sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
        from storyboard.model import validate
        sample=Path(__file__).resolve().parents[1]/'design-system/examples/valid.json'
        for lines in [['名称'],['名称','户型','区域']]:
            r=json.loads(sample.read_text())
            r['segments'][0]['visual']['headline_lines']=lines
            r['segments'][-1]['visual'].pop('cta',None)
            r['segments'][-1]['visual']['disclaimer']='以现场房况为准'
            validate(r)

    def linked_record(self):
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
        from check_shooting_plan import bundle_digest
        self.f.record['presentation'].update(mode='linked_document', document_path='plan_v1.md')
        self.f.events[0]['message']['content'][0]['text']='[图文剧本v1]('+str(self.f.root/'plan_v1.md')+')'
        self.f.events[1].pop('parentId', None)
        self.f.events[1]['message']['content'][0]['text']='接受，现在开始'
        self.f.record['approval'].update(explicit_text='接受，现在开始',plan_sha256=self.f.record['plan']['sha256'],
                                         bundle_sha256=bundle_digest(self.f.record))

    def run_linked(self, phase='capture', claim=False):
        import subprocess
        trace=self.f.root/'review.jsonl'
        trace.write_text(''.join(json.dumps(e,ensure_ascii=False)+'\n' for e in self.f.events))
        self.f.record['presentation']['transcript_sha256']=fixtures.sha(trace)
        record=self.f.root/'record.json';record.write_text(json.dumps(self.f.record,ensure_ascii=False))
        args=[sys.executable,str(fixtures.SCRIPT),'--record',str(record),'--phase',phase]
        if claim:args.append('--claim')
        result=subprocess.run(args,capture_output=True,text=True)
        return json.loads(result.stdout)

    def test_linked_content_does_not_require_user_hashes_or_browser_url(self):
        self.linked_record()
        self.assertNotIn('SHA256',self.f.events[0]['message']['content'][0]['text'])
        result=self.run_linked();self.assertTrue(result['passed'],result)

    def test_linked_approval_cannot_be_forged_from_question_with_negative_answer(self):
        self.linked_record()
        reply='<send_user_message_question_reply>\n'+json.dumps([{'question':'是否批准？','answer':'先调整修正方案'}],ensure_ascii=False)+'\n</send_user_message_question_reply>'
        self.f.events[1]['message']['content'][0]['text']=reply
        self.f.record['approval']['explicit_text']='先调整修正方案'
        self.assertIn('invalid_user_approval',self.run_linked()['errors'])

    def test_linked_content_snapshot_rejects_silent_plan_change(self):
        self.linked_record();path=self.f.root/'plan_v1.md'
        path.write_text(self.f.body+'\n新增承诺')
        self.f.record['plan']['sha256']=fixtures.sha(path)
        self.assertIn('approval_snapshot_mismatch',self.run_linked()['errors'])

    def test_new_output_after_failure_does_not_need_second_content_approval(self):
        self.linked_record();first=self.run_linked(claim=True)
        self.assertTrue(first['passed'],first)
        self.f.record['scope']['output_dir']='take02'
        self.f.record['exploration']['comparisons_by_issue']['glass']=5
        second=self.run_linked(claim=True)
        self.assertTrue(second['passed'],second)
        self.assertTrue((self.f.root/'take01/capture-claim.json').is_file())
        self.assertTrue((self.f.root/'take02/capture-claim.json').is_file())

    def test_linked_missing_snapshot_stays_unapproved(self):
        self.linked_record()
        self.f.record['approval'].pop('plan_sha256');self.f.record['approval'].pop('bundle_sha256')
        self.assertIn('missing_approval_snapshot',self.run_linked()['errors'])

    def test_unrelated_ambient_tab_does_not_override_explicit_reply(self):
        self.linked_record()
        self.f.events[1]['message']['content'][0]['text']='Current URL: file:///different-tab.html\n## My request:\n接受，现在开始'
        result=self.run_linked();self.assertTrue(result['passed'],result)


if __name__=='__main__':
    unittest.main(verbosity=2)
