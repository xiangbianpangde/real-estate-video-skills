#!/usr/bin/env python3
"""Optional offline mlx-whisper word timestamp adapter (Apple Silicon).

Requires an already-installed package and local model directory; no downloads,
paid calls, script prompting or replacement of recognized words with a script.
"""
import argparse
import json
from pathlib import Path
import os
import sys
sys.dont_write_bytecode=True
from media import sha,write_json


def align(audio,model,out):
    audio=Path(audio).resolve();model=Path(model).resolve();out=Path(out).resolve()
    if not audio.is_file() or not model.is_dir():raise ValueError('Existing audio and local model directory required')
    if out.exists() or out==audio:raise FileExistsError(out)
    os.environ['HF_HUB_OFFLINE']='1'
    import mlx_whisper
    result=mlx_whisper.transcribe(str(audio),path_or_hf_repo=str(model),language='zh',word_timestamps=True,condition_on_previous_text=False,temperature=0,verbose=False)
    words=[{'text':w['word'],'start_s':w['start'],'end_s':w['end'],'probability':w.get('probability')} for segment in result.get('segments',[]) for w in segment.get('words',[])]
    if not words:raise ValueError('No word timestamps returned')
    report={'schema':'vr-voice-alignment/v1','audio_path':str(audio),'audio_sha256':sha(audio),'text':result['text'],'words':words,'timing_origin':'mlx-whisper word timestamps, no script prompt','model_directory':str(model),'content_listening_verified':False}
    write_json(out,report);return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--audio',required=True);p.add_argument('--model-dir',required=True);p.add_argument('--out',required=True);a=p.parse_args()
    print(json.dumps(align(a.audio,a.model_dir,a.out),ensure_ascii=False,indent=2))
