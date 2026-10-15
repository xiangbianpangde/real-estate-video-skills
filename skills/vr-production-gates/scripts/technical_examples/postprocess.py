#!/usr/bin/env python3
"""Offline example: placed narration + aligned subtitles + crossfaded BGM -> MP4.

Reads explicit assets/timings, never generates speech or pretends to recognize
fixture tones. Burn-in uses Pillow because some FFmpeg builds lack libass.
Requires Python Pillow, ffmpeg/ffprobe and a font supplied by the caller.
"""
import argparse
from fractions import Fraction
import json
import math
from pathlib import Path
import subprocess
import sys
sys.dont_write_bytecode=True
from media import sha,probe,write_json,output_folder


def finite(value):
    return type(value) in (int,float) and math.isfinite(value)


def srt_time(value):
    ms=round(value*1000)
    return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'


def prepare(plan_path):
    path=Path(plan_path).resolve();plan=json.loads(path.read_text());base=path.parent
    resolve=lambda name:(base/name).resolve()
    video=resolve(plan['video']);font=resolve(plan['font']);music=resolve(plan['music']) if plan.get('music') else None
    info=probe(video);duration=info['duration_s'];stream=next(s for s in info['streams'] if s['codec_type']=='video')
    inputs=[path,video,font]+([music] if music else []);chapters=[];cues=[];previous_end=0
    for item in plan['narration']:
        audio=resolve(item['audio']);alignment=resolve(item['alignment']);timing=json.loads(alignment.read_text());length=probe(audio)['duration_s'];start=item['start_s']
        if timing['audio_sha256']!=sha(audio):raise ValueError('Alignment audio SHA mismatch')
        if not finite(start) or start<0 or start<previous_end or start+length>duration+.001:raise ValueError('Narration overlap or outside video')
        previous_end=start+length
        words=timing['words'];previous=0
        if not words:raise ValueError('Word timestamps required; no uniform character timing fallback')
        for word in words:
            a,b=word['start_s'],word['end_s']
            if not isinstance(word['text'],str) or not word['text'] or not all(finite(v) for v in [a,b]) or a<previous or b<=a or b>length+.001:raise ValueError('Invalid word timing')
            previous=b
        # A mismatch is exposed, not silently replaced with the approved script.
        actual=''.join(w['text'] for w in words)
        if actual!=item['text']:raise ValueError('Transcript differs from expected text; review before rendering')
        cue={'text':actual,'start_s':start+words[0]['start_s'],'end_s':start+words[-1]['end_s'],'words':[dict(w,start_s=start+w['start_s'],end_s=start+w['end_s']) for w in words]}
        cues.append(cue);chapters.append({**item,'audio':audio,'alignment':alignment,'duration_s':length,'timing_origin':timing['timing_origin']});inputs += [audio,alignment]
    if not chapters:raise ValueError('At least one narration item required by this audio example')
    fps=plan.get('fps',float(Fraction(stream['avg_frame_rate'])))
    if not finite(fps) or fps<=0:raise ValueError('Finite positive fps required')
    gain=plan.get('music_gain',.12)
    if not finite(gain) or gain<0:raise ValueError('Finite nonnegative music gain required')
    return plan,video,font,music,info,stream,duration,fps,gain,chapters,cues,inputs


def build(plan_path,out):
    plan,video,font_path,music,info,stream,duration,fps,gain,chapters,cues,inputs=prepare(plan_path)
    from PIL import Image,ImageDraw,ImageFont
    width,height=stream['width'],stream['height'];font=ImageFont.truetype(str(font_path),max(12,round(height*.045)))
    stroke=max(1,round(font.size*.12));patches=[]
    for cue in cues:
        lines=[];line=''
        for character in cue['text']:
            if line and font.getlength(line+character)>width*.88:lines.append(line);line=''
            line+=character
        if line:lines.append(line)
        text='\n'.join(lines);box=font.getbbox('Ag',stroke_width=stroke);line_height=box[3]-box[1]+stroke*2+4
        patch=Image.new('RGBA',(width,line_height*len(lines)+stroke*4));draw=ImageDraw.Draw(patch)
        for i,line in enumerate(lines):draw.text((width/2,stroke*2+i*line_height),line,font=font,anchor='mt',fill='white',stroke_width=stroke,stroke_fill='black')
        y=round(height*.61-patch.height/2)
        if y<0 or y+patch.height>height:raise ValueError('Subtitle block does not fit; split the utterance or adjust layout')
        patches.append((cue,patch,y))
    folder=output_folder(out,inputs);filters=[];args=['ffmpeg','-v','error','-n'];labels=[]
    for i,item in enumerate(chapters):
        args+=['-i',str(item['audio'])]
        filters.append(f'[{i}:a]aresample=48000,aformat=channel_layouts=stereo,adelay={round(item["start_s"]*1000)}:all=1,apad,atrim=duration={duration}[v{i}]');labels.append(f'[v{i}]')
    filters.append(''.join(labels)+f'amix=inputs={len(labels)}:normalize=0:duration=longest[voice]')
    if music:
        index=len(chapters);args+=['-i',str(music)];length=probe(music)['duration_s'];cross=min(.5,length/4)
        repeats=max(1,math.ceil(max(0,duration-length)/(length-cross))+1)
        stem=f'[{index}:a]aresample=48000,aformat=channel_layouts=stereo'
        if repeats>1:
            filters.append(stem+f',asplit={repeats}'+''.join(f'[m{i}]' for i in range(repeats)))
            current='m0'
            for i in range(1,repeats):
                label=f'loop{i}';filters.append(f'[{current}][m{i}]acrossfade=d={cross}:c1=tri:c2=tri[{label}]');current=label
        else:filters.append(stem+'[music0]');current='music0'
        fade=min(1,duration/4)
        filters.append(f'[{current}]atrim=duration={duration},volume={gain},afade=t=in:d={fade},afade=t=out:st={duration-fade}:d={fade}[bed]')
        filters.append('[voice]asplit=2[spoken][side]')
        filters.append('[bed][side]sidechaincompress=threshold=0.03:ratio=6:attack=40:release=350[ducked]')
        filters.append(f'[spoken][ducked]amix=inputs=2:normalize=0:duration=longest,alimiter=limit=0.95:latency=1,atrim=duration={duration}[final]')
    else:filters.append('[voice]anull[final]');cross=None;repeats=0
    mixed=folder/'mixed.wav';mix_cmd=args+['-filter_complex',';'.join(filters),'-map','[final]','-ar','48000',str(mixed)];subprocess.run(mix_cmd,check=True)
    (folder/'subtitles.srt').write_text('\n\n'.join(f'{i+1}\n{srt_time(c["start_s"])} --> {srt_time(c["end_s"])}\n{c["text"]}' for i,c in enumerate(cues))+'\n')
    write_json(folder/'subtitle-timing.json',{'cues':cues,'timing_origins':[i['timing_origin'] for i in chapters],'synthetic_fixture':plan.get('synthetic_fixture',False)})
    target=folder/'final.mp4';decode_cmd=['ffmpeg','-v','error','-i',str(video),'-vf',f'fps={fps}','-f','rawvideo','-pix_fmt','rgb24','-']
    encode_cmd=['ffmpeg','-v','error','-n','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{width}x{height}','-framerate',str(fps),'-i','-','-i',str(mixed),'-map','0:v:0','-map','1:a:0','-c:v','libx264','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-movflags','+faststart',str(target)]
    source_sha=sha(video);frames=0
    with (folder/'decode.log').open('w') as de, (folder/'encode.log').open('w') as en:
        decoder=subprocess.Popen(decode_cmd,stdout=subprocess.PIPE,stderr=de);encoder=subprocess.Popen(encode_cmd,stdin=subprocess.PIPE,stderr=en)
        try:
            while True:
                block=decoder.stdout.read(width*height*3)
                if not block:break
                if len(block)!=width*height*3:raise ValueError('Incomplete decoded frame')
                frame=Image.frombytes('RGB',(width,height),block);t=frames/fps
                for cue,patch,y in patches:
                    if cue['start_s']<=t<cue['end_s']:frame.paste(patch,(0,y),patch);break
                encoder.stdin.write(frame.tobytes());frames+=1
            encoder.stdin.close()
            if decoder.wait()!=0 or encoder.wait()!=0:raise RuntimeError('FFmpeg render failed; inspect logs')
        finally:
            for process in (decoder,encoder):
                if process.poll() is None:process.kill();process.wait()
            decoder.stdout.close()
            if not encoder.stdin.closed:encoder.stdin.close()
    subprocess.run(['ffmpeg','-v','error','-i',str(target),'-f','null','-'],check=True)
    report={'schema':'vr-post-example/v1','synthetic_fixture':plan.get('synthetic_fixture',False),'output_sha256':sha(target),'source_sha256':source_sha,'source_unchanged':sha(video)==source_sha,'duration_s':probe(target)['duration_s'],'frames':frames,'source_audio':'replaced explicitly by plan narration/music; source untouched','music_crossfade_s':cross,'music_repeats':repeats,'mix_command':mix_cmd,'decode_command':decode_cmd,'encode_command':encode_cmd,'audio_listening_verified':False,'human_accepted':False,'scope':'caption and audio example; opening/floorplan/CTA not implemented here, reuse storyboard previews for those layers'}
    write_json(folder/'post-receipt.json',report);return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--plan',required=True);p.add_argument('--out',required=True);a=p.parse_args()
    print(json.dumps(build(a.plan,a.out),ensure_ascii=False,indent=2))
