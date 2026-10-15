#!/usr/bin/env python3
"""Apply a complete, ordered speed map to ONE video. No concatenated takes.

Offline; does not generate speech or change the input. Original audio requires
explicit discard because new narration must be aligned to the edited timeline.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from storyboard.model import validate_editing
from media import probe,sha,write_json,output_folder


def retime(source,mapping,out,fps=30,discard_audio=False):
    source=Path(source).resolve();report=json.loads(Path(mapping).read_text());info=probe(source)
    if sha(source)!=report['source_sha256']:raise ValueError('Source SHA mismatch')
    duration=report['source_duration_s']
    if abs(info['duration_s']-duration)>.001:raise ValueError('Source duration mismatch')
    if any(s['codec_type']=='audio' for s in info['streams']) and not discard_audio:
        raise ValueError('Source has audio; choose its treatment explicitly (--discard-audio for this example)')
    record={'scope':{'continuity_class':'cross_room_travel','editing_policy':{'single_take_required':True,'allow_cuts':False,'allow_remove_intervals':False,'allow_speed_changes':True},'editing_source_duration_s':duration,'speed_map':report['speed_map']}}
    validate_editing(record)
    if type(fps) is not int or fps<=0:raise ValueError('Positive integer fps required')
    elapsed=0.;parts=[]
    for segment in report['speed_map']:
        a,b,speed=(segment[k] for k in ('source_start_s','source_end_s','speed'))
        expression=f'({elapsed:.12g}+(T-{a:.12g})/{speed:.12g})'
        parts.append((b,expression));elapsed+=(b-a)/speed
    expression=parts[-1][1]
    for end,value in reversed(parts[:-1]):expression=f'if(lt(T,{end:.12g}),{value},{expression})'
    folder=output_folder(out,[source,mapping]);target=folder/'retimed.mp4'
    # A single timestamp transform, no trim/concat or source interval deletion.
    filters=f"setpts=PTS-STARTPTS,setpts='{expression}/TB',fps={fps}"
    cmd=['ffmpeg','-v','error','-n','-i',str(source),'-map','0:v:0','-an','-vf',filters,'-c:v','libx264','-pix_fmt','yuv420p','-crf','20','-movflags','+faststart',str(target)]
    subprocess.run(cmd,check=True)
    result={**report,'schema':'vr-continuous-edit/v1','expected_output_duration_s':elapsed,'actual_output_duration_s':probe(target)['duration_s'],'output_sha256':sha(target),'ffmpeg_argv':cmd,'fps_normalization':'CFR sampling, no optical interpolation; frames may be sampled but no source time interval is omitted','speed_boundary':'piecewise constant; not speed ramping','source_unchanged':sha(source)==report['source_sha256'],'visual_verified':False,'human_accepted':False}
    write_json(folder/'continuous-edit.json',result)
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',required=True);parser.add_argument('--map',required=True)
    parser.add_argument('--out',required=True);parser.add_argument('--fps',type=int,default=30)
    parser.add_argument('--discard-audio',action='store_true');a=parser.parse_args()
    print(json.dumps(retime(a.source,a.map,a.out,a.fps,a.discard_audio),ensure_ascii=False,indent=2))
