"""Real FFmpeg/Pillow examples with explicitly synthetic assets. No live services.

Checks timing, burn-in, audio, preservation and refusal before output on invalid
input. Run with a Python runtime containing Pillow, not a skipped dependency.
"""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
sys.dont_write_bytecode=True
SCRIPTS=Path(__file__).resolve().parents[1]/'scripts/technical_examples'


class TechnicalExamples(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.p=Path(self.tmp.name)
        self.call(['ffmpeg','-v','error','-f','lavfi','-i','testsrc2=s=160x284:r=12:d=6','-an','-c:v','libx264','-pix_fmt','yuv420p',str(self.p/'source.mp4')])
        self.source_sha=self.sha(self.p/'source.mp4')
        self.mapping={'schema':'vr-continuous-edit/v1','source_sha256':self.source_sha,'source_duration_s':6,'speed_map':[{'source_start_s':0,'source_end_s':2,'speed':1},{'source_start_s':2,'source_end_s':4,'speed':2},{'source_start_s':4,'source_end_s':6,'speed':1}]}
        self.map=self.p/'map.json';self.map.write_text(json.dumps(self.mapping))

    def tearDown(self):self.tmp.cleanup()
    def sha(self,p):return hashlib.sha256(p.read_bytes()).hexdigest()
    def call(self,args):return subprocess.run(args,capture_output=True,text=True,check=True)
    def script(self,name,*args,good=True):
        result=subprocess.run([sys.executable,str(SCRIPTS/name),*map(str,args)],capture_output=True,text=True)
        self.assertEqual(result.returncode==0,good,result.stderr)
        return result

    def retime(self):
        self.script('retime.py','--source',self.p/'source.mp4','--map',self.map,'--out',self.p/'edited','--fps','12')
        receipt=json.loads((self.p/'edited/continuous-edit.json').read_text())
        self.assertAlmostEqual(receipt['actual_output_duration_s'],5,delta=1/12)
        self.assertEqual(self.sha(self.p/'source.mp4'),self.source_sha)
        return self.p/'edited/retimed.mp4'

    def audio_plan(self,video):
        self.call(['ffmpeg','-v','error','-f','lavfi','-i','sine=frequency=600:sample_rate=48000:duration=1',str(self.p/'voice.wav')])
        self.call(['ffmpeg','-v','error','-f','lavfi','-i','sine=frequency=220:sample_rate=48000:duration=2',str(self.p/'music.wav')])
        self.timing={'audio_sha256':self.sha(self.p/'voice.wav'),'text':'DEMO ONLY','timing_origin':'synthetic_fixture_timing, not speech recognition','words':[{'text':'DEMO ','start_s':.1,'end_s':.4},{'text':'ONLY','start_s':.4,'end_s':.9}]}
        (self.p/'timing.json').write_text(json.dumps(self.timing))
        fonts=[Path('/System/Library/Fonts/Supplemental/Arial.ttf'),Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')]
        font=next((f for f in fonts if f.exists()),None)
        if font is None:raise RuntimeError('Supply a local test font; test not skipped')
        self.plan={'synthetic_fixture':True,'video':str(video),'font':str(font),'music':'music.wav','fps':12,'narration':[{'id':'S01','text':'DEMO ONLY','audio':'voice.wav','alignment':'timing.json','start_s':.5}]}
        plan=self.p/'post.json';plan.write_text(json.dumps(self.plan));return plan

    def test_continuous_mapping_changes_duration_and_preserves_input(self):self.retime()

    def test_gap_rejected_before_output(self):
        self.mapping['speed_map'][1]['source_start_s']=2.2;self.map.write_text(json.dumps(self.mapping))
        self.script('retime.py','--source',self.p/'source.mp4','--map',self.map,'--out',self.p/'bad',good=False)
        self.assertFalse((self.p/'bad').exists())

    def test_end_to_end_real_media_has_audio_burn_in_and_full_text(self):
        video=self.retime();plan=self.audio_plan(video)
        self.script('postprocess.py','--plan',plan,'--out',self.p/'post')
        receipt=json.loads((self.p/'post/post-receipt.json').read_text())
        self.assertTrue(receipt['source_unchanged']);self.assertFalse(receipt['audio_listening_verified']);self.assertFalse(receipt['human_accepted'])
        self.assertGreater(receipt['music_repeats'],1);self.assertIn('DEMO ONLY',(self.p/'post/subtitles.srt').read_text())
        info=json.loads(self.call(['ffprobe','-v','error','-show_streams','-of','json',str(self.p/'post/final.mp4')]).stdout)
        self.assertTrue(any(s['codec_type']=='audio' for s in info['streams']))
        # At t=1, white/black caption pixels must differ around .61H. Both inputs
        # use the same codec settings; a large local difference exposes no burn-in.
        def frame(path):return subprocess.check_output(['ffmpeg','-v','error','-ss','1','-i',str(path),'-vf','crop=150:36:4:155','-frames:v','1','-f','rawvideo','-pix_fmt','rgb24','-'])
        before,after=frame(video),frame(self.p/'post/final.mp4')
        self.assertGreater(sum(abs(a-b)>80 for a,b in zip(before,after)),100)

    def test_wrong_alignment_hash_cannot_render(self):
        plan=self.audio_plan(self.p/'source.mp4');self.timing['audio_sha256']='0'*64;(self.p/'timing.json').write_text(json.dumps(self.timing))
        self.script('postprocess.py','--plan',plan,'--out',self.p/'bad',good=False);self.assertFalse((self.p/'bad').exists())

    def test_script_mismatch_is_not_silently_replaced(self):
        plan=self.audio_plan(self.p/'source.mp4');self.plan['narration'][0]['text']='OTHER WORDS';plan.write_text(json.dumps(self.plan))
        self.script('postprocess.py','--plan',plan,'--out',self.p/'bad',good=False);self.assertFalse((self.p/'bad').exists())


    def test_bgm_short_source_not_padded_or_looped_and_original_preserved(self):
        source=self.p/'library';source.mkdir();audio=source/'short.wav'
        self.call(['ffmpeg','-v','error','-f','lavfi','-i','sine=frequency=330:sample_rate=48000:duration=1',str(audio)])
        original=self.sha(audio)
        self.script('prepare_bgm.py','--source-dir',source,'--out',source/'ready','--seconds','35')
        report=json.loads((source/'ready/清单.json').read_text());entry=report['entries'][0]
        self.assertEqual(entry['excerpt_source_s'],[0,1])
        self.assertEqual(self.sha(audio),original)
        for out in entry['outputs'].values():
            self.assertAlmostEqual(out['duration_s'],1,delta=.08)
            self.assertLess(out['true_peak_dbfs'],0)
            self.assertTrue(out['full_decode_passed'])
            self.assertTrue((source/'ready'/out['path']).exists())

    def test_bgm_existing_output_not_overwritten(self):
        source=self.p/'library';source.mkdir();audio=source/'source.wav'
        self.call(['ffmpeg','-v','error','-f','lavfi','-i','sine=frequency=330:duration=1',str(audio)])
        out=source/'ready';out.mkdir();sentinel=out/'keep.txt';sentinel.write_text('user work')
        self.script('prepare_bgm.py','--source-dir',source,'--out',out,good=False)
        self.assertEqual(sentinel.read_text(),'user work')
        self.assertEqual(list(out.iterdir()),[sentinel])

    def test_bgm_silent_source_does_not_claim_usable_output(self):
        source=self.p/'library';source.mkdir()
        self.call(['ffmpeg','-v','error','-f','lavfi','-i','anullsrc=r=48000:cl=stereo','-t','1',str(source/'silent.wav')])
        self.script('prepare_bgm.py','--source-dir',source,'--out',source/'ready',good=False)
        self.assertFalse((source/'ready/试听索引.html').exists())


if __name__=='__main__':unittest.main(verbosity=2)
