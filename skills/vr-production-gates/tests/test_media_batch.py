"""Synthetic CLI regression: partial success must never regenerate successful media."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT=Path(__file__).resolve().parents[1]/'scripts/check_media_batch.py'

class MediaBatchTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.request={'requests':[{'text':'完整章节甲。','output_file':'A.mp3','speed':.8},{'text':'完整章节乙。','output_file':'B.mp3','speed':.9}]}
        self.response={'code':0,'total_requested':2,'total_success':1,'total_failed':1,'success_items':[{'node_id':'asset-A','file_name':'A.mp3'}],'failed_items':[{'index':1,'err_code':429,'error_msg':'rate limited'}]}
    def tearDown(self):self.temp.cleanup()
    def invoke(self):
        for name,data in [('request',self.request),('response',self.response)]:
            (self.root/(name+'.json')).write_text(json.dumps(data))
        result=subprocess.run([sys.executable,str(SCRIPT),'--request',str(self.root/'request.json'),'--response',str(self.root/'response.json'),'--retry-output',str(self.root/'retry.json')],capture_output=True,text=True)
        self.assertTrue(result.stdout,result.stderr)
        return result.returncode,json.loads(result.stdout)
    def test_partial_zero_code_retries_only_failed_original(self):
        code,data=self.invoke();self.assertEqual(code,0);self.assertFalse(data['complete']);self.assertEqual(json.loads((self.root/'retry.json').read_text()),{'requests':[self.request['requests'][1]]})
    def test_count_mismatch_blocks(self):
        self.response['total_success']=2;code,data=self.invoke();self.assertNotEqual(code,0);self.assertFalse((self.root/'retry.json').exists())
    def test_unaccounted_item_blocks(self):
        self.response['failed_items']=[];code,data=self.invoke();self.assertNotEqual(code,0)
    def test_success_and_failure_same_item_blocks(self):
        self.response['failed_items'][0]['index']=0;code,data=self.invoke();self.assertNotEqual(code,0)
    def test_auth_failure_never_retries(self):
        self.response['failed_items'][0]['err_code']=401;code,data=self.invoke();self.assertNotEqual(code,0);self.assertFalse((self.root/'retry.json').exists())
    def test_full_success_has_no_retry(self):
        self.response.update(total_success=2,total_failed=0,success_items=[{'node_id':'asset-A','file_name':'A.mp3'},{'node_id':'asset-B','file_name':'B.mp3'}],failed_items=[])
        code,data=self.invoke();self.assertEqual(code,0);self.assertTrue(data['complete']);self.assertFalse((self.root/'retry.json').exists())
    def test_existing_retry_file_preserved(self):
        (self.root/'retry.json').write_text('keep');code,data=self.invoke();self.assertNotEqual(code,0);self.assertEqual((self.root/'retry.json').read_text(),'keep')
    def test_top_level_failure_blocks_even_if_items_claim_success(self):
        self.response['code']=401;code,data=self.invoke();self.assertNotEqual(code,0)

if __name__=='__main__':unittest.main()
