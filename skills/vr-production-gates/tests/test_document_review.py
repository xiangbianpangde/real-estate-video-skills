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
