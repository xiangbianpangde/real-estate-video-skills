"""Transport failures, resume behavior and real FFmpeg decode with synthetic audio."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

SCRIPT=Path(__file__).resolve().parents[1]/'scripts/minimax_tts_cn.py'
spec=importlib.util.spec_from_file_location('minimax_tts_cn',SCRIPT)
tts=importlib.util.module_from_spec(spec);spec.loader.exec_module(tts)


class TtsTests(unittest.TestCase):
    def test_payload_and_cn_region(self):
        body=tts.payload('你好','voice','speech-2.8-hd',1)
        self.assertFalse(body['stream'])
        self.assertEqual(body['output_format'],'hex')
        self.assertEqual(tts.BASE,'https://api.minimax.cn/v1')
        with self.assertRaises(ValueError):tts.api('/x',{},base='https://example.com')
    def test_bad_audio_and_incomplete_status_rejected(self):
        for data in [{'status':1,'audio':'ff'},{'status':2,'audio':'xyz'},{'status':2,'audio':''}]:
            with self.assertRaises(ValueError):tts.decode({'data':data})
    def test_missing_auth_explicit_without_secret(self):
        with patch.dict(os.environ,{},clear=True):
            with self.assertRaisesRegex(RuntimeError,'API_KEY'):tts.api('/x',{})
    def test_remote_failure_does_not_retry_or_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'take';calls=[]
            def fail(*a,**kw):calls.append(1);raise RuntimeError('API 2049')
            with self.assertRaisesRegex(RuntimeError,'2049'):tts.synthesize('你好',out,'voice',transport=fail)
            self.assertEqual(len(calls),1)
            self.assertEqual(json.loads((out/'voiceover-manifest.json').read_text())['status'],'failed_or_unknown')
            with self.assertRaises((KeyError,ValueError)):tts.synthesize('你好',out,'voice',transport=fail)
            self.assertEqual(len(calls),1)
    def test_real_decode_resume_and_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/'synthetic.mp3'
            subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i','sine=frequency=440:duration=0.3','-ar','32000',str(source)],check=True)
            def fake(*a,**kw):return {'data':{'status':2,'audio':source.read_bytes().hex()},'trace_id':'synthetic','extra_info':{'usage_characters':2}}
            out=Path(tmp)/'output'
            result=tts.synthesize('你好',out,'voice',transport=fake)
            self.assertEqual(result['status'],'technical_passed')
            self.assertGreater(result['duration_s'],0)
            self.assertTrue(tts.synthesize('你好',out,'voice',transport=fake)['reused'])
            with self.assertRaises(ValueError):tts.synthesize('改文案',out,'voice',transport=fake)
            self.assertFalse(result['human_listening_verified'])
