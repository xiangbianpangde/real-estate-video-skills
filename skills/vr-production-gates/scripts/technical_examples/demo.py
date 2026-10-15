#!/usr/bin/env python3
"""Create an offline synthetic demo. Test tones are NOT generated speech/music."""
import argparse
from pathlib import Path
import subprocess
import sys
sys.dont_write_bytecode=True
from media import output_folder,sha,probe,write_json
from retime import retime
from postprocess import build


def demo(out,font):
    font=Path(font).resolve()
    if not font.is_file():raise ValueError('Supply an existing font')
    folder=output_folder(out,[font]);source=folder/'source.mp4'
    def generate(spec,target,video=False):
        args=['ffmpeg','-v','error','-n','-f','lavfi','-i',spec]
        if video:args+=['-an','-c:v','libx264','-pix_fmt','yuv420p']
        subprocess.run(args+[str(target)],check=True)
    generate('testsrc2=s=320x568:r=12:d=6',source,True)
    generate('sine=frequency=600:sample_rate=48000:duration=1',folder/'voice.wav')
    generate('sine=frequency=220:sample_rate=48000:duration=2',folder/'music.wav')
    write_json(folder/'map.json',{'schema':'vr-continuous-edit/v1','source_sha256':sha(source),'source_duration_s':probe(source)['duration_s'],'speed_map':[{'source_start_s':0,'source_end_s':2,'speed':1},{'source_start_s':2,'source_end_s':4,'speed':2},{'source_start_s':4,'source_end_s':6,'speed':1}]})
    retime(source,folder/'map.json',folder/'edited',fps=12)
    write_json(folder/'timing.json',{'audio_sha256':sha(folder/'voice.wav'),'text':'DEMO ONLY','timing_origin':'synthetic fixture, NOT ASR','words':[{'text':'DEMO ','start_s':.1,'end_s':.4},{'text':'ONLY','start_s':.4,'end_s':.9}]})
    write_json(folder/'post.json',{'synthetic_fixture':True,'video':'edited/retimed.mp4','font':str(font),'music':'music.wav','fps':12,'narration':[{'id':'S01','text':'DEMO ONLY','audio':'voice.wav','alignment':'timing.json','start_s':.5}]})
    build(folder/'post.json',folder/'post')
    (folder/'review.html').write_text('''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>技术示范 · 合成测试素材</title><style>body{font:18px system-ui;max-width:900px;margin:32px auto;background:#f4f8f8;color:#193c46}video{max-height:70vh;max-width:100%;background:#000}p{line-height:1.6}</style><h1>技术示范 · 合成测试素材</h1><p>6秒单源完整区间映射为约5秒：中间2秒以2倍速播放。字幕使用人工测试时码，两个正弦测试音用于检查混音。此示范不证明真人配音、音乐审美、房源运动或实际语音识别已通过。</p><video controls preload="metadata" src="post/final.mp4"></video><p><a href="edited/continuous-edit.json">变速回执</a> · <a href="post/post-receipt.json">后期回执</a> · <a href="post/subtitles.srt">字幕</a></p></html>''')
    print(folder/'review.html')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',required=True);p.add_argument('--font',required=True);a=p.parse_args();demo(a.out,a.font)
