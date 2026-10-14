"""Real CLI checks for browser-document approvals; all inputs are synthetic."""
import base64
import hashlib
import html
import json
from pathlib import Path
import subprocess
import sys
import unittest
from run import GateTests, sha, SCRIPT


class DocumentReviewTests(unittest.TestCase):
    def setUp(self):
        self.fixture = GateTests()
        self.fixture.setUp()
        self.root = self.fixture.root
        self.record = self.fixture.record
        image = base64.b64encode((self.root/'overview.png').read_bytes()).decode()
        doc = '<html><pre>'+html.escape(self.fixture.body)+'</pre>'
        doc += ('<img src="data:image/png;base64,'+image+'">')*3+'</html>'
        (self.root/'script.html').write_text(doc)
        self.record['assets'].append({'path':'script.html','sha256':sha(self.root/'script.html'),'role':'integrated_review_source'})
        core={k:self.record[k] for k in ('plan','assets','segments','scope','exploration')}
        bundle=hashlib.sha256(json.dumps(core,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
        self.url=(self.root/'script.html').as_uri()
        self.items=[
            {'type':'response_item','payload':{'type':'function_call_output','output':json.dumps({'passed':True,'phase':'review','plan_sha256':self.record['plan']['sha256'],'bundle_sha256':bundle})}},
            {'type':'response_item','payload':{'type':'message','id':'shown','role':'assistant','content':[{'type':'output_text','text':'[完整剧本]('+str(self.root/'script.html')+')'}]}},
            {'type':'response_item','payload':{'type':'message','id':'approved','role':'user','content':[{'type':'input_text','text':'Current URL: '+self.url+'\n## My request:\n审核通过开始下一步。'}]}}
        ]
        self.record['presentation']={'mode':'rendered_document','document_path':'script.html','transcript_path':'document-review.jsonl','assistant_event_id':'shown'}
        self.record['approval']={'user_event_id':'approved','explicit_text':'审核通过开始下一步。'}

    def tearDown(self):
        self.fixture.tearDown()

    def run_gate(self):
        trace=self.root/'document-review.jsonl'
        trace.write_text(''.join(json.dumps(i,ensure_ascii=False)+'\n' for i in self.items))
        self.record['presentation']['transcript_sha256']=sha(trace)
        (self.root/'record.json').write_text(json.dumps(self.record,ensure_ascii=False))
        result=subprocess.run([sys.executable,str(SCRIPT),'--record',str(self.root/'record.json'),'--phase','capture'],capture_output=True,text=True)
        return json.loads(result.stdout)

    def add_shot_constraints(self, framing):
        self.record['scope'].update(shot_constraints={'duration_range_s':[9,11],'excluded_spaces':['bathroom'],'avoid_wall_facing':True},route_space_ids=['living_dining'])
        for seg in self.record['segments']:
            seg.update(space_ids=['living_dining'],framing_status=framing,visual={'title':'公共区','layout':'source_reference','motion':{'kind':'travel','label':'保持主体'}})
        core={k:self.record[k] for k in ('plan','assets','segments','scope','exploration')}
        bundle=hashlib.sha256(json.dumps(core,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
        self.items[0]['payload']['output']=json.dumps({'passed':True,'phase':'review','plan_sha256':self.record['plan']['sha256'],'bundle_sha256':bundle})

    def test_subject_constraints_preserve_capture_gate(self):
        self.add_shot_constraints('subject');self.assertTrue(self.run_gate()['passed'])

    def test_pending_framing_blocks_capture(self):
        self.add_shot_constraints('pending');result=self.run_gate();self.assertFalse(result['passed']);self.assertIn('shot_framing_pending',result['errors'])

    def add_complete_route(self, include_in_body=True):
        self.record['design_system']={'id':'real-estate-storyboard','version':'1.1.0'}
        self.record['scope']['route']='0→1';self.fixture.precheck['route']='0→1';self.fixture.save_precheck()
        self.record['segments'][0]['visual']={'role':'opening','title':'开场','layout':'opening_composite','headline_lines':['测试','测试户型'],'motion':{'kind':'static','label':'主体静态'}}
        self.record['segments'][1]['visual']={'role':'ending','title':'收束','layout':'ending_composite','cta':'留言','motion':{'kind':'static','label':'主体收束'}}
        self.record['review_route']={'purpose':'script_review_only','included_in_video':False,'floorplan':'overview.png','route':'0→1','caption':'合成测试示意','nodes':[{'pano_index':0,'floorplan_xy':[.2,.2]},{'pano_index':1,'floorplan_xy':[.8,.8]}],'chapters':[{'id':seg['id'],'title':seg['visual']['title'],'start_s':seg['start_s'],'end_s':seg['end_s'],'pano_indices':[0] if i==0 else [0,1],'stop_pano':i,'motion_kind':'static'} for i,seg in enumerate(self.record['segments'])]}
        (self.root/'route.png').write_bytes((self.root/'overview.png').read_bytes())
        (self.root/'route.html').write_text('<div data-complete-route-board="true">'+''.join(f'<li data-route-chapter="{s["id"]}" data-start="{s["start_s"]}" data-end="{s["end_s"]}" data-panos="{"0" if s["id"]=="S01" else "0→1"}"></li>' for s in self.record['segments'])+'</div>')
        for name,role in [('route.png','review_route'),('route.html','review_route_source')]:self.record['assets'].append({'path':name,'sha256':sha(self.root/name),'role':role})
        self.record['scope']['review_route_layout']={'board':'route.png','source':'route.html'}
        self.fixture.body+='\n0→1\n'
        if include_in_body:self.fixture.body+='\n## 户型运镜路线图（仅用于剧本审核）\n![完整路线方案板](route.png)\n'
        (self.root/'plan_v1.md').write_text(self.fixture.body);self.record['plan']['sha256']=sha(self.root/'plan_v1.md')
        for asset in self.record['assets']:
            if asset['path']=='plan_v1.md':asset['sha256']=self.record['plan']['sha256']
        image=base64.b64encode((self.root/'overview.png').read_bytes()).decode()
        (self.root/'script.html').write_text('<html><pre>'+html.escape(self.fixture.body)+'</pre>'+('<img src="data:image/png;base64,'+image+'">')*4+'</html>')
        next(a for a in self.record['assets'] if a['path']=='script.html')['sha256']=sha(self.root/'script.html')
        self.refresh_digest()

    def refresh_digest(self):
        core={k:self.record[k] for k in ('plan','assets','segments','scope','exploration')}
        bundle=hashlib.sha256(json.dumps(core,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
        self.items[0]['payload']['output']=json.dumps({'passed':True,'phase':'review','plan_sha256':self.record['plan']['sha256'],'bundle_sha256':bundle})

    def test_complete_route_document_passes(self):
        self.add_complete_route();self.assertTrue(self.run_gate()['passed'])

    def test_nested_script_resolves_images_from_script_directory(self):
        self.add_complete_route()
        import re
        body=re.sub(r'(!\[[^\]]*\]\()([^)]*)(\))',r'\1../\2\3',self.fixture.body)
        (self.root/'package').mkdir()
        (self.root/'package/plan_v1.md').write_text(body)
        self.record['plan'].update(path='package/plan_v1.md',sha256=sha(self.root/'package/plan_v1.md'))
        image=base64.b64encode((self.root/'overview.png').read_bytes()).decode()
        (self.root/'script.html').write_text('<html><pre>'+html.escape(body)+'</pre>'+('<img src="data:image/png;base64,'+image+'">')*4+'</html>')
        next(a for a in self.record['assets'] if a['path']=='script.html')['sha256']=sha(self.root/'script.html')
        self.refresh_digest()
        self.assertTrue(self.run_gate()['passed'])

    def test_complete_route_omitted_from_body_rejected(self):
        self.add_complete_route(False);result=self.run_gate();self.assertFalse(result['passed']);self.assertIn('complete_route_board_not_in_plan',result['errors'])

    def test_complete_route_layout_missing_rejected(self):
        self.add_complete_route();self.record['scope'].pop('review_route_layout');self.refresh_digest();result=self.run_gate();self.assertFalse(result['passed']);self.assertIn('missing_complete_route_layout',result['errors'])

    def test_document_approval_passes(self):
        self.assertTrue(self.run_gate()['passed'])

    def test_other_document_rejected(self):
        self.items[-1]['payload']['content'][0]['text']=self.items[-1]['payload']['content'][0]['text'].replace('script.html','other.html')
        self.assertFalse(self.run_gate()['passed'])

    def test_no_prior_digest_rejected(self):
        self.items.pop(0)
        self.assertFalse(self.run_gate()['passed'])

    def test_late_presentation_rejected(self):
        self.items[1],self.items[2]=self.items[2],self.items[1]
        self.assertFalse(self.run_gate()['passed'])

    def test_changed_document_rejected(self):
        (self.root/'script.html').write_text('changed after approval')
        self.assertFalse(self.run_gate()['passed'])

    def test_missing_script_content_rejected(self):
        (self.root/'script.html').write_text('<h1>title only</h1>')
        self.record['assets'][-1]['sha256']=sha(self.root/'script.html')
        self.assertFalse(self.run_gate()['passed'])


if __name__=='__main__':
    unittest.main()
