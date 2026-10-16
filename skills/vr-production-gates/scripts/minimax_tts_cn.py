#!/usr/bin/env python3
"""MiniMax mainland-China HTTP TTS. Python 3.10+, stdlib, FFmpeg/ffprobe.
API key: MINIMAX_CN_API_KEY or MINIMAX_API_KEY. Never logs authentication.
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import urllib.error
import urllib.request

BASES = {'https://api.minimax.cn/v1', 'https://api.minimaxi.com/v1'}
BASE = 'https://api.minimax.cn/v1'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def api(path, payload, base=BASE, timeout=120):
    if base not in BASES:
        raise ValueError('Only official mainland-China API bases are supported')
    key = os.environ.get('MINIMAX_CN_API_KEY') or os.environ.get('MINIMAX_API_KEY')
    if not key:
        raise RuntimeError('MINIMAX_CN_API_KEY or MINIMAX_API_KEY is required')
    request = urllib.request.Request(base + path, json.dumps(payload).encode(),
        {'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'})
    # Do not follow redirects carrying a bearer token to another origin.
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl): return None
    try:
        with urllib.request.build_opener(NoRedirect).open(request, timeout=timeout) as response:
            result = json.load(response)
    except urllib.error.HTTPError as exc:
        raise RuntimeError('MiniMax HTTP %s; no automatic retry' % exc.code) from None
    except (urllib.error.URLError, TimeoutError):
        raise RuntimeError('MiniMax network/timeout; outcome unknown, no automatic retry') from None
    status = result.get('base_resp', {})
    if 'status_code' not in status:
        raise RuntimeError('Missing MiniMax base_resp.status_code')
    if status['status_code'] != 0:
        # Remote messages may contain private data; persist only code/trace.
        raise RuntimeError('MiniMax API code %s; trace_id=%s' % (status['status_code'], result.get('trace_id', 'unknown')))
    return result


def payload(text, voice, model, speed):
    if not isinstance(text, str) or not text.strip() or len(text) > 10000:
        raise ValueError('Non-empty text up to 10000 characters required')
    if not voice or type(speed) not in (int,float) or not math.isfinite(speed) or not .5 <= speed <= 2:
        raise ValueError('Explicit voice and speed 0.5-2 required')
    return {'model': model, 'text': text, 'stream': False,
        'voice_setting': {'voice_id': voice, 'speed': speed, 'vol': 1, 'pitch': 0},
        'audio_setting': {'sample_rate': 32000, 'bitrate': 128000, 'format': 'mp3', 'channel': 1},
        'output_format': 'hex', 'subtitle_enable': False}


def decode(result):
    if result.get('data', {}).get('status') != 2:
        raise ValueError('TTS response not complete')
    try:
        audio = bytes.fromhex(result['data']['audio'])
    except (KeyError, TypeError, ValueError):
        raise ValueError('Missing or invalid audio hex') from None
    if not audio: raise ValueError('Empty audio')
    return audio


def synthesize(text, output, voice, model='speech-2.8-hd', speed=1.0, base=BASE, transport=api):
    request = payload(text, voice, model, speed)
    identity = sha(json.dumps({'base':base,'request':request}, sort_keys=True, ensure_ascii=False).encode())
    output = Path(output)
    # Resume only fully verified matching artifacts, never silently regenerate.
    if output.exists():
        manifest = json.loads((output/'voiceover-manifest.json').read_text())
        if manifest.get('status')!='technical_passed':
            raise ValueError('Existing incomplete output needs diagnosis; no new request sent')
        if manifest['request_sha256'] != identity or manifest['audio_sha256'] != sha((output/'配音.mp3').read_bytes()):
            raise ValueError('Existing output differs from requested text/voice/audio')
        return dict(manifest, reused=True)
    output.mkdir(parents=True, exist_ok=False)
    def record(data):
        (output/'voiceover-manifest.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    manifest = {'provider':'minimax_cn','api_base':base,'model':model,'voice_id':voice,'speed':speed,
        'request_sha256':identity,'text_sha256':sha(text.encode()),'status':'request_pending',
        'human_listening_verified':False,'subscription_billing':'not_proven_by_api_response'}
    record(manifest)
    try:
        result = transport('/t2a_v2', request, base=base)
        audio = decode(result)
        with (output/'配音.mp3').open('xb') as stream: stream.write(audio)
        manifest.update(status='audio_saved',audio_sha256=sha(audio),trace_id=result.get('trace_id'),
            usage_characters=result.get('extra_info',{}).get('usage_characters'))
        record(manifest)
        probe = subprocess.run(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(output/'配音.mp3')],capture_output=True,text=True,check=True)
        info = json.loads(probe.stdout)
        duration = float(info['format']['duration'])
        if not math.isfinite(duration) or duration<=0 or not any(s.get('codec_type')=='audio' for s in info['streams']):
            raise ValueError('Invalid decoded audio duration/stream')
        subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(output/'配音.mp3'),'-f','null','-'],check=True,capture_output=True)
        manifest.update(status='technical_passed',duration_s=duration)
        record(manifest)
        return manifest
    except Exception as exc:
        manifest.update(status='failed_or_unknown',error_type=type(exc).__name__,
                        retry_note='Preserve artifacts; diagnose before sending another generation request')
        record(manifest)
        raise


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--api-base', choices=sorted(BASES),default=BASE)
    sub=p.add_subparsers(dest='command',required=True)
    sub.add_parser('voices')
    generation=sub.add_parser('synthesize')
    generation.add_argument('--text-file',type=Path,required=True)
    generation.add_argument('--output-dir',type=Path,required=True)
    generation.add_argument('--voice',required=True)
    generation.add_argument('--model',default='speech-2.8-hd')
    generation.add_argument('--speed',type=float,default=1)
    args=p.parse_args()
    if args.command=='voices':
        result=api('/get_voice',{'voice_type':'system'},base=args.api_base)
        print(json.dumps({'system_voice':result.get('system_voice',[]),'trace_id':result.get('trace_id')},ensure_ascii=False,indent=2))
    else:
        print(json.dumps(synthesize(args.text_file.read_text(encoding='utf-8'),args.output_dir,args.voice,args.model,args.speed,args.api_base),ensure_ascii=False,indent=2))


if __name__=='__main__':main()
